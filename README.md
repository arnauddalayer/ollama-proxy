# ollama-proxy

## Présentation

Cette solution vise à rendre accessible une instance Ollama distante au travers de Cloudflare Zero Trust, sans exposer directement Ollama sur Internet, notamment au moyen d'un reverse proxy traditionnel (par exemple Nginx Proxy Manager).

---

## Objectifs

Cette architecture est particulièrement utile lorsque le poste de travail de l'utilisateur ne dispose pas des ressources matérielles nécessaires à l'exécution efficace de modèles de langage locaux.

Le projet permet ainsi de déporter la charge d'inférence vers une machine plus puissante hébergeant Ollama (par exemple un poste fixe à domicile ou un serveur personnel équipé d'un GPU adapté), tout en conservant une expérience comparable à celle d'une instance Ollama locale.

Ce projet répond également à une autre problématique fréquente : de nombreux outils (Cline, Continue, Roo Code, etc.) s'attendent à communiquer avec une instance Ollama locale (`http://localhost:11434`) et ne permettent pas toujours d'ajouter les en-têtes HTTP requis pour l'authentification Cloudflare Access.

### Cas d'usage typique

Un utilisateur travaille sur un ordinateur portable professionnel ne disposant pas d'un GPU suffisamment puissant pour exécuter localement des modèles modernes.

Le proxy lui permet :

- d'utiliser ses outils habituels (Cline, Continue, Roo Code, etc.);
- de conserver une configuration Ollama locale standard;
- de déporter les traitements vers une machine personnelle plus puissante;
- de protéger l'accès à cette machine via Cloudflare Zero Trust.

## Fonctionnement et architecture générale

Le script `proxy.py` agit comme un proxy local. Il se présente comme une instance Ollama locale auprès des applications clientes, puis ajoute automatiquement les en-têtes d'authentification nécessaires avant de transmettre les requêtes vers votre infrastructure Cloudflare Zero Trust.

L'utilisation d'un Service Token Cloudflare permet au proxy de s'authentifier de manière automatisée, sans intervention de l'utilisateur. Cette approche est également rendue nécessaire par le fait que de nombreux clients compatibles Ollama (Cline, Continue, Roo Code, etc.) ne prennent en charge que l'API Ollama standard et n'offrent pas de mécanisme intégré pour réaliser une authentification utilisateur Cloudflare Access au moyen d'un flux OAuth, OpenID Connect ou autre méthode d'authentification interactive.

Le proxy joue ainsi un double rôle :

- présenter une interface Ollama locale standard aux applications clientes;
- injecter automatiquement les en-têtes d'authentification Cloudflare Access requis pour accéder à l'instance Ollama distante protégée par Zero Trust.

### Schéma

```text
+--------------------------+
| Poste de travail         |
|                          |
|  Cline / Continue / etc. |
|           |              |
|           v              |
|      proxy.py            |
|      localhost:11434     |
+-----------|--------------+
            |
            | HTTPS + Service Token
            v
+--------------------------+
| Cloudflare Zero Trust    |
+-----------|--------------+
            |
            | Tunnel Cloudflare
            v
+--------------------------+
| Réseau domestique        |
|                          |
| cloudflared              |
|           |              |
|           v              |
|        Ollama            |
|      port 11434          |
+--------------------------+
```

### Emplacement des composants

Dans le scénario visé :

- `proxy.py` est exécuté sur le poste de travail de l'utilisateur (bureau, ordinateur portable, etc.);
- `cloudflared` est exécuté sur une machine située à domicile ou dans le réseau hébergeant Ollama.
- `Ollama` peut être installé :
  - sur la même machine que `cloudflared` ;
  - sur une autre machine du même réseau local.

Le proxy local et l'instance Ollama peuvent donc être géographiquement séparés.

## Structure du projet

```text
src/
├── proxy.py                    # Script principal
├── index.html                  # Interface de clavardage minimale (facultative)
├── static/                     # Ressources de l'interface (Tailwind, Prism), hébergées localement
├── config.example.py           # Exemple de configuration
├── config.py                   # Copie personnalisée de config.example.py (non versionnée)
├── requirements.txt            # Dépendances Python
├── W_install_requirements.bat  # Installation sous Windows
├── W_go.bat                    # Exécution sous Windows
├── M_install_requirements.command  # Installation sous macOS/Linux
└── M_go.command                # Exécution sous macOS/Linux
```

## Prérequis

### Infrastructure Ollama

Préparez la machine hébergeant Ollama :

- configurez une adresse IP fixe ou une réservation DHCP;
- configurez Ollama pour accepter les connexions depuis le réseau local;
- vérifiez que l'instance est accessible sur le port 11434.

### Infrastructure Cloudflare

Vous devez :

- disposer d'un compte Cloudflare;
- disposer d'un nom de domaine géré par Cloudflare;
- installer et configurer un tunnel Cloudflare;
- installer un connecteur `cloudflared` sur votre réseau domestique (Docker ou installation native).

Créer ensuite une route entre un sous-domaine et votre instance Ollama :

```text
ollama.mondomaine.com
          |
          v
http://192.168.1.101:11434
```

### Configuration Zero Trust

Dans Cloudflare Zero Trust :

1. créez une Application Access associée au sous-domaine;
2. créez un Service Token;
3. créez une politique d'accès autorisant ce Service Token;
4. associez cette politique à l'application créée précédemment.

Les valeurs du Service Token seront utilisées par `proxy.py`.

---

## Installation

### 1. Installer Python

Installez Python 3.10 ou plus récent (testé avec Python 3.14), ou utilisez un environnement Miniforge/Conda.

### 2. Installer les dépendances

Sous Windows :

```cmd
W_install_requirements.bat
```

Sous macOS/Linux :

```bash
./M_install_requirements.command
```

Ces scripts :

- créent un environnement virtuel `.venv`;
- installent les dépendances requises.

### 3. Configurer le proxy

Copiez `config.example.py` vers `config.py`, puis renseignez les valeurs. Chaque paramètre peut aussi être fourni par une variable d'environnement, qui a priorité sur la valeur par défaut du fichier :

| Variable d'environnement | Rôle | Valeur par défaut |
|---|---|---|
| `OLLAMA_PROXY_TARGET` | URL Cloudflare de votre instance Ollama | `https://ollama.mondomaine.com` |
| `CF_ACCESS_CLIENT_ID` | Client ID du Service Token | `REPLACE_ME` |
| `CF_ACCESS_CLIENT_SECRET` | Secret du Service Token | `REPLACE_ME` |
| `UI_USERNAME` | Utilisateur de l'interface web (Basic Auth) | `admin` |
| `UI_PASSWORD` | Mot de passe de l'interface web (**à changer**) | `changeme` |
| `ENABLE_UI` | Active l'interface web (`True` / `False`) | `True` |
| `VERBOSE_LOGGING` | Journalise chaque requête dans la console | `False` |

## Utilisation

Sous Windows :

```cmd
W_go.bat
```

Sous macOS/Linux :

```bash
./M_go.command
```

Une fois lancé :

- le proxy écoute localement sur `http://localhost:11434`;
- les applications compatibles Ollama (Cline, Continue, etc.) peuvent être configurées comme si Ollama était installé localement;
- si l'instance distante est injoignable, le proxy répond par une erreur HTTP 502 (ou 504 en cas de délai dépassé) avec un message JSON, et l'affiche dans la console.

Une interface de clavardage minimale est également disponible à :

```text
http://localhost:11434/index.html
```

Elle fonctionne sans accès à des CDN externes (toutes ses ressources sont servies localement), ce qui la rend compatible avec les bloqueurs de contenu.

## Architecture et revue de sécurité

L'architecture repose sur un modèle **Zero Trust** via Cloudflare :

- **Authentification :** le proxy local utilise un Service Token Cloudflare. Cela garantit que seules les requêtes provenant d'un proxy configuré avec ce jeton peuvent traverser le tunnel Cloudflare;
- **Chiffrement :** le flux entre le poste de travail et Cloudflare est chiffré en HTTPS;
- **Aucune exposition directe d'Ollama sur Internet**.

### Comportement du proxy

- Comme Ollama, le proxy n'authentifie pas les requêtes `/api/*` : tout programme qui s'exécute sur le poste local peut s'en servir, avec les accès de votre Service Token.
- Les en-têtes `CF-Access-*` envoyés par les clients sont ignorés : seuls ceux de `config.py` sont transmis.
- Les en-têtes `Authorization` et `Cookie` ne sont pas relayés vers l'instance distante (Ollama ne les utilise pas), ce qui évite de lui transmettre les identifiants de l'interface web ou des cookies d'autres applications locales.
- Les redirections ne sont pas suivies, afin que les en-têtes d'authentification Cloudflare ne soient jamais envoyés à un autre domaine.

### Vulnérabilités potentielles et mitigations

- En éditant le fichier `W_go.bat` (ou `M_go.command`), il est possible d'exécuter le proxy sur `0.0.0.0`, ce qui rend le proxy accessible depuis d'autres machines du réseau local. **Ces machines pourraient alors utiliser votre Service Token sans authentification.** Si cela n'est pas requis, assurez-vous que le proxy n'écoute que sur `127.0.0.1`.
- Une attention particulière doit être portée sur le segment final du tunnel : la communication entre le connecteur `cloudflared` et l'instance Ollama.
- Si `cloudflared` et Ollama résident sur deux machines distinctes au sein de votre réseau domestique, ce segment de communication est local.
- Bien que ce segment soit hors de portée d'Internet, il est recommandé de s'assurer que ce réseau local est sécurisé, par exemple à l'aide d'un VLAN dédié.
- Le fichier `config.py` peut contenir des secrets Cloudflare. Son accès doit être limité aux utilisateurs autorisés et le fichier ne doit jamais être publié dans un dépôt Git. L'utilisation de variables d'environnement pour le stockage des secrets est recommandée pour les déploiements plus sensibles.
- L'interface web (`index.html`) n'est protégée que par une authentification HTTP Basic, qui ne protège **que la page elle-même** et non l'API `/api/*` (voir plus haut). Cette authentification n'assure pas non plus le chiffrement des identifiants : pour un accès exclusivement local, cela ne constitue généralement pas un problème, mais cette considération devient importante si le proxy est rendu accessible à d'autres machines du réseau. Changez le mot de passe par défaut. L'interface demeure facultative et peut être désactivée via la variable `ENABLE_UI` (dans ce cas, `/` est relayé vers Ollama).
- L'interface web affiche du contenu généré par le LLM. Celui-ci est échappé avant l'affichage, et une politique de sécurité de contenu (CSP) n'autorise que les ressources locales. Les discussions sont conservées dans le `localStorage` du navigateur, en clair.

### Gouvernance, conformité et usage (Important)

Le script `proxy.py` agit comme un tunnel transparent. Aucun filtrage de contenu ou anonymisation des données n'est effectué.

Bien que la connexion soit techniquement sécurisée et chiffrée, l'utilisateur doit s'assurer que les types de données envoyés à l'instance Ollama distante sont conformes à la politique de confidentialité de son organisation.

## Changelog et licence

Voir [CHANGELOG.md](CHANGELOG.md). Ce projet est distribué sous licence MIT (voir [LICENSE](LICENSE)).

## Utilisation de l'IAg

La création de ce projet a été réalisée avec l’IA (en local avec gemma4:12b via Ollama, et avec Github Copilot en mode auto).

<img alt="Réalisé avec l'IA" loading="lazy" src="https://d1qywhc7l90rsa.cloudfront.net/accounts/152505/images/Label-IA_fondclair.png" width="200" height="80">