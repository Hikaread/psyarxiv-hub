#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const ROOT = process.cwd();
const DATA_PATH = path.join(ROOT, 'data', 'papers.json');
const OVERRIDES_PATH = path.join(ROOT, 'curation', 'osf-overrides.json');
const API_BASE = 'https://api.osf.io/v2';
const shouldWrite = process.argv.includes('--write');
const requestPauseMs = Number(process.env.PSYHUB_SYNC_PAUSE_MS || 250);
const numbersArg = process.argv.find((value) => value.startsWith('--numbers='));
const limitedNumbers = new Set(
  String(numbersArg || '')
    .replace('--numbers=', '')
    .split(',')
    .map((value) => Number(value.trim()))
    .filter(Number.isFinite)
);

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function compactOsfId(value) {
  return String(value || '').replace(/_v\d+$/i, '').trim();
}

function buildCanonicalPsyArxivLink(value) {
  return `https://osf.io/preprints/psyarxiv/${String(value || '').trim()}`;
}

function deriveStoredId(paper) {
  if (paper.osf_id) return String(paper.osf_id).trim();
  const link = String(paper.link || '').trim();
  const match = link.match(/osf\.io\/(?:preprints\/psyarxiv\/)?([a-z0-9_]+)/i);
  return match ? match[1] : '';
}

function formatDate(value) {
  if (!value) return '';
  const iso = String(value).slice(0, 10);
  const parts = iso.split('-');
  if (parts.length !== 3) return iso;
  return parts[2] + '.' + parts[1] + '.' + parts[0];
}

function sanitizeTitle(value, fallback) {
  const title = String(value || '').trim();
  const cleaned = title.replace(/^\d{3}:\s*Personal Data Not Found\s*[—-]\s*/i, '').trim();
  return cleaned || fallback;
}

async function fetchJson(url, headers = {}) {
  for (let attempt = 0; attempt < 4; attempt += 1) {
    const response = await fetch(url, {
      headers
    });
    if (response.ok) {
      if (requestPauseMs > 0) {
        await sleep(requestPauseMs);
      }
      return response.json();
    }
    if (response.status === 429 && attempt < 3) {
      const retryAfter = Number(response.headers.get('retry-after') || 0);
      const backoffMs = retryAfter > 0 ? retryAfter * 1000 : (attempt + 1) * 2000;
      await sleep(backoffMs);
      continue;
    }
    throw new Error(`HTTP ${response.status} for ${url}`);
  }
}

function normalizeText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\b(a|an|and|for|in|of|on|the|to|with|its|their|using|study|systematic|review|meta|analysis|clinical|psychological|paper|this|that|these|those|adults|adult|pilot|randomized|controlled|trial)\b/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function scoreText(left, right) {
  const leftTokens = new Set(normalizeText(left).split(' ').filter(Boolean));
  const rightTokens = new Set(normalizeText(right).split(' ').filter(Boolean));
  if (!leftTokens.size || !rightTokens.size) return 0;
  let overlap = 0;
  for (const token of leftTokens) {
    if (rightTokens.has(token)) overlap += 1;
  }
  return overlap / Math.max(leftTokens.size, rightTokens.size);
}

function getAuthorLastName(value) {
  return String(value || '')
    .split(/,|\s+/)
    .filter(Boolean)
    .slice(-1)[0]
    ?.toLowerCase() || '';
}

function extractOsfIdFromDoi(value) {
  const match = String(value || '').match(/^10\.31234\/osf\.io\/([a-z0-9_]+)$/i);
  return match ? match[1] : '';
}

async function fetchPreprintRecord(idOrCompact) {
  const queryUrl = `${API_BASE}/preprints/?filter[provider]=psyarxiv&filter[id]=${encodeURIComponent(compactOsfId(idOrCompact))}&page[size]=5`;
  const payload = await fetchJson(queryUrl, {
    accept: 'application/vnd.api+json'
  });
  const candidates = payload.data || [];
  if (!candidates.length) return null;
  const exact = candidates.find((item) => String(item.id).toLowerCase() === String(idOrCompact).toLowerCase());
  return exact || candidates[0];
}

async function queryCrossrefItems(paper, includeAuthor = true) {
  const author = getAuthorLastName(paper.authors);
  const queryTitle = encodeURIComponent(paper.title || '');
  const authorParam = includeAuthor && author ? `&query.author=${encodeURIComponent(author)}` : '';
  const queryUrl = `https://api.crossref.org/works?rows=12&query.title=${queryTitle}${authorParam}`;
  const payload = await fetchJson(queryUrl, {
    accept: 'application/json',
    'user-agent': 'psyarxiv-hub-link-recovery/1.0 (local sync)'
  });
  return payload.message?.items || [];
}

function pickBestCrossrefMatch(paper, items, minimumScore) {
  const author = getAuthorLastName(paper.authors);
  let best = null;
  for (const item of items) {
    const recoveredId = extractOsfIdFromDoi(item.DOI);
    if (!recoveredId) continue;
    const title = Array.isArray(item.title) ? item.title[0] : '';
    const titleScore = scoreText(paper.title, title);
    const summaryScore = scoreText(paper.summary, title);
    const authorBonus = author && JSON.stringify(item.author || []).toLowerCase().includes(author) ? 0.2 : 0;
    const combined = titleScore * 0.7 + summaryScore * 0.15 + authorBonus;
    if (!best || combined > best.score) {
      best = {
        id: recoveredId,
        score: combined
      };
    }
  }

  if (!best || best.score < minimumScore) return null;
  return best;
}

async function searchCrossrefPreprint(paper) {
  const authorItems = await queryCrossrefItems(paper, true);
  const withAuthor = pickBestCrossrefMatch(paper, authorItems, 0.32);
  if (withAuthor) {
    return fetchPreprintRecord(withAuthor.id);
  }

  const titleOnlyItems = await queryCrossrefItems(paper, false);
  const titleOnly = pickBestCrossrefMatch(paper, titleOnlyItems, 0.48);
  if (!titleOnly) return null;
  return fetchPreprintRecord(titleOnly.id);
}

async function fetchContributorNames(preprintId) {
  const url = `${API_BASE}/preprints/${encodeURIComponent(preprintId)}/contributors/?page[size]=25&embed=users`;
  const payload = await fetchJson(url, {
    accept: 'application/vnd.api+json'
  });
  return (payload.data || [])
    .filter((item) => item?.attributes?.bibliographic !== false)
    .map((item) => item?.embeds?.users?.data?.attributes?.full_name)
    .filter(Boolean);
}

async function loadOverrides() {
  try {
    return JSON.parse(await readFile(OVERRIDES_PATH, 'utf8'));
  } catch (error) {
    return [];
  }
}

async function main() {
  const papers = JSON.parse(await readFile(DATA_PATH, 'utf8'));
  const overrides = await loadOverrides();
  const overrideMap = new Map(overrides.map((item) => [Number(item.number), item.osf_id]));
  const changes = [];

  for (const paper of papers) {
    if (limitedNumbers.size && !limitedNumbers.has(Number(paper.number))) {
      continue;
    }

    const overrideId = overrideMap.get(Number(paper.number));
    if (overrideId) {
      paper.osf_id = overrideId;
      paper.link = buildCanonicalPsyArxivLink(overrideId);
    }

    const storedId = deriveStoredId(paper);
    if (!storedId) {
      if (!paper.authors || paper.authors === 'Unknown') continue;
      try {
        const recoveredPreprint = await searchCrossrefPreprint(paper);
        if (!recoveredPreprint) continue;
        paper.osf_id = recoveredPreprint.id;
        paper.link = buildCanonicalPsyArxivLink(recoveredPreprint.id);
      } catch (error) {
        changes.push({
          number: paper.number,
          error: error.message
        });
        continue;
      }
    }

    try {
      const preprint = await fetchPreprintRecord(deriveStoredId(paper));
      if (!preprint) continue;
      const authors = await fetchContributorNames(preprint.id);

      paper.osf_id = preprint.id;
      paper.link = buildCanonicalPsyArxivLink(preprint.id);
      paper.title = sanitizeTitle(preprint.attributes.title, paper.title);
      if (authors.length) {
        paper.authors = authors.join(', ');
      }
      if (preprint.attributes.date_created) {
        paper.date_posted = String(preprint.attributes.date_created).slice(0, 10);
        paper.source_date = formatDate(preprint.attributes.date_created);
      }

      changes.push({
        number: paper.number,
        osf_id: paper.osf_id,
        title: paper.title
      });
    } catch (error) {
      changes.push({
        number: paper.number,
        error: error.message
      });
    }
  }

  if (shouldWrite) {
    await writeFile(DATA_PATH, JSON.stringify(papers, null, 2) + '\n', 'utf8');
  }

  console.log(JSON.stringify({
    updated: changes.filter((item) => !item.error).length,
    errored: changes.filter((item) => item.error).length,
    wroteData: shouldWrite,
    sample: changes.slice(0, 20)
  }, null, 2));
}

main().catch((error) => {
  console.error(error.message || error);
  process.exitCode = 1;
});
