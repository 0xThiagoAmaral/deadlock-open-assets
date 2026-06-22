# Assets — Umblock Data Layer

Fonte de verdade centralizada para a Super Team Umbrella e scripts Deadlock.

## Estrutura

```
assets/
├── manifest.json          # Catálogo machine-readable para agentes
├── game/                    # Dados curados do jogo (JSON)
│   ├── heroes.json          # 38 heróis, binds Q/F/C/E, abilities
│   ├── items.json           # 173 itens (tier, cost, category)
│   ├── economy.json         # Economia de almas, fases, orbs
│   └── knowledge_base.json  # Stats/cooldowns do vdata
├── vdata/                   # Dumps nativos KeyValues
│   ├── abilities.vdata
│   └── heroes.vdata
├── docs/
│   ├── api/                 # API Umbrella (60 arquivos .lua)
│   ├── builds/index.md      # Índice de builds
│   ├── research/            # Pesquisa de meta
│   └── agents/              # Regras internas dos agentes
├── reference/
│   └── deadlock-open-data/  # Repo comunitário (JSON por herói)
├── extracted/               # Dump VPK (ver tools/run_full_dump.py)
│   ├── vdata/               # 76 arquivos .vdata decompilados
│   ├── particles/abilities/ # .vpcf (tier full)
│   ├── panorama/            # layout + styles (tier full)
│   ├── indexes/             # particles, sounds, models
│   └── catalog/
│       └── deadlock_knowledge.json  # Catálogo DeepSeek
└── extension/               # Extensão VSCode Umbrella
```

## Dump completo do jogo

```powershell
python tools/run_full_dump.py                  # essential + DeepSeek
python tools/run_full_dump.py --tier full        # tudo (~30-60 min)
```

Ver `tools/README_full_dump.md`.

## Launcher standalone

Duplo-clique: **`UmblockExtractor.bat`** na raiz do projeto.

## Uso pelos agentes

O `orchestrator.py` carrega automaticamente via `assets_loader.py`:

1. **A0** — consulta `vdata/` e `knowledge_base.json` para saber o que extrair
2. **A0.5** — estrutura dados de `game/*.json`
3. **A1/A3** — usa `heroes.json`, `economy.json`, `docs/builds/`
4. **A2/A4/A5/A7** — referencia `docs/api/` (nunca inventar API)
5. **A6** — lê `docs/agents/hermes-integracao.md`

## Migração (jun/2026)

| Caminho antigo | Caminho novo |
|----------------|--------------|
| `data/heroes_deadlock.json` | `game/heroes.json` |
| `data/itens_deadlock.json` | `game/items.json` |
| `data/economia_deadlock.json` | `game/economy.json` |
| `data/ai_knowledge_base.json` | `game/knowledge_base.json` |
| `data/docs/umbrella_api/` | `docs/api/` |
| `data/docs/Builds Index.md` | `docs/builds/index.md` |
| `data/data/github_deadlock_data/` | `reference/deadlock-open-data/` |
