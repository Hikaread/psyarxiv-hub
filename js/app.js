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
  var searchQuery = '', sortMode = 'newest', categoryView = false;
  var PAGE_SIZE = 25;
  var ticking = false;
  var activeQuickNavCategory = '';
  var suppressHashSync = false;

  /* ===== LOCAL STORAGE HELPERS ===== */
  function loadJSON(key, fallback) {
    try { var v = JSON.parse(localStorage.getItem(key)); return v && typeof v === 'object' ? v : fallback; } catch(e) { return fallback; }
  }
  function saveJSON(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch(e) {}
  }

  /* ===== READ / STAR STATE ===== */
  var readPapers = loadJSON('psyarxiv-read', {});
  var starPapers = loadJSON('psyarxiv-star', {});

  function getReadIcon(isReadState) {
    if (isReadState) {
      return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12c2.2-3.3 5.4-5 9-5s6.8 1.7 9 5c-2.2 3.3-5.4 5-9 5s-6.8-1.7-9-5Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M7.5 12c1.2-1.7 2.8-2.5 4.5-2.5s3.3.8 4.5 2.5c-1.2 1.7-2.8 2.5-4.5 2.5s-3.3-.8-4.5-2.5Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12s3.8-6 9-6 9 6 9 6-3.8 6-9 6-9-6-9-6Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>';
  }

  function isRead(num) { return !!readPapers[num]; }
  function isStar(num) { return !!starPapers[num]; }

  function toggleRead(num) {
    if (readPapers[num]) { delete readPapers[num]; } else { readPapers[num] = true; }
    saveJSON('psyarxiv-read', readPapers);
    updateCardState(num);
  }

  function toggleStar(num) {
    if (starPapers[num]) { delete starPapers[num]; } else { starPapers[num] = true; }
    saveJSON('psyarxiv-star', starPapers);
    updateCardState(num);
  }

  /* ===== SHARE ===== */
  var pendingSharedPaperNumber = null;

  function getPaperPermalink(num) {
    return window.location.origin + window.location.pathname + '#paper=' + num;
  }

  function copyTextToClipboard(value) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(value);
    }

    return new Promise(function(resolve, reject) {
      var textarea = document.createElement('textarea');
      textarea.value = value;
      textarea.setAttribute('readonly', 'readonly');
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();

      try {
        if (document.execCommand('copy')) {
          resolve();
        } else {
          reject(new Error('Copy command failed'));
        }
      } catch (error) {
        reject(error);
      } finally {
        textarea.remove();
      }
    });
  }

  function sharePaper(p) {
    var url = getPaperPermalink(p.number);
    var leadAuthor = (p.authors || '').split(',')[0].trim();
    var text = leadAuthor ? (p.title + ' — ' + leadAuthor + ' et al.') : p.title;
    if (navigator.share) {
      navigator.share({ title: p.title, text: text, url: url }).catch(function() {});
    } else {
      copyTextToClipboard(url).then(function() { showToast('Link copied'); }).catch(function() {});
    }
  }

  function showToast(msg) {
    var existing = document.getElementById('share-toast');
    if (existing) existing.remove();
    var t = document.createElement('div');
    t.id = 'share-toast';
    t.textContent = msg;
    document.body.appendChild(t);
    requestAnimationFrame(function() { t.classList.add('visible'); });
    setTimeout(function() { t.classList.remove('visible'); setTimeout(function() { t.remove(); }, 300); }, 1500);
  }

  function highlightSharedCard(card) {
    if (!card) return;
    card.classList.remove('shared-target');
    card.offsetWidth;
    card.classList.add('shared-target');
    setTimeout(function() {
      card.classList.remove('shared-target');
    }, 2200);
  }

  function ensurePaperRendered(num) {
    var card = document.querySelector('.paper-card[data-num="' + num + '"]');
    if (card) return card;

    while (shown < filtered.length) {
      var before = shown;
      showMore();
      card = document.querySelector('.paper-card[data-num="' + num + '"]');
      if (card || shown === before) break;
    }

    return card;
  }

  function revealSharedPaper() {
    if (!pendingSharedPaperNumber) return;
    var card = ensurePaperRendered(pendingSharedPaperNumber);
    if (!card) return;
    card.scrollIntoView({ behavior: 'auto', block: 'start' });
    highlightSharedCard(card);
    var paper = findPaperByNumber(pendingSharedPaperNumber);
    if (paper) openModal(paper);
    pendingSharedPaperNumber = null;
  }

  function findPaperByNumber(num) {
    for (var i = 0; i < papers.length; i++) {
      if (papers[i].number === num) return papers[i];
    }
    return null;
  }

  function updateCardState(num) {
    var card = document.querySelector('[data-num="' + num + '"]');
    if (!card) return;
    var r = isRead(num), s = isStar(num);
    card.classList.toggle('read-dimmed', r);
    var readBtn = card.querySelector('.btn-read');
    var starBtn = card.querySelector('.btn-star');
    if (readBtn) {
      readBtn.classList.toggle('active-read', r);
      readBtn.innerHTML = getReadIcon(r);
      readBtn.setAttribute('aria-label', r ? 'Mark as unread' : 'Mark as read');
      readBtn.setAttribute('title', r ? 'Mark as unread' : 'Mark as read');
    }
    if (starBtn) {
      starBtn.classList.toggle('active-star', s);
      starBtn.textContent = s ? '\u2605' : '\u2606';
      starBtn.setAttribute('aria-label', s ? 'Remove from favorites' : 'Add to favorites');
    }
  }

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
    document.querySelectorAll('.setting-options').forEach(function(group) {
      var key = group.dataset.setting;
      group.querySelectorAll('.opt-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.value === s[key]);
      });
    });
  }

  document.querySelectorAll('.setting-options').forEach(function(group) {
    var key = group.dataset.setting;
    group.querySelectorAll('.opt-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        settings[key] = this.dataset.value;
        applySettings(settings);
        saveSettings();
        if (key === 'pageSize') { shown = 0; document.getElementById('papers-list').innerHTML = ''; showMore(); }
      });
    });
  });

  /* ===== SETTINGS DRAWER ===== */
  var settingsDrawer = document.getElementById('settings-drawer');
  var settingsOverlay = document.getElementById('settings-overlay');

  function positionSettingsDrawer() {
    var headerBottom = document.getElementById('site-header').getBoundingClientRect().bottom;
    document.documentElement.style.setProperty('--settings-top', Math.max(headerBottom, 0) + 'px');
  }

  function openSettings() {
    document.getElementById('site-header').classList.remove('hidden');
    positionSettingsDrawer();
    settingsDrawer.classList.add('open');
    settingsOverlay.classList.add('open');
    document.getElementById('settings-toggle').setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }
  function closeSettings() {
    settingsDrawer.classList.remove('open');
    settingsOverlay.classList.remove('open');
    document.getElementById('settings-toggle').setAttribute('aria-expanded', 'false');
    if (!sidebar.classList.contains('open')) document.body.style.overflow = '';
  }
  document.getElementById('settings-toggle').addEventListener('click', function(e) {
    e.stopPropagation();
    if (settingsDrawer.classList.contains('open')) closeSettings(); else openSettings();
  });
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

  window.addEventListener('scroll', function() {
    if (!ticking) {
      requestAnimationFrame(function() {
        updateQuickNav();
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  /* ===== INIT ===== */
  console.log("INIT: about to fetch, papers array length = " + papers.length);
  fetch('data/papers.json')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      papers = data;
      buildCategoryFilters();
      applyStateFromHash();
      applyFilters();
    })
    .catch(function(err) {
      console.error('Paper load failed:', err);
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
        var haystack = [p.title, p.authors, p.summary, p.clinical_insight, p.relevant_for, p.methodology_note].join(' ').toLowerCase();
        if (haystack.indexOf(q) === -1) return false;
      }
      return true;
    });
    sortPapers();
    shown = 0;
    document.getElementById('papers-list').innerHTML = '';
    lastRenderedCat = '';
    buildQuickNav();
    showMore();
    revealSharedPaper();
  }

  /* ===== DATE PARSING (dd.mm.yyyy -> sortable number) ===== */
  function parseDateNum(d) {
    if (!d) return 0;
    var p = d.split('.');
    if (p.length !== 3) return 0;
    return (parseInt(p[2], 10) || 0) * 10000 + (parseInt(p[1], 10) || 0) * 100 + (parseInt(p[0], 10) || 0);
  }

  function sortPapers() {
    filtered.sort(function(a, b) {
      if (categoryView) {
        return getCatSort(a) - getCatSort(b) || compareBySortMode(a, b, sortMode);
      }
      return compareBySortMode(a, b, sortMode);
    });
  }

  function compareBySortMode(a, b, mode) {
    switch (mode) {
      case 'oldest':    return a.number - b.number;
      case 'newest':    return b.number - a.number;
      case 'favorites':
        var aS = isStar(a.number) ? 1 : 0, bS = isStar(b.number) ? 1 : 0;
        if (aS !== bS) return bS - aS;
        return b.number - a.number;
      case 'unread':
        var aR = isRead(a.number) ? 1 : 0, bR = isRead(b.number) ? 1 : 0;
        if (aR !== bR) return aR - bR;
        return b.number - a.number;
      case 'date-desc': return parseDateNum(b.source_date) - parseDateNum(a.source_date);
      case 'date-asc':  return parseDateNum(a.source_date) - parseDateNum(b.source_date);
      default:          return b.number - a.number;
    }
  }

  function getCatSort(p) {
    var c = (p.categories || [])[0] || '';
    var id = labelToId[c] || 'other';
    return CATEGORIES.findIndex(function(cat) { return cat.id === id; });
  }

  function getDirectPsyArxivUrl(p) {
    var explicitId = p && p.osf_id ? String(p.osf_id).trim() : '';
    var linkValue = p && p.link ? String(p.link).trim() : '';
    var extractedId = '';

    if (!explicitId && linkValue) {
      var match = linkValue.match(/osf\.io\/(?:preprints\/psyarxiv\/)?([a-z0-9]{5}(?:_v\d+)*)/i);
      if (match) extractedId = match[1];
    }

    var finalId = explicitId || extractedId;
    if (!finalId) return '';
    return 'https://osf.io/preprints/psyarxiv/' + finalId;
  }

  function getPsyArxivLinkInfo(p) {
    var directUrl = getDirectPsyArxivUrl(p);
    if (directUrl) {
      return {
        href: directUrl,
        label: 'View on PsyArXiv',
        modalLabel: 'View on PsyArXiv &rarr;',
        title: 'Open this paper on PsyArXiv'
      };
    }
    // Fallback: use link field if it's a valid URL
    var linkValue = p && p.link ? String(p.link).trim() : '';
    if (linkValue && /^https?:\/\//i.test(linkValue)) {
      return {
        href: linkValue,
        label: 'View paper',
        modalLabel: 'View paper &rarr;',
        title: 'Open this paper'
      };
    }
    return null;
  }

  function linkifyText(value) {
    var text = String(value || '');
    var urlPattern = /https?:\/\/[^\s]+/g;
    var result = '';
    var lastIndex = 0;
    var match;

    while ((match = urlPattern.exec(text)) !== null) {
      var url = match[0];
      var trailing = '';
      while (/[.,;:!?)]$/.test(url)) {
        trailing = url.slice(-1) + trailing;
        url = url.slice(0, -1);
      }
      result += esc(text.slice(lastIndex, match.index));
      result += '<a class="text-link" href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(url) + '</a>';
      result += esc(trailing);
      lastIndex = match.index + match[0].length;
    }

    return result + esc(text.slice(lastIndex));
  }

  function getAuthorDisplayValue(value) {
    if (!value || value === 'Unknown') {
      return 'Author metadata unavailable';
    }
    return value;
  }

  /* ===== QUICK NAV (category view only) ===== */
  function buildQuickNav() {
    var qn = document.getElementById('quick-nav');
    qn.innerHTML = '';
    activeQuickNavCategory = '';
    if (!categoryView) { qn.classList.remove('visible'); return; }
    var seen = [];
    filtered.forEach(function(p) {
      var c = (p.categories || [])[0] || 'Other Clinical';
      if (seen.indexOf(c) === -1) seen.push(c);
    });
    if (seen.length < 3) { qn.classList.remove('visible'); return; }
    var pills = document.createElement('div');
    pills.className = 'qn-pills';
    attachQuickNavScroller(pills);
    seen.forEach(function(cat) {
      var btn = document.createElement('button');
      btn.className = 'qn-btn';
      btn.type = 'button';
      btn.setAttribute('aria-label', 'Jump to ' + cat);
      btn.dataset.cat = cat;
      btn.innerHTML = '<span class="qn-label">' + esc(cat) + '</span>';
      btn.addEventListener('click', function() {
        jumpToCategory(cat);
      });
      pills.appendChild(btn);
    });
    qn.appendChild(pills);
    qn.classList.add('visible');
  }

  function attachQuickNavScroller(element) {
    if (!element || element.dataset.bound === 'true') return;
    element.dataset.bound = 'true';

    element.addEventListener('wheel', function(e) {
      if (element.scrollWidth <= element.clientWidth) return;
      var delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
      if (!delta) return;
      e.preventDefault();
      element.scrollLeft += delta;
    }, { passive: false });
  }

  function keepQuickNavButtonVisible(button) {
    if (!button || typeof button.scrollIntoView !== 'function') return;
    button.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'center'
    });
  }

  function updateQuickNav() {
    if (!categoryView) return;
    var dividers = document.querySelectorAll('.cat-divider');
    var qnBtns = document.querySelectorAll('.qn-btn');
    if (!dividers.length || !qnBtns.length) return;
    var mid = window.innerHeight / 2;
    var activeCat = '';
    dividers.forEach(function(d) { if (d.getBoundingClientRect().top < mid + 40) activeCat = d.id; });
    qnBtns.forEach(function(b) {
      var isActive = b.dataset.cat && document.getElementById('cat-' + catToAnchor(b.dataset.cat)) === document.getElementById(activeCat);
      b.classList.toggle('active', isActive);
      if (isActive && activeQuickNavCategory !== b.dataset.cat) {
        activeQuickNavCategory = b.dataset.cat;
        keepQuickNavButtonVisible(b);
      }
    });
  }

  function catToAnchor(cat) {
    return cat.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }

  function scrollCategoryIntoView(element) {
    if (!element) return;
    element.scrollIntoView({ behavior: 'auto', block: 'start' });
  }

  function ensureCategoryRendered(categoryName) {
    var anchorId = 'cat-' + catToAnchor(categoryName);
    var existing = document.getElementById(anchorId);
    if (existing) return existing;

    while (shown < filtered.length) {
      var before = shown;
      showMore();
      existing = document.getElementById(anchorId);
      if (existing || shown === before) break;
    }

    return existing;
  }

  function jumpToCategory(categoryName) {
    var element = ensureCategoryRendered(categoryName);
    if (element) scrollCategoryIntoView(element);
  }

  /* ===== RENDERING ===== */
  var lastRenderedCat = '';

  function showMore() {
    var list = document.getElementById('papers-list');
    var end = Math.min(shown + PAGE_SIZE, filtered.length);
    for (var i = shown; i < end; i++) {
      if (categoryView) {
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
    card.dataset.num = p.number;
    card.id = 'paper-' + p.number;

    var r = isRead(p.number), s = isStar(p.number);
    if (r) card.classList.add('read-dimmed');

    var h = '<div class="paper-card-header">';
    h += '<span class="paper-number">#' + p.number + '</span>';
    h += '<div class="paper-heading">';
    h += '<div class="paper-title has-modal">' + esc(p.title) + '</div>';
    if (p.published) {
      h += '<span class="badge-published">PR</span>';
    }
    h += '</div>';
    h += '<div class="paper-actions">';
    h += '<button class="paper-action-btn btn-read' + (r ? ' active-read' : '') + '" data-action="read" aria-label="' + (r ? 'Mark as unread' : 'Mark as read') + '" title="' + (r ? 'Mark as unread' : 'Mark as read') + '">' + getReadIcon(r) + '</button>';
    h += '<button class="paper-action-btn btn-star' + (s ? ' active-star' : '') + '" data-action="star" aria-label="' + (s ? 'Remove from favorites' : 'Add to favorites') + '" title="' + (s ? 'Remove from favorites' : 'Add to favorites') + '">' + (s ? '\u2605' : '\u2606') + '</button>';
    h += '<button class="paper-action-btn btn-share" data-action="share" aria-label="Share paper" title="Share paper"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><polyline points="16 6 12 2 8 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="2" x2="12" y2="15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>';
    h += '</div>';
    h += '</div>';

    h += '<div class="paper-meta">';
    h += '<span class="author-name">' + esc(getAuthorDisplayValue(p.authors)) + '</span>';
    if (p.source_date) h += '<span class="date-text">' + esc(p.source_date) + '</span>';
    h += '</div>';

    if (p.summary) {
      h += '<div class="paper-summary md-content">' + renderMd(p.summary, true) + '</div>';
    }

    if (p.categories && p.categories.length) {
      h += '<div class="paper-badges">';
      p.categories.forEach(function(c) {
        var dataCat = labelToId[c] || 'other';
        h += '<span class="badge" data-cat="' + dataCat + '">' + esc(c) + '</span>';
      });
      h += '</div>';
    }

    var linkInfo = getPsyArxivLinkInfo(p);
    if (linkInfo) {
      h += '<div class="paper-link-wrap"><a href="' + esc(linkInfo.href) + '" target="_blank" rel="noopener" class="paper-osf-link" title="' + esc(linkInfo.title) + '">' + linkInfo.label + '</a></div>';
    }

    if (p.published && p.published !== 'false' && p.published !== false) {
      h += '<div class="paper-published-text">\u2714 Peer reviewed: ' + linkifyText(p.published) + '</div>';
    }

    card.innerHTML = h;
    renderKaTeXInContainer(card);

    // Title click -> modal
    card.querySelector('.paper-title').addEventListener('click', function() { openModal(p); });

    // Read / Star toggle buttons
    card.querySelector('.btn-read').addEventListener('click', function(e) {
      e.stopPropagation();
      toggleRead(p.number);
    });
    card.querySelector('.btn-star').addEventListener('click', function(e) {
      e.stopPropagation();
      toggleStar(p.number);
    });
    card.querySelector('.btn-share').addEventListener('click', function(e) {
      e.stopPropagation();
      sharePaper(p);
    });

    return card;
  }

  /* ===== MODAL ===== */
  function openModal(p) {
    var modal = document.getElementById('paper-modal');
    var body = document.getElementById('modal-body');
    var r = isRead(p.number), s = isStar(p.number);

    var h = '<div class="modal-title">' + esc(p.title) + '</div>';
    h += '<div class="modal-meta"><span class="author-name">' + esc(getAuthorDisplayValue(p.authors)) + '</span>';
    if (p.source_date) h += ' &middot; ' + esc(p.source_date);
    h += '</div>';

    if (p.categories && p.categories.length) {
      h += '<div class="paper-badges" style="margin-bottom:12px;">';
      p.categories.forEach(function(c) {
        var dataCat = labelToId[c] || 'other';
        h += '<span class="badge" data-cat="' + dataCat + '">' + esc(c) + '</span>';
      });
      if (p.published) h += '<span class="badge-published">PR</span>';
      h += '</div>';
    }

    if (p.summary) {
      h += '<div class="modal-section"><div class="modal-section-label">Summary</div><div class="modal-section-text md-content">' + renderMd(p.summary) + '</div></div>';
    }
    if (p.clinical_insight) {
      h += '<div class="modal-section"><div class="modal-section-label">Clinical Insight</div><div class="modal-section-text md-content">' + renderMd(p.clinical_insight) + '</div></div>';
    }
    if (p.relevant_for) {
      h += '<div class="modal-section"><div class="modal-section-label">Relevant For</div><div class="modal-section-text md-content">' + renderMd(p.relevant_for) + '</div></div>';
    }
    if (p.methodology_note) {
      h += '<div class="modal-section methodology-section">';
      h += '<button class="methodology-toggle" type="button"><span class="methodology-toggle-icon">▶</span> Methodology Note</button>';
      h += '<div class="methodology-content md-content" style="display:none;">' + renderMd(p.methodology_note) + '</div>';
      h += '</div>';
    }
    if (p.published && p.published !== 'false' && p.published !== false) {
      h += '<div class="modal-section"><div class="modal-section-label">Published</div><div class="modal-section-text">' + linkifyText(p.published) + '</div></div>';
    }

    h += '<div class="modal-actions">';
    var modalLinkInfo = getPsyArxivLinkInfo(p);
    if (modalLinkInfo) {
      h += '<a class="modal-link" href="' + esc(modalLinkInfo.href) + '" target="_blank" rel="noopener" title="' + esc(modalLinkInfo.title) + '">' + modalLinkInfo.modalLabel + '</a>';
    }
    h += '<button class="modal-share-btn" id="modal-share-btn" type="button">Share</button>';
    h += '</div>';

    body.innerHTML = h;
    renderKaTeXInContainer(body);
    document.getElementById('modal-share-btn').addEventListener('click', function() { sharePaper(p); });
    // Methodology toggle
    var methToggle = body.querySelector('.methodology-toggle');
    if (methToggle) {
      methToggle.addEventListener('click', function() {
        var content = this.nextElementSibling;
        var icon = this.querySelector('.methodology-toggle-icon');
        var isOpen = content.style.display !== 'none';
        content.style.display = isOpen ? 'none' : 'block';
        icon.textContent = isOpen ? '▶' : '▼';
      });
    }
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
    document.getElementById('stat-total').textContent = papers.length;
    document.getElementById('stat-shown').textContent = filtered.length;
  }

  /* ===== SEARCH ===== */
  var searchTimer;
  var searchInput = document.getElementById('search-input');
  var searchClear = document.getElementById('search-clear');

  function syncSearchClearButton() {
    searchClear.classList.toggle('visible', !!searchInput.value);
  }

  searchInput.addEventListener('input', function() {
    clearTimeout(searchTimer);
    var val = this.value;
    syncSearchClearButton();
    searchTimer = setTimeout(function() {
      searchQuery = val;
      applyFilters();
      saveHash();
    }, 200);
  });

  searchClear.addEventListener('click', function() {
    searchInput.value = '';
    searchQuery = '';
    syncSearchClearButton();
    applyFilters();
    saveHash();
    searchInput.focus();
  });

  /* ===== SORT ===== */
  document.getElementById('sort-select').addEventListener('change', function() {
    sortMode = this.value;
    lastRenderedCat = '';
    applyFilters();
    saveHash();
  });

  document.getElementById('category-view-toggle').addEventListener('click', function() {
    categoryView = !categoryView;
    this.classList.toggle('active', categoryView);
    this.setAttribute('aria-pressed', categoryView ? 'true' : 'false');
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
    if (categoryView) state.view = 'category';
    var hash = '#' + Object.keys(state).map(function(k) { return k + '=' + encodeURIComponent(state[k]); }).join('&');
    suppressHashSync = true;
    history.replaceState(null, '', hash);
    setTimeout(function() { suppressHashSync = false; }, 0);
  }

  function resetStateToDefaults() {
    searchQuery = '';
    sortMode = 'newest';
    categoryView = false;
    pendingSharedPaperNumber = null;
    CATEGORIES.forEach(function(c) { activeCats[c.id] = true; });
    document.getElementById('search-input').value = '';
    document.getElementById('sort-select').value = 'newest';
    document.getElementById('category-view-toggle').classList.remove('active');
    document.getElementById('category-view-toggle').setAttribute('aria-pressed', 'false');
    syncCheckboxes();
    syncSearchClearButton();
  }

  function applyStateFromHash() {
    resetStateToDefaults();
    var hash = location.hash.slice(1);
    if (!hash) return;
    var params = {};
    hash.split('&').forEach(function(pair) {
      var parts = pair.split('=');
      if (parts.length === 2) params[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1]);
    });
    if (params.paper) {
      var paperNumber = parseInt(params.paper, 10);
      if (!isNaN(paperNumber)) pendingSharedPaperNumber = paperNumber;
    }
    if (params.q) { searchQuery = params.q; document.getElementById('search-input').value = params.q; }
    if (params.off) { params.off.split(',').forEach(function(c) { activeCats[c] = false; }); syncCheckboxes(); }
    if (params.sort === 'category') {
      categoryView = true;
    } else if (params.sort) {
      sortMode = params.sort;
      document.getElementById('sort-select').value = sortMode;
    }
    if (params.view === 'category') {
      categoryView = true;
    }
    if (categoryView) {
      var toggle = document.getElementById('category-view-toggle');
      toggle.classList.add('active');
      toggle.setAttribute('aria-pressed', 'true');
    }
    syncSearchClearButton();
  }

  window.addEventListener('hashchange', function() {
    if (suppressHashSync || !papers.length) return;
    closeModal();
    applyStateFromHash();
    applyFilters();
  });

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

  /* ===== MARKDOWN + LATEX RENDERER ===== */
  var MD_ALLOWED = /^([a-z0-9]+(?:\s+[a-z\-]+)*)$/i;
  function renderMd(text, forCard) {
    if (!text) return '';
    // 1. Escape HTML first (XSS safety)
    var html = esc(text);
    // 2. Protect display math $$...$$
    var displayMaths = [];
    html = html.replace(/\$\$([\s\S]*?)\$\$/g, function(m, inner) {
      displayMaths.push(inner);
      return '%%DM' + (displayMaths.length - 1) + '%%';
    });
    // 3. Protect inline math $...$
    var inlineMaths = [];
    html = html.replace(/\$([\s\S]*?)\$/g, function(m, inner) {
      inlineMaths.push(inner);
      return '%%IM' + (inlineMaths.length - 1) + '%%';
    });
    // 4. Bold **text** and __text__
    html = html.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
    html = html.replace(/__(.+?)__/g, '<b>$1</b>');
    // 5. Italic *text* and _text_
    html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
    // 6. Bullet lists: lines starting with - 
    html = html.replace(/(?:^|<br>)\s*[-*]\s+([^<]*(?:<[^>]*>[^<]*)*)/gm, function(m, item) {
      return '<li>' + item.trim() + '</li>';
    });
    // Wrap consecutive <li> in <ul>
    html = html.replace(/((?:<li>[\s\S]*?<\/li>\s*)+)/g, '<ul>$1</ul>');
    // 7. Newlines to <br> (but not inside <ul>)
    html = html.replace(/\n/g, '<br>');
    // 8. Restore math placeholders with KaTeX spans
    for (var i = 0; i < displayMaths.length; i++) {
      html = html.replace('%%DM' + i + '%%', '<span class="katex-display" data-math="' + esc(displayMaths[i]) + '"></span>');
    }
    for (var j = 0; j < inlineMaths.length; j++) {
      html = html.replace('%%IM' + j + '%%', '<span class="katex-inline" data-math="' + esc(inlineMaths[j]) + '"></span>');
    }
    // 9. Sanitize: strip any tags not in whitelist
    var whitelist = ['b','i','em','strong','br','ul','ol','li','p','span','sub','sup'];
    html = html.replace(/<\/?([a-z][a-z0-9]*)\b[^>]*>/gi, function(tag, name) {
      name = name.toLowerCase();
      // Allow katex spans
      if (name === 'span') {
        var cls = tag.match(/class="([^"]+)"/);
        if (cls && (cls[1].indexOf('katex') >= 0)) return tag;
      }
      if (whitelist.indexOf(name) >= 0) return tag;
      return '';
    });
    return html;
  }
  // Render KaTeX in a container after DOM insert
  function renderKaTeXInContainer(el) {
    if (typeof katex === 'undefined') return;
    var inlines = el.querySelectorAll('.katex-inline');
    for (var i = 0; i < inlines.length; i++) {
      var math = inlines[i].getAttribute('data-math');
      try { katex.render(math, inlines[i], { throwOnError: false, displayMode: false }); } catch(e) { inlines[i].textContent = math; }
    }
    var displays = el.querySelectorAll('.katex-display');
    for (var j = 0; j < displays.length; j++) {
      var dmath = displays[j].getAttribute('data-math');
      try { katex.render(dmath, displays[j], { throwOnError: false, displayMode: true }); } catch(e) { displays[j].textContent = dmath; }
    }
  }
})();
