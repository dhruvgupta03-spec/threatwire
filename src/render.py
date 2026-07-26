"""LOOP 3 — RENDER.

Turn the ranked feed into a static, Wall-Street-Journal-style site:

  * index.html          — the front page (lead, columns, rail, wire)
  * story/<id>.html      — a ThreatWire "brief" page for every story, with our
                           own summary + a prominent link out to the source

Headlines link to the on-site brief (keeping readers on ThreatWire); each brief
attributes and links to the original publisher. Outputs a self-contained site/.
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import SITE

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
SITE_DIR = ROOT / "site"
STORY_DIR = SITE_DIR / "story"

SEV_LABELS = {3: "Critical", 2: "High", 1: "Notable", 0: "Wire"}


def time_ago(ts: float, now: float) -> str:
    delta = max(now - ts, 0)
    mins = int(delta // 60)
    if mins < 1:
        return "just now"
    if mins < 60:
        return f"{mins}m ago"
    hours = mins // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def _decorate(items: list[dict], now: float) -> list[dict]:
    for it in items:
        it["ago"] = time_ago(it["published_ts"], now)
        it["sev_label"] = SEV_LABELS.get(it.get("severity", 0), "Wire")
        it["kicker"] = it["topics"][0] if it.get("topics") else it["category"]
        it["href"] = f"story/{it['id']}.html"  # internal brief (from front page)
    return items


def _related(item: dict, items: list[dict], k: int = 6) -> list[dict]:
    """Other stories sharing a topic, then recency fallback — never the item itself."""
    topics = set(item.get("topics", []))
    same = [i for i in items if i["id"] != item["id"] and topics & set(i.get("topics", []))]
    if len(same) < k:
        seen = {i["id"] for i in same} | {item["id"]}
        same += [i for i in items if i["id"] not in seen]
    return same[:k]


def build_context(items: list[dict], now: float) -> dict:
    lead = items[0] if items else None
    secondary = items[1:5]
    feature_pool = items[5:]

    critical = [i for i in items if i.get("severity", 0) >= 3][:6]
    sev_counts = {3: 0, 2: 0, 1: 0, 0: 0}
    source_counts: dict[str, int] = {}
    for i in items:
        sev_counts[i.get("severity", 0)] += 1
        source_counts[i["source"]] = source_counts.get(i["source"], 0) + 1
    top_sources = sorted(source_counts.items(), key=lambda kv: kv[1], reverse=True)[:6]

    if sev_counts[3] >= 3:
        posture, posture_class = "ELEVATED", "sev-3"
    elif sev_counts[3] >= 1 or sev_counts[2] >= 5:
        posture, posture_class = "GUARDED", "sev-2"
    else:
        posture, posture_class = "STEADY", "sev-1"

    return {
        "site": SITE,
        "lead": lead,
        "secondary": secondary,
        "features": feature_pool,
        "critical": critical,
        "sev_counts": sev_counts,
        "top_sources": top_sources,
        "posture": posture,
        "posture_class": posture_class,
        "total": len(items),
        "built_at": time.strftime("%A, %B %-d, %Y · %H:%M UTC", time.gmtime(now)),
        "built_epoch": int(now),
        "edition": time.strftime("Vol. 1 · No. %j", time.gmtime(now)),
    }


def render(items: list[dict]) -> Path:
    now = time.time()
    items = _decorate(items, now)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    index_tpl = env.get_template("index.html.j2")
    story_tpl = env.get_template("story.html.j2")

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    STORY_DIR.mkdir(parents=True, exist_ok=True)

    # Front page
    out = SITE_DIR / "index.html"
    out.write_text(index_tpl.render(**build_context(items, now)), encoding="utf-8")

    # A ThreatWire brief for every story
    built_at = time.strftime("%A, %B %-d, %Y · %H:%M UTC", time.gmtime(now))
    for item in items:
        page = story_tpl.render(
            site=SITE, item=item, related=_related(item, items), built_at=built_at
        )
        (STORY_DIR / f"{item['id']}.html").write_text(page, encoding="utf-8")

    # Static assets, self-contained
    for asset in STATIC.glob("*"):
        shutil.copy2(asset, SITE_DIR / asset.name)

    print(f"Rendered front page + {len(items)} briefs → {SITE_DIR}")
    return out


if __name__ == "__main__":
    from .fetch import fetch_all
    from .process import process

    render(process(fetch_all()))
