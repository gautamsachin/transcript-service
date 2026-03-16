from youtube_transcript_api import YouTubeTranscriptApi
import re

def clean_text(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'>>', '', text)
    return text.strip()

def fetch_transcript(video_id):

    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)

    segments = []

    for entry in transcript:
        segments.append({
            "text": clean_text(entry.text),
            "start": entry.start,
            "duration": entry.duration
        })

    full_text = " ".join([s["text"] for s in segments])

    return {
        "video_id": video_id,
        "transcript": full_text,
        "segments": segments
    }