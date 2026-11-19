/* Year 8's own script. Two jobs.

   1. Saved answers from before the move. Until 19 November 2026 this site kept
      ticks and typed answers under "y8:<page>", as {c0: true, "f3-0-1": "..."}.
      The shared shell keeps them under its own names. The first time a student
      opens a lesson after the move, anything saved the old way is put back into
      the boxes, and the shell keeps it from there. Each fill-in box carries its
      old name in data-old. The old entries are left where they are.

   2. The assessment run. Two teachers share one set of iPads, so Film
      Soundtrack's lessons run in two orders. The term page lets a student pick
      their class's run, and a lesson page then offers previous and next along
      that run instead of the plain 1 to 25 order. The choice is a per-device
      convenience only: it is never sent anywhere, and it says which order a
      class takes, never where a class is up to.

   Runs after shell.js (both are deferred, in that order), so the shell's
   listeners are in place and an "input" or "change" event is enough for it to
   save what is restored. */
(function () {
  "use strict";

  var site = document.documentElement.getAttribute("data-site") || "site";
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function put(k, v) {
    try { if (v) { localStorage.setItem(k, v); } else { localStorage.removeItem(k); } } catch (e) {}
  }

  /* ------------------------------------------------ 1. saved answers */
  var old = {};
  try { old = JSON.parse(get("y8:" + location.pathname) || "{}") || {}; } catch (e) { old = {}; }
  if (Object.keys(old).length) {
    if (!get(site + ":ticks:" + location.pathname)) {
      Array.prototype.forEach.call(document.querySelectorAll(".sc-list input[type=checkbox]"), function (b, i) {
        if (!old["c" + i]) return;
        b.checked = true;
        b.dispatchEvent(new Event("change"));
      });
    }
    if (!get(site + ":answers:" + location.pathname)) {
      Array.prototype.forEach.call(document.querySelectorAll("textarea.field[data-old]"), function (f) {
        var v = old["f" + f.getAttribute("data-old")];
        if (!v || f.value) return;
        f.value = v;
        f.dispatchEvent(new Event("input"));
      });
    }
  }

  /* ------------------------------------------------- 2. the runs */
  var runs = document.querySelector(".runs");
  var navs = document.querySelectorAll(".runnav");
  if (!runs && !navs.length) return;

  // One choice per topic. The term page names its topic; a lesson page takes it
  // from its own address, the folder above the lesson's.
  var topic = runs ? runs.getAttribute("data-topic")
    : location.pathname.replace(/\/(index\.html)?$/, "").split("/").slice(-2)[0];
  var key = "y8:run:" + topic;

  if (runs) {
    var buttons = runs.querySelectorAll(".runbtn");
    var panels = runs.querySelectorAll(".run");
    var prompt = runs.querySelector(".runprompt");
    var ids = Array.prototype.map.call(panels, function (p) { return p.getAttribute("data-run"); });
    var show = function (id) {
      Array.prototype.forEach.call(panels, function (p) { p.hidden = p.getAttribute("data-run") !== id; });
      Array.prototype.forEach.call(buttons, function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-run") === id));
      });
      prompt.hidden = !!id;
    };
    runs.querySelector(".runswitch").hidden = false;
    // A teacher can link straight to a run (#listening-first) from Canvas.
    var fromHash = location.hash.slice(1);
    var chosen = ids.indexOf(fromHash) >= 0 ? fromHash : get(key);
    if (ids.indexOf(chosen) < 0) chosen = null;
    if (chosen) put(key, chosen);
    show(chosen);
    Array.prototype.forEach.call(buttons, function (b) {
      b.addEventListener("click", function () {
        var id = b.getAttribute("data-run");
        put(key, id);
        show(id);
        try { history.replaceState(null, "", "#" + id); } catch (e) {}
      });
    });
  }

  if (navs.length) {
    // The shell's own previous and next, the plain lesson order.
    var plain = document.querySelector("main > .prevnext");
    // Inside Canvas, Canvas moves students between lessons, so neither order shows.
    var framed = document.documentElement.classList.contains("framed");
    var follow = function (id) {
      if (framed) id = null;
      var any = false;
      Array.prototype.forEach.call(navs, function (n) {
        n.hidden = n.getAttribute("data-run") !== id;
        if (!n.hidden) any = true;
      });
      if (plain) plain.hidden = any;
    };
    follow(get(key));
    Array.prototype.forEach.call(document.querySelectorAll(".run-off"), function (b) {
      b.addEventListener("click", function () { put(key, null); follow(null); });
    });
  }
})();
