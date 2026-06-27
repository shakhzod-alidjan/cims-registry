/* AI Category Suggestion — BusinessApp Admin */
document.addEventListener('DOMContentLoaded', function () {
  const categorySelect = document.getElementById('id_category');
  const nameInput      = document.getElementById('id_name');
  if (!categorySelect || !nameInput) return;

  const btn = document.createElement('button');
  btn.type      = 'button';
  btn.innerHTML = '🤖 AI категория';
  btn.title     = 'Определить категорию автоматически по названию и вендору';
  btn.style.cssText = (
    'margin-left:8px;padding:4px 12px;background:#417690;color:#fff;' +
    'border:none;border-radius:4px;cursor:pointer;font-size:12px;vertical-align:middle'
  );

  categorySelect.insertAdjacentElement('afterend', btn);

  btn.addEventListener('click', function () {
    const name = nameInput.value.trim();
    if (!name) { alert('Сначала введите название приложения'); return; }

    const vendorSel  = document.getElementById('id_vendor');
    const vendorText = vendorSel ? (vendorSel.options[vendorSel.selectedIndex] || {}).text || '' : '';

    btn.disabled    = true;
    btn.textContent = '⏳ Определяю...';

    const url = '/licenses/suggest-category/?name=' +
      encodeURIComponent(name) + '&vendor=' + encodeURIComponent(vendorText);

    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.category) {
          categorySelect.value = data.category;
          btn.innerHTML = '✅ ' + data.label;
        } else {
          btn.textContent = '❌ Не удалось';
        }
      })
      .catch(function () { btn.textContent = '❌ Ошибка'; })
      .finally(function () {
        btn.disabled = false;
        setTimeout(function () { btn.innerHTML = '🤖 AI категория'; }, 2500);
      });
  });
});
