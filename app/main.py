from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re

from app.cache import get_cache, set_cache
from app.transcript_service import fetch_transcript

app = Flask(__name__)

CORS(app)

API_KEY = os.getenv("API_KEY")


def is_valid_video_id(video_id):

    return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))


@app.route("/health")
def health():

    return jsonify({
        "status": "ok"
    })


@app.route("/transcript")
def transcript():

    api_key = request.headers.get("x-api-key")

    if api_key != API_KEY:

        return jsonify({
            "error": "unauthorized"
        }), 401


    video_id = request.args.get("video_id")

    if not video_id:

        return jsonify({
            "error": "video_id required"
        }), 400


    if not is_valid_video_id(video_id):

        return jsonify({
            "error": "invalid video id"
        }), 400


    cached = get_cache(video_id)

    if cached:

        return jsonify({
            "source": "cache",
            "data": cached
        })


    try:

        data = fetch_transcript(video_id)

        set_cache(video_id, data)

        return jsonify({
            "source": "youtube",
            "data": data
        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )