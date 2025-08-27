from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel, ValidationError
import json5
from transcript_loader import fetch_transcript
import re
import time

class Schema(BaseModel):
    summary: str
    sentiment: str

prompt_template = """
You are an assistant.
Your task is to summarize the article's text into 3 sentences and analyze its sentiment.
Respond with ONLY valid JSON, no explanations, no Markdown, no prose, no commentary.
The response MUST be in this exact JSON format:
{{
  "summary": "...",
  "sentiment": "positive" | "neutral" | "negative"
}}

Article: {article_text}
"""

url = "https://www.youtube.com/watch?v=_K-eupuDVEc&ab_channel=IGotAnOffer%3AEngineering"
article_text = fetch_transcript(url)
prompt = prompt_template.format(article_text=article_text)

def sanitize_json_text(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = "\n".join(cleaned.splitlines()[1:-1])
    cleaned = cleaned.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    cleaned = re.sub(r"\s+", " ", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    if not cleaned.endswith("}"):
        cleaned += "}"

    return cleaned

def call_llm_with_retries(prompt, max_retries=3, wait_seconds=2):
    for attempt in range(max_retries):
        response: ChatResponse = chat(
            model='gemma3',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.2, 'num_predict': 200}
        )
        raw_output = response['message']['content']
        cleaned_output = sanitize_json_text(raw_output)

        try:
            data = json5.loads(cleaned_output)
            validate_response = Schema(**data)
            return validate_response

        except (ValueError, ValidationError):
            print(f"Attempt {attempt+1} failed. Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)

            prompt = f"""
            Reformat the following text into VALID JSON matching this schema:
            {{
              "summary": "...",
              "sentiment": "positive" | "neutral" | "negative"
            }}

            Text:
            {raw_output}
            """

    return None

response = call_llm_with_retries(prompt)
print(response)
