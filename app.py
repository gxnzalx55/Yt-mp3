from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads/"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Ruta al FFmpeg portable incluido en el proyecto
FFMPEG_DIR = os.path.join(os.getcwd(), "ffmpeg", "bin")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")

        try:
            unique = uuid.uuid4().hex
            output_template = os.path.join(DOWNLOAD_FOLDER, f"{unique}.%(ext)s")

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "ffmpeg_location": FFMPEG_DIR,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }],
                "quiet": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

            mp3_path = os.path.join(DOWNLOAD_FOLDER, f"{unique}.mp3")

            return send_file(mp3_path, as_attachment=True, download_name=f"{info['title']}.mp3")

        except Exception as e:
            return f"Error: {e}"

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)