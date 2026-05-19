FROM python:3.12-slim
WORKDIR /opt/campaign-manager

# System deps + Node.js (MJML runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    nodejs \
    npm \
    curl \
    unzip \
    && npm install -g mjml \
    && rm -rf /var/lib/apt/lists/*

# Python deps (cached layer — only rebuilds when requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app/ app/
COPY worker/ worker/

# Entrypoint — auto-installs TinyMCE on first start
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Runtime dirs
RUN mkdir -p /data /email_templates /uploads /logs

EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
