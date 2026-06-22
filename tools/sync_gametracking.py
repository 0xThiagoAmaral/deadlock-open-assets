#!/usr/bin/env python3
"""Sync plaintext game files from SteamDatabase/GameTracking-Deadlock."""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "game" / "localization"
BASE = "https://raw.githubusercontent.com/SteamTracking/GameTracking-Deadlock/master/game/citadel"

FILES = {
    "citadel_heroes_english.txt": "resource/localization/citadel_heroes/citadel_heroes_english.txt",
    "citadel_mods_english.txt": "resource/localization/citadel_mods/citadel_mods_english.txt",
    "citadel_main_english.txt": "resource/localization/citadel_main/citadel_main_english.txt",
}


def fetch(path: str) -> str | None:
    url = f"{BASE}/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "umblock-hub/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [!] {path}: {e}")
        return None


def parse_items_kv(text: str) -> dict:
    items = {}
    for m in re.finditer(
        r'"([^"]+)"\s*\n\s*\{\s*\n\s*"name"\s+"([^"]+)"',
        text,
    ):
        key, name = m.group(1), m.group(2)
        items[key] = {"display_name": name, "internal": key}
    return items


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"fetched_at": datetime.now().isoformat(), "source": "SteamTracking/GameTracking-Deadlock", "files": {}}

    for local_name, remote_path in FILES.items():
        text = fetch(remote_path)
        if not text:
            continue
        dest = OUT / local_name
        dest.write_text(text, encoding="utf-8")
        result["files"][local_name] = {"path": str(dest.relative_to(ROOT)).replace("\\", "/"), "bytes": len(text)}
        print(f"  [+] {local_name} ({len(text):,} bytes)")

    items_path = OUT / "citadel_mods_english.txt"
    if items_path.exists():
        parsed = parse_items_kv(items_path.read_text(encoding="utf-8", errors="replace"))
        if not parsed:
            # fallback: key-value lines "key" "value"
            text = items_path.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r'"([^"]+)"\s+"([^"]+)"', text):
                parsed[m.group(1)] = {"display_name": m.group(2), "internal": m.group(1)}
        parsed_path = OUT / "items_display_names.json"
        with open(parsed_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        result["items_parsed"] = len(parsed)
        print(f"  [+] items_display_names.json ({len(parsed)} entries)")

    meta = OUT / "sync_meta.json"
    with open(meta, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"[*] Meta -> {meta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
