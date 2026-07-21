import uuid
import asyncio
import os
from urllib.parse import quote, urlparse
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from services import extract_and_convert_audio, remove_file
from frontend import get_frontend_html

# 1. Rate Limiting: 5 requêtes par minute par IP
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="YouTube to MP3 Converter")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Contrôle de concurrence: Maximum 3 conversions simultanées pour protéger le CPU/RAM
MAX_CONCURRENT_CONVERSIONS = 3
conversion_semaphore = asyncio.Semaphore(MAX_CONCURRENT_CONVERSIONS)

class ConvertRequest(BaseModel):
    url: str

def is_valid_youtube_url(url: str) -> bool:
    """Vérifie que l'URL appartient bien à YouTube pour éviter le SSRF."""
    try:
        parsed = urlparse(url)
        allowed_domains = ["www.youtube.com", "youtube.com", "youtu.be", "m.youtube.com"]
        return parsed.netloc in allowed_domains
    except Exception:
        return False

@app.get("/", response_class=HTMLResponse)
async def index():
    """Route principale affichant l'interface web."""
    return get_frontend_html()

@app.post("/api/convert")
@limiter.limit("5/minute")
async def convert_video(payload: ConvertRequest, request: Request):
    """Route API pour convertir une vidéo YouTube en MP3."""
    url = payload.url
    
    # Validation de l'URL
    if not is_valid_youtube_url(url):
        raise HTTPException(status_code=400, detail="URL invalide. Seuls les liens YouTube sont autorisés.")

    # On s'assure de ne pas surcharger le serveur
    if conversion_semaphore.locked():
        print("Serveur en charge, la requête est mise en file d'attente...")
        
    async with conversion_semaphore:
        task_id = uuid.uuid4().hex
        
        # Exécution asynchrone pour ne pas bloquer les autres utilisateurs
        loop = asyncio.get_running_loop()
        try:
            file_path, final_filename = await loop.run_in_executor(
                None, extract_and_convert_audio, url, task_id
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            print(f"Erreur d'exécution: {e}")
            raise HTTPException(status_code=500, detail="Erreur interne lors de la conversion")

    # On retourne un lien pour le téléchargement natif au lieu d'envoyer le fichier directement
    return {"file_id": task_id, "filename": final_filename}

@app.get("/api/download/{file_id}")
async def download_file(file_id: str, name: str, background_tasks: BackgroundTasks):
    """Route pour télécharger le fichier et le supprimer ensuite de façon sûre."""
    if not file_id.isalnum():
        raise HTTPException(status_code=400, detail="ID invalide")
    
    file_path = f"tmp_{file_id}.mp3"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier introuvable ou déjà téléchargé")
        
    # Le fichier sera supprimé après que le téléchargement soit terminé
    background_tasks.add_task(remove_file, file_path)
    
    encoded_filename = quote(name)
    return FileResponse(
        path=file_path,
        filename=name,
        media_type='audio/mpeg',
        headers={"Content-Disposition": f'attachment; filename="{encoded_filename}"'}
    )
