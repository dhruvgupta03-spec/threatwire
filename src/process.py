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
_CVE_RE = re.compile(r"cve-\d{4}-\d{4,7}", re.I)

# Common words that carry no signal when matching two headlines to one incident.
_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "via",
    "new", "flaw", "bug", "attack", "attacks", "hackers", "hacker", "security",
    "cyber", "cyberattack", "vulnerability", "vulnerabilities", "exploit",
    "exploited", "exploits", "patch", "patches", "warns", "says", "report",
    "reports", "amid", "after", "over", "how", "why", "what", "used", "using",
    "into", "from", "your", "you", "are", "is", "as", "by", "at", "it", "its",
}


def _norm_title(title: str) -> str:
    return _NORM_RE.sub("", title.lower()).strip()


def _signature(title: str) -> tuple[set[str], set[str]]:
    """Return (significant word tokens, CVE ids) used to match same-incident stories."""
    cves = {c.lower() for c in _CVE_RE.findall(title)}
    words = {w for w in _norm_title(title).split() if len(w) > 3 and w not in _STOP}
    return words, cves


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


def _same_incident(a: dict, b: dict) -> bool:
    """Two stories describe the same incident if they share a CVE, or enough
    significant title words (Jaccard + absolute overlap)."""
    wa, ca = a["_sig"]
    wb, cb = b["_sig"]
    if ca & cb:                      # a shared CVE is a near-certain match
        return True
    if not wa or not wb:
        return False
    shared = wa & wb
    union = wa | wb
    jaccard = len(shared) / len(union)
    return len(shared) >= 3 and jaccard >= 0.42


def cluster(items: list[dict]) -> list[dict]:
    """Fold same-incident stories from different wires into one representative,
    keeping the highest-ranked as the lead and listing the rest as coverage.

    Assumes `items` is already sorted best-first, so the first seen in a cluster
    becomes its lead. Exact-link duplicates are dropped outright.
    """
    for it in items:
        it["_sig"] = _signature(it["title"])

    seen_links: set[str] = set()
    leads: list[dict] = []
    for item in items:
        if item["link"] in seen_links:
            continue
        seen_links.add(item["link"])
        match = next((lead for lead in leads if _same_incident(lead, item)), None)
        if match is None:
            item["also_sources"] = []
            leads.append(item)
        else:
            match["also_sources"].append(
                {"source": item["source"], "link": item["link"]}
            )
    for lead in leads:
        del lead["_sig"]
        # Distinct source count = this wire + everyone who also covered it.
        names = {lead["source"]} | {a["source"] for a in lead["also_sources"]}
        lead["coverage"] = len(names)
    return leads


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

    fresh.sort(key=lambda i: (i["rank"], i["published_ts"]), reverse=True)
    # Cluster AFTER sorting so the top-ranked story leads each incident, then a
    # multi-source story gets a small boost (more coverage = more important).
    clustered = cluster(fresh)
    for it in clustered:
        it["rank"] += min(it.get("coverage", 1) - 1, 3) * 2
    clustered.sort(key=lambda i: (i["rank"], i["published_ts"]), reverse=True)
    return clustered[:MAX_ITEMS]


if __name__ == "__main__":
    from .fetch import fetch_all

    ranked = process(fetch_all())
    for i in ranked[:8]:
        print(f"[sev {i['severity']}] {i['source']:>18} — {i['title']}")
