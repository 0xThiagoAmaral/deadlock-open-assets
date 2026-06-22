"""Professional CLI progress display — bars, ETA, live streaming."""

from __future__ import annotations

import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field

# ANSI
R = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"


def enable_vt():
    if sys.platform == "win32":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
        except Exception:
            pass


def fmt_time(seconds: float) -> str:
    if seconds < 0 or seconds == float("inf"):
        return "--:--"
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60:02d}s"
    return f"{s // 3600}h {(s % 3600) // 60:02d}m"


def fmt_size(nbytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.0f}{unit}" if unit == "B" else f"{nbytes:.1f}{unit}"
        nbytes /= 1024
    return f"{nbytes:.1f}TB"


@dataclass
class ProgressTracker:
    """Thread-safe progress with bar + ETA + throughput."""

    total: int
    label: str = ""
    width: int = 36
    start: float = field(default_factory=time.time)
    current: int = 0
    last_file: str = ""
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def advance(self, n: int = 1, filename: str = "") -> None:
        with self._lock:
            self.current += n
            if filename:
                self.last_file = filename
            self._render()

    def set(self, current: int, filename: str = "") -> None:
        with self._lock:
            self.current = current
            if filename:
                self.last_file = filename
            self._render()

    def _render(self) -> None:
        elapsed = time.time() - self.start
        pct = self.current / self.total if self.total else 0
        filled = int(self.width * pct)
        bar = f"{GREEN}{'#' * filled}{DIM}{'.' * (self.width - filled)}{R}"
        rate = self.current / elapsed if elapsed > 0.1 else 0
        remaining = (self.total - self.current) / rate if rate > 0 else float("inf")
        eta = fmt_time(remaining)
        line = (
            f"\r  {CYAN}{self.label}{R} [{bar}] "
            f"{WHITE}{self.current}/{self.total}{R} "
            f"{YELLOW}{pct * 100:5.1f}%{R} "
            f"{DIM}ETA {eta}{R} "
            f"{DIM}{rate:.1f}/s{R}   "
        )
        sys.stdout.write(line)
        sys.stdout.flush()

    def log_file(self, filename: str) -> None:
        """Print current file below the bar (call sparingly)."""
        short = filename if len(filename) <= 56 else "..." + filename[-53:]
        print(f"\n  {DIM}|{R} {GREEN}>{R} {short}")

    def finish(self, ok: bool = True) -> None:
        elapsed = fmt_time(time.time() - self.start)
        icon = f"{GREEN}[+]{R}" if ok else f"{RED}[!]{R}"
        print(f"\n  {icon} {self.label} {DIM}done in {elapsed}{R} ({self.current} files)")


class JobRunner:
    """Multi-phase job with overall progress and per-phase ETA."""

    TIER_ETA = {
        "essential": 300,
        "full": 2400,
        "complete": 5400,
    }

    PHASE_ETA = {
        "vdata": 15,
        "heroes_sm": 30,
        "heroes_mm": 30,
        "heroes_card": 45,
        "heroes_backgrounds": 120,
        "items": 45,
        "upgrades": 60,
        "abilities_icons": 60,
        "ui_ranked": 30,
        "ui_shop": 30,
        "ui_minimap": 30,
        "ui_icons": 30,
        "ui_postgame": 20,
        "ui_hud": 90,
        "particles": 1800,
        "particles_index": 10,
        "panorama_layout": 60,
        "panorama_styles": 60,
        "sounds_index": 30,
        "models_index": 15,
    }

    def __init__(self, phases: list[str], tier: str = "custom"):
        self.phases = phases
        self.tier = tier
        self.start = time.time()
        self.phase_idx = 0
        self.results: dict[str, int] = {}

    def estimated_total(self) -> int:
        if self.tier in self.TIER_ETA:
            return self.TIER_ETA[self.tier]
        return sum(self.PHASE_ETA.get(p, 60) for p in self.phases)

    def print_plan(self) -> None:
        total_eta = self.estimated_total()
        print(f"\n  {BOLD}{CYAN}JOB PLAN{R}  {DIM}{len(self.phases)} phases | est. {fmt_time(total_eta)}{R}\n")
        for i, p in enumerate(self.phases, 1):
            eta = self.PHASE_ETA.get(p, 60)
            print(f"  {DIM}{i:2}.{R} {WHITE}{p:22}{R} {DIM}~{fmt_time(eta)}{R}")
        print(f"\n  {DIM}{'-' * 58}{R}")

    def begin_phase(self, name: str) -> None:
        self.phase_idx += 1
        elapsed = fmt_time(time.time() - self.start)
        est_total = self.estimated_total()
        overall_pct = min(99, int((time.time() - self.start) / est_total * 100)) if est_total else 0
        print(
            f"\n  {MAGENTA}[{self.phase_idx}/{len(self.phases)}]{R} "
            f"{BOLD}{WHITE}{name}{R}  "
            f"{DIM}elapsed {elapsed} | overall ~{overall_pct}%{R}"
        )

    def end_phase(self, name: str, count: int) -> None:
        self.results[name] = count
        print(f"  {GREEN}+{R} {name}: {WHITE}{count}{R} files")

    def summary(self) -> None:
        elapsed = fmt_time(time.time() - self.start)
        total_files = sum(self.results.values())
        print(f"\n  {BOLD}{'=' * 58}{R}")
        print(f"  {GREEN}{BOLD}COMPLETE{R}  {DIM}{elapsed}{R}  |  {WHITE}{total_files}{R} total files")
        for k, v in self.results.items():
            print(f"    {DIM}{k:22}{R} {v}")
        print(f"  {BOLD}{'=' * 58}{R}\n")


def stream_subprocess(cmd: list[str], cwd: str | None = None, on_line=None) -> int:
    """Run command streaming stdout/stderr live. Returns exit code."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        bufsize=1,
    )
    dump_re = re.compile(r'Dump written to "(.+)"', re.IGNORECASE)
    for line in proc.stdout:
        line = line.rstrip()
        if not line:
            continue
        m = dump_re.search(line)
        if m:
            path = m.group(1)
            short = path.split("\\")[-1] if "\\" in path else path.split("/")[-1]
            print(f"  {DIM}|{R} {GREEN}>{R} {short}")
            if on_line:
                on_line(path)
        elif "error" in line.lower() or "failed" in line.lower():
            print(f"  {DIM}|{R} {RED}{line}{R}")
        elif on_line is None:
            print(f"  {DIM}|{R} {line}")
    return proc.wait()


def extract_vpk_files(
    vpk_path,
    out_dir,
    path_filter: str,
    extensions: list[str],
    match=None,
    progress: ProgressTracker | None = None,
) -> list[str]:
    """Extract raw compiled files from VPK with live progress."""
    from vpk_common import open_vpk
    import os

    pak = open_vpk(vpk_path)
    paths = []
    for path in pak:
        if not any(path.endswith(f".{e}") for e in extensions):
            continue
        if path_filter not in path:
            continue
        if match and not match.match(path):
            continue
        paths.append(path)

    if progress:
        progress.total = len(paths)
        progress.current = 0

    for i, path in enumerate(paths):
        dest = out_dir / path.replace("/", os.sep)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            f.write(pak[path].read())
        if progress:
            progress.advance(1, path)
            if (i + 1) % 10 == 0 or i + 1 == len(paths):
                progress.log_file(path)
    if progress:
        progress.finish()
    return paths
