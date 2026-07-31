def get_frontend_html() -> str:
    """Génère et retourne le code HTML/CSS/JS d'une interface premium Vercel/Linear-like."""
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube MP3 - Premium</title>
        
        <!-- Space Grotesk pour le titre -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">
        
        <!-- Inter pour le reste de l'UI -->
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

        <!-- Lucide Icons -->
        <script src="https://unpkg.com/lucide@latest"></script>

        <style>
            :root {{
                --bg-body: #0A0A0A;
                --bg-card: #141414;
                --border-card: rgba(255, 255, 255, 0.05);
                --text-primary: #ffffff;
                --text-muted: rgba(255, 255, 255, 0.3);
                --red-500: #ef4444;
                --red-600: #dc2626;
            }}

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: 'Inter', sans-serif;
            }}

            body {{
                background-color: var(--bg-body);
                color: var(--text-primary);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}

            /* Ambiance: Grand cercle rouge flouté en fond */
            .ambient-glow {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 600px;
                height: 600px;
                background: radial-gradient(circle, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0) 70%);
                filter: blur(80px);
                z-index: 0;
                pointer-events: none;
            }}

            /* Carte Centrale (#141414 avec fine bordure) */
            .card {{
                background-color: var(--bg-card);
                border: 1px solid var(--border-card);
                border-radius: 20px;
                padding: 48px 40px;
                width: 100%;
                max-width: 520px;
                position: relative;
                z-index: 1;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                display: flex;
                flex-direction: column;
                gap: 32px;
            }}

            /* Titre Space Grotesk ultra serré */
            h1 {{
                font-family: 'Space Grotesk', sans-serif;
                font-size: 2.75rem;
                font-weight: 700;
                letter-spacing: -0.04em;
                text-align: center;
                color: #ffffff;
                line-height: 1.1;
            }}

            /* Search Bar (Fused layout) */
            .search-bar {{
                display: flex;
                background: #0A0A0A;
                border: 1px solid var(--border-card);
                border-radius: 9999px; /* Pilule parfaite */
                padding: 4px;
                transition: border-color 0.2s, box-shadow 0.2s;
            }}
            
            .search-bar:focus-within {{
                border-color: rgba(255, 255, 255, 0.2);
                box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.05);
            }}

            .input-wrapper {{
                flex-grow: 1;
                display: flex;
                align-items: center;
                padding-left: 16px;
            }}
            
            .input-wrapper i {{
                color: rgba(255, 255, 255, 0.4);
                width: 18px;
                height: 18px;
                margin-right: 12px;
            }}

            input[type="text"] {{
                width: 100%;
                background: transparent;
                border: none;
                color: white;
                font-size: 0.95rem;
                outline: none;
                font-family: inherit;
            }}

            input[type="text"]::placeholder {{
                color: rgba(255, 255, 255, 0.3);
            }}

            /* Bouton "Edge-cutting" */
            button.convert-btn {{
                background: linear-gradient(180deg, var(--red-500) 0%, var(--red-600) 100%);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25), 0 8px 16px -4px rgba(239, 68, 68, 0.3);
                color: white;
                border: none;
                border-radius: 9999px;
                padding: 10px 24px;
                font-size: 0.9rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                gap: 8px;
                white-space: nowrap;
            }}

            button.convert-btn:hover {{
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4), 0 12px 24px -4px rgba(239, 68, 68, 0.4);
                transform: translateY(-1px);
            }}
            
            button.convert-btn:active {{
                transform: translateY(0);
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
            }}
            
            button.convert-btn:disabled {{
                background: #27272a;
                color: #52525b;
                box-shadow: none;
                cursor: not-allowed;
                transform: none;
            }}

            #status {{
                text-align: center;
                font-size: 0.85rem;
                min-height: 20px;
                font-weight: 500;
            }}
            .error {{ color: var(--red-500); }}
            .success {{ color: #10b981; }}

            /* Ligne de features minimaliste */
            .features-line {{
                text-align: center;
                color: var(--text-muted);
                font-size: 0.75rem;
                font-weight: 500;
                letter-spacing: 0.02em;
                margin-top: 8px;
            }}

            /* Animations utiles */
            .lucide-spin {{
                animation: spin 1s linear infinite;
            }}
            @keyframes spin {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
            
            /* Responsive */
            @media (max-width: 480px) {{
                .card {{ padding: 32px 24px; }}
                h1 {{ font-size: 2.25rem; }}
                .search-bar {{ padding: 4px; padding-right: 4px; }}
                button.convert-btn {{ padding: 10px 16px; font-size: 0.85rem; }}
            }}
        </style>
    </head>
    <body>
        <div class="ambient-glow"></div>
        
        <div class="card">
            <h1>YouTube vers MP3</h1>

            <div class="search-bar">
                <div class="input-wrapper">
                    <i data-lucide="link"></i>
                    <input type="text" id="url" placeholder="Coller l'URL YouTube..." required autocomplete="off" />
                </div>
                <button id="btn" class="convert-btn" onclick="convert()">
                    <i data-lucide="arrow-right"></i>
                    Télécharger
                </button>
            </div>
            
            <div id="status"></div>

            <div class="features-line">
                Sans limite &middot; Haute Qualité &middot; 100% Sécurisé
            </div>
        </div>

        <script>
            lucide.createIcons();

            async function convert() {{
                const url = document.getElementById('url').value.trim();
                const btn = document.getElementById('btn');
                const status = document.getElementById('status');
                
                if (!url) {{ 
                    status.innerHTML = "<span class='error'>Veuillez entrer un lien valide.</span>"; 
                    return; 
                }}
                
                btn.disabled = true;
                btn.innerHTML = '<i data-lucide="loader-2" class="lucide-spin"></i> Traitement...';
                lucide.createIcons();
                status.innerHTML = "Conversion en cours...";
                
                try {{
                    const res = await fetch('/api/convert', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ url: url }})
                    }});
                    
                    if (res.ok) {{
                        const data = await res.json();
                        const downloadUrl = `/api/download/${{data.file_id}}?name=${{encodeURIComponent(data.filename)}}`;
                        window.location.href = downloadUrl;
                        
                        status.innerHTML = "<span class='success'>Téléchargement démarré !</span>";
                        document.getElementById('url').value = '';
                    }} else {{
                        const data = await res.json();
                        status.innerHTML = `<span class='error'>${{data.detail || "Une erreur est survenue"}}</span>`;
                    }}
                }} catch (e) {{
                    status.innerHTML = "<span class='error'>Erreur de connexion au serveur.</span>";
                }} finally {{
                    btn.disabled = false;
                    btn.innerHTML = '<i data-lucide="arrow-right"></i> Télécharger';
                    lucide.createIcons();
                }}
            }}
        </script>
    </body>
    </html>
    """
