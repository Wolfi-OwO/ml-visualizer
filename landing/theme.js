// Colour scheme switch: system, light or dark. Runs in <head> so the stored
// choice is on <html> before the first paint; a late script would flash the
// wrong theme on every load for anyone who overrides their system setting.
(function () {
  "use strict";

  var KEY = "ml-theme";
  var root = document.documentElement;
  var PIN = { light: "#f4f5f7", dark: "#12161d" };

  function stored() {
    try {
      var v = localStorage.getItem(KEY);
      return v === "light" || v === "dark" ? v : null;
    } catch (e) {
      return null; // private mode or blocked storage: behave like "system"
    }
  }

  function persist(mode) {
    try {
      if (mode) localStorage.setItem(KEY, mode);
      else localStorage.removeItem(KEY);
    } catch (e) {
      /* the choice then only lasts for this page view */
    }
  }

  // The two theme-color metas are media-scoped for "system". A pinned mode
  // overrides both, otherwise the browser chrome follows the OS, not the page.
  var metas = [];
  var original = [];

  function initMetas() {
    metas = Array.prototype.slice.call(
      document.querySelectorAll('meta[name="theme-color"]')
    );
    original = metas.map(function (m) {
      return { content: m.getAttribute("content"), media: m.getAttribute("media") };
    });
  }

  function syncMetas(mode) {
    metas.forEach(function (m, i) {
      if (mode) {
        m.setAttribute("content", PIN[mode]);
        m.removeAttribute("media");
      } else {
        m.setAttribute("content", original[i].content);
        if (original[i].media) m.setAttribute("media", original[i].media);
      }
    });
  }

  function apply(mode) {
    if (mode) root.setAttribute("data-theme", mode);
    else root.removeAttribute("data-theme");
    syncMetas(mode);
    document.dispatchEvent(new CustomEvent("themechange"));
  }

  var current = stored();
  if (current) root.setAttribute("data-theme", current);

  var ICONS = {
    system:
      '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    light:
      '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    dark: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
  };
  var LABELS = { system: "System", light: "Hell", dark: "Dunkel" };

  function build() {
    var nav = document.querySelector(".topbar nav");
    if (!nav) return;
    initMetas();
    syncMetas(current);

    var group = document.createElement("div");
    group.className = "theme-switch";
    group.setAttribute("role", "group");
    group.setAttribute("aria-label", "Farbschema");

    var buttons = {};
    ["system", "light", "dark"].forEach(function (mode) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", LABELS[mode]);
      b.title = LABELS[mode];
      b.innerHTML =
        '<svg viewBox="0 0 24 24" aria-hidden="true">' + ICONS[mode] + "</svg>";
      b.addEventListener("click", function () {
        current = mode === "system" ? null : mode;
        persist(current);
        apply(current);
        mark();
      });
      buttons[mode] = b;
      group.appendChild(b);
    });

    function mark() {
      var active = current || "system";
      Object.keys(buttons).forEach(function (m) {
        buttons[m].setAttribute("aria-pressed", m === active ? "true" : "false");
      });
    }

    mark();
    nav.insertBefore(group, nav.querySelector(".btn"));

    // In "system" mode an OS switch changes the colours without any click here,
    // and the canvas has to hear about it too.
    if (window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: dark)");
      var onChange = function () {
        if (!current) document.dispatchEvent(new CustomEvent("themechange"));
      };
      if (mq.addEventListener) mq.addEventListener("change", onChange);
      else if (mq.addListener) mq.addListener(onChange);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
