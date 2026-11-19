/* Copied from music-shell cff34be41f, body 8bb5f29212. Do not edit here: edit Sites/music-shell and run sync.py. */
/* The shared shell's only script. Every page works without it: a recording's
   name is a link to the recording, a cue time is a link to that second, a tick
   lasts the visit. This adds five things.

   1. Players unfold in place. Pressing a recording's name or picture swaps the
      picture for the player, one player on the page at a time (two tracks
      playing over each other is the whole room's problem). Nothing is asked of
      YouTube's player until someone presses play.
   2. Cue times seek. A cue remounts its work's player at that second with
      ?start=, which needs no player API and so no third-party script.
   3. Ticks and typed answers are kept on this device, per site and per page.
   4. Dated checkpoints (a depth study's milestones) work out done and next up
      from today's date, not the build date.
   5. Inside a Canvas frame, links to other pages of the site go inert, because
      the Canvas app hands any in-frame link to another page out to Safari.

   No framework, no build step, no dependency: nobody is going to be in a
   session when this breaks. Year 9's player script, generalised. */
(function () {
  "use strict";

  var HOST = "https://www.youtube-nocookie.com/embed/";
  var root = document.documentElement;
  var site = root.getAttribute("data-site") || "site";

  /* ------------------------------------------------------------ players */

  function close(fig) {
    var frame = fig.querySelector("iframe");
    if (!frame) return;
    frame.parentNode.removeChild(frame);
    var img = fig.querySelector(".clip-frame img");
    if (img) img.hidden = false;
    var play = fig.querySelector(".clip-play");
    if (play) play.hidden = false;
    var name = fig.querySelector(".clip-name");
    if (name) name.setAttribute("aria-expanded", "false");
    Array.prototype.forEach.call(document.querySelectorAll(".cue[aria-current]"), function (c) {
      if (c.closest(".gw") && c.closest(".gw").contains(fig)) c.removeAttribute("aria-current");
    });
  }

  function mount(fig, at) {
    var id = fig.getAttribute("data-yt");
    if (!id) return;
    Array.prototype.forEach.call(document.querySelectorAll(".clip[data-yt]"), function (f) {
      if (f !== fig) close(f);
    });
    var box = fig.querySelector(".clip-frame");
    var old = box.querySelector("iframe");
    if (old) old.parentNode.removeChild(old);
    var frame = document.createElement("iframe");
    frame.src = HOST + encodeURIComponent(id) + "?autoplay=1&rel=0" + (at ? "&start=" + at : "");
    frame.title = (fig.querySelector(".clip-name") || {}).textContent || "Recording";
    frame.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    frame.setAttribute("allowfullscreen", "");
    var img = box.querySelector("img");
    if (img) img.hidden = true;
    var play = box.querySelector(".clip-play");
    if (play) play.hidden = true;
    box.appendChild(frame);
    var name = fig.querySelector(".clip-name");
    if (name) name.setAttribute("aria-expanded", "true");
  }

  document.addEventListener("click", function (ev) {
    var t = ev.target.closest ? ev.target.closest(".clip-name, .clip-play, .cue") : null;
    if (!t || ev.metaKey || ev.ctrlKey || ev.shiftKey) return;
    if (t.classList.contains("cue")) {
      var fig = t.closest(".gw") && t.closest(".gw").querySelector(".clip[data-yt]");
      if (!fig) return;
      ev.preventDefault();
      mount(fig, parseInt(t.getAttribute("data-at"), 10) || 0);
      Array.prototype.forEach.call(t.closest(".gw").querySelectorAll(".cue"), function (c) {
        if (c === t) c.setAttribute("aria-current", "true"); else c.removeAttribute("aria-current");
      });
      if (fig.getBoundingClientRect().top < 0) fig.scrollIntoView({ block: "start" });
      return;
    }
    var f = t.closest(".clip[data-yt]");
    if (!f) return;
    ev.preventDefault();
    if (f.querySelector("iframe")) close(f); else mount(f, 0);
  });

  Array.prototype.forEach.call(document.querySelectorAll(".clip[data-yt] .clip-name"), function (a) {
    a.setAttribute("aria-expanded", "false");
    a.setAttribute("role", "button");
  });

  /* ------------------------------------------------- kept on this device */

  function keep(selector, kind, read, write, event) {
    var els = document.querySelectorAll(selector);
    if (!els.length) return;
    var key = site + ":" + kind + ":" + location.pathname;
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(key) || "{}"); } catch (err) { saved = {}; }
    var timer;
    Array.prototype.forEach.call(els, function (el, i) {
      if (saved[i] !== undefined) write(el, saved[i]);
      el.addEventListener(event, function () {
        saved[i] = read(el);
        // Typing fires per keystroke, so the write is coalesced.
        clearTimeout(timer);
        timer = setTimeout(function () {
          try { localStorage.setItem(key, JSON.stringify(saved)); } catch (err) { /* private mode: lasts the visit */ }
        }, 250);
      });
    });
  }

  keep(".sc-list input[type=checkbox]", "ticks",
       function (el) { return el.checked; }, function (el, v) { el.checked = !!v; }, "change");
  keep("textarea.field", "answers",
       function (el) { return el.value; }, function (el, v) { el.value = v; }, "input");

  /* --------------------------------------------- dated checkpoints */
  /* A schedule row with data-date is a checkpoint everyone shares. Its state
     was baked in at build time, and the page can sit for weeks between builds,
     so work it out again from today's date: past ones are done, and the first
     one still ahead is next up. */

  var dated = document.querySelectorAll(".row[data-date]");
  if (dated.length) {
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    var words = { done: "Done", next: "Next up", at: "Assessment" };
    var found = false;
    Array.prototype.forEach.call(dated, function (li) {
      var due = new Date(li.getAttribute("data-date") + "T00:00:00");
      var st = due < today ? "done" : (!found ? "next" : "");
      if (st === "next") found = true;
      li.classList.toggle("row-done", st === "done");
      li.classList.toggle("row-next", st === "next");
      var want = st || (li.classList.contains("row-at") ? "at" : "");
      var pill = li.querySelector(".pill");
      if (!want) { if (pill) pill.parentNode.removeChild(pill); return; }
      if (!pill) { pill = document.createElement("span"); li.appendChild(pill); }
      pill.className = "pill pill-" + want;
      pill.textContent = words[want];
    });
  }

  /* ------------------------------------------------- inside a Canvas frame */

  if (root.classList.contains("framed")) {
    Array.prototype.forEach.call(document.querySelectorAll("main a.int"), function (a) {
      var span = document.createElement("span");
      span.className = "inert";
      span.innerHTML = a.innerHTML;
      a.parentNode.replaceChild(span, a);
    });
  }
})();
