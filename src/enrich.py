"""OPTIONAL — LLM-rewritten briefs.

Off by default. When enabled, rewrites each story's syndicated summary into an
original 2-3 sentence ThreatWire brief, so the on-site page is genuinely our own
prose (not the publisher's text) while still linking out to the source.

Enable by setting BOTH environment variables (locally or as GitHub Actions
secrets), then it runs automatically inside `build.py`:

    USE_LLM_BRIEFS=1
    ANTHROPIC_API_KEY=sk-ant-...

Cost note: uses Claude Haiku (cheapest tier) and only rewrites the top N stories
per build to keep spend negligible. Uses the standard library only.
"""
from __future__ import annotations

import json
import os
import ssl
import urllib.request

import certifi

_SSL_CTX = ssl.create_default_context(cafile=certifi.where())
MODEL = "claude-haiku-4-5-20251001"
API_URL = "https://api.anthropic.com/v1/messages"
MAX_REWRITES = 30  # cap per build → bounded cost


def enabled() -> bool:
    return os.environ.get("USE_LLM_BRIEFS") == "1" and bool(os.environ.get("ANTHROPIC_API_KEY"))


def _rewrite(title: str, summary: str, source: str, key: str) -> str | None:
    prompt = (
        "You are a cybersecurity news editor for ThreatWire. Rewrite the following "
        "wire summary into an original, neutral 2-3 sentence brief. Do not copy phrasing; "
        "summarize the facts. No preamble.\n\n"
        f"Headline: {title}\nSource: {source}\nWire summary: {summary}"
    )
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 220,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(API_URL, data=body, method="POST")
    req.add_header("x-api-key", key)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return "".join(b.get("text", "") for b in data.get("content", [])).strip() or None
    except Exception as exc:  # noqa: BLE001 — never let enrichment break the build
        print(f"  ! enrich failed for {title[:40]!r}: {exc}")
        return None


def enrich(items: list[dict]) -> list[dict]:
    """Replace summaries with LLM briefs for the top MAX_REWRITES items, in place."""
    if not enabled():
        return items
    key = os.environ["ANTHROPIC_API_KEY"]
    print(f"Enriching up to {MAX_REWRITES} briefs with {MODEL}...")
    done = 0
    for it in items[:MAX_REWRITES]:
        if not it.get("summary"):
            continue
        brief = _rewrite(it["title"], it["summary"], it["source"], key)
        if brief:
            it["summary"] = brief
            it["llm_brief"] = True
            done += 1
    print(f"  enriched {done} briefs.")
    return items
