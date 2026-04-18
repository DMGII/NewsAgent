# NewsAgent — Daily AI Digest

Pulls from Hacker News, Reddit (r/MachineLearning, r/artificial, r/LocalLLaMA), Google News (OpenAI / Anthropic / DeepMind / Meta AI), and arXiv. Uses Claude Haiku 4.5 to filter noise and synthesize a morning digest, posts the summary to Slack with a link to a full HTML archive hosted on GitHub Pages.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your keys
```

Required env vars:
- **One of** `ANTHROPIC_API_KEY` ([console.anthropic.com](https://console.anthropic.com)) or `OPENAI_API_KEY` ([platform.openai.com](https://platform.openai.com)). ~$5 credit lasts months on Haiku or `gpt-4o-mini`. If both are set, Anthropic wins by default — override with `LLM_PROVIDER=openai`.
- `SLACK_WEBHOOK_URL` — see below

Optional:
- `ANTHROPIC_MODEL` / `OPENAI_MODEL` — override the model (defaults: `claude-haiku-4-5-20251001`, `gpt-4o-mini`)

### Create a Slack Incoming Webhook

1. [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**
2. Name it (e.g. "AI Digest"), pick your workspace
3. Sidebar: **Incoming Webhooks** → toggle **On**
4. Click **Add New Webhook to Workspace**, pick the channel
5. Copy the webhook URL into `SLACK_WEBHOOK_URL`

## Run

```bash
python main.py          # generate + send (default)
python main.py generate # just collect + synthesize + archive to digests/
python main.py send     # re-send the last generated digest to Slack
```

Without `ANTHROPIC_API_KEY`, `generate` prints collected items and exits. Without `SLACK_WEBHOOK_URL`, `send` prints the digest to stdout. Archive HTML is always saved to `digests/YYYY-MM-DD.html`.

## Feedback loop

Edit `feedback.json` to filter out topics:

```json
{ "disliked_topics": ["crypto+AI hype", "minor GPT wrapper startups"] }
```

These get injected into the ranking prompt.

## Scheduled daily run (GitHub Actions + Pages)

1. Push this repo to GitHub — **must be a public repo** for Pages on the free tier.
2. Repo → Settings → **Secrets and variables** → **Actions** → add:
   - `ANTHROPIC_API_KEY` **or** `OPENAI_API_KEY` (at least one)
   - `SLACK_WEBHOOK_URL`
   - *(optional)* repository **Variable** `LLM_PROVIDER=openai` to force OpenAI if both keys are set
3. Repo → Settings → **Pages** → Source: **Deploy from a branch** → Branch: **main**, folder: **/ (root)** → Save.
   After a minute, your site is live at `https://<your-username>.github.io/<repo-name>/`.
4. The workflow at [.github/workflows/daily.yml](.github/workflows/daily.yml) runs at 11:00 UTC (= 07:00 ET, daylight saving). GitHub Actions cron is always UTC — adjust for your timezone.
5. Trigger manually once from the Actions tab to verify.

Each run commits `digests/YYYY-MM-DD.html` to main, waits for Pages to rebuild, then posts to Slack with a link to the archive page.

## Local schedule (macOS, if Mac is awake at 7am)

```
0 7 * * * cd /Users/dimeji/Code/Agents/NewsAgent && /Users/dimeji/Code/Agents/NewsAgent/.venv/bin/python main.py >> digest.log 2>&1
```

For reliability, use GitHub Actions.
