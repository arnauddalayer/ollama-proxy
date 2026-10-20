# Changelog

## 2026-10-20

- Les en-têtes `CF-Access-*`, `Authorization`, `Cookie` et hop-by-hop du client ne sont plus relayés; les redirections ne sont plus suivies.
- Réponse 502/504 avec message dans la console si l'instance distante est injoignable ou trop lente.
- Prise en charge de `HEAD`; `content-encoding` est conservé pour rester cohérent avec les octets relayés.
- Interface web : ressources (Tailwind, Prism) hébergées localement, CSP, titre des discussions affiché sans interprétation HTML.
- Correction du Basic Auth avec des caractères non ASCII; `/` est relayé vers Ollama quand `ENABLE_UI=False`.
- `W_go.bat` s'exécute depuis son propre dossier; `index.html` est trouvé indépendamment du dossier courant.
- `M_go.command` lance le proxy avec uvicorn.
- Dépendances : versions minimales et limite de version majeure dans `requirements.txt`.
- Ajout de la licence MIT.

## 2026-09-22

- Version initiale.
