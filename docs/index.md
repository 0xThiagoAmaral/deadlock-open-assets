# Deadlock Open Assets Hub

<div id="hub-stats" class="hub-stats"></div>

The **#1 open reference** for Deadlock game data — extracted from the official VPK, organized, named, and ready to use.

!!! success "What's included"
    - **1,771** PNG icons (heroes, abilities, items, upgrades, UI)
    - **73** heroes with codename maps and ability data
    - **173** shop items + **209** upgrades
    - **76** vdata files (abilities, heroes, modifiers)
    - **9,463** decompiled ability particles
    - **412** Panorama layouts + **420** CSS styles
    - **79,044** sound path index + model index

## Quick links

| Resource | Path |
|----------|------|
| Hero browser | [Browse Heroes](browse/heroes.md) |
| JSON manifests | [Manifests API](api/manifests.md) |
| Full catalog | [Catalog](CATALOG.md) |
| Download | [Download guide](download.md) |

## Use in your project

```python
import json

heroes = json.load(open("manifests/heroes.json"))
abrams = heroes["heroes"]["abrams"]
icon = abrams["images"]["path_sm"]
# → images/deadlock/heroes_circle/abrams.png
```

```javascript
// From CDN (no clone required)
const base = "https://cdn.jsdelivr.net/gh/0xThiagoAmaral/deadlock-open-assets@main";
const icon = `${base}/images/deadlock/heroes_circle/abrams.png`;
```

## Update pipeline

```powershell
python tools/extract_deadlock_assets.py --tier complete
python tools/build_community_hub.py --sync-remote
```

!!! warning "Legal"
    Not affiliated with Valve. Game assets are property of Valve Corporation.
    See [Legal](legal.md) for full disclaimer.
