/* Portfolio artistique : menu mobile, visionneuse, protection légère des images. */
(function () {
  "use strict";

  /* ---- Menu mobile ---- */
  var sidebar = document.querySelector(".sidebar");
  var toggle = document.querySelector(".sidebar__toggle");
  if (sidebar && toggle) {
    toggle.addEventListener("click", function () {
      var open = sidebar.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.textContent = open ? "fermer" : "menu";
    });
  }

  /* ---- Protection légère (dissuasive seulement) ---- */
  if (document.body.hasAttribute("data-protect")) {
    document.addEventListener("contextmenu", function (e) {
      if (e.target.tagName === "IMG") e.preventDefault();
    });
    document.addEventListener("dragstart", function (e) {
      if (e.target.tagName === "IMG") e.preventDefault();
    });
  }

  /* ---- Visionneuse ---- */
  var box = document.getElementById("lightbox");
  if (!box) return;

  var img = box.querySelector(".lightbox__img");
  var caption = box.querySelector(".lightbox__caption");
  var count = box.querySelector(".lightbox__count");
  var btnClose = box.querySelector(".lightbox__close");
  var btnPrev = box.querySelector(".lightbox__nav--prev");
  var btnNext = box.querySelector(".lightbox__nav--next");

  var items = [];      // [{href, caption, alt}]
  var index = 0;
  var opener = null;

  function collect(link) {
    var gallery = link.closest("[data-gallery]");
    var links = gallery ? gallery.querySelectorAll("a.work__link") : [link];
    return Array.prototype.map.call(links, function (a) {
      var i = a.querySelector("img");
      return { href: a.getAttribute("href"), caption: a.getAttribute("data-caption") || "", alt: i ? i.alt : "", el: a };
    });
  }

  function show(i) {
    index = (i + items.length) % items.length;
    var it = items[index];
    img.classList.add("is-loading");
    img.onload = function () { img.classList.remove("is-loading"); };
    img.src = it.href;
    img.alt = it.alt;
    caption.innerHTML = it.caption;           // contenu rédigé par l'autrice dans le front matter
    caption.hidden = !it.caption;
    count.textContent = (index + 1) + " / " + items.length;
    if (items.length > 1) {                    // précharge la suivante
      var pre = new Image();
      pre.src = items[(index + 1) % items.length].href;
    }
  }

  function open(link) {
    items = collect(link);
    opener = link;
    box.classList.toggle("is-single", items.length < 2);
    box.hidden = false;
    document.body.classList.add("lightbox-open");
    var start = 0;
    items.forEach(function (it, k) { if (it.el === link) start = k; });
    show(start);
    btnClose.focus();
  }

  function close() {
    box.hidden = true;
    document.body.classList.remove("lightbox-open");
    img.removeAttribute("src");
    if (opener) opener.focus();
  }

  document.addEventListener("click", function (e) {
    var link = e.target.closest("a.work__link, a.entry__media");
    if (!link || e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    open(link);
  });

  btnClose.addEventListener("click", close);
  btnPrev.addEventListener("click", function () { show(index - 1); });
  btnNext.addEventListener("click", function () { show(index + 1); });

  // clic sur le fond (hors image et boutons) : fermer
  box.addEventListener("click", function (e) {
    if (e.target === box || e.target.classList.contains("lightbox__stage")) close();
  });

  document.addEventListener("keydown", function (e) {
    if (box.hidden) return;
    if (e.key === "Escape") close();
    else if (e.key === "ArrowLeft" && items.length > 1) show(index - 1);
    else if (e.key === "ArrowRight" && items.length > 1) show(index + 1);
    else if (e.key === "Tab") {                // garde le focus dans la visionneuse
      var f = Array.prototype.filter.call(box.querySelectorAll("button"), function (b) {
        return getComputedStyle(b).visibility !== "hidden";
      });
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  // balayage sur écran tactile
  var x0 = null;
  box.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  box.addEventListener("touchend", function (e) {
    if (x0 === null || items.length < 2) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
    x0 = null;
  });
})();
