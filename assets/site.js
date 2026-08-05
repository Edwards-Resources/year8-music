// Success-criteria ticks, saved per lesson on this device only. Nothing leaves
// the browser: the site is public and must never hold anything about a student.
(function () {
  var boxes = document.querySelectorAll('.crit input[type=checkbox]');
  if (!boxes.length) return;
  var key = 'y8:' + location.pathname;
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) {}
  boxes.forEach(function (b) {
    if (saved[b.id]) b.checked = true;
    b.addEventListener('change', function () {
      saved[b.id] = b.checked;
      try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
    });
  });
})();
