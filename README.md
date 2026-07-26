# THREATWIRE

**A proactive threat-intelligence news aggregator, presented like a front page.**
Clips the latest reporting from many cybersecurity wires, ranks it by severity and
recency, and renders a Wall-Street-Journal-style edition that stays current on a loop.

Built with plain Python (no framework) → a static site → free public hosting on
GitHub Pages behind your own domain.

---

## Loop engineering

ThreatWire is three loops, per the loop-engineering model (goal → context → act →
verify → state → stop):

| Loop | File | Role |
|------|------|------|
| **1 · Fetch**   | `src/fetch.py`   | Pull latest entries from every source, normalize them |
| **2 · Process** | `src/process.py` | Dedupe, tag topics, score severity, rank by severity + recency |
| **3 · Render**  | `src/render.py`  | Build the WSJ-style `site/index.html` |

`src/build.py` runs exactly **one** iteration (fetch → process → render) with a
**verification gate** (an empty fetch fails the build, so a blank edition is never
published) and **state** (each edition is saved to `data/latest.json`).

The **trigger** is external: locally `src/loop.py`, in production the GitHub Actions
cron (`.github/workflows/build.yml`, every 15 min).

## Run it locally

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt

# one build
./.venv/bin/python -m src.build
open site/index.html

# or run the live dev loop (rebuild every 5 min)
./.venv/bin/python -m src.loop 5
```

## Configure sources

Edit `src/config.py` — add/remove feeds in `FEEDS`, tune `SEVERITY` / `TOPICS`
keywords, or adjust `MAX_ITEMS` / `MAX_AGE_DAYS`.

## Deploy (public site + custom domain)

1. Push this repo to GitHub.
2. Repo **Settings → Pages → Source: GitHub Actions**.
3. The workflow builds and deploys on push and every 15 min.
4. Add your domain under **Settings → Pages → Custom domain**, then point the
   DNS records at GitHub Pages. Set `SITE["base_url"]` in `src/config.py` to match.

## Sources

Headlines link to the original publishers; copyright remains with each outlet.
Current wires: Krebs on Security, BleepingComputer, The Hacker News, Dark Reading,
SANS ISC, CISA, The Record, Schneier on Security, Google Security, Microsoft Security.
