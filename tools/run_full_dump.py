#!/usr/bin/env python3
"""
Master pipeline: extract all Deadlock assets + organize with DeepSeek.

Usage:
  python tools/run_full_dump.py                    # essential tier + AI organize
  python tools/run_full_dump.py --tier full        # full extraction (~30-60 min)
  python tools/run_full_dump.py --tier full --no-ai
  python tools/run_full_dump.py --extract-only --tier essential
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def run_script(name: str, args: list[str]) -> int:
    cmd = [sys.executable, str(TOOLS / name)] + args
    print(f"\n{'='*60}")
    print(f"[*] Running: {' '.join(cmd)}")
    print("=" * 60)
    return subprocess.call(cmd)


def main():
    parser = argparse.ArgumentParser(description="Full Deadlock dump pipeline")
    parser.add_argument("--tier", choices=["essential", "full", "complete"], default="essential")
    parser.add_argument("--game-path")
    parser.add_argument("--no-ai", action="store_true")
    parser.add_argument("--extract-only", action="store_true")
    parser.add_argument("--organize-only", action="store_true")
    parser.add_argument("--keep-raw", action="store_true")
    args = parser.parse_args()

    game_args = ["--game-path", args.game_path] if args.game_path else []

    if not args.organize_only:
        extract_args = ["--tier", args.tier] + game_args
        if args.keep_raw:
            extract_args.append("--keep-raw")
        code = run_script("extract_deadlock_assets.py", extract_args)
        if code != 0:
            sys.exit(code)

        run_script("sync_deadlock_images.py", [])

    if not args.extract_only:
        org_args = []
        if args.no_ai:
            org_args.append("--no-ai")
        code = run_script("organize_with_deepseek.py", org_args)
        if code != 0:
            sys.exit(code)

    if not args.extract_only:
        code = run_script("build_community_hub.py", ["--sync-remote"])
        if code != 0:
            print("[!] Hub build had warnings (continuing)")

    print("\n[*] Pipeline complete.")
    print("    manifests/hub.json")
    print("    docs/CATALOG.md")
    print("    assets/extracted/manifest.json")
    print("    images/deadlock/")
    print("    assets/vdata/")


if __name__ == "__main__":
    main()
