# Deadlock Open Assets Hub

<div id="hub-stats" class="hub-stats"></div>

**The #1 open reference** for Deadlock — built for **modders**, **scripters**, **tool devs** and **counterspell** authors. Every asset mapped, named, and one click away.

<div class="hub-cta-row">
  <a class="hub-cta-primary" href="browse/heroes/">Browse Heroes</a>
  <a class="hub-cta-secondary" href="for-developers/">Integration Guide</a>
  <a class="hub-cta-secondary" href="https://github.com/0xThiagoAmaral/deadlock-open-assets" target="_blank">★ Star on GitHub</a>
</div>

## Built for your workflow

<div class="hub-use-grid">
  <div class="hub-use-card">
    <h3>🎯 Lua / Scripts</h3>
    <p>Hero codenames, ability icons, particle indexes — everything for Umbrella-style overlays and automation.</p>
  </div>
  <div class="hub-use-card">
    <h3>🛠 Mods & Panorama</h3>
    <p>412 UI layouts + 420 CSS styles decompiled. Swap assets knowing exact VPK paths.</p>
  </div>
  <div class="hub-use-card">
    <h3>⚡ Counterspell / Dodge</h3>
    <p>9,463 ability particles indexed by hero codename. Map cast VFX → ability in seconds.</p>
  </div>
  <div class="hub-use-card">
    <h3>📊 Build Tools</h3>
    <p>173 items + 209 upgrades with tier, cost, category and icon paths in JSON.</p>
  </div>
</div>

!!! success "What's included"
    - **1,771** PNG icons (heroes, abilities, items, upgrades, UI)
    - **73** heroes with codename maps and ability data
    - **173** shop items + **209** upgrades
    - **76** vdata files (abilities, heroes, modifiers)
    - **9,463** decompiled ability particles
    - **412** Panorama layouts + **420** CSS styles
    - **79,044** sound path index + model index

## One-liner integration

=== "Lua"
    ```lua
    -- Hero icon from repo CDN
    local icon = "https://raw.githubusercontent.com/0xThiagoAmaral/deadlock-open-assets/main/images/deadlock/heroes_circle/haze.png"
    ```

=== "Python"
    ```python
    import json, urllib.request
    heroes = json.loads(urllib.request.urlopen(
        "https://raw.githubusercontent.com/0xThiagoAmaral/deadlock-open-assets/main/manifests/heroes.json"
    ).read())
    ```

=== "JavaScript"
    ```javascript
    const heroes = await fetch(
      "https://raw.githubusercontent.com/0xThiagoAmaral/deadlock-open-assets/main/manifests/heroes.json"
    ).then(r => r.json());
    ```

## Share this repo

Embed in your README:

```markdown
[![Deadlock Open Assets](https://img.shields.io/badge/Deadlock-Open%20Assets-e85d04?style=for-the-badge)](https://0xthiagoamaral.github.io/deadlock-open-assets/)
```

## Quick links

| Resource | Link |
|----------|------|
| Browse heroes + copy paths | [Heroes](browse/heroes.md) |
| Items by category | [Items](browse/items.md) |
| JSON manifests | [API](api/manifests.md) |
| Codename map | [Codenames](api/codenames.md) |
| Full catalog | [Catalog](CATALOG.md) |

!!! warning "Legal"
    Not affiliated with Valve. [Legal disclaimer](legal.md).
