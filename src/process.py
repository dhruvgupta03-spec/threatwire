"""LOOP 2 — PROCESS.

Take the raw fetched items and turn them into a ranked, deduplicated,
tagged newsroom feed:

  * drop items older than MAX_AGE_DAYS
  * dedupe by link and by near-identical title
  * assign a severity score (0-3) and topic tags via keyword heuristics
  * sort by a blended score of severity + recency so the lead story is both
    important and fresh
"""
from __future__ import annotations

import re
import time

from .config import MAX_AGE_DAYS, MAX_ITEMS, SEVERITY, TOPICS

_NORM_RE = re.compile(r"[^a-z0-9 ]+")


def _norm_title(title: str) -> str:
    return _NORM_RE.sub("", title.lower()).strip()


def _haystack(item: dict) -> str:
    return f"{item['title']} {item['summary']}".lower()


def score_severity(item: dict) -> int:
    hay = _haystack(item)
    for level in (3, 2, 1):
        if any(kw in hay for kw in SEVERITY[level]):
            return level
    return 0


def tag_topics(item: dict) -> list[str]:
    hay = _haystack(item)
    tags = [topic for topic, kws in TOPICS.items() if any(kw in hay for kw in kws)]
    return tags[:3]


def dedupe(items: list[dict]) -> list[dict]:
    seen_links: set[str] = set()
    seen_titles: set[str] = set()
    out: list[dict] = []
    for item in items:
        norm = _norm_title(item["title"])
        if item["link"] in seen_links or norm in seen_titles:
            continue
        seen_links.add(item["link"])
        seen_titles.add(norm)
        out.append(item)
    return out


def process(items: list[dict]) -> list[dict]:
    now = time.time()
    cutoff = now - MAX_AGE_DAYS * 86400

    fresh: list[dict] = []
    for item in items:
        ts = item.get("published_ts")
        # Items with no date are treated as "now" so they aren't unfairly dropped.
        if ts is None:
            item["published_ts"] = now
            ts = now
        if ts < cutoff:
            continue

        item["severity"] = score_severity(item)
        item["topics"] = tag_topics(item)
        age_hours = max((now - ts) / 3600.0, 0.0)
        # Recency decays over ~72h; severity dominates but freshness breaks ties.
        recency = max(0.0, 1.0 - age_hours / 72.0)
        item["rank"] = item["severity"] * 10 + recency * 5
        fresh.append(item)

    fresh = dedupe(fresh)
    fresh.sort(key=lambda i: (i["rank"], i["published_ts"]), reverse=True)
    return fresh[:MAX_ITEMS]


if __name__ == "__main__":
    from .fetch import fetch_all

    ranked = process(fetch_all())
    for i in ranked[:8]:
        print(f"[sev {i['severity']}] {i['source']:>18} — {i['title']}")
