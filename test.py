from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

def clean_text(text):
    # remove [music], [applause] etc
    return re.sub(r'\[.*?\]', '', text).strip()


@app.route("/transcript", methods=["GET"])
def get_transcript():

    video_id = request.args.get("video_id")

    if not video_id:
        return jsonify({"error": "video_id is required"}), 400

    try:

        api = YouTubeTranscriptApi()

        transcript = api.fetch(video_id)

        segments = []

        for entry in transcript:
            segments.append({
                "text": clean_text(entry.text),
                "start": entry.start,
                "duration": entry.duration
            })

        full_text = " ".join([seg["text"] for seg in segments])

        return jsonify({
            "video_id": video_id,
            "transcript": full_text,
            "segments": segments
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)