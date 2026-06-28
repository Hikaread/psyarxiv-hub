(function() {
  'use strict';

  var PAGE_SIZE = 25;
  var CATEGORIES = [
    {id:'couples',        label:'Couples Therapy & Sexology'},
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
    {id:'other',           label:'Other Clinical'}
  ];

  var catMap = {};
  CATEGORIES.forEach(function(c) { catMap[c.id] = c.label; });

  var papers = [];
  var filtered = [];
  var shown = 0;
  var activeCats = {};
  CATEGORIES.forEach(function(c) { activeCats[c.id] = true; });
  var searchQuery = '';
  var sortMode = 'newest';

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
      document.getElementById('papers-list').innerHTML = '<p style="color:#c62828;padding:40px 0;">Failed to load paper data.</p>';
    });

  /* ===== CATEGORY FILTERS ===== */
  function buildCategoryFilters() {
    var counts = {};
    CATEGORIES.forEach(function(c) { counts[c.id] = 0; });
    papers.forEach(function(p) {
      (p.categories || []).forEach(function(c) {
        if (counts[c] !== undefined) counts[c]++;
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
      if (!activeCats[p.categories[0]] && p.categories.every(function(c) { return !activeCats[c]; })) {
        return false;
      }
      if (q) {
        var haystack = [
          p.title, p.authors, p.summary, p.clinical_insight, p.relevant_for
        ].join(' ').toLowerCase();
        if (haystack.indexOf(q) === -1) return false;
      }
      return true;
    });
    sortPapers();
    shown = 0;
    document.getElementById('papers-list').innerHTML = '';
    showMore();
  }

  function sortPapers() {
    filtered.sort(function(a, b) {
      switch (sortMode) {
        case 'oldest':    return a.number - b.number;
        case 'newest':    return b.number - a.number;
        case 'date-desc': return (b.source_date || '').localeCompare(a.source_date || '');
        case 'date-asc':  return (a.source_date || '').localeCompare(b.source_date || '');
        case 'category':  return (a.categories[0] || '').localeCompare(b.categories[0] || '') || b.number - a.number;
        default:          return b.number - a.number;
      }
    });
  }

  /* ===== RENDERING ===== */
  function showMore() {
    var list = document.getElementById('papers-list');
    var end = Math.min(shown + PAGE_SIZE, filtered.length);
    for (var i = shown; i < end; i++) {
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

    var hasMore = p.clinical_insight || p.relevant_for || p.published;

    var h = '<div class="paper-card-header">';
    h += '<span class="paper-number">#' + p.number + '</span>';
    h += '<div class="paper-title">' + esc(p.title) + '</div>';
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
        var catId = c.toLowerCase().replace(/[^a-z]/g, '').substring(0, 12);
        var dataCat = '';
        for (var k in catMap) {
          if (catMap[k].toLowerCase().indexOf(catId) === 0 || catId.indexOf(k) === 0) { dataCat = k; break; }
        }
        if (!dataCat) dataCat = 'other';
        h += '<span class="badge" data-cat="' + dataCat + '">' + esc(c) + '</span>';
      });
      h += '</div>';
    }

    if (p.published) {
      h += '<div class="paper-published">Published: ' + esc(p.published) + '</div>';
    }

    if (hasMore) {
      h += '<button class="paper-expand-btn" data-idx="' + p.number + '">Read more</button>';
    }

    card.innerHTML = h;

    var btn = card.querySelector('.paper-expand-btn');
    if (btn) {
      btn.addEventListener('click', function() { openModal(p); });
    }

    return card;
  }

  /* ===== MODAL ===== */
  function openModal(p) {
    var modal = document.getElementById('paper-modal');
    var body = document.getElementById('modal-body');
    var h = '<div class="modal-title">' + esc(p.title) + '</div>';
    h += '<div class="modal-meta"><span class="author-name">' + esc(p.authors) + '</span>';
    if (p.source_date) h += ' &middot; ' + esc(p.source_date);
    h += ' &middot; <a href="' + esc(p.link) + '" target="_blank" rel="noopener">OSF</a>';
    h += '</div>';

    if (p.categories && p.categories.length) {
      h += '<div class="paper-badges" style="margin-bottom:14px;">';
      p.categories.forEach(function(c) {
        var catId = c.toLowerCase().replace(/[^a-z]/g, '').substring(0, 12);
        var dataCat = 'other';
        for (var k in catMap) {
          if (catMap[k].toLowerCase().indexOf(catId) === 0 || catId.indexOf(k) === 0) { dataCat = k; break; }
        }
        h += '<span class="badge" data-cat="' + dataCat + '">' + esc(c) + '</span>';
      });
      h += '</div>';
    }

    if (p.summary) {
      h += '<div class="modal-section">';
      h += '<div class="modal-section-label">Summary</div>';
      h += '<div class="modal-section-text">' + esc(p.summary) + '</div>';
      h += '</div>';
    }
    if (p.clinical_insight) {
      h += '<div class="modal-section">';
      h += '<div class="modal-section-label">Clinical Insight</div>';
      h += '<div class="modal-section-text">' + esc(p.clinical_insight) + '</div>';
      h += '</div>';
    }
    if (p.relevant_for) {
      h += '<div class="modal-section">';
      h += '<div class="modal-section-label">Relevant For</div>';
      h += '<div class="modal-section-text">' + esc(p.relevant_for) + '</div>';
      h += '</div>';
    }
    if (p.published) {
      h += '<div class="modal-section">';
      h += '<div class="modal-section-label">Published</div>';
      h += '<div class="modal-section-text">' + esc(p.published) + '</div>';
      h += '</div>';
    }

    h += '<a class="modal-link" href="' + esc(p.link) + '" target="_blank" rel="noopener">View on PsyArXiv &rarr;</a>';

    body.innerHTML = h;
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }

  document.getElementById('modal-close').addEventListener('click', closeModal);
  document.getElementById('paper-modal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
  });

  function closeModal() {
    document.getElementById('paper-modal').style.display = 'none';
    document.body.style.overflow = '';
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
    }, 250);
  });

  /* ===== SORT ===== */
  document.getElementById('sort-select').addEventListener('change', function() {
    sortMode = this.value;
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
    var cbs = document.querySelectorAll('#category-filters input[type="checkbox"]');
    cbs.forEach(function(cb) { cb.checked = activeCats[cb.dataset.cat]; });
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
    if (params.q) {
      searchQuery = params.q;
      document.getElementById('search-input').value = params.q;
    }
    if (params.off) {
      params.off.split(',').forEach(function(c) { activeCats[c] = false; });
      syncCheckboxes();
    }
    if (params.sort) {
      sortMode = params.sort;
      document.getElementById('sort-select').value = sortMode;
    }
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