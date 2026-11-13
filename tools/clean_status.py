#!/usr/bin/env python3
"""Read a printer status JSON on stdin, print only the screen-safe fields.

Same whitelist as the collector: no job or file names, serials, codes or tokens
can reach the public status.json, even if something else gets sent.
"""
import json
import re
import sys
from datetime import datetime, timezone

STATES = {"printing", "preparing", "paused", "done", "stopped", "attention", "offline", "free", "unknown"}


def s(v, n):
    return v[:n] if isinstance(v, str) else None


def num(v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return int(min(hi, max(lo, round(v))))


def iso(v):
    return v if isinstance(v, str) and re.fullmatch(r"\d{4}-\d\d-\d\dT[\d:.]+Z", v) else None


def hexc(v):
    return v.lower() if isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v) else None


def drop_none(d):
    return {k: v for k, v in d.items() if v is not None}


def clean(d):
    if not isinstance(d, dict):
        d = {}
    printers = []
    for p in (d.get("printers") if isinstance(d.get("printers"), list) else [])[:60]:
        if not isinstance(p, dict):
            continue
        o = drop_none({
            "name": s(p.get("name"), 40) or "Printer", "model": s(p.get("model"), 20), "group": s(p.get("group"), 20),
            "state": p.get("state") if p.get("state") in STATES else "unknown", "since": iso(p.get("since")),
            "progress": num(p.get("progress"), 0, 100), "remaining_min": num(p.get("remaining_min"), 0, 9999),
            "layer": num(p.get("layer"), 0, 99999), "total_layers": num(p.get("total_layers"), 0, 99999),
            "stage": s(p.get("stage"), 40),
        })
        if isinstance(p.get("filaments"), list):
            o["filaments"] = [{"color": hexc(f.get("color")) or "#d8dcd9", "type": s(f.get("type"), 12) or "",
                               "active": f.get("active") is True} for f in p["filaments"][:16] if isinstance(f, dict)]
        printers.append(o)
    out = drop_none({
        "updated": iso(d.get("updated")) or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stale_after_s": num(d.get("stale_after_s"), 30, 86400) or 1080,
        "note": s(d.get("note"), 140),
        "printers": printers,
        "demo": True if d.get("demo") is True else None,
    })
    return out


if __name__ == "__main__":
    raw = sys.stdin.read().strip()
    try:
        data = json.loads(raw) if raw and raw != "null" else {}
    except ValueError:
        data = {}
    print(json.dumps(clean(data), separators=(",", ":")))
