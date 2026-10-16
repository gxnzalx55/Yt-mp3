# YouTube MP3 Downloader

Aplicación web con Flask y yt-dlp que convierte un video de YouTube a MP3.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre http://localhost:5000, pega la URL del video y pulsa **Descargar**.

FFmpeg se detecta automáticamente (el del sistema o el incluido en `imageio-ffmpeg`).
