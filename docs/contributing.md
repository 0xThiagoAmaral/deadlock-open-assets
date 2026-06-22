# Contributing

See the full guide on GitHub: [CONTRIBUTING.md](https://github.com/0xThiagoAmaral/deadlock-open-assets/blob/main/CONTRIBUTING.md)

## Quick update workflow

```powershell
python tools/extract_deadlock_assets.py --tier complete
python tools/build_community_hub.py --sync-remote
```

## PR checklist

- [ ] `manifests/hub.json` regenerated
- [ ] `docs/CATALOG.md` updated
- [ ] No API keys or local Steam paths committed
- [ ] Patch date noted in PR description

## Report missing assets

[Open an issue](https://github.com/0xThiagoAmaral/deadlock-open-assets/issues/new) with the game patch version and what's missing.
