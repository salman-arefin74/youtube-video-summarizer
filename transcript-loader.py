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
    print("video id: ", video_id)
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    # print("transcript: ", transcript)
    cleaned_snippets = [re.sub(r'\s+', ' ', snippet.text.strip()) for snippet in transcript.snippets]
    
    # Join into a single string
    transcript_text = " ".join(cleaned_snippets)
    return transcript_text

# Example usage
url = "https://www.youtube.com/watch?v=_K-eupuDVEc&ab_channel=IGotAnOffer%3AEngineering"
try:
    text = fetch_transcript(url)
    print(text)
except Exception as e:
    print("Error:", e)
