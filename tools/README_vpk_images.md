# VPK Image Dump — Deadlock

Como extrair **todas** as imagens do jogo instalado (mesma lógica do dump de vdata).

## Por que vdata foi fácil e imagens parecem "mais difíceis"?

| | vdata (habilidades/stats) | imagens (ícones/texturas) |
|--|---------------------------|---------------------------|
| Formato no VPK | `.vdata_c` → texto KeyValues3 | `.vtex_c` → textura compilada binária |
| Leitura direta | Sim (após decompilar para `.vdata`) | Não — precisa converter para PNG |
| Ferramenta | Source2Viewer-CLI `-d` | Source2Viewer-CLI `-d` (mesma!) |
| Volume | ~2 arquivos grandes | ~1961 texturas panorama |

**Nada impede o dump de imagens** — é o mesmo VPK (`pak01_dir.vpk`), só com um passo extra de conversão `vtex_c → PNG`.

## O que tem no VPK do seu PC

Detectado em `C:\Program Files (x86)\Steam\steamapps\common\Deadlock\game\citadel\`:

| Categoria | Arquivos `.vtex_c` |
|-----------|-------------------|
| heroes | 410 |
| abilities | 232 |
| items | 181 |
| upgrades | 210 |
| outros panorama | 928 |
| **Total panorama** | **1961** |

## Pipeline

```
Steam/Deadlock/game/citadel/pak01_dir.vpk
        │
        ▼  Source2Viewer-CLI -d -f "panorama/images/heroes/" ...
   assets/dump/vpk_images/   (temporário)
        │
        ▼  rename + organize
   images/deadlock/
   ├── heroes_circle/     ← haze.png, infernus.png (de haze_sm_psd, inferno_sm_psd)
   ├── heroes_minimap/
   ├── items/spirit/...
   ├── abilities_vpk/...
   └── upgrades/...
        │
        ▼
   assets/game/images_manifest.json
```

## Como rodar

```powershell
# Ver quantos arquivos serão extraídos
python tools/extract_deadlock_images.py --list

# Extrair ícones de menu dos heróis (~40 PNGs, ~30s)
python tools/extract_deadlock_images.py --only heroes_sm

# Extrair heróis + itens + abilities (~400 PNGs, ~2min)
python tools/extract_deadlock_images.py

# Caminho customizado
python tools/extract_deadlock_images.py --game-path "D:\Steam\steamapps\common\Deadlock"
```

Na primeira execução, baixa automaticamente o [Source2Viewer-CLI](https://github.com/ValveResourceFormat/ValveResourceFormat) para `tools/Source2Viewer-CLI/`.

## Renomeação automática

O jogo usa codenames internos nos arquivos:

| Arquivo VPK | Renomeado para |
|-------------|----------------|
| `archer_sm_psd.png` | `grey_talon.png` |
| `inferno_sm_psd.png` | `infernus.png` |
| `digger_sm_psd.png` | `mo_and_krill.png` |

Mapa completo em `tools/extract_deadlock_images.py` → `CODENAME_TO_HERO`.

## Uso nos scripts Lua

```lua
local img = require("image_assets")

-- Opção A: panorama (sempre atualizado, funciona no Menu)
menu:Icon(img.hero_panorama("haze"))

-- Opção B: PNG extraído do VPK (overlays estilo Dota)
Render.LoadImage("images/deadlock/heroes_circle/haze.png")
```

## Pós-patch (novo update Steam)

Re-rode após cada update do Deadlock:

```powershell
python tools/extract_deadlock_images.py
python tools/sync_deadlock_images.py   # merge com wiki assets
```

## Ferramentas

- [Source2Viewer-CLI](https://s2v.app/ValveResourceFormat/guides/command-line.html) — decompila `vtex_c` → PNG
- [vpk (Python)](https://github.com/ValvePython/vpk) — lista arquivos no VPK
- `tools/sync_deadlock_images.py` — complementa com PNGs da wiki (deadlock-open-data)
