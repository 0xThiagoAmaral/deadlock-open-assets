#!/usr/bin/env python3
"""
Full Deadlock asset extractor — VPK -> organized assets for scripts, builds, mods, tools.

Usage:
  python tools/extract_deadlock_assets.py --list
  python tools/extract_deadlock_assets.py --tier essential   # ~5 min
  python tools/extract_deadlock_assets.py --tier full        # ~30-60 min
  python tools/extract_deadlock_assets.py --only vdata
  python tools/extract_deadlock_assets.py --only particles

Tiers:
  essential  vdata + hero/item images + particle index
  full       essential + all panorama images + particles decompiled + panorama UI
  complete   full + sound/model indexes (no binary extract)
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

from cli_progress import JobRunner, ProgressTracker, enable_vt, fmt_size, fmt_time, BOLD, CYAN, DIM, GREEN, R, WHITE, YELLOW
from vpk_common import (
    CODENAME_TO_HERO,
    ROOT,
    count_files,
    decompile_vpk,
    ensure_cli,
    find_game_path,
    get_vpk_path,
    open_vpk,
    rename_hero_png,
)

EXTRACTED = ROOT / "assets" / "extracted"
IMAGES_OUT = ROOT / "images" / "deadlock"
DUMP_RAW = ROOT / "assets" / "dump" / "raw"

IMAGE_CATEGORIES = {
    "heroes_sm": {
        "filter": "panorama/images/heroes/",
        "ext": "vtex_c",
        "match": re.compile(r"^panorama/images/heroes/([a-z0-9_]+)_sm_psd\.vtex_c$"),
        "out": "heroes_circle",
        "rename": "hero_sm",
    },
    "heroes_mm": {
        "filter": "panorama/images/heroes/",
        "ext": "vtex_c",
        "match": re.compile(r"^panorama/images/heroes/([a-z0-9_]+)_mm_psd\.vtex_c$"),
        "out": "heroes_minimap",
        "rename": "hero_mm",
    },
    "heroes_card": {
        "filter": "panorama/images/heroes/",
        "ext": "vtex_c",
        "match": re.compile(r"^panorama/images/heroes/([a-z0-9_]+)_card_psd\.vtex_c$"),
        "out": "heroes_card",
        "rename": "hero_card",
    },
    "heroes_backgrounds": {
        "filter": "panorama/images/heroes/backgrounds/",
        "ext": "vtex_c",
        "out": "backgrounds",
        "rename": "keep",
    },
    "abilities_icons": {
        "filter": "panorama/images/hud/abilities/",
        "ext": "vtex_c",
        "out": "abilities",
        "rename": "keep",
    },
    "items": {
        "filter": "panorama/images/items/",
        "ext": "vtex_c",
        "out": "items",
        "rename": "keep",
    },
    "upgrades": {
        "filter": "panorama/images/upgrades/",
        "ext": "vtex_c",
        "out": "upgrades",
        "rename": "keep",
    },
    "ui_ranked": {
        "filter": "panorama/images/ranked/",
        "ext": "vtex_c",
        "out": "ui/ranked",
        "rename": "keep",
    },
    "ui_shop": {
        "filter": "panorama/images/shop/",
        "ext": "vtex_c",
        "out": "ui/shop",
        "rename": "keep",
    },
    "ui_minimap": {
        "filter": "panorama/images/minimap/",
        "ext": "vtex_c",
        "out": "ui/minimap",
        "rename": "keep",
    },
    "ui_hud": {
        "filter": "panorama/images/hud/",
        "ext": "vtex_c",
        "out": "ui/hud",
        "rename": "keep",
        "exclude": "panorama/images/hud/abilities/",
    },
    "ui_icons": {
        "filter": "panorama/images/icons/",
        "ext": "vtex_c",
        "out": "ui/icons",
        "rename": "keep",
    },
    "ui_postgame": {
        "filter": "panorama/images/post_game/",
        "ext": "vtex_c",
        "out": "ui/postgame",
        "rename": "keep",
    },
}

DATA_CATEGORIES = {
    "vdata": {
        "filter": "scripts/",
        "ext": ["vdata_c"],
        "out": "vdata",
        "output_ext": "vdata",
    },
    "particles": {
        "filter": "particles/abilities/",
        "ext": ["vpcf_c"],
        "out": "particles/abilities",
        "output_ext": "vpcf",
    },
    "panorama_layout": {
        "filter": "panorama/layout/",
        "ext": ["vxml_c"],
        "out": "panorama/layout",
        "output_ext": "xml",
    },
    "panorama_styles": {
        "filter": "panorama/styles/",
        "ext": ["vcss_c"],
        "out": "panorama/styles",
        "output_ext": "css",
    },
}

TIERS = {
    "essential": ["vdata", "heroes_sm", "items", "abilities_icons", "particles_index"],
    "full": [
        "vdata", "heroes_sm", "heroes_mm", "heroes_card", "heroes_backgrounds",
        "items", "upgrades", "abilities_icons", "ui_ranked", "ui_shop",
        "ui_minimap", "ui_icons", "ui_postgame", "particles",
        "panorama_layout", "panorama_styles",
    ],
    "complete": None,  # all categories + indexes
}


def list_inventory(vpk_path: Path) -> dict:
    pak = open_vpk(vpk_path)
    by_ext = Counter()
    panorama = Counter()
    for path in pak:
        ext = path.rsplit(".", 1)[-1] if "." in path else "none"
        by_ext[ext] += 1
        if path.startswith("panorama/images/"):
            parts = path.split("/")
            if len(parts) >= 3:
                panorama[parts[2]] += 1
    return {
        "total_files": sum(by_ext.values()),
        "by_extension": dict(by_ext.most_common(30)),
        "panorama_images": dict(panorama.most_common(20)),
        "image_categories": {k: _count_image_cat(vpk_path, k) for k in IMAGE_CATEGORIES},
        "data_categories": {k: _count_data_cat(vpk_path, k) for k in DATA_CATEGORIES},
    }


def _count_image_cat(vpk_path: Path, cat: str) -> int:
    cfg = IMAGE_CATEGORIES[cat]
    pak = open_vpk(vpk_path)
    n = 0
    for path in pak:
        if not path.endswith(f".{cfg['ext']}"):
            continue
        if cfg["filter"] not in path:
            continue
        if cfg.get("exclude") and cfg["exclude"] in path:
            continue
        if cfg.get("match") and not cfg["match"].match(path):
            continue
        n += 1
    return n


def _count_data_cat(vpk_path: Path, cat: str) -> int:
    cfg = DATA_CATEGORIES[cat]
    pak = open_vpk(vpk_path)
    n = 0
    for path in pak:
        if not any(path.endswith(f".{e}") for e in cfg["ext"]):
            continue
        if cfg["filter"] not in path:
            continue
        n += 1
    return n


def build_particles_index(vpk_path: Path) -> dict:
    pak = open_vpk(vpk_path)
    by_hero: dict[str, list[str]] = defaultdict(list)
    for path in sorted(pak):
        if not path.endswith(".vpcf_c"):
            continue
        if not path.startswith("particles/abilities/"):
            continue
        parts = path.split("/")
        hero = parts[2] if len(parts) > 2 else "unknown"
        name = Path(path).stem.replace(".vpcf", "")
        by_hero[hero].append({
            "vpk_path": path,
            "name": name,
            "hero_codename": hero,
            "hero_id": CODENAME_TO_HERO.get(hero, hero),
            "local_path": f"assets/extracted/particles/abilities/{'/'.join(parts[2:])}".replace(".vpcf_c", ".vpcf"),
        })
    return {
        "total": sum(len(v) for v in by_hero.values()),
        "heroes": {k: len(v) for k, v in sorted(by_hero.items(), key=lambda x: -len(x[1]))},
        "entries": dict(by_hero),
    }


def build_sounds_index(vpk_path: Path, limit: int = 5000) -> dict:
    pak = open_vpk(vpk_path)
    samples = []
    total = 0
    for path in pak:
        if not path.endswith(".vsnd_c"):
            continue
        total += 1
        if len(samples) < limit:
            samples.append(path)
    return {"total": total, "sample_paths": samples}


def build_models_index(vpk_path: Path) -> dict:
    pak = open_vpk(vpk_path)
    heroes = []
    other = 0
    for path in pak:
        if not path.endswith(".vmdl_c"):
            continue
        if "models/heroes" in path or "models/heroes_staging" in path:
            heroes.append(path)
        else:
            other += 1
    return {"hero_models": heroes, "hero_count": len(heroes), "other_count": other}


def organize_image(raw_dir: Path, cat: str, catalog: dict, verbose: bool = True) -> int:
    cfg = IMAGE_CATEGORIES[cat]
    src = raw_dir
    if not src.exists():
        return 0
    pngs = list(src.rglob("*.png"))
    if verbose and pngs:
        print(f"  {CYAN}>{R} Organizing {len(pngs)} PNGs...")
        progress = ProgressTracker(total=len(pngs), label="Organize")
    else:
        progress = None
    copied = 0
    for png in pngs:
        rel = png.relative_to(src)
        rename = cfg.get("rename", "keep")

        if rename == "hero_sm":
            name = rename_hero_png(png.name, "hero_sm")
            if not name:
                continue
            dest = IMAGES_OUT / cfg["out"] / name
            hero_id = name.replace(".png", "")
            catalog.setdefault("heroes", {}).setdefault(hero_id, {})["path_sm"] = (
                f"images/deadlock/{cfg['out']}/{name}"
            )
        elif rename == "hero_mm":
            name = rename_hero_png(png.name, "hero_mm")
            if not name:
                continue
            dest = IMAGES_OUT / cfg["out"] / name
            hero_id = name.replace(".png", "")
            catalog.setdefault("heroes", {}).setdefault(hero_id, {})["path_mm"] = (
                f"images/deadlock/{cfg['out']}/{name}"
            )
        elif rename == "hero_card":
            name = rename_hero_png(png.name, "hero_card")
            if not name:
                continue
            dest = IMAGES_OUT / cfg["out"] / name
            hero_id = name.replace(".png", "")
            catalog.setdefault("heroes", {}).setdefault(hero_id, {})["path_card"] = (
                f"images/deadlock/{cfg['out']}/{name}"
            )
        else:
            parts = list(rel.parts)
            if len(parts) > 2 and parts[0] == "panorama":
                parts = parts[3:]
            clean = png.stem.replace("_psd", "") + ".png"
            dest = IMAGES_OUT / cfg["out"] / Path(*parts[:-1]) / clean
            key = str(dest.relative_to(IMAGES_OUT)).replace("\\", "/")
            section = cfg["out"].split("/")[0]
            catalog.setdefault(section, {})[clean.replace(".png", "")] = f"images/deadlock/{key}"

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png, dest)
        copied += 1
        if progress:
            progress.advance(1, dest.name)
    if progress:
        progress.finish()
    return copied


def extract_data(cli, vpk_path: Path, cat: str, keep_in_place: bool = True, verbose: bool = True) -> int:
    cfg = DATA_CATEGORIES[cat]
    raw = DUMP_RAW / cat
    dest = EXTRACTED / cfg["out"]
    if raw.exists():
        shutil.rmtree(raw, ignore_errors=True)
    decompile_vpk(cli, vpk_path, raw, cfg["filter"], cfg["ext"], verbose=verbose)
    if not raw.exists():
        return 0
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(raw, dest)
    count = count_files(dest, [cfg["output_ext"], *cfg["ext"]])
    if verbose:
        print(f"  {GREEN}+{R} {cat}: {WHITE}{count}{R} files -> {DIM}{dest}{R}")
    if not keep_in_place:
        shutil.rmtree(raw, ignore_errors=True)
    return count


def extract_image(cli, vpk_path: Path, cat: str, catalog: dict, verbose: bool = True) -> int:
    cfg = IMAGE_CATEGORIES[cat]
    raw = DUMP_RAW / cat
    if raw.exists():
        shutil.rmtree(raw, ignore_errors=True)
    match = cfg.get("match")
    if match:
        decompile_vpk(cli, vpk_path, raw, cfg["filter"], cfg["ext"], match=match, verbose=verbose)
    else:
        decompile_vpk(cli, vpk_path, raw, cfg["filter"], cfg["ext"], verbose=verbose)
    n = organize_image(raw, cat, catalog, verbose=verbose)
    if verbose:
        print(f"  {GREEN}+{R} {cat}: {WHITE}{n}{R} PNGs -> {DIM}images/deadlock/{cfg['out']}{R}")
    shutil.rmtree(raw, ignore_errors=True)
    return n


def sync_vdata_to_assets() -> None:
    src = EXTRACTED / "vdata" / "scripts"
    if not src.exists():
        return
    dst = ROOT / "assets" / "vdata"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.vdata"):
        shutil.copy2(f, dst / f.name)
    for sub in src.iterdir():
        if sub.is_dir():
            target = dst / sub.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(sub, target)
    print(f"  -> vdata synced -> assets/vdata/")


def write_manifest(vpk_path: Path, tier: str, stats: dict, catalog: dict) -> None:
    manifest = {
        "version": "3.0.0",
        "game": "Deadlock",
        "dump_date": datetime.now().isoformat(),
        "tier": tier,
        "source_vpk": str(vpk_path),
        "tool": "Source2Viewer-CLI 19.2 + extract_deadlock_assets.py",
        "stats": stats,
        "catalog": catalog,
        "paths": {
            "extracted_root": "assets/extracted/",
            "images_root": "images/deadlock/",
            "vdata": "assets/vdata/",
            "indexes": "assets/extracted/indexes/",
            "catalog_ai": "assets/extracted/catalog/",
        },
        "tooling_use_cases": {
            "lua_scripts": ["particles", "vdata", "heroes", "abilities"],
            "build_creator": ["vdata", "items", "upgrades", "heroes"],
            "mods": ["panorama/layout", "panorama/styles", "images"],
            "counterspell": ["particles", "abilities"],
            "ui_automation": ["panorama/layout", "panorama/styles"],
        },
    }
    out = EXTRACTED / "manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"[*] Manifest -> {out}")


def run(categories: list[str], vpk_path: Path, tier: str = "custom", keep_raw: bool = False) -> dict:
    enable_vt()
    job = JobRunner(categories, tier)
    job.print_plan()

    cli = ensure_cli()
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    IMAGES_OUT.mkdir(parents=True, exist_ok=True)
    (EXTRACTED / "indexes").mkdir(parents=True, exist_ok=True)

    stats: dict = {"categories": {}}
    catalog: dict = {"heroes": {}, "items": {}, "abilities": {}}

    for cat in categories:
        job.begin_phase(cat)
        if cat == "particles_index":
            prog = ProgressTracker(total=100, label="Indexing particles")
            prog.advance(10, "scanning VPK...")
            idx = build_particles_index(vpk_path)
            prog.set(90, f"{idx['total']} entries")
            path = EXTRACTED / "indexes" / "particles_index.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(idx, f, indent=2, ensure_ascii=False)
            stats["categories"]["particles_index"] = idx["total"]
            prog.finish()
            job.end_phase(cat, idx["total"])
            continue
        if cat == "sounds_index":
            idx = build_sounds_index(vpk_path)
            path = EXTRACTED / "indexes" / "sounds_index.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(idx, f, indent=2)
            stats["categories"]["sounds_index"] = idx["total"]
            job.end_phase(cat, idx["total"])
            continue
        if cat == "models_index":
            idx = build_models_index(vpk_path)
            path = EXTRACTED / "indexes" / "models_index.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(idx, f, indent=2)
            stats["categories"]["models_index"] = idx["hero_count"]
            job.end_phase(cat, idx["hero_count"])
            continue
        if cat in DATA_CATEGORIES:
            n = extract_data(cli, vpk_path, cat, keep_in_place=keep_raw)
            stats["categories"][cat] = n
            if cat == "vdata":
                sync_vdata_to_assets()
            job.end_phase(cat, n)
        elif cat in IMAGE_CATEGORIES:
            n = extract_image(cli, vpk_path, cat, catalog)
            stats["categories"][cat] = n
            job.end_phase(cat, n)

    inv = list_inventory(vpk_path)
    inv_path = EXTRACTED / "indexes" / "vpk_inventory.json"
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=2)
    stats["vpk_inventory"] = inv["total_files"]

    job.summary()
    return stats, catalog


def main():
    parser = argparse.ArgumentParser(description="Full Deadlock asset extractor")
    parser.add_argument("--game-path")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--tier", choices=["essential", "full", "complete"], default="essential")
    parser.add_argument("--only", help="Single category (e.g. vdata, particles, heroes_sm)")
    parser.add_argument("--keep-raw", action="store_true")
    args = parser.parse_args()

    game = find_game_path(args.game_path)
    vpk = get_vpk_path(game)
    enable_vt()
    vpk_size = vpk.stat().st_size if vpk.exists() else 0
    print(f"\n  {BOLD}{CYAN}DEADLOCK VPK EXTRACTOR{R}")
    print(f"  {DIM}Game:{R} {game}")
    print(f"  {DIM}VPK:{R}  {vpk.name} ({fmt_size(vpk_size)})")

    if args.list:
        inv = list_inventory(vpk)
        print(json.dumps(inv, indent=2))
        return

    if args.only:
        cats = [args.only]
        if args.only not in IMAGE_CATEGORIES and args.only not in DATA_CATEGORIES and args.only not in (
            "particles_index", "sounds_index", "models_index"
        ):
            print(f"Unknown category: {args.only}")
            print("Available:", list(IMAGE_CATEGORIES) + list(DATA_CATEGORIES) + ["particles_index"])
            return
    elif args.tier == "complete":
        cats = (
            list(DATA_CATEGORIES.keys())
            + list(IMAGE_CATEGORIES.keys())
            + ["particles_index", "sounds_index", "models_index"]
        )
    else:
        cats = TIERS[args.tier]

    tier_name = args.tier if not args.only else args.only
    print(f"  {DIM}Mode:{R} {tier_name} ({len(cats)} phases)")
    stats, catalog = run(cats, vpk, tier=tier_name if not args.only else "custom", keep_raw=args.keep_raw)
    write_manifest(vpk, tier_name, stats, catalog)


if __name__ == "__main__":
    main()
