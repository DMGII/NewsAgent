import os
import re
from datetime import date
import requests

MAX_BLOCK_CHARS = 2800


def _md_to_slack(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<\2|\1>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)", r"_\1_", text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"*\1*", text)
    text = re.sub(r"^#{1,6}\s+(.+)$", r"*\1*", text, flags=re.M)
    return text


def _split_para(para: str) -> list[str]:
    """Split a paragraph that is too large by line, then hard-truncate any remaining giants."""
    if len(para) <= MAX_BLOCK_CHARS:
        return [para]
    chunks, current = [], ""
    for line in para.split("\n"):
        line = line[:MAX_BLOCK_CHARS]  # hard cap a single line
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > MAX_BLOCK_CHARS and current:
            chunks.append(current)
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def _flush(blocks: list[dict], text: str) -> None:
    for chunk in _split_para(text):
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": chunk}})


def _chunk_into_blocks(text: str) -> list[dict]:
    blocks = []
    current = ""
    for para in text.split("\n\n"):
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) > MAX_BLOCK_CHARS and current:
            _flush(blocks, current)
            current = para
        else:
            current = candidate
    if current:
        _flush(blocks, current)
    return blocks


def deliver(markdown_text: str, archive_url: str | None = None) -> None:
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        print("[deliver] SLACK_WEBHOOK_URL missing — printing to console.\n")
        print(markdown_text)
        if archive_url:
            print(f"\nArchive: {archive_url}")
        return

    title = f"AI Digest — {date.today().isoformat()}"
    slack_text = _md_to_slack(markdown_text)

    blocks: list[dict] = [{"type": "header", "text": {"type": "plain_text", "text": title}}]
    if archive_url:
        blocks.append({
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"<{archive_url}|Open the full archive in your browser>"}],
        })
    blocks.extend(_chunk_into_blocks(slack_text))

    r = requests.post(webhook, json={"text": title, "blocks": blocks}, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"Slack webhook error {r.status_code}: {r.text}")
    print(f"[deliver] sent to Slack ({len(blocks)} blocks)")
