#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const ROOT = process.cwd();
const DATA_PATH = path.join(ROOT, 'data', 'papers.json');
const OVERRIDES_PATH = path.join(ROOT, 'curation', 'osf-overrides.json');
const API_BASE = 'https://api.osf.io/v2';
const shouldWrite = process.argv.includes('--write');

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

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: {
      accept: 'application/vnd.api+json'
    }
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} for ${url}`);
  }
  return response.json();
}

async function fetchPreprintRecord(idOrCompact) {
  const queryUrl = `${API_BASE}/preprints/?filter[provider]=psyarxiv&filter[id]=${encodeURIComponent(compactOsfId(idOrCompact))}&page[size]=5`;
  const payload = await fetchJson(queryUrl);
  const candidates = payload.data || [];
  if (!candidates.length) return null;
  const exact = candidates.find((item) => String(item.id).toLowerCase() === String(idOrCompact).toLowerCase());
  return exact || candidates[0];
}

async function fetchContributorNames(preprintId) {
  const url = `${API_BASE}/preprints/${encodeURIComponent(preprintId)}/contributors/?page[size]=25&embed=users`;
  const payload = await fetchJson(url);
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
    const overrideId = overrideMap.get(Number(paper.number));
    if (overrideId) {
      paper.osf_id = overrideId;
      paper.link = buildCanonicalPsyArxivLink(overrideId);
    }

    const storedId = deriveStoredId(paper);
    if (!storedId) continue;

    try {
      const preprint = await fetchPreprintRecord(storedId);
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
