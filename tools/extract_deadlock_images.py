#!/usr/bin/env python3
"""
Extract Deadlock panorama images from installed Steam VPK → organized PNGs.

Pipeline (same family as vdata dump):
  pak01_dir.vpk  →  .vtex_c (compiled texture)  →  Source2Viewer-CLI  →  .png

Usage:
  python tools/extract_deadlock_images.py                  # heroes + items + abilities
  python tools/extract_deadlock_images.py --only heroes_sm  # menu icons only (~40 PNGs)
  python tools/extract_deadlock_images.py --list            # preview VPK file counts
  python tools/extract_deadlock_images.py --game-path "D:\\Steam\\...\\Deadlock"

Requires: pip install vpk
Auto-downloads Source2Viewer-CLI to tools/Source2Viewer-CLI/ on first run.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI_DIR = ROOT / "tools" / "Source2Viewer-CLI"
CLI_EXE = CLI_DIR / "Source2Viewer-CLI.exe"
CLI_URL = "https://github.com/ValveResourceFormat/ValveResourceFormat/releases/download/19.2/cli-windows-x64.zip"

STEAM_PATHS = [
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\Deadlock"),
    Path(r"C:\Program Files\Steam\steamapps\common\Deadlock"),
    Path(r"D:\Steam\steamapps\common\Deadlock"),
    Path(r"E:\Steam\steamapps\common\Deadlock"),
]

# Internal codename (filename) → canonical hero id (matches heroes.json / image_assets.lua)
CODENAME_TO_HERO = {
    "bull": "abrams", "bebop": "bebop", "punkgoat": "billy", "nano": "calico",
    "celestial": "celeste", "doorman": "doorman", "drifter": "drifter",
    "sumo": "dynamo", "spectre": "lady_geist", "archer": "grey_talon",
    "haze": "haze", "astro": "holliday", "inferno": "infernus", "tengu": "ivy",
    "kelvin": "kelvin", "lash": "lash", "mirage": "mirage", "digger": "mo_and_krill",
    "bookworm": "paige", "chrono": "paradox", "synth": "pocket", "familiar": "rem",
    "gigawatt": "seven", "shiv": "shiv", "magician": "sinclair", "priest": "venator",
    "hornet": "vindicta", "viscous": "viscous", "frank": "victor", "viper": "vyper",
    "warden": "warden", "wraith": "wraith", "yamato": "yamato", "fencer": "apollo",
    "mcginnis": "mcginnis", "mina": "mina",
}

CATEGORIES = {
    "heroes_sm": {
        "filter": "panorama/images/heroes/",
        "ext": "vtex_c",
        "match": re.compile(r"^panorama/images/heroes/([a-z0-9_]+)_sm_psd\.vtex_c$"),
        "out_subdir": "heroes_circle",
        "rename": "hero_sm",
    },
    "heroes_mm": {
        "filter": "panorama/images/heroes/",
        "ext": "vtex_c",
        "match": re.compile(r"^panorama/images/heroes/([a-z0-9_]+)_mm_psd\.vtex_c$"),
        "out_subdir": "heroes_minimap",
        "rename": "hero_mm",
    },
    "abilities": {
        "filter": "panorama/images/hud/abilities/",
        "ext": "vtex_c",
        "out_subdir": "abilities_vpk",
        "rename": "keep_path",
    },
    "items": {
        "filter": "panorama/images/items/",
        "ext": "vtex_c",
        "out_subdir": "items",
        "rename": "keep_path",
    },
    "upgrades": {
        "filter": "panorama/images/upgrades/",
        "ext": "vtex_c",
        "out_subdir": "upgrades",
        "rename": "keep_path",
    },
}


def find_game_path(custom: str | None) -> Path:
    if custom:
        p = Path(custom)
        vpk = p / "game" / "citadel" / "pak01_dir.vpk"
        if vpk.exists():
            return p
        raise FileNotFoundError(f"VPK not found at {vpk}")
    for p in STEAM_PATHS:
        if (p / "game" / "citadel" / "pak01_dir.vpk").exists():
            return p
    raise FileNotFoundError(
        "Deadlock not found. Use --game-path or install via Steam."
    )


def ensure_cli() -> Path:
    if CLI_EXE.exists():
        return CLI_EXE
    print(f"[*] Downloading Source2Viewer-CLI → {CLI_DIR}")
    CLI_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = CLI_DIR / "cli.zip"
    urllib.request.urlretrieve(CLI_URL, zip_path)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(CLI_DIR)
    zip_path.unlink(missing_ok=True)
    if not CLI_EXE.exists():
        raise RuntimeError("Source2Viewer-CLI.exe not found after download")
    return CLI_EXE


def vpk_stats(vpk_path: Path) -> dict[str, int]:
    import vpk
    pak = vpk.open(str(vpk_path))
    stats: dict[str, int] = {}
    for cat, cfg in CATEGORIES.items():
        filt = cfg["filter"]
        ext = cfg.get("ext", "vtex_c")
        match_re = cfg.get("match")
        n = 0
        for path in pak:
            if ext and not path.endswith(f".{ext}"):
                continue
            if filt not in path:
                continue
            if match_re and not match_re.match(path):
                continue
            n += 1
        stats[cat] = n
    return stats


def decompile_category(cli: Path, vpk_path: Path, cat: str, raw_dir: Path) -> Path:
    import vpk

    cfg = CATEGORIES[cat]
    out = raw_dir / cat
    out.mkdir(parents=True, exist_ok=True)
    match_re = cfg.get("match")

    if match_re:
        # CLI -f não suporta glob; pré-filtramos com regex via Python vpk
        pak = vpk.open(str(vpk_path))
        ext = cfg.get("ext", "vtex_c")
        extracted = 0
        for path in pak:
            if not path.endswith(f".{ext}"):
                continue
            if cfg["filter"] not in path:
                continue
            if not match_re.match(path):
                continue
            dest = out / path.replace("/", os.sep)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                f.write(pak[path].read())
            extracted += 1
        print(f"  -> Extracted {extracted} {cat} files from VPK")
        if extracted == 0:
            return out
        cmd = [str(cli), "-i", str(out), "-o", str(out), "-d", "--recursive", "--threads", "4"]
    else:
        cmd = [
            str(cli), "-i", str(vpk_path), "-o", str(out), "-d",
            "-f", cfg["filter"], "-e", cfg.get("ext", "vtex_c"), "--threads", "4",
        ]

    print(f"  -> Decompiling {cat} ...")
    subprocess.run(cmd, capture_output=True, text=True)
    return out


def rename_hero_png(src_name: str, variant: str) -> str | None:
    """archer_sm_psd.png → grey_talon.png"""
    m = re.match(r"^([a-z0-9_]+)_(sm|mm)_psd(?:_[a-f0-9]+)?\.png$", src_name)
    if not m:
        return None
    codename, kind = m.group(1), m.group(2)
    if kind != variant.replace("hero_", ""):
        return None
    hero_id = CODENAME_TO_HERO.get(codename, codename)
    return f"{hero_id}.png"


def organize_pngs(raw_dir: Path, dest_root: Path, categories: list[str]) -> dict:
    catalog: dict = {"heroes": {}, "items": {}, "abilities": {}, "upgrades": {}}

    for cat in categories:
        cfg = CATEGORIES[cat]
        src_root = raw_dir / cat
        if not src_root.exists():
            continue
        pngs = list(src_root.rglob("*.png"))
        print(f"  -> Organizing {cat}: {len(pngs)} PNGs")

        for png in pngs:
            rel = png.relative_to(src_root)
            rename_mode = cfg.get("rename", "keep_path")

            if rename_mode == "hero_sm":
                new_name = rename_hero_png(png.name, "hero_sm")
                if not new_name:
                    continue
                dest = dest_root / cfg["out_subdir"] / new_name
                hero_id = new_name.replace(".png", "")
                catalog["heroes"].setdefault(hero_id, {})["local_circle_vpk"] = (
                    f"images/deadlock/{cfg['out_subdir']}/{new_name}"
                )
                catalog["heroes"][hero_id]["vpk_codename"] = png.stem.replace("_sm_psd", "")

            elif rename_mode == "hero_mm":
                new_name = rename_hero_png(png.name, "hero_mm")
                if not new_name:
                    continue
                dest = dest_root / cfg["out_subdir"] / new_name
                hero_id = new_name.replace(".png", "")
                catalog["heroes"].setdefault(hero_id, {})["local_minimap_vpk"] = (
                    f"images/deadlock/{cfg['out_subdir']}/{new_name}"
                )

            elif rename_mode == "keep_path":
                # panorama/images/items/spirit/foo_psd.png → items/spirit/foo.png
                parts = list(rel.parts)
                # strip leading 'panorama/images/' if present
                if len(parts) > 2 and parts[0] == "panorama":
                    parts = parts[3:]  # drop panorama/images/{category}
                clean_name = png.stem.replace("_psd", "") + ".png"
                dest = dest_root / cfg["out_subdir"] / Path(*parts[:-1]) / clean_name

                key_path = str(dest.relative_to(dest_root)).replace("\\", "/")
                if cat == "items":
                    catalog["items"][clean_name.replace(".png", "")] = f"images/deadlock/{key_path}"
                elif cat == "abilities":
                    catalog["abilities"][clean_name.replace(".png", "")] = f"images/deadlock/{key_path}"
                else:
                    catalog["upgrades"][clean_name.replace(".png", "")] = f"images/deadlock/{key_path}"
            else:
                dest = dest_root / cfg["out_subdir"] / rel

            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(png, dest)

    return catalog


def merge_manifest(new_catalog: dict, vpk_path: Path) -> None:
    manifest_path = ROOT / "assets" / "game" / "images_manifest.json"
    existing = {}
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as f:
            existing = json.load(f)

    existing.setdefault("heroes", {})
    for hero_id, data in new_catalog.get("heroes", {}).items():
        entry = existing["heroes"].setdefault(hero_id, {"id": hero_id, "abilities": {}})
        entry.update(data)

    for section in ("items", "abilities", "upgrades"):
        existing.setdefault(f"vpk_{section}", {})
        existing[f"vpk_{section}"].update(new_catalog.get(section, {}))

    existing["vpk_dump"] = {
        "last_run": str(date.today()),
        "source_vpk": str(vpk_path),
        "tool": "Source2Viewer-CLI 19.2",
        "categories_extracted": list(new_catalog.keys()),
    }
    existing["version"] = "2.0.0"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    print(f"[*] Manifest updated -> {manifest_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract Deadlock images from VPK")
    parser.add_argument("--game-path", help="Custom Deadlock install path")
    parser.add_argument(
        "--only", choices=list(CATEGORIES.keys()),
        help="Extract single category (default: heroes_sm + items + abilities)"
    )
    parser.add_argument("--list", action="store_true", help="List VPK texture counts and exit")
    parser.add_argument("--keep-raw", action="store_true", help="Keep raw decompile in assets/dump/")
    args = parser.parse_args()

    game = find_game_path(args.game_path)
    vpk = game / "game" / "citadel" / "pak01_dir.vpk"
    print(f"[*] Game: {game}")
    print(f"[*] VPK:  {vpk}")

    if args.list:
        stats = vpk_stats(vpk)
        print("\nPanorama textures in VPK:")
        for cat, n in stats.items():
            print(f"  {cat:12} {n:4} files")
        print(f"\n  TOTAL        {sum(stats.values())} (filtered)")
        return

    cats = [args.only] if args.only else ["heroes_sm", "items", "abilities"]
    cli = ensure_cli()
    raw_dir = ROOT / "assets" / "dump" / "vpk_images"
    dest_root = ROOT / "images" / "deadlock"

    if raw_dir.exists() and not args.keep_raw:
        shutil.rmtree(raw_dir, ignore_errors=True)

    catalog: dict = {"heroes": {}, "items": {}, "abilities": {}, "upgrades": {}}
    for cat in cats:
        decompile_category(cli, vpk, cat, raw_dir)
        part = organize_pngs(raw_dir, dest_root, [cat])
        for section in part:
            catalog[section].update(part[section])

    merge_manifest(catalog, vpk)

    if not args.keep_raw:
        shutil.rmtree(raw_dir, ignore_errors=True)

    print(f"[*] Done -> {dest_root}")
    print(f"    Heroes: {len(catalog['heroes'])}  Items: {len(catalog['items'])}  "
          f"Abilities: {len(catalog['abilities'])}")


if __name__ == "__main__":
    main()
