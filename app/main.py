from flask import Flask, request, jsonify
from flask_cors import CORS
from app.transcript_service import fetch_transcript
from app.cache import get_cache, set_cache
import re
import concurrent.futures

app = Flask(__name__)

# allow requests from n8n / other clients
CORS(app)


# -------------------------
# Helpers
# -------------------------

def is_valid_video_id(video_id):
    """
    YouTube video ids are 11 characters
    """
    return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))


def run_with_timeout(func, timeout, *args, **kwargs):
    """
    Prevent hanging requests
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args, **kwargs)
        return future.result(timeout=timeout)


# -------------------------
# Routes
# -------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok"
    })


@app.route("/transcript", methods=["GET"])
def transcript():

    video_id = request.args.get("video_id")

    if not video_id:
        return jsonify({
            "error": "video_id parameter required"
        }), 400

    if not is_valid_video_id(video_id):
        return jsonify({
            "error": "invalid video_id"
        }), 400

    # -------------------------
    # Check Cache
    # -------------------------

    cached = get_cache(video_id)

    if cached:
        return jsonify({
            "source": "cache",
            "data": cached
        })


    # -------------------------
    # Fetch Transcript
    # -------------------------

    try:

        data = run_with_timeout(
            fetch_transcript,
            10,
            video_id
        )

        set_cache(video_id, data)

        return jsonify({
            "source": "youtube",
            "data": data
        })


    except concurrent.futures.TimeoutError:

        return jsonify({
            "error": "transcript fetch timeout"
        }), 504


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# -------------------------
# Run Local Server
# -------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )