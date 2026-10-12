// Success-criteria ticks and worksheet-table answers, saved per lesson on this
// device only. Nothing leaves the browser: the site is public and must never hold
// anything about a student.
(function () {
  var key = 'y8:' + location.pathname;
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) {}

  var pending = null;
  function store() {
    // Typing fires per keystroke, so the write is coalesced. localStorage is
    // synchronous, and a class typing into a projected table should not be paying
    // for a disk write per character.
    if (pending) return;
    pending = setTimeout(function () {
      pending = null;
      try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
    }, 250);
  }

  document.querySelectorAll('.crit input[type=checkbox]').forEach(function (b) {
    if (saved[b.id]) b.checked = true;
    b.addEventListener('change', function () {
      saved[b.id] = b.checked;
      store();
    });
  });

  // The key carries the block index and the cell, so two tables in one lesson do
  // not overwrite each other, and an edit to one lesson cannot reach another.
  document.querySelectorAll('input.fill').forEach(function (f) {
    var k = 'f' + f.dataset.cell;
    if (saved[k]) f.value = saved[k];
    f.addEventListener('input', function () {
      if (f.value) { saved[k] = f.value; } else { delete saved[k]; }
      store();
    });
  });
})();

// The assessment run. Two teachers share one set of iPads, so the term's lessons
// run in two orders. The term page lets a student pick their class's run, and a
// lesson page then offers previous and next along that run instead of the plain
// 1 to 25 order. The choice is a per-device convenience only: it is never sent
// anywhere, and it says which order a class takes, never where a class is up to.
(function () {
  var runs = document.querySelector('.runs');
  var navs = document.querySelectorAll('.runnav');
  if (!runs && !navs.length) return;

  // One choice per topic. The term page names its topic; a lesson page takes it
  // from the term page's address, the second-to-last folder of its own.
  var topic = runs ? runs.dataset.topic
    : location.pathname.replace(/\/$/, '').split('/').slice(-2)[0];
  var key = 'y8:run:' + topic;
  function get() { try { return localStorage.getItem(key); } catch (e) { return null; } }
  function set(v) {
    try { if (v) { localStorage.setItem(key, v); } else { localStorage.removeItem(key); } } catch (e) {}
  }

  if (runs) {
    var buttons = runs.querySelectorAll('.runbtn');
    var panels = runs.querySelectorAll('.run');
    var prompt = runs.querySelector('.runprompt');
    var ids = Array.prototype.map.call(panels, function (p) { return p.dataset.run; });
    function show(id) {
      panels.forEach(function (p) { p.hidden = p.dataset.run !== id; });
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.run === id)); });
      prompt.hidden = !!id;
    }
    runs.querySelector('.runswitch').hidden = false;
    // A teacher can link straight to a run (#listening-first) from Canvas.
    var fromHash = location.hash.slice(1);
    var chosen = ids.indexOf(fromHash) >= 0 ? fromHash : get();
    if (ids.indexOf(chosen) < 0) chosen = null;
    if (chosen) set(chosen);
    show(chosen);
    buttons.forEach(function (b) {
      b.addEventListener('click', function () {
        set(b.dataset.run);
        show(b.dataset.run);
        try { history.replaceState(null, '', '#' + b.dataset.run); } catch (e) {}
      });
    });
  }

  if (navs.length) {
    var plain = document.querySelector('.prevnext.static');
    function follow(id) {
      var any = false;
      navs.forEach(function (n) { n.hidden = n.dataset.run !== id; if (!n.hidden) any = true; });
      if (plain) plain.hidden = any;
    }
    follow(get());
    document.querySelectorAll('.run-off').forEach(function (b) {
      b.addEventListener('click', function () { set(null); follow(null); });
    });
  }
})();
