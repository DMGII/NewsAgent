from datetime import datetime, timedelta, timezone
import feedparser

FEEDS = [
    ("OpenAI news", "https://news.google.com/rss/search?q=OpenAI+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Anthropic news", "https://news.google.com/rss/search?q=Anthropic+Claude+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Google DeepMind news", "https://news.google.com/rss/search?q=%22Google+DeepMind%22+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("Meta AI news", "https://news.google.com/rss/search?q=%22Meta+AI%22+OR+%22Llama%22+when:1d&hl=en-US&gl=US&ceid=US:en"),
    ("AI research arXiv", "http://export.arxiv.org/rss/cs.AI"),
    ("ML research arXiv", "http://export.arxiv.org/rss/cs.LG"),
]


def _entry_time(entry):
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def fetch(hours: int = 30):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    items = []
    for label, url in FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"[rss] {label} failed: {e}")
            continue
        for entry in feed.entries[:25]:
            ts = _entry_time(entry)
            if ts and ts < cutoff:
                continue
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            if not title or not link:
                continue
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            items.append({
                "source": "rss",
                "subsource": label,
                "title": title,
                "url": link,
                "summary": summary[:400],
                "score": 0,
                "comments_url": "",
            })
    return items
