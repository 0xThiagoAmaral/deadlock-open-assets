"""Sync Deadlock image assets from reference repo into images/deadlock/."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_HEROES = ROOT / "assets" / "reference" / "deadlock-open-data" / "data" / "heroes"
OUT = ROOT / "images" / "deadlock"
MANIFEST_OUT = ROOT / "assets" / "game" / "images_manifest.json"

# Panorama paths extracted from AutoCounterspell.lua (canonical in-game icons)
PANORAMA_HEROES = {
    "abrams": "panorama/images/heroes/bull_sm_psd.vtex_c",
    "bebop": "panorama/images/heroes/bebop_sm_psd.vtex_c",
    "billy": "panorama/images/heroes/punkgoat_sm_psd.vtex_c",
    "calico": "panorama/images/heroes/nano_sm_psd.vtex_c",
    "celeste": "panorama/images/heroes/celestial_sm_psd.vtex_c",
    "doorman": "panorama/images/heroes/doorman_sm_psd.vtex_c",
    "drifter": "panorama/images/heroes/drifter_sm_psd.vtex_c",
    "dynamo": "panorama/images/heroes/sumo_sm_psd.vtex_c",
    "grey_talon": "panorama/images/heroes/archer_sm_psd.vtex_c",
    "haze": "panorama/images/heroes/haze_sm_psd.vtex_c",
    "holliday": "panorama/images/heroes/astro_sm_psd.vtex_c",
    "infernus": "panorama/images/heroes/inferno_sm_psd.vtex_c",
    "ivy": "panorama/images/heroes/tengu_sm_psd.vtex_c",
    "kelvin": "panorama/images/heroes/kelvin_sm_psd.vtex_c",
    "lady_geist": "panorama/images/heroes/spectre_sm_psd.vtex_c",
    "lash": "panorama/images/heroes/lash_sm_psd.vtex_c",
    "mcginnis": "panorama/images/heroes/mcginnis_sm_psd.vtex_c",
    "mina": "panorama/images/heroes/mina_sm_psd.vtex_c",
    "mirage": "panorama/images/heroes/mirage_sm_psd.vtex_c",
    "mo_and_krill": "panorama/images/heroes/digger_sm_psd.vtex_c",
    "paige": "panorama/images/heroes/bookworm_sm_psd.vtex_c",
    "paradox": "panorama/images/heroes/chrono_sm_psd.vtex_c",
    "pocket": "panorama/images/heroes/synth_sm_psd.vtex_c",
    "rem": "panorama/images/heroes/familiar_sm_psd.vtex_c",
    "seven": "panorama/images/heroes/gigawatt_sm_psd.vtex_c",
    "shiv": "panorama/images/heroes/shiv_sm_psd.vtex_c",
    "sinclair": "panorama/images/heroes/magician_sm_psd.vtex_c",
    "venator": "panorama/images/heroes/priest_sm_psd.vtex_c",
    "vindicta": "panorama/images/heroes/hornet_sm_psd.vtex_c",
    "viscous": "panorama/images/heroes/viscous_sm_psd.vtex_c",
    "victor": "panorama/images/heroes/frank_sm_psd.vtex_c",
    "vyper": "panorama/images/heroes/viper_sm_psd.vtex_c",
    "warden": "panorama/images/heroes/warden_sm_psd.vtex_c",
    "wraith": "panorama/images/heroes/wraith_sm_psd.vtex_c",
    "yamato": "panorama/images/heroes/yamato_sm_psd.vtex_c",
    "apollo": "panorama/images/heroes/fencer_sm_psd.vtex_c",
}

PANORAMA_PREFIXES = {
    "abilities": "panorama/images/hud/abilities/",
    "items_spirit": "panorama/images/items/spirit/",
    "items_weapon": "panorama/images/items/weapon/",
    "items_vitality": "panorama/images/items/vitality/",
    "upgrades_tech": "panorama/images/upgrades/mods_tech/",
}

SHARED_UI = [
    ("ArcPanel/umbrellacorp.png", "ui/umbrellacorp.png"),
    ("ArcPanel/umbrellacorpmini.png", "ui/umbrellacorpmini.png"),
    ("watermark/watermark.png", "ui/watermark.png"),
]


def sync_heroes() -> dict:
    heroes_dir = OUT / "heroes_circle"
    square_dir = OUT / "heroes_square"
    abilities_dir = OUT / "abilities"
    heroes_dir.mkdir(parents=True, exist_ok=True)
    square_dir.mkdir(parents=True, exist_ok=True)
    abilities_dir.mkdir(parents=True, exist_ok=True)

    catalog = {}
    for hero_path in sorted(REF_HEROES.iterdir()):
        if not hero_path.is_dir():
            continue
        hero_id = hero_path.name
        assets = hero_path / "assets"
        if not assets.exists():
            continue

        entry = {"id": hero_id, "abilities": {}}
        thumb = assets / "hero_thumbnail.png"
        model = assets / "hero_model.png"
        if thumb.exists():
            dest = heroes_dir / f"{hero_id}.png"
            shutil.copy2(thumb, dest)
            entry["local_circle"] = f"images/deadlock/heroes_circle/{hero_id}.png"
        if model.exists():
            dest = square_dir / f"{hero_id}.png"
            shutil.copy2(model, dest)
            entry["local_square"] = f"images/deadlock/heroes_square/{hero_id}.png"

        if hero_id in PANORAMA_HEROES:
            entry["panorama_sm"] = PANORAMA_HEROES[hero_id]

        for ab_png in sorted(assets.glob("ability_*.png")):
            ab_name = ab_png.stem
            dest = abilities_dir / hero_id / ab_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ab_png, dest.with_suffix(".png"))
            entry["abilities"][ab_name] = f"images/deadlock/abilities/{hero_id}/{ab_name}.png"

        catalog[hero_id] = entry

    # Panorama-only heroes (no reference PNG yet)
    for hero_id, panorama in PANORAMA_HEROES.items():
        if hero_id not in catalog:
            catalog[hero_id] = {"id": hero_id, "panorama_sm": panorama, "abilities": {}}

    return catalog


def sync_shared_ui() -> list:
    ui_dir = OUT / "ui"
    ui_dir.mkdir(parents=True, exist_ok=True)
    synced = []
    for src_rel, dst_rel in SHARED_UI:
        src = ROOT / "images" / src_rel
        dst = OUT / dst_rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            synced.append(f"images/deadlock/{dst_rel}")
    return synced


def main():
    heroes = sync_heroes()
    shared = sync_shared_ui()

    manifest = {
        "version": "1.0.0",
        "game": "Deadlock",
        "last_updated": "2026-06-22",
        "root": "images/deadlock/",
        "usage": {
            "menu_icons": "Use panorama_sm paths in Menu:Icon() — nativo do jogo",
            "overlay_render": "Use local_circle/local_square com Render.LoadImage() ou LIB_RENDER.image()",
            "shared_dota_ui": "images/MenuIcons/, images/ArcPanel/ — reutilizáveis entre Dota2 e Deadlock",
        },
        "panorama_prefixes": PANORAMA_PREFIXES,
        "shared_ui": shared,
        "heroes": heroes,
        "dota_parity_folders": {
            "heroes_circle": "images/heroes_circle/ (Dota2) → images/deadlock/heroes_circle/",
            "items_square": "images/items_square/ (Dota2) → images/deadlock/items/ (pendente)",
            "MenuIcons": "images/MenuIcons/ (compartilhado)",
            "DmgIndicator": "images/DmgIndicator/ (compartilhado — adaptar cores)",
            "ArcPanel": "images/ArcPanel/ (compartilhado)",
        },
    }

    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_OUT, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Synced {len(heroes)} heroes -> {OUT}")
    print(f"Manifest -> {MANIFEST_OUT}")


if __name__ == "__main__":
    main()
