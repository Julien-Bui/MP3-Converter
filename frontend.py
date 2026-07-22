def get_frontend_html() -> str:
    """Génère et retourne le code HTML/CSS/JS d'une interface simpliste."""
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube MP3 Downloader</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                background-color: #0f172a;
                color: #f8fafc;
                margin: 0;
            }}
            .card {{
                background-color: #1e293b;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
                text-align: center;
                width: 90%;
                max-width: 400px;
            }}
            h2 {{
                margin-top: 0;
                color: #f8fafc;
            }}
            input[type="text"] {{
                width: 100%;
                padding: 12px;
                margin: 15px 0;
                border: 1px solid #334155;
                background-color: #0f172a;
                color: white;
                border-radius: 4px;
                box-sizing: border-box;
                font-size: 16px;
            }}
            input[type="text"]:focus {{
                outline: none;
                border-color: #ef4444;
            }}
            button {{
                width: 100%;
                padding: 12px;
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                transition: background-color 0.3s;
            }}
            button:hover {{
                background-color: #dc2626;
            }}
            button:disabled {{
                background-color: #475569;
                cursor: not-allowed;
                color: #94a3b8;
            }}
            #status {{
                margin-top: 15px;
                font-size: 14px;
                min-height: 20px;
            }}
            .error {{ color: #ef4444; }}
            .success {{ color: #10b981; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>YouTube vers MP3</h2>
            <input type="text" id="url" placeholder="Lien YouTube (ex: https://youtu.be/...)" required />
            <button id="btn" onclick="convert()">Télécharger MP3</button>
            <div id="status"></div>
        </div>
        <script>
            async function convert() {{
                const url = document.getElementById('url').value.trim();
                const btn = document.getElementById('btn');
                const status = document.getElementById('status');
                
                if (!url) {{ 
                    status.innerHTML = "<span class='error'>Veuillez entrer un lien.</span>"; 
                    return; 
                }}
                
                btn.disabled = true;
                status.innerHTML = "Téléchargement et conversion en cours...";
                
                try {{
                    const res = await fetch('/api/convert', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ url: url }})
                    }});
                    
                    if (res.ok) {{
                        const data = await res.json();
                        
                        // Déclenche un vrai téléchargement via le navigateur
                        const downloadUrl = `/api/download/${{data.file_id}}?name=${{encodeURIComponent(data.filename)}}`;
                        window.location.href = downloadUrl;
                        
                        status.innerHTML = "<span class='success'>Téléchargement en cours !</span>";
                        document.getElementById('url').value = '';
                    }} else {{
                        const data = await res.json();
                        status.innerHTML = `<span class='error'>Erreur : ${{data.detail}}</span>`;
                    }}
                }} catch (e) {{
                    status.innerHTML = "<span class='error'>Erreur de connexion au serveur.</span>";
                }} finally {{
                    btn.disabled = false;
                }}
            }}
        </script>
    </body>
    </html>
    """
