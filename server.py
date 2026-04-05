from flask import Flask, request, jsonify
import yt_dlp, os

app = Flask(__name__)

COOKIES_FILE = "cookies.txt"

@app.route("/stream")
def stream():
    video_id = request.args.get("id")
    if not video_id:
        return jsonify({"error": "Missing id"}), 400
    try:
        opts = {
            "format": "bestaudio/best",
            "quiet": True,
        }
        if os.path.exists(COOKIES_FILE):
            opts["cookiefile"] = COOKIES_FILE

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False
            )
            url = info.get("url") or next(
                (f["url"] for f in info.get("formats", [])
                 if f.get("vcodec") == "none" and f.get("url")), None
            )
            if not url:
                return jsonify({"error": "No audio URL"}), 400
            return jsonify({"url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
