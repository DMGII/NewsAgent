import json
from pathlib import Path

PATH = Path(__file__).parent / "feedback.json"


def load_disliked() -> list[str]:
    if not PATH.exists():
        return []
    try:
        data = json.loads(PATH.read_text())
        return data.get("disliked_topics", [])
    except Exception:
        return []


def add_disliked(topic: str) -> None:
    data = {"disliked_topics": load_disliked()}
    if topic not in data["disliked_topics"]:
        data["disliked_topics"].append(topic)
    PATH.write_text(json.dumps(data, indent=2))
