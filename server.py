from flask import Flask, request, jsonify
import yt_dlp, os

app = Flask(__name__)

@app.route("/stream")
def stream():
    video_id = request.args.get("id")
    if not video_id:
        return jsonify({"error": "Missing id"}), 400
    try:
        opts = {
            "quiet": True,
            "cookiefile": "cookies.txt",
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False
            )
            formats = info.get("formats", [])

            # 音訊專用格式（無視訊）
            audio_only = [f for f in formats if f.get("vcodec") == "none" and f.get("url")]
            # 備選：任何有 url 的格式
            any_fmt = [f for f in formats if f.get("url")]

            candidates = audio_only if audio_only else any_fmt
            if not candidates:
                return jsonify({"error": f"No formats found. Total formats: {len(formats)}"}), 400

            candidates.sort(key=lambda f: f.get("abr") or f.get("tbr") or 0, reverse=True)
            best = candidates[0]
            return jsonify({"url": best["url"], "ext": best.get("ext", ""), "abr": best.get("abr")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
