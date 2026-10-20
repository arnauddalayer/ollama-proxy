from pathlib import Path
import secrets

import httpx
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

from config import TARGET, CF_HEADERS, UI_USERNAME, UI_PASSWORD, ENABLE_UI, VERBOSE_LOGGING

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
security = HTTPBasic()

# L'interface n'utilise que des ressources locales (aucun CDN).
UI_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "frame-ancestors 'none'"
)


def require_ui_auth(credentials: HTTPBasicCredentials = Depends(security)):
    # compare_digest sur des str lève une TypeError si elles contiennent des caractères non ASCII
    valid_user = secrets.compare_digest(credentials.username.encode("utf-8"), UI_USERNAME.encode("utf-8"))
    valid_pass = secrets.compare_digest(credentials.password.encode("utf-8"), UI_PASSWORD.encode("utf-8"))
    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=401,
            detail="Authentification requise",
            headers={"WWW-Authenticate": "Basic"},
        )

# Pas de suivi des redirections : httpx ne retire pas les en-têtes CF-Access-*
# lors d'une redirection vers un autre domaine (ex. page de login Cloudflare Access).
client = httpx.AsyncClient(
    timeout=httpx.Timeout(600, connect=10),
    follow_redirects=False,
)

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}

# Ollama n'utilise ni Authorization ni Cookie. Les retirer évite de transmettre
# à l'instance distante les identifiants de l'interface web (Basic Auth) ou les
# cookies d'autres applications locales (les cookies ne sont pas isolés par port).
REQUEST_EXCLUDED_HEADERS = HOP_BY_HOP_HEADERS | {
    "host",
    "content-length",
    "accept-encoding",
    "authorization",
    "cookie",
}

# Les octets sont relayés tels quels (aiter_raw) : content-encoding doit donc
# être conservé pour rester cohérent avec le contenu, mais pas content-length.
RESPONSE_EXCLUDED_HEADERS = HOP_BY_HOP_HEADERS | {"content-length"}

# Routes de l'interface web, déclarées AVANT la route "catch-all" (proxy).
# Si l'UI est désactivée, ces routes n'existent pas : "/" est alors relayé vers Ollama,
# comme avec une instance locale.
if ENABLE_UI:
    @app.get("/")
    @app.get("/index.html")
    async def read_root(_auth: None = Depends(require_ui_auth)):
        return FileResponse(BASE_DIR / "index.html", headers={"Content-Security-Policy": UI_CSP})

    # Ressources publiques (Tailwind, Prism) : pas d'authentification requise.
    app.mount("/ui-static", StaticFiles(directory=BASE_DIR / "static"), name="ui-static")
# -----------------

@app.api_route(
    "/{path:path}",
    methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
)
async def proxy(path: str, request: Request):
    body = await request.body()

    # Copier les headers reçus, sauf ceux qui ne doivent pas être relayés.
    # Les en-têtes CF-Access-* du client sont ignorés (comparaison insensible
    # à la casse) pour que seules les valeurs de config.py soient envoyées.
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in REQUEST_EXCLUDED_HEADERS
        and not k.lower().startswith("cf-access-")
    }

    # Éviter la compression Brotli/Gzip
    headers["accept-encoding"] = "identity"

    # Ajouter les headers Cloudflare Access
    headers.update(CF_HEADERS)

    if VERBOSE_LOGGING:
        print(f"{request.method} /{path}")

    req = client.build_request(
        method=request.method,
        url=f"{TARGET}/{path}",
        headers=headers,
        params=request.query_params,
        content=body,
    )
    try:
        resp = await client.send(req, stream=True)
    except httpx.TimeoutException as exc:
        print(f"[ERREUR] Délai dépassé vers Ollama distant ({type(exc).__name__}) : {request.method} /{path}")
        return JSONResponse({"error": "Ollama distant : délai dépassé"}, status_code=504)
    except httpx.RequestError as exc:
        print(f"[ERREUR] Ollama distant injoignable ({type(exc).__name__}) : {request.method} /{path}")
        return JSONResponse({"error": "Ollama distant injoignable"}, status_code=502)

    if VERBOSE_LOGGING:
        print(f"{request.method} /{path} -> {resp.status_code}")

    response_headers = {
        k: v
        for k, v in resp.headers.items()
        if k.lower() not in RESPONSE_EXCLUDED_HEADERS
    }

    async def stream_body():
        try:
            async for chunk in resp.aiter_raw():
                yield chunk
        except (httpx.ReadError, httpx.RemoteProtocolError):
            # En cas d'erreur de lecture ou de protocole, on arrête le générateur.
            # La connexion a été interrompue par le serveur distant ou le réseau.
            pass
        finally:
            await resp.aclose()

    return StreamingResponse(
        stream_body(),
        status_code=resp.status_code,
        headers=response_headers,
        media_type=resp.headers.get("content-type"),
    )
