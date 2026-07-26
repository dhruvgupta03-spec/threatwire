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

## Features

- **15 threat-intel wires** aggregated, deduplicated, and ranked by severity + recency
- **Story clustering** — the same incident reported by multiple outlets folds into
  one lead story with an "also covered by" list
- **On-site briefs** — every story gets a ThreatWire page that links out to the source
- **Section pages** — one per topic (Ransomware, Zero-Day, …) plus a Critical desk
- **Client-side search** — `search.html` over `search-index.json`, no backend
- **Own feeds** — `feed.xml` (RSS 2.0) and `feed.json` (JSON Feed) so others can subscribe
- **Live auto-update** — the page polls `status.json` and reloads itself when a new
  edition publishes; a "LIVE" badge shows how fresh the edition is

## Configure sources

Edit `src/config.py` — add/remove feeds in `FEEDS`, tune `SEVERITY` / `TOPICS`
keywords, or adjust `MAX_ITEMS` / `MAX_AGE_DAYS`.

## Optional: LLM-rewritten briefs

Off by default. To make each brief original ThreatWire prose instead of the
publisher's syndicated summary, set two GitHub Actions secrets:
`USE_LLM_BRIEFS=1` and `ANTHROPIC_API_KEY=...`. Uses Claude Haiku, capped per
build to keep cost negligible. See `src/enrich.py`.

## Optional: custom domain

Buy a domain, set `SITE["domain"] = "yourdomain.com"` in `src/config.py` (emits a
`CNAME` file on build), then point DNS at GitHub Pages:
`A` records → `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`, and a
`CNAME` for `www` → `<username>.github.io`.

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
