/* HSK 1+2 Review site — front-end logic
 *
 * Responsibilities:
 *   1. Persist per-sheet state (last-done date, self-assessment) in localStorage.
 *   2. Wire up the self-assessment buttons on each practice sheet.
 *   3. Render the dashboard sheet list with due/shaky/redo flags and a "next up"
 *      recommendation.
 *
 * localStorage shape:
 *   key: "hsk12review.v1"
 *   value: { "01": { mark: "solid"|"shaky"|"redo", date: "2026-04-18" }, ... }
 */

(function () {
  "use strict";

  const STORAGE_KEY = "hsk12review.v1";
  const DUE_AFTER_DAYS = 2;

  // --- Sheet catalogue (kept in sync with /sheets/*.html and index.html) ----
  const SHEETS = [
    { id: "01", tier: 1, title: "Pronouns · 是 · 吗 · negation",          file: "01-pronouns-shi-ma.html" },
    { id: "02", tier: 1, title: "的 — possessive & nominaliser",            file: "02-possessive-de.html" },
    { id: "03", tier: 1, title: "Question words I: 什么 / 谁 / 哪 / 哪儿",   file: "03-question-words-1.html" },
    { id: "04", tier: 1, title: "Question words II: 几 / 多少 / 怎么 / 怎么样 / 多", file: "04-question-words-2.html" },
    { id: "05", tier: 1, title: "Numbers & measure words",                   file: "05-numbers-measure.html" },
    { id: "06", tier: 1, title: "Time & date expressions",                    file: "06-time-date.html" },
    { id: "07", tier: 1, title: "Location: 在 · 有 (existential)",            file: "07-location.html" },
    { id: "08", tier: 1, title: "Conjunctions: 和 · 因为…所以 · 虽然…但是",     file: "08-conjunctions.html" },
    { id: "09", tier: 1, title: "Modal verbs: 想 / 要 / 会 / 能",              file: "09-modals.html" },
    { id: "10", tier: 1, title: "Degree adverbs: 太 / 最 / 真 / 有点儿 / 还 / 就 / 再", file: "10-degree-adverbs.html" },
    { id: "11", tier: 2, title: "了 part 1: completed action",                file: "11-le-completed.html" },
    { id: "12", tier: 2, title: "了 part 2: change of state & imminent action", file: "12-le-change.html" },
    { id: "13", tier: 2, title: "在…呢 — ongoing action",                     file: "13-zai-ne.html" },
    { id: "14", tier: 2, title: "着 — continuing state",                       file: "14-zhe.html" },
    { id: "15", tier: 2, title: "过 & contrast: 了 vs 过 vs 着",                file: "15-guo-contrast.html" },
    { id: "16", tier: 2, title: "是…的 focus structure",                       file: "16-shi-de.html" },
    { id: "17", tier: 2, title: "Complements: 结果 & 得-state",                file: "17-complements.html" },
    { id: "18", tier: 2, title: "比 comparison · round-up & mixed cumulative", file: "18-bi-roundup.html" },
  ];

  // --- Storage helpers ------------------------------------------------------
  function loadState() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); }
    catch { return {}; }
  }
  function saveState(s) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  }
  function today() {
    const d = new Date();
    return d.toISOString().slice(0, 10);
  }
  function daysSince(dateStr) {
    if (!dateStr) return Infinity;
    const then = new Date(dateStr + "T00:00");
    const now = new Date(today() + "T00:00");
    return Math.round((now - then) / 86400000);
  }
  function prettyDate(dateStr) {
    if (!dateStr) return "never";
    const d = daysSince(dateStr);
    if (d === 0) return "today";
    if (d === 1) return "yesterday";
    if (d < 7) return d + " days ago";
    return dateStr;
  }

  // --- Sheet page: self-assessment -----------------------------------------
  function initSheet() {
    const assess = document.querySelector(".assess");
    if (!assess) return;
    const sheetId = assess.dataset.sheet;
    if (!sheetId) return;

    const state = loadState();
    const rec = state[sheetId] || {};

    // Reflect existing mark.
    assess.querySelectorAll("button[data-mark]").forEach((b) => {
      if (b.dataset.mark === rec.mark) b.classList.add("active");
    });

    // Show last-done.
    const lastEl = assess.querySelector(".last-done");
    if (lastEl) {
      lastEl.textContent = rec.date
        ? `Last reviewed: ${prettyDate(rec.date)}  ·  Marked: ${rec.mark || "—"}`
        : "Not yet reviewed.";
    }

    assess.addEventListener("click", (ev) => {
      const btn = ev.target.closest("button[data-mark]");
      if (!btn) return;
      const mark = btn.dataset.mark;
      const s = loadState();
      s[sheetId] = { mark, date: today() };
      saveState(s);
      assess.querySelectorAll("button[data-mark]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      if (lastEl) lastEl.textContent = `Last reviewed: today  ·  Marked: ${mark}`;
    });
  }

  // --- Dashboard page: sheet list + progress + next-up ----------------------
  function initDashboard() {
    const list = document.getElementById("sheet-list");
    if (!list) return;

    const state = loadState();

    // Build list with tier group headings.
    let lastTier = 0;
    list.innerHTML = "";
    SHEETS.forEach((sheet) => {
      if (sheet.tier !== lastTier) {
        const hdr = document.createElement("li");
        hdr.className = "tier-head";
        hdr.textContent = sheet.tier === 1
          ? "Tier 1 — Foundations (HSK 1 core)"
          : "Tier 2 — Aspect, complements, comparison";
        list.appendChild(hdr);
        lastTier = sheet.tier;
      }
      const rec = state[sheet.id] || {};
      const li = document.createElement("li");
      const due = rec.mark === "redo" ||
                  rec.mark === "shaky" ||
                  !rec.date ||
                  daysSince(rec.date) >= DUE_AFTER_DAYS;
      if (due && rec.mark !== "solid") li.classList.add("due");

      li.innerHTML = `
        <span class="dot ${rec.mark || ""}" title="${rec.mark || "not reviewed"}"></span>
        <span class="idx">${sheet.id}</span>
        <a href="sheets/${sheet.file}">${sheet.title}</a>
        <span class="when">${rec.date ? prettyDate(rec.date) : "—"}</span>
      `;
      list.appendChild(li);
    });

    // Progress ring: % solid.
    const total = SHEETS.length;
    const solid = SHEETS.filter(s => (state[s.id] || {}).mark === "solid").length;
    const pct = Math.round((solid / total) * 100);
    const circ = 2 * Math.PI * 34;
    const ring = document.querySelector(".progress-ring .fg");
    if (ring) {
      ring.setAttribute("stroke-dasharray", circ);
      ring.setAttribute("stroke-dashoffset", circ * (1 - pct / 100));
    }
    const pctText = document.querySelector(".progress-ring text");
    if (pctText) pctText.textContent = pct + "%";
    const counter = document.getElementById("sheet-counter");
    if (counter) counter.textContent = `${solid} of ${total} sheets at solid`;

    // "Next up": prefer redo > shaky > never-done > oldest solid past due.
    const next = pickNext(state);
    const nextEl = document.getElementById("next-up");
    if (nextEl && next) {
      const reason = {
        redo:  "marked redo",
        shaky: "marked shaky",
        new:   "not yet reviewed",
        due:   `last done ${prettyDate((state[next.id] || {}).date)}`,
      }[next.reason];
      nextEl.innerHTML = `
        Next up: <a href="sheets/${next.sheet.file}"><strong>${next.sheet.id} · ${next.sheet.title}</strong></a>
        <span class="muted">— ${reason}</span>
      `;
    } else if (nextEl) {
      nextEl.innerHTML = `<span class="muted">Everything is solid and recently reviewed. Take a break. 🌿</span>`;
    }

    // Shuffle button → random sheet weighted toward due/shaky/redo.
    const shuffleBtn = document.getElementById("shuffle");
    if (shuffleBtn) {
      shuffleBtn.addEventListener("click", () => {
        const pool = SHEETS.filter(s => {
          const r = state[s.id] || {};
          return r.mark !== "solid" || daysSince(r.date) >= DUE_AFTER_DAYS;
        });
        const pick = (pool.length ? pool : SHEETS)[Math.floor(Math.random() * (pool.length || SHEETS.length))];
        window.location.href = "sheets/" + pick.file;
      });
    }

    // Reset button (debug/fresh start).
    const resetBtn = document.getElementById("reset");
    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        if (confirm("Clear all progress? This cannot be undone.")) {
          localStorage.removeItem(STORAGE_KEY);
          location.reload();
        }
      });
    }
  }

  function pickNext(state) {
    // Priority order: redo, shaky, never-done, oldest due.
    for (const sheet of SHEETS) {
      if ((state[sheet.id] || {}).mark === "redo") return { sheet, reason: "redo" };
    }
    for (const sheet of SHEETS) {
      if ((state[sheet.id] || {}).mark === "shaky") return { sheet, reason: "shaky" };
    }
    for (const sheet of SHEETS) {
      if (!(state[sheet.id] || {}).date) return { sheet, reason: "new" };
    }
    let oldest = null;
    for (const sheet of SHEETS) {
      const r = state[sheet.id];
      if (daysSince(r.date) >= DUE_AFTER_DAYS) {
        if (!oldest || daysSince(r.date) > daysSince(state[oldest.id].date)) oldest = sheet;
      }
    }
    return oldest ? { sheet: oldest, reason: "due" } : null;
  }

  // --- Theme toggle ---------------------------------------------------------
  // The head snippet on every page applies the saved theme (key below,
  // falling back to the system preference) before first paint; this wires
  // the ☾/☀ button that flips data-theme on <html> and persists the choice.
  // Deliberately a separate key from STORAGE_KEY so "Reset progress"
  // (which removes STORAGE_KEY) keeps the chosen theme.
  const THEME_KEY = "hsk12review.theme";

  function themeInit() {
    const root = document.documentElement;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "theme-toggle";
    const paint = () => {
      const dark = root.getAttribute("data-theme") === "dark";
      btn.textContent = dark ? "☀" : "☾";
      btn.setAttribute("aria-pressed", dark ? "true" : "false");
      btn.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
    };
    btn.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem(THEME_KEY, next); } catch { /* private mode */ }
      paint();
    });
    paint();
    const nav = document.querySelector(".topnav");
    if (nav) {
      nav.appendChild(btn);
    } else {
      btn.classList.add("theme-toggle--fixed");
      document.body.appendChild(btn);
    }
  }

  // --- Bootstrap ------------------------------------------------------------
  document.addEventListener("DOMContentLoaded", () => {
    themeInit();
    initSheet();
    initDashboard();
  });
})();
