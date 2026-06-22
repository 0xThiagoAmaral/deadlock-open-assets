# Browse Heroes

Search and explore all mapped heroes with icons, abilities, and VPK codenames.

<input type="search" id="hero-search" class="hub-search" placeholder="Search heroes…" autocomplete="off">
<div id="hero-grid" class="asset-grid"></div>

<script>
document.addEventListener("DOMContentLoaded", () => {
  HubBrowse.initHeroes();
});
</script>
