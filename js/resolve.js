(function() {
  'use strict';

  var API_BASE = 'https://api.osf.io/v2';
  var statusEl = document.getElementById('resolver-status');
  var paperEl = document.getElementById('resolver-paper');
  var actionsEl = document.getElementById('resolver-actions');

  function setStatus(text) {
    statusEl.textContent = text;
  }

  function esc(value) {
    var node = document.createElement('div');
    node.textContent = value || '';
    return node.innerHTML;
  }

  function normalizeText(value) {
    return String(value || '')
      .toLowerCase()
      .replace(/&/g, ' and ')
      .replace(/[^a-z0-9]+/g, ' ')
      .replace(/\b(a|an|and|for|in|of|on|the|to|with)\b/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function tokenize(value) {
    return normalizeText(value).split(' ').filter(Boolean);
  }

  function similarity(left, right) {
    var leftTokens = tokenize(left);
    var rightTokens = tokenize(right);
    if (!leftTokens.length || !rightTokens.length) return 0;
    var rightSet = {};
    rightTokens.forEach(function(token) { rightSet[token] = true; });
    var overlap = 0;
    leftTokens.forEach(function(token) {
      if (rightSet[token]) overlap += 1;
    });
    return overlap / Math.max(leftTokens.length, rightTokens.length);
  }

  function getDirectPsyArxivUrlFromId(value) {
    if (!value) return '';
    return 'https://osf.io/preprints/psyarxiv/' + value;
  }

  function getQueryPaperNumber() {
    var params = new URLSearchParams(location.search);
    return parseInt(params.get('paper'), 10) || 0;
  }

  function renderPaper(paper) {
    paperEl.innerHTML = '<div class="resolver-title">' + esc(paper.title) + '</div>' +
      '<div class="resolver-meta">#' + esc(String(paper.number || '')) + '</div>';
  }

  function renderActions(items) {
    actionsEl.innerHTML = items.map(function(item) {
      return '<a class="resolver-link" href="' + esc(item.href) + '" target="_blank" rel="noopener">' + esc(item.label) + '</a>';
    }).join('');
  }

  function fetchJson(url) {
    return fetch(url, {
      headers: {
        accept: 'application/vnd.api+json'
      }
    }).then(function(response) {
      if (!response.ok) throw new Error('Request failed: ' + response.status);
      return response.json();
    });
  }

  function pickBestOsfCandidate(paper, candidates) {
    var best = null;
    candidates.forEach(function(candidate) {
      var title = candidate && candidate.attributes ? candidate.attributes.title : '';
      var description = candidate && candidate.attributes ? candidate.attributes.description : '';
      var score = similarity(paper.title, title) * 0.7 + similarity(paper.summary, description) * 0.3;
      if (!best || score > best.score) {
        best = { candidate: candidate, score: score };
      }
    });
    return best && best.score >= 0.55 ? best.candidate : null;
  }

  function searchOsfByTitle(paper) {
    var exactUrl = API_BASE + '/preprints/?filter[provider]=psyarxiv&filter[title]=' + encodeURIComponent(paper.title) + '&page[size]=10';
    return fetchJson(exactUrl).then(function(payload) {
      var exactItems = payload.data || [];
      if (exactItems.length === 1) return exactItems[0];
      if (exactItems.length > 1) return pickBestOsfCandidate(paper, exactItems);

      var searchTerms = tokenize(paper.title).concat(tokenize(paper.summary)).slice(0, 8).join(' ');
      if (!searchTerms) return null;
      var broadUrl = API_BASE + '/preprints/?filter[provider]=psyarxiv&filter[title]=' + encodeURIComponent(searchTerms) + '&page[size]=10';
      return fetchJson(broadUrl).then(function(broadPayload) {
        return pickBestOsfCandidate(paper, broadPayload.data || []);
      });
    });
  }

  function pickBestCrossrefItem(paper, items) {
    var best = null;
    items.forEach(function(item) {
      var doi = item && item.DOI ? String(item.DOI) : '';
      if (doi.toLowerCase().indexOf('10.31234/osf.io/') !== 0) return;
      var title = item.title && item.title.length ? item.title[0] : '';
      var score = similarity(paper.title, title);
      if (!best || score > best.score) {
        best = { item: item, score: score };
      }
    });
    return best && best.score >= 0.55 ? best.item : null;
  }

  function searchCrossref(paper) {
    var crossrefUrl = 'https://api.crossref.org/works?rows=10&query.title=' + encodeURIComponent(paper.title);
    return fetch(crossrefUrl).then(function(response) {
      if (!response.ok) throw new Error('Crossref failed: ' + response.status);
      return response.json();
    }).then(function(payload) {
      return pickBestCrossrefItem(paper, payload.message && payload.message.items ? payload.message.items : []);
    });
  }

  function redirectTo(url) {
    setStatus('Direct paper page found. Redirecting...');
    renderActions([{ href: url, label: 'Open paper now' }]);
    location.replace(url);
  }

  function showFallback(paper) {
    setStatus('A verified direct page could not be recovered automatically for this record.');
    renderActions([
      { href: 'https://osf.io/preprints/psyarxiv/?q=' + encodeURIComponent(paper.title), label: 'Search on PsyArXiv' },
      { href: 'https://scholar.google.com/scholar?q=' + encodeURIComponent(paper.title), label: 'Search in Google Scholar' }
    ]);
  }

  function resolvePaper(paper) {
    renderPaper(paper);

    if (paper.osf_id) {
      redirectTo(getDirectPsyArxivUrlFromId(paper.osf_id));
      return Promise.resolve();
    }

    return searchOsfByTitle(paper).then(function(candidate) {
      if (candidate && candidate.id) {
        redirectTo(getDirectPsyArxivUrlFromId(candidate.id));
        return;
      }
      return searchCrossref(paper).then(function(item) {
        var doi = item && item.DOI ? String(item.DOI) : '';
        var match = doi.match(/^10\.31234\/osf\.io\/([a-z0-9_]+)$/i);
        if (match) {
          redirectTo(getDirectPsyArxivUrlFromId(match[1]));
          return;
        }
        showFallback(paper);
      });
    }).catch(function() {
      showFallback(paper);
    });
  }

  fetch('data/papers.json')
    .then(function(response) { return response.json(); })
    .then(function(papers) {
      var paperNumber = getQueryPaperNumber();
      var paper = papers.find(function(item) { return item.number === paperNumber; });
      if (!paper) {
        setStatus('Paper record not found.');
        return;
      }
      return resolvePaper(paper);
    })
    .catch(function() {
      setStatus('Unable to load paper data.');
    });
})();
