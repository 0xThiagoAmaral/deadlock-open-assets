# For Developers

Integration guide for **Lua scripters**, **mod authors**, **counterspell tools** and **build creators**.

## Why this repo exists

Other Deadlock resources are scattered — wiki pages, partial open-data repos, manual VPK digging. This hub gives you **one JSON + one CDN base** for everything.

## Base URLs

| Use | URL |
|-----|-----|
| **Site** | `https://0xthiagoamaral.github.io/deadlock-open-assets/` |
| **Raw manifests** | `https://raw.githubusercontent.com/0xThiagoAmaral/deadlock-open-assets/main/manifests/` |
| **Images (LFS)** | `https://media.githubusercontent.com/media/0xThiagoAmaral/deadlock-open-assets/main/images/` |

## Lua / Umbrella scripts

### Load hero icon overlay

```lua
local BASE = "https://media.githubusercontent.com/media/0xThiagoAmaral/deadlock-open-assets/main/"
local icon = BASE .. "images/deadlock/heroes_circle/haze.png"
-- Render.LoadImage(icon) or your framework's image loader
```

### Codename → hero_id

```lua
-- VPK uses "bull", your script uses "abrams"
local codenames = {
    bull = "abrams", astro = "holliday", archer = "grey_talon",
    -- full map: manifests/codenames.json
}
```

### Panorama native path

```lua
-- In-game icon (no PNG needed)
Menu:Icon("panorama/images/heroes/bull_sm_psd.vtex_c")
-- Codename map tells you bull = abrams
```

## Counterspell / particle mapping

```python
import json
particles = json.load(open("assets/extracted/indexes/particles_index.json"))
# particles["entries"]["haze"] → list of .vpcf names
# Cross-ref with abilities.vdata for cast detection
```

Key particles are pre-tagged in `assets/extracted/catalog/local_index.json` under `top_cast_particles`.

## Mod development

| Asset | Path |
|-------|------|
| Panorama layout | `assets/extracted/panorama/layout/` |
| Panorama CSS | `assets/extracted/panorama/styles/` |
| UI icons | `images/deadlock/ui/` |
| Item icons | `images/deadlock/items/{category}/` |

Override game files in `addons/` using the same relative paths from the VPK.

## Build creator data

```python
items = json.load(open("manifests/items.json"))
for item in items["items"]:
    print(item["name"], item["tier"], item["cost"], item.get("image"))
```

## Share & credit

Help the community find this resource:

```markdown
[![Deadlock Open Assets](https://img.shields.io/badge/Data-Deadlock%20Open%20Assets-e85d04)](https://0xthiagoamaral.github.io/deadlock-open-assets/)
```

```markdown
Icons from [deadlock-open-assets](https://github.com/0xThiagoAmaral/deadlock-open-assets)
```

## Stay updated

1. **Watch** the GitHub repo for patch updates
2. **Star** to boost visibility in search
3. Re-run `python tools/build_community_hub.py` after each game patch

## Community links

| Project | Purpose |
|---------|---------|
| [deadlock-open-data](https://github.com/deadlock-open-data) | Hero stats reference |
| [deadlock-api.com](https://deadlock-api.com) | Live win rates & meta |
| [Source 2 Viewer](https://s2v.app) | VPK extraction engine |
| [GameTracking-Deadlock](https://github.com/SteamTracking/GameTracking-Deadlock) | Patch file tracking |

!!! info "Request an asset"
    [Open an issue](https://github.com/0xThiagoAmaral/deadlock-open-assets/issues/new) with the patch version and what's missing.
