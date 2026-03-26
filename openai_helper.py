import os, json
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)

SYSTEM_PROMPT = """
You are an English vocabulary extractor.
Given a Korean study text, extract the most important English words or short phrases to memorize.
Return ONLY a JSON array like:
[
  {"word": "photosynthesis", "meaning": "광합성", "level": 1},
  {"word": "chlorophyll",    "meaning": "엽록소",  "level": 2}
]
level: 1=easy, 2=medium, 3=hard.
Return 5 to 10 words. No explanation, no markdown, just raw JSON.
"""

def extract_keywords(text: str) -> list[dict]:
    """텍스트에서 핵심 영단어를 추출합니다."""
    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": text}
        ],
        temperature=0.3
    )

    raw = response.choices[0].message.content.strip()
    # 혹시 마크다운 코드블록이 붙어 있으면 제거
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)