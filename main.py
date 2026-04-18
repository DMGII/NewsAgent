import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from collect import collect_all
from synthesize import synthesize, has_llm_key
from deliver import deliver
from feedback import load_disliked
from archive import archive

load_dotenv()

ROOT = Path(__file__).parent
DIGEST_FILE = ROOT / "last_digest.md"
URL_FILE = ROOT / "last_url.txt"


def generate() -> None:
    items = collect_all()
    if not items:
        print("[main] no items collected — aborting")
        sys.exit(1)

    disliked = load_disliked()
    print(f"[main] {len(disliked)} disliked topics in feedback")

    if not has_llm_key():
        print("[main] no LLM key (ANTHROPIC_API_KEY or OPENAI_API_KEY) — cannot synthesize. Items collected:")
        for it in items[:20]:
            print(f"  [{it['subsource']}] {it['title']}")
        sys.exit(2)

    digest = synthesize(items, disliked)
    DIGEST_FILE.write_text(digest)

    path, url = archive(digest)
    URL_FILE.write_text(url or "")
    print(f"[main] archived to {path}")
    if url:
        print(f"[main] will be live at {url} (after push + Pages rebuild)")


def send() -> None:
    if not DIGEST_FILE.exists():
        print("[main] no last_digest.md — run generate first")
        sys.exit(1)
    digest = DIGEST_FILE.read_text()
    url = URL_FILE.read_text().strip() if URL_FILE.exists() else ""
    deliver(digest, archive_url=url or None)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "generate":
        generate()
    elif mode == "send":
        send()
    elif mode == "all":
        generate()
        send()
    else:
        print(f"unknown mode: {mode} (use: generate | send | all)")
        sys.exit(2)
