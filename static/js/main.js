/* IT Registry — main.js */
'use strict';

/* ── MOBILE SIDEBAR ─────────────────────────────────────── */
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('mob-ov').classList.toggle('show');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('mob-ov').classList.remove('show');
}

/* ── SITE SWITCHER ──────────────────────────────────────── */
function toggleSiteDd() {
  const btn = document.getElementById('site-btn');
  const dd  = document.getElementById('site-dd');
  btn.classList.toggle('open');
  dd.classList.toggle('open');
}

function switchSite(siteId, siteName, siteColor) {
  const csrfToken = document.cookie
    .split('; ')
    .find(r => r.startsWith('csrftoken='))
    ?.split('=')[1];

  fetch('/switch-site/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrfToken || '',
    },
    body: 'site_id=' + encodeURIComponent(siteId),
  })
  .then(r => r.json())
  .then(data => {
    if (data.ok) {
      // Update UI immediately
      document.getElementById('site-label').textContent = data.name;
      document.getElementById('site-dot').style.background = data.color || '#0052CC';
      document.getElementById('site-btn').classList.remove('open');
      document.getElementById('site-dd').classList.remove('open');
      // Reload page to get filtered data
      window.location.reload();
    }
  })
  .catch(err => console.error('Site switch error:', err));
}

// Close dropdown on outside click
document.addEventListener('click', function(e) {
  const sw = document.getElementById('site-sw');
  if (sw && !sw.contains(e.target)) {
    document.getElementById('site-btn')?.classList.remove('open');
    document.getElementById('site-dd')?.classList.remove('open');
  }
});

/* ── ACCORDION ──────────────────────────────────────────── */
function toggleGroup(id) {
  const grp  = document.getElementById('ag-' + id);
  const body = document.getElementById('ab-' + id);
  if (!grp || !body) return;
  const isOpen = grp.classList.contains('is-open');
  if (isOpen) {
    grp.classList.remove('is-open');
    body.style.maxHeight = '0';
  } else {
    grp.classList.add('is-open');
    body.style.maxHeight = body.scrollHeight + 200 + 'px';
  }
}

/* ── AUTO DISMISS MESSAGES ──────────────────────────────── */
document.addEventListener('DOMContentLoaded', function() {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      alert.style.transition = 'opacity .4s';
      alert.style.opacity = '0';
      setTimeout(function() { alert.remove(); }, 400);
    }, 4000);
  });
});

/* ── AI SEARCH ───────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function() {
  const inp   = document.getElementById('ai-search-inp');
  const panel = document.getElementById('ai-srch-panel');
  const body  = document.getElementById('ai-srch-body');
  const wrap  = document.getElementById('ai-srch-wrap');
  if (!inp) return;

  let timer = null;

  inp.addEventListener('input', function() {
    clearTimeout(timer);
    const q = inp.value.trim();
    if (q.length < 2) { panel.style.display = 'none'; return; }

    body.textContent = '⏳ Думаю...';
    panel.style.display = 'block';

    timer = setTimeout(function() {
      fetch('/ai-search/?q=' + encodeURIComponent(q))
        .then(function(r) { return r.json(); })
        .then(function(data) {
          body.textContent = data.answer || 'Ничего не найдено.';
        })
        .catch(function() { body.textContent = 'Ошибка поиска.'; });
    }, 600);
  });

  inp.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') { panel.style.display = 'none'; inp.value = ''; }
  });

  document.addEventListener('click', function(e) {
    if (wrap && !wrap.contains(e.target)) panel.style.display = 'none';
  });
});
