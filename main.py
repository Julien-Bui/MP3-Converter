import uuid
from urllib.parse import quote, urlparse
from fastapi import FastAPI, BackgroundTasks, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from config import API_KEY
from services import extract_and_convert_audio, remove_file
from frontend import get_frontend_html

app = FastAPI(title="YouTube to MP3 Converter")

class ConvertRequest(BaseModel):
    url: str

def verify_api_key(x_api_key: str = Header(None)):
    """Vérifie la présence et la validité de la clé API si elle est configurée."""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Clé API invalide ou manquante")
    return x_api_key

def is_valid_youtube_url(url: str) -> bool:
    """Vérifie que l'URL appartient bien à YouTube pour éviter le SSRF (Server-Side Request Forgery)."""
    try:
        parsed = urlparse(url)
        # Liste des domaines autorisés
        allowed_domains = ["www.youtube.com", "youtube.com", "youtu.be", "m.youtube.com"]
        return parsed.netloc in allowed_domains
    except Exception:
        return False

@app.get("/", response_class=HTMLResponse)
async def index():
    """Route principale affichant l'interface web."""
    return get_frontend_html()

@app.post("/api/convert")
async def convert_video(request: ConvertRequest, background_tasks: BackgroundTasks, x_api_key: str = Depends(verify_api_key)):
    """Route API pour convertir une vidéo YouTube en MP3."""
    url = request.url
    
    # Sécurité: Validation de l'URL
    if not is_valid_youtube_url(url):
        raise HTTPException(status_code=400, detail="URL invalide. Seuls les liens YouTube sont autorisés.")

    task_id = uuid.uuid4().hex
    
    # 1. Extraction et conversion via les fonctions utilitaires
    file_path, final_filename = extract_and_convert_audio(url, task_id)

    # 2. Ajout de la tâche de fond pour supprimer le fichier après le téléchargement
    background_tasks.add_task(remove_file, file_path)
    
    # 3. Encodage du nom de fichier pour le header HTTP
    encoded_filename = quote(final_filename)

    return FileResponse(
        path=file_path,
        filename=final_filename,
        media_type='audio/mpeg',
        headers={"Content-Disposition": f'attachment; filename="{encoded_filename}"'}
    )
