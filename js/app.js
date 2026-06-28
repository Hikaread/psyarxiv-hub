(function() {
  'use strict';

  /* ===== CATEGORIES ===== */
  var CATEGORIES = [
    {id:'anxiety',         label:'Anxiety & OCD'},
    {id:'couples',         label:'Couples Therapy & Sexology'},
    {id:'neurodivergence', label:'Neurodivergence'},
    {id:'mood',            label:'Mood Disorders'},
    {id:'trauma',          label:'Trauma & Stressor-Related'},
    {id:'personality',     label:'Personality Disorders'},
    {id:'modalities',      label:'Therapeutic Modalities'},
    {id:'psychopathology', label:'Psychopathology & Assessment'},
    {id:'eating',          label:'Eating Disorders'},
    {id:'somatic',         label:'Somatic & Functional'},
    {id:'suicidality',     label:'Suicidality & Self-Harm'},
    {id:'psychosis',       label:'Psychosis & Schizophrenia'},
    {id:'addiction',       label:'Addiction & Substance Use'},
    {id:'ocd',             label:'Obsessive-Compulsive'},
    {id:'other',           label:'Other Clinical'}
  ];
  var catMap = {}, labelToId = {};
  CATEGORIES.forEach(function(c) { catMap[c.id] = c.label; labelToId[c.label] = c.id; });

  /* ===== STATE ===== */
  var papers = [], filtered = [], shown = 0;
  var activeCats = {};
  CATEGORIES.forEach(function(c) { activeCats[c.id] = true; });
  var searchQuery = '', sortMode = 'newest';
  var PAGE_SIZE = 25;
  var lastScrollY = 0, ticking = false;

  /* ===== SETTINGS ===== */
  var settings = loadSettings();
  applySettings(settings);

  function loadSettings() {
    try {
      var s = JSON.parse(localStorage.getItem('psyarxiv-settings'));
      if (s) return s;
    } catch(e) {}
    return { theme: 'light', fontSize: 'medium', dyslexic: 'off', pageSize: '25' };
  }
  function saveSettings() {
    try { localStorage.setItem('psyarxiv-settings', JSON.stringify(settings)); } catch(e) {}
  }
  function applySettings(s) {
    document.documentElement.setAttribute('data-theme', s.theme);
    document.documentElement.setAttribute('data-fontsize', s.fontSize);
    document.documentElement.setAttribute('data-dyslexic', s.dyslexic);
    PAGE_SIZE = parseInt(s.pageSize, 10) || 25;
    // Update button states
    document.querySelectorAll('.setting-options').forEach(function(group) {
      var key = group.dataset.setting;
      group.querySelectorAll('.opt-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.value === s[key]);
      });
    });
  }

  // Settings button clicks
  document.querySelectorAll('.setting-options').forEach(function(group) {
    var key = group.dataset.setting;
    group.querySelectorAll('.opt-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        settings[key] = this.dataset.value;
        applySettings(settings);
        saveSettings();
        // Re-render if page size changed
        if (key === 'pageSize') { shown = 0; document.getElementById('papers-list').innerHTML = ''; showMore(); }
      });
    });
  });

  /* ===== SETTINGS DRAWER ===== */
  var settingsDrawer = document.getElementById('settings-drawer');
  var settingsOverlay = document.getElementById('settings-overlay');

  function openSettings() {
    settingsDrawer.classList.add('open');
    settingsOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeSettings() {
    settingsDrawer.classList.remove('open');
    settingsOverlay.classList.remove('open');
    if (!sidebar.classList.contains('open')) document.body.style.overflow = '';
  }
  document.getElementById('settings-toggle').addEventListener('click', openSettings);
  document.getElementById('settings-close').addEventListener('click', closeSettings);
  settingsOverlay.addEventListener('click', closeSettings);

  /* ===== MOBILE SIDEBAR ===== */
  var sidebar = document.getElementById('sidebar');
  var sidebarOverlay = document.getElementById('sidebar-overlay');
  var sidebarToggle = document.getElementById('sidebar-toggle');

  function openSidebar() {
    sidebar.classList.add('open');
    sidebarOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('open');
    if (!settingsDrawer.classList.contains('open')) document.body.style.overflow = '';
  }

  sidebarToggle.addEventListener('click', function(e) {
    e.stopPropagation();
    if (sidebar.classList.contains('open')) closeSidebar(); else openSidebar();
  });
  sidebarOverlay.addEventListener('click', closeSidebar);

  /* ===== AUTO-HIDE HEADER ===== */
  var header = document.getElementById('site-header');
  var statsBar = document.getElementById('stats-bar');

  window.addEventListener('scroll', function() {
    if (!ticking) {
      requestAnimationFrame(function() {
        var sy = window.scrollY;
        if (sy > lastScrollY && sy > 60) {
          header.classList.add('hidden');
          statsBar.classList.add('hidden');
        } else {
          header.classList.remove('hidden');
          statsBar.classList.remove('hidden');
        }
        lastScrollY = sy;
        updateQuickNav();
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  /* ===== INIT ===== */
  fetch('data/papers.json')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      papers = data;
      buildCategoryFilters();
      applyStateFromHash();
      applyFilters();
    })
    .catch(function() {
      document.getElementById('papers-list').innerHTML = '<p style="color:#c62828;padding:40px 0;text-align:center;">Failed to load paper data.</p>';
    });

  /* ===== CATEGORY FILTERS ===== */
  function buildCategoryFilters() {
    var counts = {};
    CATEGORIES.forEach(function(c) { counts[c.id] = 0; });
    papers.forEach(function(p) {
      (p.categories || []).forEach(function(c) {
        var id = labelToId[c];
        if (id && counts[id] !== undefined) counts[id]++;
      });
    });
    var container = document.getElementById('category-filters');
    container.innerHTML = '';
    CATEGORIES.forEach(function(c) {
      var lbl = document.createElement('label');
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = activeCats[c.id];
      cb.dataset.cat = c.id;
      cb.addEventListener('change', function() {
        activeCats[c.id] = this.checked;
        applyFilters();
        saveHash();
      });
      var span = document.createElement('span');
      span.textContent = c.label;
      var cnt = document.createElement('span');
      cnt.className = 'cat-count';
      cnt.textContent = counts[c.id];
      lbl.appendChild(cb);
      lbl.appendChild(span);
      lbl.appendChild(cnt);
      container.appendChild(lbl);
    });
  }

  /* ===== FILTERING ===== */
  function applyFilters() {
    var q = searchQuery.toLowerCase().trim();
    filtered = papers.filter(function(p) {
      var catIds = (p.categories || []).map(function(c) { return labelToId[c] || 'other'; });
      if (!catIds.some(function(id) { return activeCats[id]; })) return false;
      if (q) {
        var haystack = [p.title, p.authors, p.summary, p.clinical_insight, p.relevant_for].join(' ').toLowerCase();
        if (haystack.indexOf(q) === -1) return false;
      }
      return true;
    });
    sortPapers();
    shown = 0;
    document.getElementById('papers-list').innerHTML = '';
    buildQuickNav();
    showMore();
  }

  function sortPapers() {
    filtered.sort(function(a, b) {
      switch (sortMode) {
        case 'oldest':    return a.number - b.number;
        case 'newest':    return b.number - a.number;
        case 'date-desc': return (b.source_date || '').localeCompare(a.source_date || '');
        case 'date-asc':  return (a.source_date || '').localeCompare(b.source_date || '');
        case 'category':  return getCatSort(a) - getCatSort(b) || b.number - a.number;
        default:          return b.number - a.number;
      }
    });
  }

  function getCatSort(p) {
    var c = (p.categories || [])[0] || '';
    var id = labelToId[c] || 'other';
    return CATEGORIES.findIndex(function(cat) { return cat.id === id; });
  }

  /* ===== QUICK NAV (category sort only) ===== */
  function buildQuickNav() {
    var qn = document.getElementById('quick-nav');
    qn.innerHTML = '';
    if (sortMode !== 'category') { qn.classList.remove('visible'); return; }
    // Find unique category order
    var seen = [];
    filtered.forEach(function(p) {
      var c = (p.categories || [])[0] || 'Other Clinical';
      if (seen.indexOf(c) === -1) seen.push(c);
    });
    if (seen.length < 3) { qn.classList.remove('visible'); return; }
    seen.forEach(function(cat) {
      var btn = document.createElement('button');
      btn.className = 'qn-btn';
      btn.setAttribute('data-tooltip', cat);
      btn.dataset.cat = cat;
      btn.addEventListener('click', function() {
        var el = document.getElementById('cat-' + catToAnchor(cat));
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      qn.appendChild(btn);
    });
    qn.classList.add('visible');
  }

  function updateQuickNav() {
    if (sortMode !== 'category') return;
    var dividers = document.querySelectorAll('.cat-divider');
    var qnBtns = document.querySelectorAll('.qn-btn');
    if (!dividers.length || !qnBtns.length) return;
    var mid = window.innerHeight / 2;
    var activeCat = '';
    dividers.forEach(function(d) { if (d.getBoundingClientRect().top < mid + 40) activeCat = d.id; });
    qnBtns.forEach(function(b) {
      b.classList.toggle('active', b.dataset.cat && document.getElementById('cat-' + catToAnchor(b.dataset.cat)) === document.getElementById(activeCat));
    });
  }

  function catToAnchor(cat) {
    return cat.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }

  /* ===== RENDERING ===== */
  var lastRenderedCat = '';

  function showMore() {
    var list = document.getElementById('papers-list');
    var end = Math.min(shown + PAGE_SIZE, filtered.length);
    for (var i = shown; i < end; i++) {
      // Insert category divider when sorting by category
      if (sortMode === 'category') {
        var cat = (filtered[i].categories || [])[0] || 'Other Clinical';
        if (cat !== lastRenderedCat) {
          var div = document.createElement('div');
          div.className = 'cat-divider';
          div.id = 'cat-' + catToAnchor(cat);
          div.textContent = cat;
          list.appendChild(div);
          lastRenderedCat = cat;
        }
      }
      list.appendChild(createCard(filtered[i]));
    }
    shown = end;
    document.getElementById('load-more').style.display = shown < filtered.length ? 'block' : 'none';
    document.getElementById('no-results').style.display = filtered.length === 0 ? 'block' : 'none';
    updateStats();
  }

  function createCard(p) {
    var card = document.createElement('div');
    card.className = 'paper-card';

    var h = '<div class="paper-card-header">';
    h += '<span class="paper-number">#' + p.number + '</span>';
    h += '<div class="paper-title has-modal">' + esc(p.title) + '</div>';
    h += '</div>';

    h += '<div class="paper-meta">';
    h += '<span class="author-name">' + esc(p.authors) + '</span>';
    if (p.source_date) h += '<span class="date-text">' + esc(p.source_date) + '</span>';
    h += '</div>';

    if (p.summary) {
      h += '<div class="paper-summary">' + esc(truncate(p.summary, 220)) + '</div>';
    }

    if (p.categories && p.categories.length) {
      h += '<div class="paper-badges">';
      p.categories.forEach(function(c) {
        var dataCat = labelToId[c] || 'other';
        h += '<span class="badge" data-cat="' + dataCat + '">' + esc(c) + '</span>';
      });
      h += '</div>';
    }

    if (p.link) {
      h += '<div style="padding-left:36px;margin-top:6px;"><a href="' + esc(p.link) + '" target="_blank" rel="noopener" class="paper-osf-link">View on PsyArXiv</a></div>';
    }

    card.innerHTML = h;
    var titleEl = card.querySelector('.paper-title');
    titleEl.addEventListener('click', function() { openModal(p); });
    return card;
  }

  /* ===== MODAL ===== */
  function openModal(p) {
    var modal = document.getElementById('paper-modal');
    var body = document.getElementById('modal-body');
    var h = '<div class="modal-title">' + esc(p.title) + '</div>';
    h += '<div class="modal-meta"><span class="author-name">' + esc(p.authors) + '</span>';
    if (p.source_date) h += ' &middot; ' + esc(p.source_date);
    h += '</div>';

    if (p.categories && p.categories.length) {
      h += '<div class="paper-badges" style="margin-bottom:12px;">';
      p.categories.forEach(function(c) {
        var dataCat = labelToId[c] || 'other';
        h += '<span class="badge" data-cat="' + dataCat + '">' + esc(c) + '</span>';
      });
      h += '</div>';
    }

    // Always show summary in modal (full text, not truncated)
    if (p.summary) {
      h += '<div class="modal-section"><div class="modal-section-label">Summary</div><div class="modal-section-text">' + esc(p.summary) + '</div></div>';
    }
    if (p.clinical_insight) {
      h += '<div class="modal-section"><div class="modal-section-label">Clinical Insight</div><div class="modal-section-text">' + esc(p.clinical_insight) + '</div></div>';
    }
    if (p.relevant_for) {
      h += '<div class="modal-section"><div class="modal-section-label">Relevant For</div><div class="modal-section-text">' + esc(p.relevant_for) + '</div></div>';
    }
    if (p.published) {
      h += '<div class="modal-section"><div class="modal-section-label">Published</div><div class="modal-section-text">' + esc(p.published) + '</div></div>';
    }

    if (p.link) {
      h += '<a class="modal-link" href="' + esc(p.link) + '" target="_blank" rel="noopener">View on PsyArXiv &rarr;</a>';
    }

    body.innerHTML = h;
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }

  document.getElementById('modal-close').addEventListener('click', closeModal);
  document.getElementById('paper-modal').addEventListener('click', function(e) { if (e.target === this) closeModal(); });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') { closeModal(); closeSidebar(); closeSettings(); }
  });

  function closeModal() {
    document.getElementById('paper-modal').style.display = 'none';
    if (!settingsDrawer.classList.contains('open') && !sidebar.classList.contains('open')) {
      document.body.style.overflow = '';
    }
  }

  /* ===== STATS ===== */
  function updateStats() {
    document.getElementById('stat-total').textContent = papers.length + ' papers';
    document.getElementById('stat-shown').textContent = filtered.length + ' shown';
  }

  /* ===== SEARCH ===== */
  var searchTimer;
  document.getElementById('search-input').addEventListener('input', function() {
    clearTimeout(searchTimer);
    var val = this.value;
    searchTimer = setTimeout(function() {
      searchQuery = val;
      applyFilters();
      saveHash();
    }, 200);
  });

  /* ===== SORT ===== */
  document.getElementById('sort-select').addEventListener('change', function() {
    sortMode = this.value;
    lastRenderedCat = '';
    applyFilters();
    saveHash();
  });

  /* ===== SELECT ALL / NONE ===== */
  document.getElementById('btn-select-all').addEventListener('click', function() {
    CATEGORIES.forEach(function(c) { activeCats[c.id] = true; });
    syncCheckboxes();
    applyFilters();
    saveHash();
  });
  document.getElementById('btn-clear-all').addEventListener('click', function() {
    CATEGORIES.forEach(function(c) { activeCats[c.id] = false; });
    syncCheckboxes();
    applyFilters();
    saveHash();
  });

  function syncCheckboxes() {
    document.querySelectorAll('#category-filters input[type="checkbox"]').forEach(function(cb) {
      cb.checked = activeCats[cb.dataset.cat];
    });
  }

  /* ===== LOAD MORE ===== */
  document.getElementById('load-more').addEventListener('click', showMore);

  /* ===== HASH STATE ===== */
  function saveHash() {
    var state = {};
    if (searchQuery) state.q = searchQuery;
    var cats = CATEGORIES.filter(function(c) { return !activeCats[c.id]; }).map(function(c) { return c.id; });
    if (cats.length) state.off = cats.join(',');
    if (sortMode !== 'newest') state.sort = sortMode;
    var hash = '#' + Object.keys(state).map(function(k) { return k + '=' + encodeURIComponent(state[k]); }).join('&');
    history.replaceState(null, '', hash);
  }

  function applyStateFromHash() {
    var hash = location.hash.slice(1);
    if (!hash) return;
    var params = {};
    hash.split('&').forEach(function(pair) {
      var parts = pair.split('=');
      if (parts.length === 2) params[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1]);
    });
    if (params.q) { searchQuery = params.q; document.getElementById('search-input').value = params.q; }
    if (params.off) { params.off.split(',').forEach(function(c) { activeCats[c] = false; }); syncCheckboxes(); }
    if (params.sort) { sortMode = params.sort; document.getElementById('sort-select').value = sortMode; }
  }

  /* ===== UTILS ===== */
  function esc(s) {
    if (!s) return '';
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }
  function truncate(s, n) {
    if (s.length <= n) return s;
    return s.substring(0, n).replace(/\s+\S*$/, '') + '...';
  }
})();