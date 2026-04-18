from sources import hackernews, reddit, rss


def _dedupe(items):
    seen_urls = set()
    seen_titles = set()
    out = []
    for it in items:
        url = it.get("url", "").split("?")[0].rstrip("/")
        title_key = it.get("title", "").lower().strip()
        if url in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(url)
        seen_titles.add(title_key)
        out.append(it)
    return out


def collect_all():
    items = []
    for fn, name in [(hackernews.fetch, "hackernews"), (reddit.fetch, "reddit"), (rss.fetch, "rss")]:
        try:
            got = fn()
            print(f"[collect] {name}: {len(got)} items")
            items.extend(got)
        except Exception as e:
            print(f"[collect] {name} failed: {e}")
    deduped = _dedupe(items)
    print(f"[collect] {len(items)} total, {len(deduped)} after dedupe")
    return deduped
