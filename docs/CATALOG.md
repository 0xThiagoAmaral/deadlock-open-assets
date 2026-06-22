# Deadlock Open Assets — Catalog

> Generated: 2026-06-22T17:24:28.988288

## Quick stats

| Asset | Count |
|-------|-------|
| heroes | 73 |
| items | 173 |
| upgrades | 209 |
| pngs | 1,771 |
| vdata_files | 76 |
| particles_vpcf | 9,463 |
| panorama_layout | 412 |
| panorama_styles | 420 |
| particles_indexed | 9,463 |

## Directory map

- **`assets/game/`** — 
- **`images/deadlock/`** — Hero, ability, item, upgrade, and UI icons (PNG from VPK) (1,771 files)
- **`assets/vdata/`** — Decompiled game data (abilities, heroes, modifiers) (76 files)
- **`assets/extracted/particles/abilities/`** — Decompiled ability particle systems — large, use Git LFS or Releases (9,463 files)
- **`assets/extracted/panorama/`** — Decompiled Panorama UI (XML layout + CSS) (412 files)
- **`assets/extracted/indexes/`** — Particle, sound, and model path indexes
- **`assets/extracted/catalog/local_index.json`** — Cross-reference index (codenames, vdata summaries, particles)
- **`tools/`** — VPK extraction and hub build pipeline

## Heroes

**73** heroes with abilities, codenames, and image paths.

| Hero ID | Display | Icons |
|---------|---------|-------|
| `abrams` | Abrams | sm |
| `airheart` | Airheart | partial |
| `apollo` | Apollo | sm |
| `bebop` | Bebop | sm |
| `billy` | Billy | sm |
| `bull` | Abrams | - |
| `cadence` | Cadence | sm |
| `calico` | Shiv | sm |
| `celestial` | Celeste | - |
| `digger` | Mo & Krill | - |
| `doorman` | The Doorman | sm |
| `drifter` | Drifter | sm |
| `druid` | Druid | sm |
| `dynamo` | Dynamo | sm |
| `engineer` | Engineer | sm |
| `familiar` | Rem | - |
| `fortuna` | Fortuna | sm |
| `frog` | Frog | partial |
| `genericperson` | Genericperson | sm |
| `graf` | Graf | sm |
| `graves` | Graves | - |
| `grey_talon` | Grey Talon | sm |
| `gunslinger` | Gunslinger | sm |
| `haze` | Haze | sm |
| `holliday` | Holliday | sm |
| `infernus` | Infernus | sm |
| `ivy` | Grey Talon | sm |
| `kali` | Kali | sm |
| `kelvin` | Kelvin | sm |
| `lady_geist` | Lady Geist | sm |
| `lash` | Lash | sm |
| `mcginnis` | McGinnis | - |
| `mina` | Mina | - |
| `mirage` | Mirage | sm |
| `mo_and_krill` | Mo And Krill | sm |
| `nano` | Calico | - |
| `necro` | Necro | sm |
| `operative` | Operative | sm |
| `paige` | Paige | sm |
| `paradox` | Paradox | sm |
| `pocket` | Viscous | sm |
| `priest` | Venator | - |
| `rem` | Rem | sm |
| `rutger` | Rutger | sm |
| `seven` | Seven | sm |
| `shiv` | Shiv | sm |
| `silver` | Silver | sm |
| `sinclair` | Sinclair | sm |
| `skyrunner` | Skyrunner | sm |
| `slork` | Slork | sm |
| `spectre` | Lady Geist | - |
| `swan` | Swan | sm |
| `synth` | Pocket | - |
| `targetdummy` | Targetdummy | sm |
| `tengu` | Ivy | - |
| `thumper` | Thumper | sm |
| `tokamak` | Tokamak | sm |
| `trapper` | Trapper | sm |
| `unicorn` | Unicorn | sm |
| `vampirebat` | Vampirebat | sm |
| `vandal` | Vandal | sm |
| `venator` | Dynamo | sm |
| `victor` | Victor | sm |
| `vindicta` | Vindicta | partial |
| `viscous` | Viscous | sm |
| `vyper` | Vyper | - |
| `warden` | Warden | sm |
| `werewolf` | Silver | - |
| `werewolf_wolf` | Werewolf Wolf | partial |
| `wraith` | Wraith | sm |
| `wrecker` | Wrecker | sm |
| `yakuza` | Yakuza | sm |
| `yamato` | Yamato | sm |

## Images

**1,771** PNG files organized under `images/deadlock/`.

| Category | Path | Count |
|----------|------|-------|
| abilities | `images/deadlock/abilities/` | 316 |
| backgrounds | `images/deadlock/backgrounds/` | 44 |
| heroes_card | `images/deadlock/heroes_card/` | 52 |
| heroes_circle | `images/deadlock/heroes_circle/` | 58 |
| heroes_minimap | `images/deadlock/heroes_minimap/` | 57 |
| heroes_square | `images/deadlock/heroes_square/` | 21 |
| items | `images/deadlock/items/` | 181 |
| ui | `images/deadlock/ui/` | 832 |
| upgrades | `images/deadlock/upgrades/` | 210 |

## Items & upgrades

- **173** shop items with stats
- **209** upgrade/mod icons catalogued

## Indexes (path references)

- `assets/extracted/indexes/particles_index.json` — 9,000+ ability particles by hero
- `assets/extracted/indexes/sounds_index.json` — 79,000+ sound file paths
- `assets/extracted/indexes/models_index.json` — hero model paths

## Usage

```python
import json
heroes = json.load(open('manifests/heroes.json'))
images = json.load(open('manifests/images.json'))
abrams_icon = images['heroes']['abrams']['path_sm']
```

## Update pipeline

```powershell
python tools/extract_deadlock_assets.py --tier complete
python tools/build_community_hub.py --sync-remote
```
