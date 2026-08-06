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
