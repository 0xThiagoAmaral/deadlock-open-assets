"""Shared utilities for Deadlock VPK extraction."""

from __future__ import annotations

import os
import re
import subprocess
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable

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
    "mcginnis": "mcginnis", "mina": "mina", "werewolf": "silver", "gunslinger": "gunslinger",
}


def find_game_path(custom: str | None = None) -> Path:
    if custom:
        p = Path(custom)
        if (p / "game" / "citadel" / "pak01_dir.vpk").exists():
            return p
        raise FileNotFoundError(f"VPK not found under {p}")
    for p in STEAM_PATHS:
        if (p / "game" / "citadel" / "pak01_dir.vpk").exists():
            return p
    raise FileNotFoundError("Deadlock install not found. Use --game-path.")


def get_vpk_path(game: Path | None = None) -> Path:
    game = game or find_game_path()
    return game / "game" / "citadel" / "pak01_dir.vpk"


def ensure_cli(on_status: Callable[[str], None] | None = None) -> Path:
    if CLI_EXE.exists():
        return CLI_EXE
    msg = f"Downloading Source2Viewer-CLI -> {CLI_DIR}"
    if on_status:
        on_status(msg)
    else:
        print(f"[*] {msg}")
    CLI_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = CLI_DIR / "cli.zip"
    urllib.request.urlretrieve(CLI_URL, zip_path)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(CLI_DIR)
    zip_path.unlink(missing_ok=True)
    if not CLI_EXE.exists():
        raise RuntimeError("Source2Viewer-CLI.exe missing after download")
    return CLI_EXE


def open_vpk(vpk_path: Path):
    import vpk
    return vpk.open(str(vpk_path))


def count_vpk_matches(vpk_path: Path, path_filter: str, extensions: list[str], match=None) -> int:
    pak = open_vpk(vpk_path)
    n = 0
    for path in pak:
        if not any(path.endswith(f".{e}") for e in extensions):
            continue
        if path_filter not in path:
            continue
        if match and not match.match(path):
            continue
        n += 1
    return n


def decompile_vpk(
    cli: Path,
    vpk_path: Path,
    out_dir: Path,
    path_filter: str,
    extensions: str | list[str],
    threads: int = 4,
    match: re.Pattern | None = None,
    on_dump: Callable[[str], None] | None = None,
    verbose: bool = True,
) -> int:
    """Decompile VPK subset with live streaming output."""
    from cli_progress import ProgressTracker, stream_subprocess, extract_vpk_files

    out_dir.mkdir(parents=True, exist_ok=True)
    exts = extensions if isinstance(extensions, list) else [extensions]

    if match:
        total = count_vpk_matches(vpk_path, path_filter, exts, match)
        if verbose:
            print(f"  {CYAN}>{R} Extracting {total} files from VPK...")
        progress = ProgressTracker(total=total, label="VPK pull") if verbose and total else None
        extract_vpk_files(vpk_path, out_dir, path_filter, exts, match, progress)
        if verbose:
            print(f"  {CYAN}>{R} Decompiling with Source2Viewer ({total} files)...")
        cmd = [str(cli), "-i", str(out_dir), "-o", str(out_dir), "-d", "--recursive", "--threads", str(threads)]
        dumped = [0]

        def on_line(path):
            dumped[0] += 1
            if on_dump:
                on_dump(path)

        code = stream_subprocess(cmd, on_line=on_line)
        return dumped[0] if code == 0 else 0

    if verbose:
        print(f"  {CYAN}>{R} Decompiling from VPK filter: {path_filter}")
    ext_arg = ",".join(exts)
    cmd = [
        str(cli), "-i", str(vpk_path), "-o", str(out_dir), "-d",
        "-f", path_filter, "-e", ext_arg, "--threads", str(threads),
    ]
    dumped = [0]

    def on_line(path):
        dumped[0] += 1
        if on_dump:
            on_dump(path)

    code = stream_subprocess(cmd, on_line=on_line)
    return dumped[0] if code == 0 else count_files(out_dir, ["png", *exts])


def count_files(root: Path, extensions: list[str]) -> int:
    if not root.exists():
        return 0
    exts = {f".{e}" for e in extensions}
    return sum(1 for f in root.rglob("*") if f.suffix in exts or f.suffix.lstrip(".") in extensions)


def rename_hero_png(src_name: str, variant: str) -> str | None:
    m = re.match(r"^([a-z0-9_]+)_(sm|mm|card)_psd(?:_[a-f0-9]+)?\.png$", src_name)
    if not m:
        return None
    codename, kind = m.group(1), m.group(2)
    if kind != variant.replace("hero_", ""):
        return None
    hero_id = CODENAME_TO_HERO.get(codename, codename)
    return f"{hero_id}.png"


def load_deepseek_key() -> str:
    for name in ("deepseek.txt", "api_deepseek.txt"):
        path = ROOT / name
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
    raise FileNotFoundError("API key not found. Create deepseek.txt or api_deepseek.txt in project root.")


# lazy import for CYAN in decompile
CYAN = "\033[96m"
R = "\033[0m"
