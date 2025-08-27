from ollama import chat
from ollama import ChatResponse
from pydantic import BaseModel, ValidationError
import json5
import re
import time

class Schema(BaseModel):
    summary: str
    sentiment: str

prompt_template = """
  You are an assistant.
  Your task is to summarize the article's text into 3 sentences and analyze its sentiment.
  Return strictly valid JSON without Markdown formatting or code fences with these keys:
  - "summary": short 3-sentence summary
  - "sentiment": overall sentiment ("positive", "neutral", "negative")

  Article: {article_text}
"""

article_text = """
This compelling piece explores the profound impact artificial intelligence is having on cultural creation, consumption, and our broader sense of authenticity. It touches on how AI tools—from ChatGPT to Perplexity—are reshaping how we engage with art, ideas, and even our own emotions. It examines both the creative possibilities and the anxieties around AI's growing role in culture, highlighting concerns from filmmakers, including Daniel Kwan, about the erosion of social trust, as well as the ways some artists are creatively integrating AI into their workflows.

Ultimately, the article argues that culture is rooted in human connection, unpredictability, and the imprints of care—qualities AI can simulate, but not truly replicate. Yet in that contrast, AI might help us re-discover the value of human originality.
"""
prompt = prompt_template.format(article_text=article_text)

def sanitize_json_text(text: str) -> str:
    """Remove markdown fences and normalize characters."""
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
            options={'temperature': 0.5, 'num_predict': 200}
        )
        raw_output = response['message']['content']
        cleaned_output = sanitize_json_text(raw_output)
        try:
            data = json5.loads(cleaned_output)  # json5 raises ValueError, not JSONDecodeError
            validate_response = Schema(**data)
            return validate_response
        except (ValueError, ValidationError) as e:
            print(f"Attempt {attempt+1} failed ({e}), retrying in {wait_seconds} seconds...")
            time.sleep(wait_seconds)
    return None

response = call_llm_with_retries(prompt)
print(response)
