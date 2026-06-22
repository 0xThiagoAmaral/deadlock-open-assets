#!/usr/bin/env python3
"""
Build unified community manifests for the Deadlock Open Assets Hub.

Merges extracted VPK data, curated JSON, image paths, indexes, and optional
live meta into consumer-ready manifests under manifests/.

Usage:
  python tools/build_community_hub.py
  python tools/build_community_hub.py --sync-remote   # also fetch API + GameTracking
  python tools/build_community_hub.py --docs-only     # regenerate CATALOG.md only
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFESTS = ROOT / "manifests"
DOCS = ROOT / "docs"

PATHS = {
    "heroes": ROOT / "assets" / "game" / "heroes.json",
    "items": ROOT / "assets" / "game" / "items.json",
    "economy": ROOT / "assets" / "game" / "economy.json",
    "knowledge": ROOT / "assets" / "game" / "knowledge_base.json",
    "images_manifest": ROOT / "assets" / "game" / "images_manifest.json",
    "extracted_manifest": ROOT / "assets" / "extracted" / "manifest.json",
    "local_index": ROOT / "assets" / "extracted" / "catalog" / "local_index.json",
    "particles_index": ROOT / "assets" / "extracted" / "indexes" / "particles_index.json",
    "sounds_index": ROOT / "assets" / "extracted" / "indexes" / "sounds_index.json",
    "models_index": ROOT / "assets" / "extracted" / "indexes" / "models_index.json",
    "vpk_inventory": ROOT / "assets" / "extracted" / "indexes" / "vpk_inventory.json",
    "items_display": ROOT / "assets" / "game" / "localization" / "items_display_names.json",
    "hero_stats": ROOT / "assets" / "game" / "meta" / "hero_stats.json",
    "item_stats": ROOT / "assets" / "game" / "meta" / "item_stats.json",
    "images_root": ROOT / "images" / "deadlock",
    "vdata_root": ROOT / "assets" / "vdata",
    "panorama_root": ROOT / "assets" / "extracted" / "panorama",
    "particles_root": ROOT / "assets" / "extracted" / "particles",
}


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def count_files(root: Path, pattern: str = "*") -> int:
    if not root.exists():
        return 0
    if pattern == "*.png":
        return sum(1 for _ in root.rglob("*.png"))
    if pattern == "*.vdata":
        return sum(1 for _ in root.rglob("*.vdata"))
    if pattern == "*.vpcf":
        return sum(1 for _ in root.rglob("*.vpcf"))
    if pattern == "*.xml":
        return sum(1 for _ in root.rglob("*.xml"))
    if pattern == "*.css":
        return sum(1 for _ in root.rglob("*.css"))
    return sum(1 for _ in root.rglob(pattern))


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_")


def build_codenames(local_index: dict | None) -> dict:
    if local_index and local_index.get("heroes_codename_map"):
        return {
            "version": "1.0.0",
            "description": "VPK internal codename -> community hero_id",
            "map": local_index["heroes_codename_map"],
            "reverse": {v: k for k, v in local_index["heroes_codename_map"].items()},
        }
    from vpk_common import CODENAME_TO_HERO
    return {
        "version": "1.0.0",
        "description": "VPK internal codename -> community hero_id",
        "map": CODENAME_TO_HERO,
        "reverse": {v: k for k, v in CODENAME_TO_HERO.items()},
    }


def build_heroes_unified(heroes: dict, extracted: dict | None, codenames: dict) -> dict:
    catalog_heroes = (extracted or {}).get("catalog", {}).get("heroes", {})
    reverse = codenames.get("reverse", {})
    unified = {}

    for display_name, info in heroes.get("heroes", {}).items():
        hero_id = None
        for internal in info.get("internal_names", []):
            if internal in reverse:
                hero_id = reverse[internal]
                break
            if internal in codenames.get("map", {}):
                hero_id = codenames["map"][internal]
                break
        if not hero_id:
            hero_id = slugify(display_name)

        entry = {
            "id": hero_id,
            "display_name": display_name,
            "internal_names": info.get("internal_names", []),
            "codename": reverse.get(hero_id),
            "role": info.get("role"),
            "tags": info.get("tags", []),
            "complexity": info.get("complexity"),
            "abilities": info.get("abilities", {}),
            "verified": info.get("verified", False),
        }
        if hero_id in catalog_heroes:
            entry["images"] = catalog_heroes[hero_id]
        unified[hero_id] = entry

    for hero_id, paths in catalog_heroes.items():
        if hero_id not in unified:
            unified[hero_id] = {"id": hero_id, "display_name": hero_id.replace("_", " ").title(), "images": paths}

    return {
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "count": len(unified),
        "bind_map": heroes.get("bind_map"),
        "heroes": unified,
    }


def build_items_unified(items: dict, extracted_catalog: dict, items_display: dict | None) -> dict:
    catalog_items = extracted_catalog.get("items", {}) if extracted_catalog else {}
    catalog_upgrades = extracted_catalog.get("upgrades", {}) if extracted_catalog else {}
    display = items_display or {}

    unified = []
    for item in items.get("items", []):
        name = item["name"]
        key = slugify(name)
        entry = {**item, "id": key}
        for cat_key, path in catalog_items.items():
            if key in cat_key or slugify(cat_key) == key:
                entry["image"] = path
                break
        if key in display:
            entry["internal_key"] = display[key].get("internal")
        unified.append(entry)

    return {
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "total_items": len(unified),
        "categories": items.get("categories", {}),
        "items": unified,
        "upgrades_catalog": catalog_upgrades,
        "upgrade_count": len(catalog_upgrades),
    }


def build_images_registry(extracted: dict | None, images_root: Path) -> dict:
    catalog = (extracted or {}).get("catalog", {})
    categories = {}
    for sub in sorted(images_root.iterdir()) if images_root.exists() else []:
        if sub.is_dir():
            categories[sub.name] = {
                "path": f"images/deadlock/{sub.name}/",
                "count": count_files(sub, "*.png"),
            }
    return {
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "root": "images/deadlock/",
        "total_pngs": count_files(images_root, "*.png"),
        "categories": categories,
        "heroes": catalog.get("heroes", {}),
        "items": catalog.get("items", {}),
        "upgrades": catalog.get("upgrades", {}),
        "abilities": catalog.get("abilities", {}),
        "ui": {k: v for k, v in catalog.items() if k.startswith("ui") or k in ("ranked", "shop", "minimap", "hud", "icons", "postgame")},
    }


def build_assets_index() -> dict:
    return {
        "version": "1.0.0",
        "generated": datetime.now().isoformat(),
        "repository": "Deadlock Open Assets Hub",
        "directories": {
            "data": {
                "path": "assets/game/",
                "description": "Curated JSON — heroes, items, economy, knowledge base, localization",
                "files": ["heroes.json", "items.json", "economy.json", "knowledge_base.json"],
            },
            "images": {
                "path": "images/deadlock/",
                "count": count_files(PATHS["images_root"], "*.png"),
                "description": "Hero, ability, item, upgrade, and UI icons (PNG from VPK)",
            },
            "vdata": {
                "path": "assets/vdata/",
                "count": count_files(PATHS["vdata_root"], "*.vdata"),
                "description": "Decompiled game data (abilities, heroes, modifiers)",
            },
            "particles": {
                "path": "assets/extracted/particles/abilities/",
                "count": count_files(PATHS["particles_root"], "*.vpcf"),
                "description": "Decompiled ability particle systems — large, use Git LFS or Releases",
            },
            "panorama": {
                "path": "assets/extracted/panorama/",
                "layout_count": count_files(PATHS["panorama_root"] / "layout", "*.xml") if (PATHS["panorama_root"] / "layout").exists() else 0,
                "styles_count": count_files(PATHS["panorama_root"] / "styles", "*.css") if (PATHS["panorama_root"] / "styles").exists() else 0,
                "description": "Decompiled Panorama UI (XML layout + CSS)",
            },
            "indexes": {
                "path": "assets/extracted/indexes/",
                "description": "Particle, sound, and model path indexes",
            },
            "catalog": {
                "path": "assets/extracted/catalog/local_index.json",
                "description": "Cross-reference index (codenames, vdata summaries, particles)",
            },
            "tools": {
                "path": "tools/",
                "description": "VPK extraction and hub build pipeline",
            },
        },
    }


def build_hub_manifest(stats: dict, extracted: dict | None) -> dict:
    dump = extracted or {}
    return {
        "version": "1.0.0",
        "name": "deadlock-open-assets",
        "game": "Deadlock",
        "generated": datetime.now().isoformat(),
        "extraction": {
            "tier": dump.get("tier"),
            "dump_date": dump.get("dump_date"),
            "tool": dump.get("tool"),
            "vpk_files": dump.get("stats", {}).get("vpk_inventory"),
        },
        "stats": stats,
        "manifests": {
            "hub": "manifests/hub.json",
            "heroes": "manifests/heroes.json",
            "items": "manifests/items.json",
            "images": "manifests/images.json",
            "codenames": "manifests/codenames.json",
            "assets_index": "manifests/assets_index.json",
            "particles_index": "assets/extracted/indexes/particles_index.json",
            "sounds_index": "assets/extracted/indexes/sounds_index.json",
            "models_index": "assets/extracted/indexes/models_index.json",
        },
        "data_sources": {
            "vpk_extraction": "Local Steam install via Source2Viewer-CLI",
            "gametracking": "SteamDatabase/GameTracking-Deadlock",
            "live_meta": "deadlock-api.com (optional)",
            "reference": "deadlock-open-data community repo",
        },
        "legal": {
            "game_assets": "Deadlock assets are property of Valve. Provided for research, modding, and tool development under Valve fan content guidelines.",
            "tooling": "MIT License — see LICENSE",
        },
    }


def write_catalog_md(hub: dict, heroes: dict, items: dict, images: dict, assets: dict) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Deadlock Open Assets — Catalog",
        "",
        f"> Generated: {hub['generated']}",
        "",
        "## Quick stats",
        "",
        f"| Asset | Count |",
        f"|-------|-------|",
    ]
    for k, v in hub.get("stats", {}).items():
        lines.append(f"| {k} | {v:,} |" if isinstance(v, int) else f"| {k} | {v} |")

    lines += [
        "",
        "## Directory map",
        "",
    ]
    for name, info in assets.get("directories", {}).items():
        desc = info.get("description", "")
        path = info.get("path", "")
        cnt = info.get("count") or info.get("layout_count")
        extra = f" ({cnt:,} files)" if cnt else ""
        lines.append(f"- **`{path}`** — {desc}{extra}")

    lines += [
        "",
        "## Heroes",
        "",
        f"**{heroes.get('count', 0)}** heroes with abilities, codenames, and image paths.",
        "",
        "| Hero ID | Display | Icons |",
        "|---------|---------|-------|",
    ]
    for hid, h in sorted(heroes.get("heroes", {}).items()):
        imgs = h.get("images", {})
        icon_note = "sm" if imgs.get("path_sm") else ("-" if not imgs else "partial")
        lines.append(f"| `{hid}` | {h.get('display_name', hid)} | {icon_note} |")

    lines += [
        "",
        "## Images",
        "",
        f"**{images.get('total_pngs', 0):,}** PNG files organized under `images/deadlock/`.",
        "",
        "| Category | Path | Count |",
        "|----------|------|-------|",
    ]
    for cat, info in sorted(images.get("categories", {}).items()):
        lines.append(f"| {cat} | `{info['path']}` | {info['count']} |")

    lines += [
        "",
        "## Items & upgrades",
        "",
        f"- **{items.get('total_items', 0)}** shop items with stats",
        f"- **{items.get('upgrade_count', 0)}** upgrade/mod icons catalogued",
        "",
        "## Indexes (path references)",
        "",
        "- `assets/extracted/indexes/particles_index.json` — 9,000+ ability particles by hero",
        "- `assets/extracted/indexes/sounds_index.json` — 79,000+ sound file paths",
        "- `assets/extracted/indexes/models_index.json` — hero model paths",
        "",
        "## Usage",
        "",
        "```python",
        "import json",
        "heroes = json.load(open('manifests/heroes.json'))",
        "images = json.load(open('manifests/images.json'))",
        "abrams_icon = images['heroes']['abrams']['path_sm']",
        "```",
        "",
        "## Update pipeline",
        "",
        "```powershell",
        "python tools/extract_deadlock_assets.py --tier complete",
        "python tools/build_community_hub.py --sync-remote",
        "```",
        "",
    ]
    (DOCS / "CATALOG.md").write_text("\n".join(lines), encoding="utf-8")


def run_sync_remote() -> None:
    tools = Path(__file__).parent
    for script in ("sync_gametracking.py", "sync_deadlock_api.py"):
        print(f"\n[*] Running {script}...")
        subprocess.call([sys.executable, str(tools / script)], cwd=str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Deadlock community hub manifests")
    parser.add_argument("--sync-remote", action="store_true", help="Fetch GameTracking + deadlock-api first")
    parser.add_argument("--docs-only", action="store_true")
    args = parser.parse_args()

    if args.sync_remote and not args.docs_only:
        run_sync_remote()

    sys.path.insert(0, str(ROOT / "tools"))

    heroes_raw = load_json(PATHS["heroes"]) or {"heroes": {}}
    items_raw = load_json(PATHS["items"]) or {"items": []}
    extracted = load_json(PATHS["extracted_manifest"])
    local_index = load_json(PATHS["local_index"])
    items_display = load_json(PATHS["items_display"])

    codenames = build_codenames(local_index)
    heroes = build_heroes_unified(heroes_raw, extracted, codenames)
    catalog = (extracted or {}).get("catalog", {})
    items = build_items_unified(items_raw, catalog, items_display)
    images = build_images_registry(extracted, PATHS["images_root"])
    assets_index = build_assets_index()

    stats = {
        "heroes": heroes["count"],
        "items": items["total_items"],
        "upgrades": items["upgrade_count"],
        "pngs": images["total_pngs"],
        "vdata_files": count_files(PATHS["vdata_root"], "*.vdata"),
        "particles_vpcf": count_files(PATHS["particles_root"], "*.vpcf"),
        "panorama_layout": assets_index["directories"]["panorama"]["layout_count"],
        "panorama_styles": assets_index["directories"]["panorama"]["styles_count"],
    }
    if local_index and local_index.get("particles"):
        stats["particles_indexed"] = local_index["particles"].get("total", 0)

    hub = build_hub_manifest(stats, extracted)

    MANIFESTS.mkdir(parents=True, exist_ok=True)
    outputs = {
        "hub.json": hub,
        "heroes.json": heroes,
        "items.json": items,
        "images.json": images,
        "codenames.json": codenames,
        "assets_index.json": assets_index,
    }
    for name, data in outputs.items():
        path = MANIFESTS / name
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  [+] manifests/{name}")

    write_catalog_md(hub, heroes, items, images, assets_index)
    print(f"  [+] docs/CATALOG.md")

    # Copy manifests for MkDocs browse pages
    data_dir = ROOT / "docs" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in outputs:
        shutil.copy2(MANIFESTS / name, data_dir / name)
    print(f"  [+] docs/data/ ({len(outputs)} manifests for site)")
    print(f"\n[*] Community hub ready — {stats['pngs']:,} PNGs, {stats['heroes']} heroes, {stats['items']} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
