# YouTube to MP3 Converter 🎵

Un service web léger et rapide pour télécharger l'audio de vidéos YouTube au format MP3 de haute qualité, sans publicité. 

## Fonctionnalités

* 🚀 **Extraction rapide** : Convertit les vidéos YouTube en MP3 (192kbps).
* 🤖 **Contournement anti-bot** : PO tokens générés localement — aucune authentification YouTube requise.
* 🛡️ **Sécurité anti-abus** : Limite de requêtes (5/min par IP), blocage de l'IP, protection SSRF (seul YouTube est autorisé).
* 🚦 **Gestion de la mémoire** : File d'attente (3 conversions max simultanées) et tâches asynchrones.
* 💾 **Nettoyage automatique** : Les fichiers MP3 temporaires sont supprimés immédiatement après le téléchargement.
* 🐳 **Prêt pour Docker** : Déploiement ultra simple via Railway ou tout autre service compatible Docker.

## Prérequis locaux

- Python 3.11+
- FFmpeg (doit être installé sur votre machine/serveur)
- Node.js >= 22 (optionnel, pour le contournement anti-bot — voir ci-dessous)

## Installation & Lancement

1. Clonez ce dépôt :
```bash
git clone https://github.com/Julien-Bui/MP3-Converter.git
cd MP3-Converter
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. (Optionnel, recommandé) Installez le générateur de PO tokens :
```bash
git clone --single-branch --branch 2.0.0 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git
cd bgutil-ytdlp-pot-provider/server && npm ci && npx tsc && cd ../..
```

4. Lancez le serveur localement :
```bash
uvicorn main:app --reload
```
Ouvrez votre navigateur sur `http://localhost:8000`.

## Contournement anti-bot YouTube (PO tokens)

YouTube bloque les téléchargements provenant d'IP de datacenter (erreur *« Sign in to confirm you're not a bot »*). Ce projet intègre le plugin [bgutil-ytdlp-pot-provider](https://github.com/Brainicism/bgutil-ytdlp-pot-provider), qui génère des **PO tokens** pour répondre à ce défi **sans compte YouTube** — aucun risque de suspension de compte, aucun cookie à gérer.

- **Docker** : rien à faire, le `Dockerfile` télécharge et compile le générateur automatiquement.
- **Local** : suivez l'étape 3 de l'installation ci-dessus.
- Sa présence est **facultative** : s'il est absent, le plugin se désactive proprement et les conversions restent possibles (sauf si l'IP est bloquée par YouTube).

### Variables d'environnement

| Variable | Défaut | Rôle |
|---|---|---|
| `BGUTIL_SERVER_HOME` | `bgutil-ytdlp-pot-provider/server` | Chemin du générateur de PO tokens |
| `YTDLP_COOKIES_FILE` | `cookies.txt` | Fichier de cookies YouTube (fallback optionnel, voir ci-dessous) |

### Fallback : cookies YouTube (déconseillé)

En dernier recours, un fichier de cookies au format Netscape peut être fourni via `YTDLP_COOKIES_FILE`. ⚠️ **À n'utiliser qu'avec un compte secondaire** : YouTube peut suspendre un compte utilisé pour du scraping. Ce fichier contient vos identifiants de session : ne le **commitez jamais** (déjà exclu via `.gitignore` et `.dockerignore`) et restreignez ses droits (`chmod 600 cookies.txt`). Les cookies expirent et doivent être renouvelés régulièrement.

## Déploiement (Railway)

Ce projet est conçu pour être déployé sur [Railway.app](https://railway.app/).
1. Connectez Railway à votre dépôt GitHub.
2. L'application détectera automatiquement le `Dockerfile` et se lancera !

## Licence

Distribué sous la licence [MIT](LICENSE). Voir `LICENSE` pour plus d'informations.

