#!/usr/bin/env python3
"""Package large asset folders for GitHub Releases (not plain git)."""

from __future__ import annotations

import argparse
import tarfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RELEASES = ROOT / "releases"

PACKAGES = {
    "particles": ROOT / "assets" / "extracted" / "particles",
    "images": ROOT / "images" / "deadlock",
    "panorama": ROOT / "assets" / "extracted" / "panorama",
}


def package(name: str, src: Path, patch: str) -> Path | None:
    if not src.exists():
        print(f"  [!] Skip {name}: {src} not found")
        return None
    RELEASES.mkdir(parents=True, exist_ok=True)
    out = RELEASES / f"deadlock-{name}-{patch}.tar.gz"
    print(f"  [*] Packing {name} -> {out.name}...")
    with tarfile.open(out, "w:gz") as tar:
        tar.add(src, arcname=name)
    mb = out.stat().st_size / (1024 * 1024)
    print(f"  [+] {out.name} ({mb:.1f} MB)")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Package large assets for GitHub Releases")
    parser.add_argument("--patch", default=date.today().isoformat())
    parser.add_argument("--only", choices=list(PACKAGES.keys()))
    args = parser.parse_args()

    targets = {args.only: PACKAGES[args.only]} if args.only else PACKAGES
    for name, src in targets.items():
        package(name, src, args.patch)
    print(f"\n[*] Upload releases/*.tar.gz to GitHub Releases (not git commit)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
