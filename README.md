# Deadlock Open Assets Hub

**Live site:** [0xthiagoamaral.github.io/deadlock-open-assets](https://0xthiagoamaral.github.io/deadlock-open-assets/)

**The most complete community-mapped Deadlock resource repository** — heroes, abilities, items, upgrades, UI icons, vdata, particles, Panorama UI, and cross-reference indexes. Everything organized, named, and ready to use.

> Not affiliated with Valve. You must own Deadlock on Steam. See [LICENSE](LICENSE) for tooling (MIT) and game asset disclaimer.

---

## What's inside

| Category | Location | Count |
|----------|----------|-------|
| Hero icons (circle, minimap, card) | `images/deadlock/heroes_*` | 55+ heroes |
| Ability icons | `images/deadlock/abilities/` | 316 PNGs |
| Item icons | `images/deadlock/items/` | 181 PNGs |
| Upgrade/mod icons | `images/deadlock/upgrades/` | 210 PNGs |
| UI assets (shop, hud, ranked…) | `images/deadlock/ui/` | 832 PNGs |
| Game data (vdata) | `assets/vdata/` | 76 files |
| Ability particles | `assets/extracted/particles/` | 9,463 .vpcf |
| Panorama UI | `assets/extracted/panorama/` | 412 XML + 420 CSS |
| Particle index | `assets/extracted/indexes/` | 9,463 entries |
| Sound path index | `assets/extracted/indexes/` | 79,044 paths |
| Curated hero roster | `assets/game/heroes.json` | 38 heroes |
| Item database | `assets/game/items.json` | 173 items |
| Codename map | `manifests/codenames.json` | VPK codename → hero_id |

**Start here:** [`docs/CATALOG.md`](docs/CATALOG.md) — full browsable index (auto-generated).

---

## Quick start (consumers)

```python
import json

# Unified hero data with image paths
heroes = json.load(open("manifests/heroes.json"))
abrams = heroes["heroes"]["abrams"]
icon = abrams["images"]["path_sm"]  # images/deadlock/heroes_circle/abrams.png

# Full image registry
images = json.load(open("manifests/images.json"))

# VPK codename mapping (bull -> abrams)
codes = json.load(open("manifests/codenames.json"))
hero_id = codes["map"]["bull"]  # "abrams"
```

```powershell
# Browse manifest summary
python -c "import json; print(json.load(open('manifests/hub.json'))['stats'])"
```

---

## Quick start (extract & update)

### Option A — Double-click launcher

```
UmblockExtractor.bat
```

Menu: **Complete extract** → **Build community hub**

### Option B — Command line

```powershell
pip install -r requirements.txt

# Full extraction from your Steam install (~5-20 min)
python tools/extract_deadlock_assets.py --tier complete

# Build unified manifests + optional live meta
python tools/build_community_hub.py --sync-remote

# Package large folders for GitHub Releases
python tools/package_release.py
```

Requires Deadlock installed via Steam. Source2Viewer-CLI downloads automatically on first run.

---

## Repository layout

```
manifests/          # Unified consumer manifests (START HERE)
docs/CATALOG.md   # Human-readable index

assets/game/      # Curated JSON (heroes, items, economy, knowledge)
assets/vdata/     # Decompiled .vdata game files
assets/extracted/ # VPK dump output (particles, panorama, indexes)
images/deadlock/  # Organized PNG icons

tools/            # Extraction + hub build pipeline
releases/         # Large tarballs for GitHub Releases (not in git)
```

---

## Manifests reference

| File | Purpose |
|------|---------|
| `manifests/hub.json` | Master catalog — stats, paths, legal, data sources |
| `manifests/heroes.json` | Heroes + abilities + codenames + image paths |
| `manifests/items.json` | Items + upgrade catalog with icon links |
| `manifests/images.json` | Complete PNG registry by category |
| `manifests/codenames.json` | VPK internal name ↔ hero_id |
| `manifests/assets_index.json` | Directory map with file counts |

---

## Extraction tiers

| Tier | What you get | Time |
|------|-------------|------|
| `essential` | vdata + core icons + particle index | ~5 min |
| `full` | + all panorama UI + ability particles | ~15-45 min |
| `complete` | + all image categories + sound/model indexes | ~5-20 min |

---

## GitHub publishing strategy

This repo is large. Recommended approach:

1. **Git + Git LFS** — PNGs, manifests, vdata, indexes, panorama CSS/XML
2. **GitHub Releases** — particle dump (`releases/deadlock-particles-*.tar.gz`)
3. **Never commit** — Source2Viewer-CLI binary, API keys, internal cheat scripts

```powershell
python tools/package_release.py   # creates releases/*.tar.gz
# Upload to GitHub Releases tab
```

---

## Data sources

| Source | What it provides |
|--------|-----------------|
| Local VPK (Steam) | Images, vdata, particles, panorama — primary |
| [Source2Viewer-CLI](https://github.com/ValveResourceFormat/ValveResourceFormat) | Decompilation engine |
| [GameTracking-Deadlock](https://github.com/SteamDatabase/GameTracking-Deadlock) | Localization strings |
| [deadlock-api.com](https://deadlock-api.com) | Live win rates, item stats (optional) |
| [deadlock-open-data](https://github.com/deadlock-open-data) | Community hero reference |

---

## Who is this for?

- **Modders** — Panorama UI, icons, codename maps
- **Tool developers** — structured JSON + image paths + particle indexes
- **Build creators** — items, upgrades, economy data
- **Counterspell/dodge tools** — particle + sound path indexes
- **Researchers** — vdata dumps, vpk inventory stats
- **Wiki/data projects** — pre-mapped assets so you don't start from zero

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `python tools/build_community_hub.py` after any extraction update.

---

## Related projects

- [ValveResourceFormat / Source 2 Viewer](https://github.com/ValveResourceFormat/ValveResourceFormat)
- [deadlock-open-data](https://github.com/deadlock-open-data)
- [deadlock-api](https://github.com/deadlock-api/deadlock-api)
- [deadbot (wiki pipeline)](https://github.com/deadlock-wiki/deadbot)
