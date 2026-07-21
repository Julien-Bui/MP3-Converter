import os
import yt_dlp
from fastapi import HTTPException

def remove_file(path: str):
    """Supprime un fichier s'il existe (utilisé en tâche de fond)."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Erreur lors de la suppression de {path}: {e}")

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
        return 'La vidéo est trop longue (limite de sécurité: 20 minutes).'
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
        # ASTUCE ANTI-BOT : Forcer yt-dlp à se faire passer pour un téléphone Android
        'extractor_args': {
            'youtube': {
                'client': ['android', 'ios', 'tv', 'web']
            }
        },
        'quiet': True,
        'no_warnings': True,
        'match_filter': duration_filter,
        'max_filesize': 50 * 1024 * 1024,  # Sécurité : taille max 50 MB
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', f'audio_{task_id}')
            final_filename = sanitize_filename(video_title, f"audio_{task_id}")
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "limite de sécurité" in error_msg:
            raise HTTPException(status_code=400, detail="La vidéo dépasse la durée maximale autorisée (20 minutes).")
        # On affiche l'erreur exacte pour le debug
        raise HTTPException(status_code=400, detail=f"Erreur yt-dlp: {error_msg}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

    file_path = f"{output_filename}.mp3"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Le fichier MP3 n'a pas pu être généré")

    return file_path, final_filename
