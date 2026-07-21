import uuid
import asyncio
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
async def convert_video(payload: ConvertRequest, request: Request, background_tasks: BackgroundTasks):
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
        
        # 3. Exécution asynchrone: On lance yt-dlp dans un thread séparé
        # pour ne pas bloquer les autres utilisateurs pendant le téléchargement
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

    # Ajout de la tâche de fond pour supprimer le fichier
    background_tasks.add_task(remove_file, file_path)
    
    encoded_filename = quote(final_filename)

    return FileResponse(
        path=file_path,
        filename=final_filename,
        media_type='audio/mpeg',
        headers={"Content-Disposition": f'attachment; filename="{encoded_filename}"'}
    )
