#!/usr/bin/env python3
"""
Organize extracted Deadlock assets into an AI-enriched catalog for scripts, builds, mods.

Uses DeepSeek to annotate and cross-reference vdata, particles, images.
Falls back to local-only index if --no-ai or API fails.

Usage:
  python tools/organize_with_deepseek.py
  python tools/organize_with_deepseek.py --no-ai
  python tools/organize_with_deepseek.py --enrich particles
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from vpk_common import CODENAME_TO_HERO, ROOT, load_deepseek_key

EXTRACTED = ROOT / "assets" / "extracted"
CATALOG_DIR = EXTRACTED / "catalog"
VDATA_DIR = EXTRACTED / "vdata" / "scripts"
PARTICLES_IDX = EXTRACTED / "indexes" / "particles_index.json"


def parse_vdata_abilities_summary() -> dict:
    path = VDATA_DIR / "abilities.vdata"
    if not path.exists():
        path = ROOT / "assets" / "vdata" / "abilities.vdata"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    abilities = {}
    blocks = re.split(r'\n\t([a-zA-Z0-9_]+)\s*=\s*\{', text)
    for i in range(1, len(blocks), 2):
        name = blocks[i]
        body = blocks[i + 1] if i + 1 < len(blocks) else ""
        entry = {"internal": name}
        for field in ("m_strName", "m_strIcon", "m_strWeaponName", "m_eAbilityType"):
            m = re.search(rf'{field}\s*=\s*"([^"]*)"', body)
            if m:
                entry[field.replace("m_str", "").replace("m_e", "").lower()] = m.group(1)
        cd = re.search(r"m_flCooldown\s*=\s*([\d.]+)", body)
        if cd:
            entry["cooldown"] = float(cd.group(1))
        abilities[name] = entry
    return abilities


def parse_vdata_heroes_summary() -> dict:
    path = VDATA_DIR / "heroes.vdata"
    if not path.exists():
        path = ROOT / "assets" / "vdata" / "heroes.vdata"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    heroes = {}
    for m in re.finditer(r'm_strName\s*=\s*"([^"]+)".*?m_HeroID\s*=\s*(\d+)', text, re.DOTALL):
        heroes[m.group(1)] = {"hero_id_num": int(m.group(2))}
    return {"count": len(heroes), "sample": dict(list(heroes.items())[:20])}


def build_local_catalog() -> dict:
    catalog = {
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "source": "local_index",
        "heroes_codename_map": CODENAME_TO_HERO,
        "abilities_vdata": parse_vdata_abilities_summary(),
        "heroes_vdata": parse_vdata_heroes_summary(),
        "asset_counts": {},
        "tool_routes": {
            "lua_scripts": {
                "particles": "assets/extracted/indexes/particles_index.json",
                "vdata_abilities": "assets/vdata/abilities.vdata",
                "images_heroes": "images/deadlock/heroes_circle/",
                "images_abilities": "images/deadlock/abilities/",
            },
            "build_creator": {
                "items": "images/deadlock/items/",
                "upgrades": "images/deadlock/upgrades/",
                "heroes": "assets/game/heroes.json",
                "economy": "assets/game/economy.json",
                "vdata": "assets/vdata/heroes.vdata",
            },
            "mods_ui": {
                "panorama_layout": "assets/extracted/panorama/layout/",
                "panorama_styles": "assets/extracted/panorama/styles/",
                "ui_assets": "images/deadlock/ui/",
            },
            "counterspell": {
                "particles_by_hero": "assets/extracted/indexes/particles_index.json",
                "reference_script": "deadlock_scripts/AutoCounterspell.lua",
            },
        },
    }

    if PARTICLES_IDX.exists():
        with open(PARTICLES_IDX, encoding="utf-8") as f:
            pdata = json.load(f)
        catalog["particles"] = {
            "total": pdata.get("total", 0),
            "heroes": pdata.get("heroes", {}),
            "top_cast_particles": _top_cast_particles(pdata),
        }
        catalog["asset_counts"]["particles"] = pdata.get("total", 0)

    manifest = EXTRACTED / "manifest.json"
    if manifest.exists():
        with open(manifest, encoding="utf-8") as f:
            m = json.load(f)
        catalog["extraction_stats"] = m.get("stats", {})
        catalog["asset_counts"].update(m.get("stats", {}).get("categories", {}))

    images_root = ROOT / "images" / "deadlock"
    if images_root.exists():
        for sub in images_root.iterdir():
            if sub.is_dir():
                n = sum(1 for _ in sub.rglob("*.png"))
                catalog["asset_counts"][f"images_{sub.name}"] = n

    return catalog


def _top_cast_particles(pdata: dict) -> dict:
    """Group likely combat particles by hero for counterspell/dodge tools."""
    result = defaultdict(list)
    keywords = ("cast", "charge", "ult", "hook", "bomb", "dash", "impact", "stun", "projectile")
    for hero, entries in pdata.get("entries", {}).items():
        for e in entries:
            name = e.get("name", "")
            if any(k in name.lower() for k in keywords):
                if len(result[hero]) < 15:
                    result[hero].append(name)
    return dict(result)


def call_deepseek(local_catalog: dict, focus: str = "all") -> dict:
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("pip install openai")

    api_key = load_deepseek_key()
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    summary = {
        "heroes_map": local_catalog.get("heroes_codename_map"),
        "abilities_count": len(local_catalog.get("abilities_vdata", {})),
        "abilities_sample": dict(list(local_catalog.get("abilities_vdata", {}).items())[:30]),
        "particles_total": local_catalog.get("particles", {}).get("total"),
        "particles_top_cast": local_catalog.get("particles", {}).get("top_cast_particles"),
        "asset_counts": local_catalog.get("asset_counts"),
        "focus": focus,
    }

    system = """You are a Deadlock game data architect for the Umblock toolchain.
Organize extracted VPK assets into a structured catalog for:
- Lua cheat scripts (Umbrella loader)
- Build creator tools
- UI mods / Panorama automation
- Counterspell/dodge systems

Output ONLY valid JSON with this structure:
{
  "meta": { "patch_notes": "...", "confidence": "high|medium" },
  "heroes": { "hero_id": { "codename": "", "display_name": "", "key_abilities": [], "counterspell_particles": [], "build_tags": [] } },
  "abilities": { "internal_name": { "display_guess": "", "type": "ult|sig|item", "script_use": "" } },
  "items": { "category_hints": [] },
  "tool_recommendations": {
    "lua_scripts": [{ "feature": "", "assets_needed": [], "priority": 1 }],
    "build_creator": [{ "feature": "", "assets_needed": [] }],
    "mods": [{ "feature": "", "assets_needed": [] }]
  },
  "cross_references": [{ "particle": "", "ability": "", "hero": "", "use_case": "counterspell|dodge|esp" }]
}

NEVER invent ability names not in the input. Use "DATA_MISSING" when unsure."""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Organize this Deadlock extraction summary:\n{json.dumps(summary, ensure_ascii=False)[:12000]}"},
        ],
        temperature=0.1,
        max_tokens=8000,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    return json.loads(content)


def merge_catalogs(local: dict, ai: dict) -> dict:
    merged = {**local, "ai_enriched": ai, "source": "local+deepseek", "enriched_at": datetime.now().isoformat()}
    return merged


def main():
    parser = argparse.ArgumentParser(description="Organize extracted assets with DeepSeek")
    parser.add_argument("--no-ai", action="store_true", help="Local index only")
    parser.add_argument("--enrich", default="all", help="Focus: all, particles, builds, scripts")
    args = parser.parse_args()

    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    local = build_local_catalog()

    local_path = CATALOG_DIR / "local_index.json"
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(local, f, indent=2, ensure_ascii=False)
    print(f"[*] Local catalog -> {local_path}")

    if args.no_ai:
        print("[*] Skipping DeepSeek (--no-ai)")
        return

    print("[*] Calling DeepSeek for enrichment...")
    try:
        from cli_progress import ProgressTracker, fmt_time, DIM, R
        import time
        t0 = time.time()
        prog = ProgressTracker(total=100, label="DeepSeek")
        prog.advance(20, "building summary...")
        ai = call_deepseek(local, args.enrich)
        prog.set(100, "catalog ready")
        prog.finish()
        print(f"  {DIM}API call took {fmt_time(time.time() - t0)}{R}")
        merged = merge_catalogs(local, ai)
        out = CATALOG_DIR / "deadlock_knowledge.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        print(f"[*] AI catalog -> {out}")

        kb = ROOT / "assets" / "game" / "knowledge_base.json"
        if kb.exists() and ai.get("abilities"):
            print(f"[*] Cross-ref available: {len(ai.get('abilities', {}))} abilities annotated")
    except Exception as e:
        print(f"[!] DeepSeek failed: {e}")
        print("[*] Local catalog still available at", local_path)


if __name__ == "__main__":
    main()
