# Images — Umblock Asset Library

Biblioteca visual compartilhada entre **Dota 2** e **Deadlock** no loader Umbrella.

## Estrutura

```
images/
├── dota/                    # (legado) pastas Dota2 na raiz — não mover
│   ├── heroes_circle/       #   120+ heróis Dota (PNG)
│   ├── items_square/
│   ├── MenuIcons/           #   ícones genéricos de UI
│   ├── DmgIndicator/
│   ├── ArcPanel/
│   └── ...
├── deadlock/                # NOVO — paridade com Dota2
│   ├── heroes_circle/       #   retratos PNG (21+ heróis)
│   ├── heroes_square/       #   model shots
│   ├── abilities/           #   ícones por herói
│   ├── items/               #   (pendente — extrair do jogo)
│   └── ui/                  #   watermark, brand
└── README.md
```

## Duas formas de usar ícones no Deadlock

| Uso | Fonte | API | Quando usar |
|-----|-------|-----|-------------|
| Menu switches | Panorama in-game | `menu:Icon("panorama/images/heroes/...")` | Ícones nativos, sempre atualizados |
| Overlay/HUD custom | PNG local | `Render.LoadImage("images/deadlock/...")` | Painéis estilo Dota (RankChecker, ESP panels) |

## Sincronizar imagens Deadlock

```bash
python tools/sync_deadlock_images.py
```

Copia PNGs de `assets/reference/deadlock-open-data/` → `images/deadlock/` e gera `assets/game/images_manifest.json`.

## Módulo Lua

```lua
local img = require("image_assets")

-- Menu (panorama — recomendado)
ui.enabled:Icon(img.hero_panorama("haze"))

-- Overlay (PNG local ou panorama via LIB_RENDER)
img.draw_hero(LIB_RENDER, Vec2(100, 100), "haze", 48)
```

## O que ainda falta (roadmap Dota → Deadlock)

| Feature Dota2 | Status Deadlock |
|---------------|-----------------|
| `heroes_circle/` | ✅ 21 heróis + panorama para 36 |
| `items_square/` | ⏳ precisa extrair do VPK/panorama |
| `DmgIndicator/` | ✅ reutilizar `images/DmgIndicator/` (genérico) |
| `MenuIcons/` | ✅ compartilhado |
| `StealerHeroes/` | ⏳ criar `images/deadlock/stealer/` |
| Panels (ArcPanel, InvokerPanel) | ✅ `ArcPanel/` compartilhado |

## Paths compartilhados (ambos os jogos)

Estes folders são **agnósticos de jogo** — use direto nos scripts Deadlock:

- `images/MenuIcons/` — botões, ícones UI
- `images/ArcPanel/` — fundos de painel
- `images/DmgIndicator/` — barras HP/dano
- `images/watermark/` — marca d'água Umbrella
