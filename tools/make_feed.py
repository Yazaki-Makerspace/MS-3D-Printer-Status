#!/usr/bin/env python3
"""Write status.rss from status.json: one item that says whether the printer feed is healthy,
dated ok_at (the last healthy update).

Power Automate's RSS connector reads it every 30 minutes and emails staff when ok_at gets old,
which catches both "the Surface stopped sending" and "it sends, but no printer is answering".

    python3 make_feed.py _site/status.json > _site/status.rss
"""
import json
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

PAGE = "https://yazaki-makerspace.github.io/MS-3D-Printer-Status/"


def when(z):
    try:
        return datetime.strptime(z[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return datetime.now(timezone.utc)


def main():
    d = json.load(open(sys.argv[1]))
    ps = d.get("printers") or []
    counts = {}
    for p in ps:
        counts[p.get("state", "unknown")] = counts.get(p.get("state", "unknown"), 0) + 1
    answering = [p for p in ps if p.get("state") not in ("offline", "unknown")]
    if d.get("demo"):
        problem = "the board is showing demo data"
    elif not ps:
        problem = "no printers in the feed (check the Bambu sign-in on the Surface)"
    elif not answering:
        problem = f"none of the {len(ps)} printers is answering (printer Wi-Fi or Bambu Cloud)"
    else:
        problem = ""
    title = "PROBLEM: " + problem if problem else "OK"
    summary = (f"Last update {d.get('updated', '?')} (UTC). Last healthy {d.get('ok_at', '?')} (UTC). "
               + (f"{len(ps)} printers: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())) if ps else "No printers."))
    ok_at, updated = when(d.get("ok_at")), when(d.get("updated"))
    print(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>3D Lab printer status: health</title>
<link>{PAGE}</link>
<description>Whether the 3D Lab printer status feed is live. The item date is the last healthy update.</description>
<lastBuildDate>{format_datetime(updated)}</lastBuildDate>
<item>
<title>{escape(title)}</title>
<link>{PAGE}</link>
<description>{escape(summary)}</description>
<pubDate>{format_datetime(ok_at)}</pubDate>
<guid isPermaLink="false">ok-{ok_at.strftime('%Y%m%dT%H%M%SZ')}</guid>
</item>
</channel>
</rss>""")


if __name__ == "__main__":
    main()
