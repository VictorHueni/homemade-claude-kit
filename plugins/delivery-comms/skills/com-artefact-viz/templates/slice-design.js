
/* ---- Slice design sheet: tabs, diagram zoom, table labels for the phone layout, copy ---- */
(function () {
  "use strict";
  var bar = document.querySelector(".tabs[role='tablist']");
  if (!bar) { return; }
  var tabs = Array.prototype.slice.call(bar.querySelectorAll(".tab"));
  var names = tabs.map(function (t) { return t.dataset.tab; });
  function show(name, focus) {
    if (names.indexOf(name) < 0) { name = bar.dataset.default; }
    tabs.forEach(function (t) {
      var on = t.dataset.tab === name;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      document.getElementById("panel-" + t.dataset.tab).hidden = !on;
      if (on && focus) { t.focus(); }
    });
  }
  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () {
      show(t.dataset.tab);
      try { history.replaceState(null, "", "#" + t.dataset.tab); } catch (e) { location.hash = t.dataset.tab; }
    });
    t.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") { return; }
      show(names[(i + (e.key === "ArrowRight" ? 1 : names.length - 1)) % names.length], true);
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll(".zoom"), function (z) {
    z.addEventListener("click", function () {
      z.setAttribute("aria-pressed", z.getAttribute("aria-pressed") === "true" ? "false" : "true");
    });
  });
  // The phone layout prints each cell under the name of its column: copy the header onto the cell.
  Array.prototype.forEach.call(document.querySelectorAll(".viz-content table"), function (table) {
    var heads = Array.prototype.map.call(table.querySelectorAll("thead th"), function (th) { return th.textContent; });
    Array.prototype.forEach.call(table.querySelectorAll("tbody tr"), function (row) {
      var column = 0;
      Array.prototype.forEach.call(row.children, function (cell) {
        var span = cell.colSpan || 1;
        if (span === 1 && heads[column]) { cell.setAttribute("data-label", heads[column]); }
        column += span;
      });
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll(".copy"), function (button) {
    var label = button.textContent;
    button.addEventListener("click", function () {
      var source = document.getElementById(button.dataset.copy);
      function select() {
        var range = document.createRange();
        range.selectNodeContents(source);
        var selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = "Selected, copy it from here";
      }
      try {
        navigator.clipboard.writeText(source.textContent).then(function () { button.textContent = "Copied"; }, select);
      } catch (e) { select(); }
      setTimeout(function () { button.textContent = label; }, 2500);
    });
  });
  function fromHash() { show((location.hash || "").replace("#", "") || bar.dataset.default); }
  window.addEventListener("hashchange", fromHash);
  fromHash();
})();
