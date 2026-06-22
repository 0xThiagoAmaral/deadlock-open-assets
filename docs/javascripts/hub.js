/* Deadlock Open Assets — browse & stats */
const HubBrowse = (() => {
  const CDN = "https://cdn.jsdelivr.net/gh/0xThiagoAmaral/deadlock-open-assets@main/";

  function dataUrl(file) {
    const local = new URL(`../data/${file}`, window.location.href);
    return local.href;
  }

  async function loadJson(file) {
    try {
      const r = await fetch(dataUrl(file));
      if (r.ok) return r.json();
    } catch (_) {}
    const r2 = await fetch(CDN + "manifests/" + file);
    if (!r2.ok) throw new Error("Failed to load " + file);
    return r2.json();
  }

  function imgUrl(path) {
    if (!path) return null;
    return CDN + path.replace(/^\//, "");
  }

  function renderStats() {
    const el = document.getElementById("hub-stats");
    if (!el) return;
    el.innerHTML = '<div class="hub-loading">Loading stats…</div>';
    loadJson("hub.json")
      .then((hub) => {
        const s = hub.stats || {};
        const items = [
          ["PNG Icons", s.pngs],
          ["Heroes", s.heroes],
          ["Items", s.items],
          ["Upgrades", s.upgrades],
          ["Particles", s.particles_vpcf],
          ["vdata", s.vdata_files],
        ];
        el.innerHTML = items
          .map(
            ([label, val]) =>
              `<div class="hub-stat"><div class="hub-stat-value">${(val || 0).toLocaleString()}</div><div class="hub-stat-label">${label}</div></div>`
          )
          .join("");
      })
      .catch(() => {
        el.innerHTML = '<div class="hub-error">Could not load hub stats.</div>';
      });
  }

  function filterCards(cards, query) {
    const q = query.toLowerCase().trim();
    if (!q) return cards;
    return cards.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.id.toLowerCase().includes(q) ||
        (c.meta && c.meta.toLowerCase().includes(q))
    );
  }

  function bindSearch(inputId, gridId, allCards, render) {
    const input = document.getElementById(inputId);
    if (!input) return;
    input.addEventListener("input", () => {
      render(filterCards(allCards, input.value));
    });
  }

  function renderGrid(gridId, cards, renderCard) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    if (!cards.length) {
      grid.innerHTML = '<div class="hub-loading">No results.</div>';
      return;
    }
    grid.innerHTML = cards.map(renderCard).join("");
  }

  async function initHeroes() {
    const gridId = "hero-grid";
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = '<div class="hub-loading">Loading heroes…</div>';
    try {
      const data = await loadJson("heroes.json");
      const cards = Object.entries(data.heroes || {}).map(([id, h]) => ({
        id,
        name: h.display_name || id,
        meta: h.codename ? `codename: ${h.codename}` : "",
        img: imgUrl((h.images || {}).path_sm),
      }));
      const render = (list) =>
        renderGrid(
          gridId,
          list,
          (c) => `
        <div class="asset-card">
          ${c.img ? `<img src="${c.img}" alt="${c.name}" loading="lazy" onerror="this.style.display='none'">` : '<div style="height:72px"></div>'}
          <div class="asset-card-name">${c.name}</div>
          ${c.meta ? `<div class="asset-card-meta">${c.meta}</div>` : ""}
          <div class="asset-card-id">${c.id}</div>
        </div>`
        );
      render(cards);
      bindSearch("hero-search", gridId, cards, render);
    } catch (e) {
      grid.innerHTML = `<div class="hub-error">${e.message}</div>`;
    }
  }

  async function initItems() {
    const gridId = "item-grid";
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = '<div class="hub-loading">Loading items…</div>';
    try {
      const data = await loadJson("items.json");
      const cards = (data.items || []).map((it) => ({
        id: it.id || it.name,
        name: it.name,
        meta: `T${it.tier} · ${it.cost} · ${it.category}`,
        img: imgUrl(it.image),
      }));
      const render = (list) =>
        renderGrid(
          gridId,
          list,
          (c) => `
        <div class="asset-card">
          ${c.img ? `<img src="${c.img}" alt="${c.name}" loading="lazy" onerror="this.style.display='none'">` : '<div style="height:56px"></div>'}
          <div class="asset-card-name">${c.name}</div>
          <div class="asset-card-meta">${c.meta}</div>
        </div>`
        );
      render(cards);
      bindSearch("item-search", gridId, cards, render);
    } catch (e) {
      grid.innerHTML = `<div class="hub-error">${e.message}</div>`;
    }
  }

  async function initUpgrades() {
    const gridId = "upgrade-grid";
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = '<div class="hub-loading">Loading upgrades…</div>';
    try {
      const data = await loadJson("items.json");
      const catalog = data.upgrades_catalog || {};
      const cards = Object.entries(catalog).map(([key, path]) => ({
        id: key,
        name: key.replace(/_/g, " ").replace(/\.png$/, ""),
        meta: path.split("/").slice(-2, -1)[0] || "",
        img: imgUrl(path),
      }));
      const render = (list) =>
        renderGrid(
          gridId,
          list,
          (c) => `
        <div class="asset-card">
          ${c.img ? `<img src="${c.img}" alt="${c.name}" loading="lazy" onerror="this.style.display='none'">` : '<div style="height:56px"></div>'}
          <div class="asset-card-name">${c.name}</div>
          <div class="asset-card-meta">${c.meta}</div>
        </div>`
        );
      render(cards);
      bindSearch("upgrade-search", gridId, cards, render);
    } catch (e) {
      grid.innerHTML = `<div class="hub-error">${e.message}</div>`;
    }
  }

  document.addEventListener("DOMContentLoaded", renderStats);

  return { initHeroes, initItems, initUpgrades, loadJson, imgUrl };
})();
