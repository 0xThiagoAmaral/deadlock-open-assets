# Deadlock Open Assets — browse, copy & integrate

const HubBrowse = (() => {
  const REPO = "0xThiagoAmaral/deadlock-open-assets";
  const BRANCH = "main";
  const MEDIA = `https://media.githubusercontent.com/media/${REPO}/${BRANCH}/`;
  const RAW = `https://raw.githubusercontent.com/${REPO}/${BRANCH}/`;
  const SITE = "https://0xthiagoamaral.github.io/deadlock-open-assets/";
  const GITHUB = `https://github.com/${REPO}`;

  function dataUrl(file) {
    return new URL(`../data/${file}`, window.location.href).href;
  }

  async function loadJson(file) {
    try {
      const r = await fetch(dataUrl(file));
      if (r.ok) return r.json();
    } catch (_) {}
    const r2 = await fetch(RAW + "manifests/" + file);
    if (!r2.ok) throw new Error("Failed to load " + file);
    return r2.json();
  }

  function imgUrl(path) {
    if (!path) return null;
    return MEDIA + path.replace(/^\//, "");
  }

  function rawUrl(path) {
    if (!path) return null;
    return RAW + path.replace(/^\//, "");
  }

  function rawJsonUrl(file) {
    return RAW + "manifests/" + file;
  }

  function copyText(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
      if (!btn) return;
      const orig = btn.textContent;
      btn.textContent = "Copied!";
      btn.classList.add("hub-copied");
      setTimeout(() => {
        btn.textContent = orig;
        btn.classList.remove("hub-copied");
      }, 1400);
    });
  }

  function actionBar(items) {
    return `<div class="hub-actions">${items.join("")}</div>`;
  }

  function btn(label, dataCopy, cls = "") {
    return `<button type="button" class="hub-btn ${cls}" data-copy="${encodeURIComponent(dataCopy)}">${label}</button>`;
  }

  function bindCopyButtons(root) {
    (root || document).querySelectorAll("[data-copy]").forEach((el) => {
      el.addEventListener("click", () => copyText(decodeURIComponent(el.dataset.copy), el));
    });
  }

  function injectShareBar() {
    if (document.querySelector(".hub-share-bar")) return;
    const bar = document.createElement("div");
    bar.className = "hub-share-bar";
    bar.innerHTML = `
      <span class="hub-share-label">Share</span>
      ${btn("Copy page link", location.href, "hub-btn-ghost")}
      ${btn("Copy repo", GITHUB, "hub-btn-ghost")}
      <a class="hub-btn hub-btn-star" href="${GITHUB}" target="_blank" rel="noopener">★ Star</a>
      <a class="hub-btn hub-btn-ghost" href="https://twitter.com/intent/tweet?text=${encodeURIComponent("Deadlock Open Assets — 1,700+ icons, heroes, particles & JSON manifests for modders")}&url=${encodeURIComponent(location.href)}" target="_blank" rel="noopener">Tweet</a>
    `;
    const main = document.querySelector(".md-content");
    if (main) main.prepend(bar);
    bindCopyButtons(bar);
  }

  function injectFilterChips(containerId, chips, onFilter) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = chips
      .map(
        (c, i) =>
          `<button type="button" class="hub-chip${i === 0 ? " active" : ""}" data-filter="${c.value}">${c.label}</button>`
      )
      .join("");
    el.querySelectorAll(".hub-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        el.querySelectorAll(".hub-chip").forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        onFilter(chip.dataset.filter);
      });
    });
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
        el.innerHTML =
          items
            .map(
              ([label, val]) =>
                `<div class="hub-stat"><div class="hub-stat-value">${(val || 0).toLocaleString()}</div><div class="hub-stat-label">${label}</div></div>`
            )
            .join("") +
          actionBar([
            btn("Copy manifests URL", rawJsonUrl("hub.json")),
            `<a class="hub-btn hub-btn-accent" href="${GITHUB}" target="_blank" rel="noopener">★ Star on GitHub</a>`,
          ]);
        bindCopyButtons(el);
      })
      .catch(() => {
        el.innerHTML = '<div class="hub-error">Could not load hub stats.</div>';
      });
  }

  function filterCards(cards, query, extraFilter) {
    let list = cards;
    if (extraFilter && extraFilter !== "all") {
      list = list.filter((c) => c.category === extraFilter || c.filterTag === extraFilter);
    }
    const q = query.toLowerCase().trim();
    if (!q) return list;
    return list.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.id.toLowerCase().includes(q) ||
        (c.meta && c.meta.toLowerCase().includes(q)) ||
        (c.codename && c.codename.toLowerCase().includes(q))
    );
  }

  function bindSearch(inputId, getCards, render) {
    const input = document.getElementById(inputId);
    if (!input) return;
    let extra = "all";
    input.addEventListener("input", () => render(filterCards(getCards(), input.value, extra)));
    return {
      setFilter(f) {
        extra = f;
        render(filterCards(getCards(), input.value, extra));
      },
    };
  }

  function heroCard(c) {
    const path = c.imgPath || "";
    const img = c.img ? `<img src="${c.img}" alt="${c.name}" loading="lazy" onerror="this.classList.add('hub-img-fail')">` : '<div class="hub-img-placeholder"></div>';
    return `
      <div class="asset-card asset-card-interactive" tabindex="0">
        ${img}
        <div class="asset-card-name">${c.name}</div>
        ${c.codename ? `<div class="asset-card-meta">codename: <code>${c.codename}</code></div>` : ""}
        <div class="asset-card-id">${c.id}</div>
        ${actionBar([
          btn("PNG", path ? imgUrl(path) : ""),
          btn("Raw", path ? rawUrl(path) : ""),
          btn("Path", path),
          btn("VPK", c.codename ? `panorama/images/heroes/${c.codename}_sm_psd.vtex_c` : ""),
        ])}
      </div>`;
  }

  function compactCard(c) {
    const img = c.img
      ? `<img src="${c.img}" alt="${c.name}" loading="lazy" onerror="this.classList.add('hub-img-fail')">`
      : '<div class="hub-img-placeholder hub-img-placeholder-sm"></div>';
    const path = c.imgPath || "";
    return `
      <div class="asset-card asset-card-interactive asset-card-compact">
        ${img}
        <div class="asset-card-name">${c.name}</div>
        <div class="asset-card-meta">${c.meta || ""}</div>
        ${path ? actionBar([btn("Copy", path), btn("URL", imgUrl(path))]) : ""}
      </div>`;
  }

  function renderGrid(gridId, cards, renderCard) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    if (!cards.length) {
      grid.innerHTML = '<div class="hub-loading">No results.</div>';
      return;
    }
    grid.innerHTML = cards.map(renderCard).join("");
    bindCopyButtons(grid);
  }

  async function initHeroes() {
    const gridId = "hero-grid";
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = '<div class="hub-loading">Loading heroes…</div>';
    injectShareBar();
    try {
      const [data, codes] = await Promise.all([loadJson("heroes.json"), loadJson("codenames.json")]);
      const codenameKeys = new Set(Object.keys(codes.map || {}));

      let cards = Object.entries(data.heroes || {})
        .filter(([id]) => {
          const mapped = (codes.map || {})[id];
          if (mapped && mapped !== id && data.heroes[mapped]) return false;
          return true;
        })
        .map(([id, h]) => {
          const path = (h.images || {}).path_sm || null;
          const codename = (codes.reverse || {})[id] || null;
          return {
            id,
            name: h.display_name || id,
            codename,
            imgPath: path,
            img: imgUrl(path),
            hasIcon: !!path,
          };
        })
        .filter((c) => c.hasIcon)
        .sort((a, b) => a.name.localeCompare(b.name));

      const render = (list) => renderGrid(gridId, list, heroCard);
      render(cards);
      const search = document.getElementById("hero-search");
      if (search) {
        search.addEventListener("input", () => render(filterCards(cards, search.value)));
      }
      const count = document.getElementById("hero-count");
      if (count) count.textContent = `${cards.filter((c) => c.hasIcon).length} with icons · ${cards.length} total`;
    } catch (e) {
      grid.innerHTML = `<div class="hub-error">${e.message}</div>`;
    }
  }

  async function initItems() {
    const gridId = "item-grid";
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = '<div class="hub-loading">Loading items…</div>';
    injectShareBar();
    try {
      const [data, images] = await Promise.all([loadJson("items.json"), loadJson("images.json")]);
      const itemImgs = images.items || {};

      let cards = (data.items || []).map((it) => {
        let path = it.image;
        if (!path) {
          const match = Object.entries(itemImgs).find(([k]) => k.includes(it.id) || k.replace(/\.png$/, "") === it.id);
          path = match ? match[1] : null;
        }
        return {
          id: it.id || it.name,
          name: it.name,
          category: it.category,
          filterTag: it.category,
          meta: `T${it.tier} · ${it.cost} souls · ${it.category}`,
          imgPath: path,
          img: imgUrl(path),
        };
      });

      const categories = ["all", ...new Set(cards.map((c) => c.category).filter(Boolean))];
      injectFilterChips("item-filters", categories.map((c) => ({ label: c, value: c })), (f) => {
        const q = document.getElementById("item-search")?.value || "";
        renderGrid(gridId, filterCards(cards, q, f), compactCard);
      });

      const render = (list) => renderGrid(gridId, list, compactCard);
      render(cards);
      const search = document.getElementById("item-search");
      if (search) {
        search.addEventListener("input", () => {
          const active = document.querySelector("#item-filters .hub-chip.active");
          render(filterCards(cards, search.value, active?.dataset.filter || "all"));
        });
      }
    } catch (e) {
      grid.innerHTML = `<div class="hub-error">${e.message}</div>`;
    }
  }

  async function initUpgrades() {
    const gridId = "upgrade-grid";
    const grid = document.getElementById(gridId);
    if (!grid) return;
    grid.innerHTML = '<div class="hub-loading">Loading upgrades…</div>';
    injectShareBar();
    try {
      const data = await loadJson("items.json");
      const catalog = data.upgrades_catalog || {};
      let cards = Object.entries(catalog).map(([key, path]) => ({
        id: key,
        name: key.replace(/_/g, " ").replace(/\.png$/, ""),
        filterTag: path.split("/").slice(-2, -1)[0] || "other",
        meta: path.split("/").slice(-2, -1)[0] || "",
        imgPath: path,
        img: imgUrl(path),
      }));

      const types = ["all", ...new Set(cards.map((c) => c.filterTag))];
      injectFilterChips("upgrade-filters", types.map((t) => ({ label: t.replace("mods_", ""), value: t })), (f) => {
        const q = document.getElementById("upgrade-search")?.value || "";
        renderGrid(gridId, filterCards(cards, q, f), compactCard);
      });

      const render = (list) => renderGrid(gridId, list, compactCard);
      render(cards);
      const search = document.getElementById("upgrade-search");
      if (search) {
        search.addEventListener("input", () => {
          const active = document.querySelector("#upgrade-filters .hub-chip.active");
          render(filterCards(cards, search.value, active?.dataset.filter || "all"));
        });
      }
    } catch (e) {
      grid.innerHTML = `<div class="hub-error">${e.message}</div>`;
    }
  }

  document.addEventListener("DOMContentLoaded", renderStats);

  return { initHeroes, initItems, initUpgrades };
})();
