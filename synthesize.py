import json
import os

ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM = """You are an editor producing a daily AI news digest for a software engineer learning to become an AI engineer.

Your job:
1. Read the raw items below (from Hacker News, Reddit, RSS feeds, arXiv).
2. Aggressively filter for SIGNAL over noise. Drop items that are:
   - minor version bumps, small UI tweaks, or marketing fluff
   - speculation, hot takes, or drama without substance
   - duplicates or near-duplicates (same story from multiple sources)
   - anything the reader has marked as irrelevant (see DISLIKED TOPICS)
3. Keep only items that matter to someone learning AI engineering: real breakthroughs, important papers, practical tool releases, major industry moves.
4. Organize surviving items into these sections (skip any section with no items):
   - **Breakthroughs & Research** — notable papers, new capabilities, benchmark results
   - **Tools & Releases** — new models, frameworks, libraries, APIs, practical dev tools
   - **Industry & Strategy** — major company announcements, funding, policy, hiring
   - **Worth a Glance** — a short list of secondary items, 1 line each
5. For each main item: one crisp sentence on WHAT it is, one on WHY it matters for an AI engineer learner. Link the title.

Output format: Markdown. Start with a one-line summary of the day (e.g., "Quiet day dominated by..." or "Big news: ..."). Use ## for section headers. Link every title. No preamble, no sign-off, no emojis.

If the day is genuinely slow and you only have 2-3 worthwhile items, say so — don't pad."""


def _build_user_prompt(items: list[dict], disliked: list[str]) -> str:
    compact = [
        {
            "title": it["title"],
            "url": it["url"],
            "source": it["subsource"],
            "score": it.get("score", 0),
            "summary": it.get("summary", "")[:300],
        }
        for it in items
    ]
    prompt = "RAW ITEMS (JSON):\n" + json.dumps(compact, indent=2)
    if disliked:
        prompt += "\n\nDISLIKED TOPICS (filter these out aggressively):\n- " + "\n- ".join(disliked)
    return prompt


def _select_provider() -> str:
    explicit = os.environ.get("LLM_PROVIDER", "").strip().lower()
    if explicit in ("anthropic", "openai"):
        return explicit
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    raise RuntimeError("No LLM API key set. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.")


def _synthesize_anthropic(user: str) -> str:
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=3000,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text


def _synthesize_openai(user: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=3000,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content


def synthesize(items: list[dict], disliked: list[str]) -> str:
    provider = _select_provider()
    print(f"[synthesize] using {provider}")
    user = _build_user_prompt(items, disliked)
    if provider == "anthropic":
        return _synthesize_anthropic(user)
    return _synthesize_openai(user)


def has_llm_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"))
