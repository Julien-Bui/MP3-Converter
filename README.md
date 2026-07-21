# YouTube to MP3 Converter 🎵

Un service web léger et rapide pour télécharger l'audio de vidéos YouTube au format MP3 de haute qualité, sans publicité. 

## Fonctionnalités

* 🚀 **Extraction rapide** : Convertit les vidéos YouTube en MP3 (192kbps).
* 🛡️ **Sécurité anti-abus** : Limite de requêtes (5/min par IP), blocage de l'IP, protection SSRF (seul YouTube est autorisé).
* 🚦 **Gestion de la mémoire** : File d'attente (3 conversions max simultanées) et tâches asynchrones.
* 💾 **Nettoyage automatique** : Les fichiers MP3 temporaires sont supprimés immédiatement après le téléchargement.
* 🐳 **Prêt pour Docker** : Déploiement ultra simple via Railway ou tout autre service compatible Docker.

## Prérequis locaux

- Python 3.11+
- FFmpeg (doit être installé sur votre machine/serveur)

## Installation & Lancement

1. Clonez ce dépôt :
```bash
git clone https://github.com/Julien-Bui/MP3-Converter.git
cd mp3-converter
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancez le serveur localement :
```bash
uvicorn main:app --reload
```
Ouvrez votre navigateur sur `http://localhost:8000`.

## Déploiement (Railway)

Ce projet est conçu pour être déployé sur [Railway.app](https://railway.app/).
1. Connectez Railway à votre dépôt GitHub.
2. L'application détectera automatiquement le `Dockerfile` et se lancera !
