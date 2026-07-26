"""LOOP 1 — FETCH.

Pull the latest entries from every configured wire source and normalize them
into a single flat list of dicts. Network failures on one feed never abort the
run; they are logged and skipped so the newsroom stays resilient.
"""
from __future__ import annotations

import hashlib
import html
import re
import socket
import ssl
import time
from calendar import timegm

import certifi
import feedparser

from .config import FEEDS

# macOS Python.org builds ship without root CA certs, so HTTPS feed fetches fail
# with CERTIFICATE_VERIFY_FAILED. Point urllib (used by feedparser) at certifi's
# bundle. Harmless on Linux/CI where certs already work.
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# feedparser sets no network timeout; one stalling server would hang the whole
# loop (and CI). Cap every socket read so a slow feed is skipped, not fatal.
FETCH_TIMEOUT = 15
socket.setdefaulttimeout(FETCH_TIMEOUT)

USER_AGENT = "ThreatWire/1.0 (+https://github.com/) threat-intel aggregator"

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _clean(text: str, limit: int = 320) -> str:
    """Strip HTML, collapse whitespace, unescape entities, and truncate."""
    if not text:
        return ""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "…"
    return text


def _entry_timestamp(entry) -> float | None:
    """Best-effort epoch seconds (UTC) for an entry."""
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return float(timegm(parsed))
    return None


def _make_id(link: str, title: str) -> str:
    return hashlib.sha1(f"{link}|{title}".encode("utf-8")).hexdigest()[:16]


def fetch_feed(source: dict) -> list[dict]:
    """Fetch one source, returning a list of normalized items (or [] on error)."""
    try:
        parsed = feedparser.parse(source["url"], agent=USER_AGENT)
    except Exception as exc:  # noqa: BLE001 — one bad feed must not kill the run
        print(f"  ! {source['name']}: fetch error: {exc}")
        return []

    if parsed.bozo and not parsed.entries:
        print(f"  ! {source['name']}: unreadable feed ({parsed.get('bozo_exception', 'unknown')})")
        return []

    items: list[dict] = []
    for entry in parsed.entries:
        link = entry.get("link", "").strip()
        title = _clean(entry.get("title", ""), limit=200)
        if not link or not title:
            continue
        summary = _clean(entry.get("summary", entry.get("description", "")))
        ts = _entry_timestamp(entry)
        items.append(
            {
                "id": _make_id(link, title),
                "title": title,
                "link": link,
                "summary": summary,
                "source": source["name"],
                "category": source["category"],
                "group": source.get("group", "news"),
                "published_ts": ts,
            }
        )
    print(f"  ✓ {source['name']}: {len(items)} items")
    return items


def fetch_all() -> list[dict]:
    """Fetch every configured source and return the combined, un-ranked list."""
    print(f"Fetching {len(FEEDS)} sources at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    all_items: list[dict] = []
    for source in FEEDS:
        all_items.extend(fetch_feed(source))
    print(f"Fetched {len(all_items)} total items.")
    return all_items


if __name__ == "__main__":
    from pprint import pprint

    pprint(fetch_all()[:3])
