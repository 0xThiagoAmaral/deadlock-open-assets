# Deadlock Full Asset Dump Pipeline

Extrai e organiza recursos do VPK para o **Deadlock Open Assets Hub** — repositorio comunitario com dados, imagens e indexes mapeados.

## Hub comunitario (GitHub)

Apos extracao, gere os manifests unificados:

```powershell
python tools/build_community_hub.py --sync-remote
```

Saida:
- `manifests/hub.json` — catalogo mestre
- `manifests/heroes.json` — herois + imagens + codenames
- `docs/CATALOG.md` — indice legivel

Ver `README.md` na raiz para estrategia de publicacao no GitHub.

## Launcher interativo (fora da IDE)

**Duplo-clique em:**

```
UmblockExtractor.bat          (raiz do projeto)
tools/LaunchExtractor.bat     (atalho)
```

Menu estilo ferramenta standalone (RECON / EXTRACT / SURGICAL / INTEL / CONFIG).

Config persistente: `tools/extractor_config.json`

## Pipeline (linha de comando)

```
Steam VPK (pak01_dir.vpk)
        |
        v  extract_deadlock_assets.py  (Source2Viewer-CLI)
assets/extracted/
  vdata/              abilities.vdata, heroes.vdata, modifiers.vdata...
  particles/abilities/  .vpcf decompilados (counterspell/dodge)
  panorama/layout/    UI XML
  panorama/styles/    UI CSS
  indexes/            particles, sounds, models, vpk inventory
        +
images/deadlock/      PNGs organizados (heroes, items, ui...)
        |
        v  organize_with_deepseek.py  (DeepSeek API)
assets/extracted/catalog/
  local_index.json           indice local (sem API)
  deadlock_knowledge.json    catalogo enriquecido por IA
```

## Uso rapido

```powershell
# Pipeline completo (essential ~5 min + DeepSeek)
python tools/run_full_dump.py

# Extracao completa (~30-60 min) + organizacao IA
python tools/run_full_dump.py --tier full

# So extrair, sem API
python tools/run_full_dump.py --extract-only --no-ai

# So reorganizar com DeepSeek (apos extracao)
python tools/run_full_dump.py --organize-only
```

## Tiers de extracao

| Tier | O que extrai | Tempo estimado |
|------|--------------|----------------|
| `essential` | vdata, hero icons, items, abilities icons, particle index | ~5 min |
| `full` | + backgrounds, ranked, shop, particles decompiled, panorama UI | ~30-60 min |
| `complete` | + todos PNGs panorama, sound/model indexes | ~1-2 h |

## Categorias individuais

```powershell
python tools/extract_deadlock_assets.py --list
python tools/extract_deadlock_assets.py --only vdata
python tools/extract_deadlock_assets.py --only particles
python tools/extract_deadlock_assets.py --only heroes_backgrounds
python tools/extract_deadlock_assets.py --only panorama_layout
```

## DeepSeek (organizacao inteligente)

Chave API: `deepseek.txt` ou `api_deepseek.txt` na raiz do projeto.

O organizador gera `deadlock_knowledge.json` com:
- Cross-reference particles <-> abilities <-> heroes
- Tags para build creator (item categories, hero roles)
- Recomendacoes de features para scripts/mods
- Rotas de assets por ferramenta

```powershell
python tools/organize_with_deepseek.py           # local + DeepSeek
python tools/organize_with_deepseek.py --no-ai   # so indice local
```

## Destino por ferramenta

| Ferramenta | Assets principais |
|------------|-------------------|
| **Scripts Lua** | `particles/`, `vdata/`, `images/deadlock/heroes_circle/` |
| **Build Creator** | `vdata/heroes.vdata`, `images/deadlock/items/`, `assets/game/heroes.json` |
| **Mods UI** | `panorama/layout/`, `panorama/styles/`, `images/deadlock/ui/` |
| **Counterspell** | `indexes/particles_index.json`, `catalog/deadlock_knowledge.json` |
| **Super Team Agents** | `catalog/deadlock_knowledge.json`, `assets/manifest.json` |

## Pos-patch

Apos update do Deadlock na Steam:

```powershell
python tools/run_full_dump.py --tier essential
```

## Dependencias

```powershell
pip install vpk openai
```

Source2Viewer-CLI baixado automaticamente em `tools/Source2Viewer-CLI/`.
