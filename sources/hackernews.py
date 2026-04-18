import re
import time
import requests

AI_PATTERN = re.compile(
    r"\b(ai|a\.i\.|gpt|llm|llms|claude|anthropic|openai|gemini|deepmind|"
    r"llama|mistral|transformer|transformers|neural|agent|agents|rag|"
    r"embedding|embeddings|diffusion|fine-tun\w*|inference|"
    r"machine learning|deep learning|generative|multimodal|chatbot|"
    r"foundation model|language model|reasoning model|prompt)\b",
    re.IGNORECASE,
)


def _matches_ai(text: str) -> bool:
    return bool(AI_PATTERN.search(text))


def fetch(hours: int = 24, min_points: int = 40):
    since = int(time.time()) - hours * 3600
    r = requests.get(
        "https://hn.algolia.com/api/v1/search",
        params={
            "tags": "story",
            "numericFilters": f"created_at_i>{since},points>{min_points}",
            "hitsPerPage": 100,
        },
        timeout=20,
    )
    r.raise_for_status()
    items = []
    for hit in r.json().get("hits", []):
        title = hit.get("title") or hit.get("story_title") or ""
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        if not title or not _matches_ai(title):
            continue
        items.append({
            "source": "hackernews",
            "subsource": "Hacker News",
            "title": title,
            "url": url,
            "summary": "",
            "score": hit.get("points", 0),
            "comments_url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
        })
    return items
