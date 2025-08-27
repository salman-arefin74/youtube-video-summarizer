from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re

def get_video_id(url: str) -> str:
    query = urlparse(url).query
    video_id = parse_qs(query).get("v", [None])[0]

    if not video_id:
        raise ValueError("Could not extract video ID from URL")
    return video_id

def fetch_transcript(url: str, lang="en"):
    video_id = get_video_id(url)
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    cleaned_snippets = [re.sub(r'\s+', ' ', snippet.text.strip()) for snippet in transcript.snippets]
    transcript_text = " ".join(cleaned_snippets)
    return transcript_text
