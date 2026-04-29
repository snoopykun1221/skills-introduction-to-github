/**
 * Japan Travel Guide — main app logic.
 * - Build interactive prefecture map (CSS grid)
 * - On tap: open modal with zoomed prefecture + category tabs
 * - Track affiliate clicks (KPI) via window.gtag if loaded; fallback console
 */
(() => {
  const { prefectures, REGION_LABEL } = window.JAPAN_DATA;
  const REGION_COLOR = {
    hokkaido: "#4cc9f0",
    tohoku:   "#4895ef",
    kanto:    "#4361ee",
    chubu:    "#7209b7",
    kansai:   "#e63946",
    chugoku:  "#f77f00",
    shikoku:  "#06d6a0",
    kyushu:   "#ffb703"
  };
  const CATEGORIES = [
    { id: "food",       label: "🍜 料理屋" },
    { id: "spot",       label: "🗾 行先" },
    { id: "shrine",     label: "⛩ 神社" },
    { id: "experience", label: "🎎 体験" }
  ];

  const byId = (id) => document.getElementById(id);
  const mapGrid    = byId("mapGrid");
  const regionCards= byId("regionCards");
  const modal      = byId("prefectureModal");
  const modalTitle = byId("modalTitle");
  const modalSub   = byId("modalSubtitle");
  const modalRegion= byId("modalRegion");
  const modalCap   = byId("modalCapital");
  const modalTags  = byId("modalTags");
  const zoomPref   = byId("zoomPref");
  const catTabs    = byId("catTabs");
  const catList    = byId("catList");
  const statPlaces = byId("stat-places");
  const yearEl     = byId("year");

  let activePref = null;
  let activeCategory = "food";

  // ---------- KPI: affiliate click tracking ----------
  function trackAffiliateClick(prefId, category, item) {
    const payload = {
      pref:     prefId,
      category: category,
      item_id:  item.id,
      item:     item.name,
      source:   item.source,
      url:      item.url
    };
    // Google Analytics gtag が読み込まれていれば送信
    if (typeof window.gtag === "function") {
      window.gtag("event", "affiliate_click", payload);
    }
    // dataLayer (GTM) があれば送信
    if (Array.isArray(window.dataLayer)) {
      window.dataLayer.push({ event: "affiliate_click", ...payload });
    }
    // 開発時の確認用
    console.log("[KPI] affiliate_click", payload);
  }

  // ---------- Build map ----------
  function buildMap() {
    const frag = document.createDocumentFragment();
    prefectures.forEach(p => {
      const el = document.createElement("button");
      el.type = "button";
      el.className = "pref" + (p.large ? " large" : "");
      el.dataset.region = p.region;
      el.dataset.id = p.id;
      el.style.gridColumn = p.large
        ? `${p.gridPos.col} / span ${p.gridPos.span}`
        : `${p.gridPos.col}`;
      el.style.gridRow = p.large
        ? `${p.gridPos.row} / span ${p.gridPos.span}`
        : `${p.gridPos.row}`;
      el.textContent = p.name;
      el.setAttribute("aria-label", `${p.name} (${p.regionLabel})`);
      el.addEventListener("click", () => openPrefecture(p.id));
      frag.appendChild(el);
    });
    mapGrid.appendChild(frag);
  }

  // ---------- Build region card list ----------
  function buildRegionCards() {
    const grouped = {};
    prefectures.forEach(p => {
      grouped[p.region] = grouped[p.region] || [];
      grouped[p.region].push(p);
    });
    const order = ["hokkaido","tohoku","kanto","chubu","kansai","chugoku","shikoku","kyushu"];
    const frag = document.createDocumentFragment();
    order.forEach(r => {
      const card = document.createElement("div");
      card.className = "region-card";
      card.style.borderTop = `3px solid ${REGION_COLOR[r]}`;
      const list = grouped[r] || [];
      card.innerHTML = `
        <h4>${REGION_LABEL[r]}</h4>
        <p class="region-meta">${list.length}都道府県</p>
        <ul></ul>
      `;
      const ul = card.querySelector("ul");
      list.forEach(p => {
        const li = document.createElement("li");
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = p.name;
        btn.addEventListener("click", () => openPrefecture(p.id));
        li.appendChild(btn);
        ul.appendChild(li);
      });
      frag.appendChild(card);
    });
    regionCards.appendChild(frag);
  }

  // ---------- Region filter ----------
  function bindRegionFilter() {
    const filters = document.getElementById("regionFilters");
    filters.addEventListener("click", (e) => {
      const btn = e.target.closest(".region-chip");
      if (!btn) return;
      filters.querySelectorAll(".region-chip").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const region = btn.dataset.region;
      mapGrid.querySelectorAll(".pref").forEach(el => {
        if (region === "all" || el.dataset.region === region) {
          el.classList.remove("dim");
        } else {
          el.classList.add("dim");
        }
      });
    });
  }

  // ---------- Modal ----------
  function openPrefecture(prefId) {
    const p = prefectures.find(x => x.id === prefId);
    if (!p) return;
    activePref = p;
    activeCategory = "food";

    modalTitle.textContent = p.name;
    modalSub.textContent = `${p.regionLabel} / ${p.kanji}`;
    modalRegion.textContent = p.regionLabel;
    modalCap.textContent = p.capital;
    modalTags.textContent = p.tags;

    // Zoomed prefecture badge with region color
    zoomPref.style.background =
      `linear-gradient(135deg, ${REGION_COLOR[p.region]} 0%, rgba(0,0,0,0.55) 100%)`;
    zoomPref.textContent = p.kanji;

    // Reset tabs
    catTabs.querySelectorAll(".cat-tab").forEach(t => {
      t.classList.toggle("active", t.dataset.cat === "food");
    });

    renderCategory();
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    if (typeof window.gtag === "function") {
      window.gtag("event", "prefecture_open", { pref: p.id, name: p.name });
    }
  }

  function closeModal() {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    activePref = null;
  }

  function renderCategory() {
    if (!activePref) return;
    const items = (activePref.items[activeCategory] || []);
    catList.innerHTML = "";
    if (items.length === 0) {
      catList.innerHTML = `<p class="cat-empty">このカテゴリのスポットは準備中です。<br>今後追加予定！</p>`;
      return;
    }
    items.forEach(item => {
      const card = document.createElement("article");
      card.className = "item-card";
      card.innerHTML = `
        <div class="item-thumb" aria-hidden="true">${item.emoji || "📍"}</div>
        <div class="item-meta">
          <h4>${escapeHtml(item.name)}</h4>
          ${item.tag ? `<span class="item-tag">${escapeHtml(item.tag)}</span>` : ""}
          <p>${escapeHtml(item.desc || "")}</p>
          <span class="source">via ${escapeHtml(item.source || "")}</span>
        </div>
        <a class="affiliate-btn" href="${item.url}" target="_blank" rel="sponsored noopener">予約・詳細 →</a>
      `;
      // Track click
      card.querySelector(".affiliate-btn").addEventListener("click", () => {
        trackAffiliateClick(activePref.id, activeCategory, item);
      });
      catList.appendChild(card);
    });
  }

  function bindCategoryTabs() {
    catTabs.addEventListener("click", (e) => {
      const tab = e.target.closest(".cat-tab");
      if (!tab) return;
      catTabs.querySelectorAll(".cat-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      activeCategory = tab.dataset.cat;
      renderCategory();
    });
  }

  function bindModalClose() {
    modal.addEventListener("click", (e) => {
      if (e.target.matches("[data-close]")) closeModal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("open")) closeModal();
    });
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (c) =>
      ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c])
    );
  }

  // ---------- Boot ----------
  function init() {
    yearEl.textContent = new Date().getFullYear();
    const totalItems = prefectures.reduce((sum, p) => {
      return sum + Object.values(p.items).reduce((s, arr) => s + arr.length, 0);
    }, 0);
    statPlaces.textContent = `${totalItems}+`;

    buildMap();
    buildRegionCards();
    bindRegionFilter();
    bindCategoryTabs();
    bindModalClose();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
