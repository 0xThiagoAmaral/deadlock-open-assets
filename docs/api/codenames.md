# Codename Map

Deadlock uses internal VPK codenames that differ from display names. This map is critical for modding, scripting, and particle lookup.

## Example mappings

| VPK codename | Hero ID | Display |
|--------------|---------|---------|
| `bull` | `abrams` | Abrams |
| `astro` | `holliday` | Holliday |
| `archer` | `grey_talon` | Grey Talon |
| `spectre` | `lady_geist` | Lady Geist |
| `punkgoat` | `billy` | Billy |
| `bookworm` | `paige` | Paige |
| `chrono` | `paradox` | Paradox |
| `digger` | `mo_and_krill` | Mo & Krill |

## Usage

```python
import json
codes = json.load(open("manifests/codenames.json"))
hero_id = codes["map"]["bull"]        # "abrams"
codename = codes["reverse"]["abrams"]  # "bull"
```

## Full map

Download: [`manifests/codenames.json`](https://github.com/0xThiagoAmaral/deadlock-open-assets/blob/main/manifests/codenames.json)

Also embedded in [`manifests/heroes.json`](https://github.com/0xThiagoAmaral/deadlock-open-assets/blob/main/manifests/heroes.json) per hero entry.
