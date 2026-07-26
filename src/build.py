"""One turn of the newsroom loop: FETCH → PROCESS → RENDER.

This is the single entry point used both locally and by CI:
    python -m src.build

Loop-engineering notes:
  * State  — the ranked edition is persisted to data/latest.json each run.
  * Verify — a minimum-item gate; an empty fetch fails the build (exit 1) so CI
             never publishes a blank front page.
  * Stop   — this function does exactly one iteration and returns; the *trigger*
             (cron / dev loop) decides when to run it again.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from .fetch import fetch_all
from .process import process
from .render import render

DATA = Path(__file__).resolve().parent.parent / "data"
MIN_ITEMS = 5  # verification gate: below this, something is wrong upstream.


def build() -> int:
    started = time.time()
    items = process(fetch_all())

    # --- Verification gate ---------------------------------------------------
    if len(items) < MIN_ITEMS:
        print(f"✗ VERIFY FAILED: only {len(items)} items (< {MIN_ITEMS}). "
              f"Not publishing. Check feed health.", file=sys.stderr)
        return 1

    # --- State ---------------------------------------------------------------
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "latest.json").write_text(
        json.dumps({"built_epoch": int(started), "count": len(items), "items": items},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    render(items)
    print(f"✓ Build OK: {len(items)} stories in {time.time() - started:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
