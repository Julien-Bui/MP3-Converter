# Étape 1 : construction du générateur de PO tokens (contournement anti-bot YouTube)
# Version épinglée (tag 2.0.0) pour un build reproductible
FROM node:22-bookworm-slim AS pot-builder
ADD https://github.com/Brainicism/bgutil-ytdlp-pot-provider/archive/refs/tags/2.0.0.tar.gz /tmp/pot.tar.gz
RUN tar -xzf /tmp/pot.tar.gz -C /opt && \
    mv /opt/bgutil-ytdlp-pot-provider-2.0.0 /opt/bgutil && \
    cd /opt/bgutil/server && npm ci --silent && npx tsc && \
    rm -rf /tmp/pot.tar.gz

FROM python:3.11-slim

# ffmpeg pour la conversion audio, libstdc++6 requis par le binaire node
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libstdc++6 && \
    rm -rf /var/lib/apt/lists/*

# Node.js (binaire officiel de l'image node) + générateur de PO tokens compilé
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=pot-builder /opt/bgutil/server /opt/bgutil/server
ENV BGUTIL_SERVER_HOME=/opt/bgutil/server

# Utilisateur non-root pour l'exécution
RUN useradd -m -u 10001 appuser

WORKDIR /app

# Copie requirements et install des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Ownership pour l'utilisateur non-root
RUN chown -R appuser:appuser /app

USER appuser

# Expose le port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://localhost:' + os.environ.get('PORT', '8000') + '/health').read()" || exit 1

# Start the app
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
