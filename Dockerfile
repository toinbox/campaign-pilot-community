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

# Download TinyMCE locally
RUN mkdir -p app/static/tinymce && \
    curl -sL "https://download.tiny.cloud/tinymce/community/tinymce_6.8.2.zip" -o /tmp/tinymce.zip && \
    unzip -q /tmp/tinymce.zip -d /tmp/tinymce_extract && \
    cp -r /tmp/tinymce_extract/tinymce/js/tinymce/* app/static/tinymce/ && \
    rm -rf /tmp/tinymce.zip /tmp/tinymce_extract


# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app/ app/
COPY worker/ worker/

# Runtime dirs
RUN mkdir -p /data /email_templates /uploads /logs

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]