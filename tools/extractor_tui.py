#!/usr/bin/env python3
"""
Umblock Deadlock Extractor — Interactive TUI (standalone, outside IDE).

Launch via:  UmblockExtractor.bat  (double-click)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
CONFIG_PATH = TOOLS / "extractor_config.json"

# ── ANSI colors (Windows 10+ VT enabled by .bat) ─────────────────────────────
R = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BG_DARK = "\033[40m"


def enable_vt():
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def clear():
    os.system("cls" if sys.platform == "win32" else "clear")


def banner():
    art = f"""{CYAN}{BOLD}
  ██╗   ██╗███╗   ███╗██████╗ ██╗      ██████╗  ██████╗██╗  ██╗
  ██║   ██║████╗ ████║██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝
  ██║   ██║██╔████╔██║██████╔╝██║     ██║   ██║██║     █████╔╝
  ██║   ██║██║╚██╔╝██║██╔══██╗██║     ██║   ██║██║     ██╔═██╗
  ╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗╚██████╔╝╚██████╗██║  ██╗
   ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝
{R}{DIM}  ─────────────────────────────────────────────────────────────{R}
  {WHITE}{BOLD}DEADLOCK VPK EXTRACTOR{R}  {DIM}v2.0  |  Source 2 Asset Ripper  |  Live Progress + ETA{R}
  {DIM}  VPK → vdata · particles · panorama · PNG · DeepSeek catalog{R}
"""
    print(art)


def status_line(cfg: dict) -> str:
    parts = []
    try:
        sys.path.insert(0, str(TOOLS))
        from vpk_common import find_game_path, get_vpk_path, load_deepseek_key
        game_args = cfg.get("game_path") or None
        game = find_game_path(game_args if game_args else None)
        vpk = get_vpk_path(game)
        size_gb = vpk.stat().st_size / (1024**3) if vpk.exists() else 0
        parts.append(f"{GREEN}[+] VPK{R} {DIM}{game.name}{R}")
    except Exception:
        parts.append(f"{RED}[!] VPK not found{R}")

    key_file = ROOT / cfg.get("deepseek_key_file", "deepseek.txt")
    if key_file.exists():
        parts.append(f"{GREEN}[+] API{R} {DIM}DeepSeek OK{R}")
    else:
        parts.append(f"{YELLOW}[~] API{R} {DIM}no key{R}")

    cli = TOOLS / "Source2Viewer-CLI" / "Source2Viewer-CLI.exe"
    if cli.exists():
        parts.append(f"{GREEN}[+] S2V{R} {DIM}CLI ready{R}")
    else:
        parts.append(f"{YELLOW}[~] S2V{R} {DIM}will auto-download{R}")

    return "  ".join(parts)


def pause(msg: str = "Press ENTER to continue..."):
    input(f"\n{DIM}{msg}{R}")


def run_tool(script: str, args: list[str] | None = None, live: bool = True) -> int:
    """Run extraction script with live stdout streaming."""
    from cli_progress import stream_subprocess, BOLD, CYAN, DIM, R

    args = args or []
    cmd = [sys.executable, str(TOOLS / script)] + args
    if cfg_game := load_config().get("game_path"):
        if "--game-path" not in args and script in (
            "extract_deadlock_assets.py", "extract_deadlock_images.py", "run_full_dump.py"
        ):
            cmd.extend(["--game-path", cfg_game])
    print(f"\n  {CYAN}{BOLD}[EXEC]{R} {DIM}{' '.join(cmd)}{R}")
    print(f"  {DIM}{'-' * 60}{R}\n")
    if live:
        return stream_subprocess(cmd, cwd=str(ROOT))
    return subprocess.call(cmd, cwd=str(ROOT))


def menu_recon():
    clear()
    print(f"{BOLD}{CYAN}  [RECON] VPK Inventory Scan{R}\n")
    run_tool("extract_deadlock_assets.py", ["--list"])
    pause()


def menu_extract_tier(tier: str, label: str):
    from cli_progress import JobRunner, fmt_time, BOLD, CYAN, DIM, GREEN, RED, R, YELLOW, WHITE

    clear()
    phases = {
        "essential": ["vdata", "heroes_sm", "items", "abilities_icons", "particles_index"],
        "full": [
            "vdata", "heroes_sm", "heroes_mm", "heroes_card", "heroes_backgrounds",
            "items", "upgrades", "abilities_icons", "ui_ranked", "ui_shop",
            "ui_minimap", "ui_icons", "ui_postgame", "particles",
            "panorama_layout", "panorama_styles",
        ],
        "complete": None,
    }
    job = JobRunner(phases.get(tier) or [], tier)
    print(f"{BOLD}{CYAN}  [EXTRACT] {label}{R}\n")
    print(f"  {DIM}Estimated time:{R} {YELLOW}{fmt_time(job.estimated_total())}{R}")
    print(f"  {DIM}Phases:{R} {WHITE}{len(job.phases)}{R}\n")
    job.print_plan()
    confirm = input(f"\n  {YELLOW}Proceed? [Y/n]:{R} ").strip().lower()
    if confirm in ("n", "no"):
        return
    t0 = time.time()
    code = run_tool("extract_deadlock_assets.py", ["--tier", tier], live=True)
    elapsed = time.time() - t0
    if code == 0:
        print(f"\n  {GREEN}[+] Tier complete in {fmt_time(time.time() - t0)}{R}")
        print(f"  {DIM}[*] Post-step: syncing hero manifest (sync_deadlock_images.py){R}")
        run_tool("sync_deadlock_images.py", [], live=True)
    else:
        print(f"\n  {RED}[!] Extraction failed (code {code}){R}")
    pause()


def menu_full_pipeline(tier: str, use_ai: bool):
    clear()
    ai_label = "with DeepSeek" if use_ai else "no AI"
    print(f"{BOLD}{CYAN}  [PIPELINE] Full dump ({tier}) {ai_label}{R}\n")
    confirm = input(f"  {YELLOW}Proceed? [Y/n]:{R} ").strip().lower()
    if confirm in ("n", "no"):
        return
    args = ["--tier", tier]
    if not use_ai:
        args.append("--no-ai")
    t0 = time.time()
    code = run_tool("run_full_dump.py", args)
    elapsed = time.time() - t0
    print(f"\n{GREEN if code == 0 else RED}[{'+'if code==0 else '!'}] Pipeline {'OK' if code==0 else 'FAILED'} in {elapsed:.0f}s{R}")
    pause()


def menu_surgical():
    categories = [
        ("vdata", "Game data (abilities, heroes, modifiers)"),
        ("heroes_sm", "Hero menu icons (_sm)"),
        ("heroes_mm", "Hero minimap icons"),
        ("heroes_card", "Hero card art"),
        ("heroes_backgrounds", "Hero splash backgrounds"),
        ("items", "Item icons"),
        ("upgrades", "Upgrade/mod icons"),
        ("abilities_icons", "Ability HUD icons"),
        ("ui_ranked", "Ranked UI assets"),
        ("ui_shop", "Shop UI assets"),
        ("ui_minimap", "Minimap assets"),
        ("ui_icons", "Generic UI icons"),
        ("ui_postgame", "Post-game UI"),
        ("particles", "Ability particles (.vpcf) — SLOW"),
        ("particles_index", "Particle index only (fast)"),
        ("panorama_layout", "Panorama layout XML"),
        ("panorama_styles", "Panorama CSS"),
        ("sounds_index", "Sound file index"),
        ("models_index", "3D model index"),
    ]
    while True:
        clear()
        print(f"{BOLD}{CYAN}  [SURGICAL] Targeted Extraction{R}\n")
        for i, (key, desc) in enumerate(categories, 1):
            print(f"  {WHITE}{i:2}{R}  {desc}  {DIM}({key}){R}")
        print(f"\n  {WHITE} 0{R}  Back")
        choice = input(f"\n  {YELLOW}Select target [0-{len(categories)}]:{R} ").strip()
        if choice == "0" or choice == "":
            return
        try:
            idx = int(choice) - 1
            key, desc = categories[idx]
        except (ValueError, IndexError):
            continue
        clear()
        print(f"{BOLD}  Extracting: {desc}{R}\n")
        cfg = load_config()
        args = ["--only", key]
        if cfg.get("keep_raw_dump"):
            args.append("--keep-raw")
        run_tool("extract_deadlock_assets.py", args)
        pause()


def menu_intel():
    clear()
    cfg = load_config()
    print(f"{BOLD}{CYAN}  [INTEL] Organize & Build Hub{R}\n")
    print(f"  {WHITE}1{R}  Organize with DeepSeek     {DIM}AI-enriched catalog{R}")
    print(f"  {WHITE}2{R}  Build community hub          {DIM}manifests/ + CATALOG.md{R}")
    print(f"  {WHITE}3{R}  Build hub + sync remote      {DIM}+ GameTracking + deadlock-api{R}")
    print(f"  {WHITE}0{R}  Back")
    c = input(f"\n  {YELLOW}Select [0-3]:{R} ").strip()
    if c == "0" or c == "":
        return
    if c == "1":
        if not (ROOT / cfg.get("deepseek_key_file", "deepseek.txt")).exists():
            print(f"  {RED}[!] Key not found: {cfg.get('deepseek_key_file')}{R}")
            pause()
            return
        use_ai = input(f"  Use DeepSeek API? [Y/n]:{R} ").strip().lower() not in ("n", "no")
        args = [] if use_ai else ["--no-ai"]
        run_tool("organize_with_deepseek.py", args)
    elif c == "2":
        run_tool("build_community_hub.py", [])
    elif c == "3":
        run_tool("build_community_hub.py", ["--sync-remote"])
    pause()


def menu_config():
    cfg = load_config()
    while True:
        clear()
        print(f"{BOLD}{CYAN}  [CONFIG] Settings{R}\n")
        print(f"  {WHITE}1{R}  Game path:     {DIM}{cfg.get('game_path') or '(auto-detect)'}{R}")
        print(f"  {WHITE}2{R}  API key file:  {DIM}{cfg.get('deepseek_key_file', 'deepseek.txt')}{R}")
        print(f"  {WHITE}3{R}  Default tier:  {DIM}{cfg.get('default_tier', 'essential')}{R}")
        print(f"  {WHITE}4{R}  Keep raw dump: {DIM}{cfg.get('keep_raw_dump', False)}{R}")
        print(f"  {WHITE}5{R}  Use DeepSeek:  {DIM}{cfg.get('use_deepseek', True)}{R}")
        print(f"  {WHITE}6{R}  Check deps     {DIM}(python packages + S2V CLI){R}")
        print(f"  {WHITE}7{R}  Open output    {DIM}(assets/extracted/){R}")
        print(f"  {WHITE}8{R}  Open images    {DIM}(images/deadlock/){R}")
        print(f"\n  {WHITE}0{R}  Back")
        c = input(f"\n  {YELLOW}Select [0-8]:{R} ").strip()

        if c == "0" or c == "":
            save_config(cfg)
            return
        elif c == "1":
            p = input("  Steam Deadlock path (empty=auto): ").strip()
            cfg["game_path"] = p
        elif c == "2":
            cfg["deepseek_key_file"] = input("  Key filename: ").strip() or "deepseek.txt"
        elif c == "3":
            t = input("  Tier [essential/full/complete]: ").strip()
            if t in ("essential", "full", "complete"):
                cfg["default_tier"] = t
        elif c == "4":
            cfg["keep_raw_dump"] = not cfg.get("keep_raw_dump", False)
        elif c == "5":
            cfg["use_deepseek"] = not cfg.get("use_deepseek", True)
        elif c == "6":
            _check_deps()
            pause()
        elif c == "7":
            os.startfile(str(ROOT / "assets" / "extracted")) if sys.platform == "win32" else None
        elif c == "8":
            os.startfile(str(ROOT / "images" / "deadlock")) if sys.platform == "win32" else None


def _check_deps():
    print(f"\n  {CYAN}Checking dependencies...{R}")
    for pkg in ("vpk", "openai"):
        try:
            __import__(pkg)
            print(f"  {GREEN}[+]{R} {pkg}")
        except ImportError:
            print(f"  {YELLOW}[~]{R} {pkg} — installing...")
            subprocess.call([sys.executable, "-m", "pip", "install", pkg, "-q"])
    cli = TOOLS / "Source2Viewer-CLI" / "Source2Viewer-CLI.exe"
    if cli.exists():
        print(f"  {GREEN}[+]{R} Source2Viewer-CLI")
    else:
        print(f"  {YELLOW}[~]{R} Source2Viewer-CLI — will download on first extract")
        run_tool("extract_deadlock_assets.py", ["--list"])


def menu_logs():
    clear()
    print(f"{BOLD}{CYAN}  [LOGS] Last extraction manifest{R}\n")
    manifest = ROOT / "assets" / "extracted" / "manifest.json"
    catalog = ROOT / "assets" / "extracted" / "catalog" / "deadlock_knowledge.json"
    for path, label in [(manifest, "manifest.json"), (catalog, "deadlock_knowledge.json")]:
        if path.exists():
            print(f"  {GREEN}[+]{R} {label}")
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if "stats" in data:
                for k, v in data.get("stats", {}).get("categories", {}).items():
                    print(f"      {DIM}{k}:{R} {v}")
            if "dump_date" in data:
                print(f"      {DIM}date:{R} {data['dump_date']}")
            elif "generated" in data:
                print(f"      {DIM}generated:{R} {data['generated']}")
        else:
            print(f"  {RED}[-]{R} {label} {DIM}(not found — run extract first){R}")
    pause()


def main_menu():
    cfg = load_config()
    while True:
        clear()
        banner()
        print(f"  {status_line(cfg)}\n")
        print(f"{BOLD}  MAIN MENU{R}\n")
        print(f"  {MAGENTA}[RECON]{R}")
        print(f"  {WHITE} 1{R}  Scan VPK inventory          {DIM}list all extractable assets{R}")
        print(f"\n  {MAGENTA}[EXTRACT]{R}")
        print(f"  {WHITE} 2{R}  Quick extract (essential)   {DIM}~5 min — vdata + icons + index{R}")
        print(f"  {WHITE} 3{R}  Full extract (full)         {DIM}~15-45 min — particles + panorama UI{R}")
        print(f"  {WHITE} 4{R}  Complete extract            {DIM}~5-20 min — all images + indexes (fast){R}")
        print(f"  {WHITE} 5{R}  Surgical extraction         {DIM}pick individual category{R}")
        print(f"\n  {MAGENTA}[PIPELINE]{R}")
        print(f"  {WHITE} 6{R}  Full pipeline + DeepSeek    {DIM}extract + AI organize{R}")
        print(f"  {WHITE} 7{R}  Full pipeline (no AI)       {DIM}extract only{R}")
        print(f"\n  {MAGENTA}[INTEL]{R}")
        print(f"  {WHITE} 8{R}  Organize / Build Hub         {DIM}DeepSeek + community manifests{R}")
        print(f"  {WHITE} 9{R}  View last manifest          {DIM}extraction logs{R}")
        print(f"\n  {MAGENTA}[SYSTEM]{R}")
        print(f"  {WHITE}10{R}  Configuration               {DIM}paths, deps, folders{R}")
        print(f"  {WHITE} 0{R}  Exit")
        print()

        choice = input(f"  {YELLOW}umblock>{R} ").strip()

        actions = {
            "1": menu_recon,
            "2": lambda: menu_extract_tier("essential", "Essential Tier (~5 min)"),
            "3": lambda: menu_extract_tier("full", "Full Tier (~30-60 min)"),
            "4": lambda: menu_extract_tier("complete", "Complete Tier (~1-2 h)"),
            "5": menu_surgical,
            "6": lambda: menu_full_pipeline(cfg.get("default_tier", "essential"), True),
            "7": lambda: menu_full_pipeline(cfg.get("default_tier", "essential"), False),
            "8": menu_intel,
            "9": menu_logs,
            "10": menu_config,
            "0": None,
        }

        if choice == "0":
            clear()
            print(f"\n  {DIM}Session closed.{R}\n")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print(f"  {RED}Invalid option{R}")
            time.sleep(0.5)


def main():
    enable_vt()
    os.chdir(ROOT)
    sys.path.insert(0, str(TOOLS))
    try:
        main_menu()
    except KeyboardInterrupt:
        clear()
        print(f"\n  {DIM}Interrupted.{R}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
