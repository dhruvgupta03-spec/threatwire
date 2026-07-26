"""Local dev trigger: run the build loop forever, every N minutes.

For production the GitHub Actions cron is the trigger; this is the same loop
for your Mac so you can watch the front page update live during development.

    python -m src.loop            # default 15 min
    python -m src.loop 5          # every 5 min
"""
from __future__ import annotations

import sys
import time

from .build import build

DEFAULT_MINUTES = 15


def main() -> None:
    minutes = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MINUTES
    interval = minutes * 60
    print(f"ThreatWire dev loop — rebuilding every {minutes} min. Ctrl-C to stop.\n")
    while True:
        try:
            build()
        except KeyboardInterrupt:
            print("\nLoop stopped.")
            return
        except Exception as exc:  # noqa: BLE001 — a bad run must not kill the loop
            print(f"! build error (will retry next cycle): {exc}")
        print(f"— sleeping {minutes} min —\n")
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nLoop stopped.")
            return


if __name__ == "__main__":
    main()
