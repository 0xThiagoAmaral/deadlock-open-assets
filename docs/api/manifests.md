# Manifests API

All consumer manifests live in `manifests/` at the repository root.

## Master catalog

```json
// manifests/hub.json
{
  "stats": {
    "heroes": 73,
    "items": 173,
    "pngs": 1771,
    "particles_vpcf": 9463
  },
  "manifests": { ... }
}
```

## Available manifests

| File | Description |
|------|-------------|
| `manifests/hub.json` | Master catalog with stats and paths |
| `manifests/heroes.json` | Heroes + abilities + image paths + codenames |
| `manifests/items.json` | Shop items + upgrade catalog |
| `manifests/images.json` | Complete PNG registry by category |
| `manifests/codenames.json` | VPK codename ↔ hero_id map |
| `manifests/assets_index.json` | Directory map with file counts |

## Indexes (large path references)

| File | Records |
|------|---------|
| `assets/extracted/indexes/particles_index.json` | 9,463 |
| `assets/extracted/indexes/sounds_index.json` | 79,044 |
| `assets/extracted/indexes/models_index.json` | 152 |

## Fetch examples

=== "Python"

    ```python
    import json, urllib.request

    url = "https://raw.githubusercontent.com/0xThiagoAmaral/deadlock-open-assets/main/manifests/heroes.json"
    heroes = json.loads(urllib.request.urlopen(url).read())
    ```

=== "JavaScript"

    ```javascript
    const base = "https://cdn.jsdelivr.net/gh/0xThiagoAmaral/deadlock-open-assets@main";
    const heroes = await fetch(`${base}/manifests/heroes.json`).then(r => r.json());
    ```

=== "curl"

    ```bash
    curl -s https://raw.githubusercontent.com/0xThiagoAmaral/deadlock-open-assets/main/manifests/hub.json | jq .stats
    ```

## Image paths

All image paths in manifests are **relative to repo root**:

```
images/deadlock/heroes_circle/abrams.png
images/deadlock/abilities/haze/ability_sleep_dagger.png
images/deadlock/items/spirit/arcane_extension.png
```

Resolve via CDN:

```
https://cdn.jsdelivr.net/gh/0xThiagoAmaral/deadlock-open-assets@main/{path}
```
