import os
import logging
import yt_dlp
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Signal interne injecté dans le message yt-dlp pour identifier un refus dû à la durée.
_DURATION_REJECT_SIGNAL = "MP3CONVERTER_DURATION_EXCEEDED"

# Fichier de cookies YouTube (format Netscape) pour passer la vérification anti-bot.
# Chemin configurable via la variable d'environnement YTDLP_COOKIES_FILE.
_COOKIES_FILE = os.environ.get("YTDLP_COOKIES_FILE", "cookies.txt")

# Générateur de PO tokens (plugin bgutil) : contourne le "Sign in to confirm you're
# not a bot" SANS compte YouTube. Nécessite le dépôt bgutil-ytdlp-pot-provider
# (chemin configurable via BGUTIL_SERVER_HOME) et Node.js >= 22 ou Deno.
_BGUTIL_SERVER_HOME = os.environ.get("BGUTIL_SERVER_HOME", "bgutil-ytdlp-pot-provider/server")

def remove_file(path: str):
    """Supprime un fichier s'il existe (utilisé en tâche de fond)."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.warning("Erreur lors de la suppression de %s: %s", path, e)

def sanitize_filename(video_title: str, fallback_name: str) -> str:
    """Nettoie le titre pour générer un nom de fichier valide."""
    safe_title = "".join([c for c in video_title if c.isalnum() or c in (' ', '-', '_')]).strip()
    if not safe_title:
        safe_title = fallback_name
    return f"{safe_title}.mp3"

def duration_filter(info, *, incomplete):
    """Filtre de sécurité : refuse les vidéos de plus de 20 minutes."""
    duration = info.get('duration')
    if duration and duration > 1200:  # 20 minutes = 1200 secondes
        return _DURATION_REJECT_SIGNAL
    return None

def extract_and_convert_audio(url: str, task_id: str) -> tuple[str, str]:
    """
    Télécharge la vidéo via yt-dlp, extrait l'audio et le convertit en MP3 via FFmpeg.
    Retourne un tuple: (chemin_du_fichier_temporaire, nom_du_fichier_final).
    """
    output_filename = f"tmp_{task_id}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_filename}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        # Les clients par défaut de yt-dlp gèrent seuls la rotation anti-403.
        # PO tokens via le plugin bgutil : anti-bot sans compte YouTube
        # (le plugin ignore proprement ce chemin si le script est absent).
        'extractor_args': {
            'youtubepot-bgutilscript': {
                'server_home': _BGUTIL_SERVER_HOME,
            }
        },
        'quiet': True,
        'no_warnings': True,
        'match_filter': duration_filter,
        'max_filesize': 50 * 1024 * 1024,  # Sécurité : taille max 50 MB
    }

    # Authentification par cookies si le fichier est fourni (requis sur IP de datacenter).
    if os.path.exists(_COOKIES_FILE):
        ydl_opts['cookiefile'] = _COOKIES_FILE

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', f'audio_{task_id}')
            final_filename = sanitize_filename(video_title, f"audio_{task_id}")
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if _DURATION_REJECT_SIGNAL in error_msg:
            raise HTTPException(status_code=400, detail="La vidéo dépasse la durée maximale autorisée (20 minutes).")
        if "Sign in to confirm" in error_msg:
            logger.error(
                "Blocage anti-bot YouTube: PO tokens inefficaces (serveur bgutil absent sur %s ?) "
                "et aucun cookies fourni (%s)", _BGUTIL_SERVER_HOME, _COOKIES_FILE
            )
            raise HTTPException(
                status_code=503,
                detail="YouTube bloque les requêtes de ce serveur (vérification anti-bot). "
                       "L'administrateur doit vérifier le générateur de PO tokens (BGUTIL_SERVER_HOME) "
                       "ou fournir un fichier de cookies (YTDLP_COOKIES_FILE)."
            )
        # On affiche l'erreur yt-dlp (utile à l'utilisateur : vidéo privée, indisponible, etc.)
        logger.warning("Échec yt-dlp: %s", error_msg)
        raise HTTPException(status_code=400, detail=f"Erreur yt-dlp: {error_msg}")
    except Exception as e:
        logger.exception("Erreur inattendue pendant la conversion")
        raise HTTPException(status_code=500, detail="Erreur interne lors de la conversion.")

    file_path = f"{output_filename}.mp3"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Le fichier MP3 n'a pas pu être généré")

    return file_path, final_filename
