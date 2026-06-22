# Browse Heroes

Every hero with **icon**, **codename**, and **copy-ready paths** for Lua scripts and mods.

<div class="hub-share-bar" style="margin-bottom:1rem">
  <span class="hub-share-label">Quick</span>
  <a class="hub-btn hub-btn-accent" href="../api/codenames/">Codename map</a>
  <a class="hub-btn" href="../for-developers/">Script integration</a>
</div>

<p class="hub-count" id="hero-count"></p>

<input type="search" id="hero-search" class="hub-search" placeholder="Search by name, id or codename…" autocomplete="off">
<div id="hero-grid" class="asset-grid"></div>

!!! tip "Copy buttons on each card"
    - **PNG** — direct image URL (works in `Render.LoadImage`)
    - **Path** — repo-relative path for manifests
    - **VPK** — internal panorama path for in-game `Menu:Icon()`

<script>
document.addEventListener("DOMContentLoaded", () => HubBrowse.initHeroes());
</script>
