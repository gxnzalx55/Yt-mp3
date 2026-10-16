import os
import re
import shutil
import tempfile
from urllib.parse import urlparse

import yt_dlp
from flask import Flask, after_this_request, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

YOUTUBE_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com",
    "youtu.be", "www.youtu.be",
}


def get_ffmpeg():
    """Usa el ffmpeg del sistema; si no existe, el binario de imageio-ffmpeg."""
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def error_response(message, status):
    if request.headers.get("X-Requested-With") == "fetch":
        return {"error": message}, status
    return render_template("index.html", error=message), status


def is_youtube_url(url):
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and (parsed.hostname or "").lower() in YOUTUBE_HOSTS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = (request.form.get("url") or "").strip()

        if not is_youtube_url(url):
            return error_response("Introduce una URL válida de YouTube.", 400)

        workdir = tempfile.mkdtemp(prefix="ytmp3_")

        @after_this_request
        def cleanup(response):
            # Se borra cuando termina de enviarse el archivo
            response.call_on_close(lambda: shutil.rmtree(workdir, ignore_errors=True))
            return response

        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(workdir, "audio.%(ext)s"),
                "ffmpeg_location": get_ffmpeg(),
                "noplaylist": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "quiet": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

            name = secure_filename(info.get("title") or "") or "audio"
            return send_file(
                os.path.join(workdir, "audio.mp3"),
                as_attachment=True,
                download_name=f"{name}.mp3",
            )

        except Exception:
            app.logger.exception("Error al descargar %s", url)
            return error_response("No se pudo descargar el audio. Revisa la URL e inténtalo de nuevo.", 500)

    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
