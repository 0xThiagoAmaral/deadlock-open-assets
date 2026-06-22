# Deadlock Images

Assets visuais para scripts Umbrella Deadlock. Espelha a organização do Dota2 em `images/heroes_circle/`, etc.

## Pastas

| Pasta | Conteúdo | Fonte |
|-------|----------|-------|
| `heroes_circle/` | Retrato circular PNG | wiki scraper / `deadlock-open-data` |
| `heroes_square/` | Model shot PNG | idem |
| `abilities/{hero}/` | Ícones Q/F/C/E | idem |
| `ui/` | Watermark, brand Umbrella | copiado de `images/ArcPanel/` |

## Atualizar

```bash
# Do VPK instalado (Steam) — fonte completa, patch atual
python tools/extract_deadlock_images.py --only heroes_sm   # ícones menu (~55 PNGs)
python tools/extract_deadlock_images.py                      # heróis + itens + abilities

# Da wiki (deadlock-open-data) — complementar
python tools/sync_deadlock_images.py
```

Ver guia completo: `tools/README_vpk_images.md`

## Catálogo machine-readable

`assets/game/images_manifest.json` — mapeia cada herói para:
- `panorama_sm` — path in-game (Menu icons)
- `local_circle` / `local_square` — PNG local (overlays)
- `abilities` — PNGs por ability

## Exemplo em script

```lua
local img = require("image_assets")

-- Counterspell-style menu icon
hero_switch:Icon(img.hero_panorama("infernus"))

-- RankChecker-style overlay panel
LIB_RENDER.image(img.ui("brand"), panel_pos, Vec2(120, 40), false, Color(255))
img.draw_hero(LIB_RENDER, Vec2(x, y), ent:get_name(), 32, Color(255), true)
```
