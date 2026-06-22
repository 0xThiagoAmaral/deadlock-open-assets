# Security Policy

## API keys

**`deepseek.txt` was never committed to the public repository.** It is listed in `.gitignore`.

If you had a local `deepseek.txt` on this machine:

1. **Rotate your DeepSeek API key immediately** at [platform.deepseek.com](https://platform.deepseek.com)
2. Never commit `deepseek.txt`, `api_deepseek.txt`, or `tools/extractor_config.json`
3. The public pipeline uses `--no-ai` by default for hub builds

## What is NOT in the public repo

| File / folder | Reason |
|---------------|--------|
| `deepseek.txt` | API secret |
| `deadlock_scripts/` | Private cheat scripts |
| `super_team_umbrella/` | Private agent tooling |
| `LoaderKernel.dll`, `*.exe` | Loader binaries |
| `images/MenuIcons/`, `images/ArcPanel/` | Umbrella cheat UI |
| `assets/docs/` | Internal Umbrella API docs |

## Reporting

If you find secrets or Umbrella-internal files in the public repo, [open a security issue](https://github.com/0xThiagoAmaral/deadlock-open-assets/security/advisories/new) or DM the maintainer.

## Safe usage

- Game assets are Valve property — see [Legal](docs/legal.md)
- Do not embed private API keys in issues, PRs, or manifests
- Use environment variables for local extraction with AI: `DEEPSEEK_API_KEY`
