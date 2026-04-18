import requests

SUBREDDITS = ["MachineLearning", "artificial", "LocalLLaMA"]
HEADERS = {"User-Agent": "NewsAgent/0.1 (daily AI digest)"}


def fetch(min_score: int = 30, limit_per_sub: int = 25):
    items = []
    for sub in SUBREDDITS:
        try:
            r = requests.get(
                f"https://www.reddit.com/r/{sub}/top.json",
                params={"t": "day", "limit": limit_per_sub},
                headers=HEADERS,
                timeout=20,
            )
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"[reddit] {sub} failed: {e}")
            continue
        for child in r.json().get("data", {}).get("children", []):
            d = child.get("data", {})
            if d.get("score", 0) < min_score or d.get("stickied"):
                continue
            items.append({
                "source": "reddit",
                "subsource": f"r/{sub}",
                "title": d.get("title", ""),
                "url": d.get("url", f"https://reddit.com{d.get('permalink', '')}"),
                "summary": (d.get("selftext") or "")[:400],
                "score": d.get("score", 0),
                "comments_url": f"https://reddit.com{d.get('permalink', '')}",
            })
    return items
