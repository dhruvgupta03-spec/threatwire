"""LOOP 3 — RENDER.

Turn the ranked, clustered feed into a static, self-updating, WSJ-style site:

  index.html                  front page (lead, columns, rail, wire, live badge)
  story/<id>.html             per-story ThreatWire brief (+ "also covered by")
  topic-<slug>.html           one section page per topic
  severity-critical.html      the critical desk
  search.html + search-index.json    client-side search
  feed.xml / feed.json        ThreatWire's own RSS + JSON feed
  status.json                 build stamp the live page polls to auto-refresh
  CNAME                       written only if SITE["domain"] is set

All internal links are prefixed with a per-page `base` ("" at root, "../" under
story/) so the same nav works at every depth.
"""
from __future__ import annotations

import html as _html
import json
import re
import shutil
import time
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import SITE, TOPICS

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
SITE_DIR = ROOT / "site"
STORY_DIR = SITE_DIR / "story"

SEV_LABELS = {3: "Critical", 2: "High", 1: "Notable", 0: "Wire"}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


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
    return f"{hours // 24}d ago"


def _decorate(items: list[dict], now: float) -> list[dict]:
    for it in items:
        it["ago"] = time_ago(it["published_ts"], now)
        it["sev_label"] = SEV_LABELS.get(it.get("severity", 0), "Wire")
        it["kicker"] = it["topics"][0] if it.get("topics") else it["category"]
        it["href"] = f"story/{it['id']}.html"           # canonical path from root
        cov = it.get("coverage", 1)
        it["coverage_label"] = f"{cov} wires" if cov > 1 else ""
    return items


def _related(item: dict, items: list[dict], k: int = 6) -> list[dict]:
    topics = set(item.get("topics", []))
    same = [i for i in items if i["id"] != item["id"] and topics & set(i.get("topics", []))]
    if len(same) < k:
        seen = {i["id"] for i in same} | {item["id"]}
        same += [i for i in items if i["id"] not in seen]
    return same[:k]


def _nav(items: list[dict]) -> list[dict]:
    """Topics with enough stories to warrant a section, most-covered first."""
    counts: dict[str, int] = {}
    for i in items:
        for t in i.get("topics", []):
            counts[t] = counts.get(t, 0) + 1
    ranked = sorted((t for t in TOPICS if counts.get(t, 0) >= 3),
                    key=lambda t: counts[t], reverse=True)
    return [{"label": t, "slug": slug(t), "count": counts[t]} for t in ranked[:7]]


def build_context(items: list[dict], now: float, nav: list[dict]) -> dict:
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
        "site": SITE, "base": "", "nav": nav,
        "lead": lead, "secondary": secondary, "features": feature_pool,
        "critical": critical, "sev_counts": sev_counts, "top_sources": top_sources,
        "posture": posture, "posture_class": posture_class, "total": len(items),
        "built_at": time.strftime("%A, %B %-d, %Y · %H:%M UTC", time.gmtime(now)),
        "built_epoch": int(now),
        "edition": time.strftime("Vol. 1 · No. %j", time.gmtime(now)),
    }


# --- Feeds --------------------------------------------------------------------
def _rss(items: list[dict], now: float) -> str:
    def esc(s: str) -> str:
        return _html.escape(s or "", quote=True)

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"><channel>',
        f"<title>{esc(SITE['name'])} — {esc(SITE['tagline'])}</title>",
        f"<description>{esc(SITE['motto'])}</description>",
        f"<link>{esc(SITE['base_url'] or 'https://github.com')}</link>",
        f"<lastBuildDate>{time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(now))}</lastBuildDate>",
    ]
    for it in items[:50]:
        pub = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(it["published_ts"]))
        cats = "".join(f"<category>{esc(t)}</category>" for t in it.get("topics", []))
        parts += [
            "<item>",
            f"<title>{esc(it['title'])}</title>",
            f"<link>{esc(it['link'])}</link>",
            f"<guid isPermaLink=\"true\">{esc(it['link'])}</guid>",
            f"<pubDate>{pub}</pubDate>",
            f"<source url=\"{esc(it['link'])}\">{esc(it['source'])}</source>",
            cats,
            f"<description><![CDATA[{it.get('summary','')} — via {it['source']} (severity: {it['sev_label']}), aggregated by ThreatWire.]]></description>",
            "</item>",
        ]
    parts.append("</channel></rss>")
    return "\n".join(parts)


def _json_feed(items: list[dict]) -> str:
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": f"{SITE['name']} — {SITE['tagline']}",
        "description": SITE["motto"],
        "home_page_url": SITE["base_url"] or "",
        "items": [
            {
                "id": it["link"], "url": it["link"], "title": it["title"],
                "content_text": f"{it.get('summary','')} — via {it['source']} (severity: {it['sev_label']}).",
                "date_published": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(it["published_ts"])),
                "tags": it.get("topics", []),
            }
            for it in items[:50]
        ],
    }
    return json.dumps(feed, indent=2, ensure_ascii=False)


def render(items: list[dict]) -> Path:
    now = time.time()
    items = _decorate(items, now)
    nav = _nav(items)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True, lstrip_blocks=True,
    )
    index_tpl = env.get_template("index.html.j2")
    story_tpl = env.get_template("story.html.j2")
    section_tpl = env.get_template("section.html.j2")
    search_tpl = env.get_template("search.html.j2")

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    STORY_DIR.mkdir(parents=True, exist_ok=True)
    built_at = time.strftime("%A, %B %-d, %Y · %H:%M UTC", time.gmtime(now))

    # Front page
    (SITE_DIR / "index.html").write_text(
        index_tpl.render(**build_context(items, now, nav)), encoding="utf-8")

    # Per-story briefs (base="../" because they live under story/)
    for item in items:
        (STORY_DIR / f"{item['id']}.html").write_text(
            story_tpl.render(site=SITE, base="../", nav=nav, item=item,
                             related=_related(item, items), built_at=built_at),
            encoding="utf-8")

    # Topic section pages
    for t in nav:
        rows = [i for i in items if t["label"] in i.get("topics", [])]
        (SITE_DIR / f"topic-{t['slug']}.html").write_text(
            section_tpl.render(site=SITE, base="", nav=nav, built_at=built_at,
                               heading=t["label"], subtitle=f"{len(rows)} stories on the wire",
                               rows=rows),
            encoding="utf-8")

    # Critical desk
    crit = [i for i in items if i.get("severity", 0) >= 3]
    (SITE_DIR / "severity-critical.html").write_text(
        section_tpl.render(site=SITE, base="", nav=nav, built_at=built_at,
                           heading="Critical Desk", subtitle=f"{len(crit)} critical-severity stories",
                           rows=crit),
        encoding="utf-8")

    # Search page + index
    (SITE_DIR / "search.html").write_text(
        search_tpl.render(site=SITE, base="", nav=nav, built_at=built_at), encoding="utf-8")
    (SITE_DIR / "search-index.json").write_text(
        json.dumps([
            {"t": i["title"], "s": i["source"], "u": i["href"],
             "k": ", ".join(i.get("topics", [])), "v": i.get("severity", 0)}
            for i in items
        ], ensure_ascii=False), encoding="utf-8")

    # Feeds + live-update stamp
    (SITE_DIR / "feed.xml").write_text(_rss(items, now), encoding="utf-8")
    (SITE_DIR / "feed.json").write_text(_json_feed(items), encoding="utf-8")
    (SITE_DIR / "status.json").write_text(
        json.dumps({"built_epoch": int(now), "total": len(items)}), encoding="utf-8")

    # Custom domain (only if configured)
    if SITE.get("domain"):
        (SITE_DIR / "CNAME").write_text(SITE["domain"].strip() + "\n", encoding="utf-8")

    # Static assets, self-contained
    for asset in STATIC.glob("*"):
        shutil.copy2(asset, SITE_DIR / asset.name)

    print(f"Rendered front page + {len(items)} briefs + {len(nav)} sections + feeds → {SITE_DIR}")
    return SITE_DIR / "index.html"


if __name__ == "__main__":
    from .fetch import fetch_all
    from .process import process

    render(process(fetch_all()))
