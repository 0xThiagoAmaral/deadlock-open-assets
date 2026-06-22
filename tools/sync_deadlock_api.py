#!/usr/bin/env python3
"""Sync live meta stats from deadlock-api.com (optional, requires network)."""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "game" / "meta"

ENDPOINTS = {
    "hero_stats": "https://api.deadlock-api.com/v1/analytics/hero-stats?game_mode=normal",
    "item_stats": "https://api.deadlock-api.com/v1/analytics/item-stats?game_mode=normal",
}


def fetch_json(url: str) -> dict | list | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "umblock-hub/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"  [!] {url}: {e}")
        return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {
        "fetched_at": datetime.now().isoformat(),
        "source": "https://deadlock-api.com",
        "license": "MIT — see https://github.com/deadlock-api/deadlock-api",
        "endpoints": {},
    }

    ok = 0
    for name, url in ENDPOINTS.items():
        data = fetch_json(url)
        if data is None:
            continue
        path = OUT / f"{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        count = len(data) if isinstance(data, list) else len(data.get("data", data))
        meta["endpoints"][name] = {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "records": count}
        print(f"  [+] {name}.json ({count} records)")
        ok += 1

    with open(OUT / "sync_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    if ok == 0:
        print("[*] API unavailable — meta sync skipped (local data still valid)")
        return 1
    print(f"[*] Meta synced ({ok}/{len(ENDPOINTS)} endpoints)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
