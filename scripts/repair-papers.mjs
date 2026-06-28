#!/usr/bin/env node

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const ROOT = process.cwd();
const DATA_PATH = path.join(ROOT, 'data', 'papers.json');
const REPORT_PATH = path.join(ROOT, 'data', 'papers-repair-report.json');
const API_BASE = 'https://api.osf.io/v2';

const args = new Set(process.argv.slice(2));
const shouldWrite = args.has('--write');
const verbose = args.has('--verbose');

function normalizeTitle(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\b(a|an|and|for|in|of|on|the|to|with)\b/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function titleSimilarity(left, right) {
  const leftTokens = new Set(normalizeTitle(left).split(' ').filter(Boolean));
  const rightTokens = new Set(normalizeTitle(right).split(' ').filter(Boolean));
  if (!leftTokens.size || !rightTokens.size) return 0;
  let intersection = 0;
  for (const token of leftTokens) {
    if (rightTokens.has(token)) intersection += 1;
  }
  return intersection / Math.max(leftTokens.size, rightTokens.size);
}

function compactOsfId(value) {
  return String(value || '').replace(/_v\d+$/i, '');
}

function formatDate(value) {
  if (!value) return '';
  return String(value).slice(0, 10);
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

async function fetchContributors(preprintId) {
  const url = `${API_BASE}/preprints/${encodeURIComponent(preprintId)}/contributors/?page[size]=25&embed=users`;
  const payload = await fetchJson(url);
  return (payload.data || [])
    .filter((item) => item?.attributes?.bibliographic !== false)
    .map((item) => item?.embeds?.users?.data?.attributes?.full_name)
    .filter(Boolean);
}

async function fetchPreprintById(osfLink) {
  const idMatch = String(osfLink || '').match(/osf\.io\/([a-z0-9]+)(?:\/)?/i);
  if (!idMatch) return null;
  const compactId = idMatch[1].toLowerCase();
  const searchUrl = `${API_BASE}/preprints/?filter[provider]=psyarxiv&filter[id]=${encodeURIComponent(compactId)}&page[size]=5`;
  const payload = await fetchJson(searchUrl);
  const direct = (payload.data || []).find((item) => compactOsfId(item.id) === compactId);
  return direct || null;
}

async function searchCandidates(title) {
  const exactUrl = `${API_BASE}/preprints/?filter[provider]=psyarxiv&filter[title]=${encodeURIComponent(title)}&page[size]=10`;
  const exactPayload = await fetchJson(exactUrl);
  const exactItems = exactPayload.data || [];
  if (exactItems.length) return exactItems;

  const significantWords = normalizeTitle(title).split(' ').filter(Boolean).slice(0, 6);
  if (!significantWords.length) return [];
  const broadQuery = significantWords.join(' ');
  const broadUrl = `${API_BASE}/preprints/?filter[provider]=psyarxiv&filter[title]=${encodeURIComponent(broadQuery)}&page[size]=10`;
  const broadPayload = await fetchJson(broadUrl);
  return broadPayload.data || [];
}

function pickBestCandidate(paper, candidates) {
  let best = null;
  for (const candidate of candidates) {
    const candidateTitle = candidate?.attributes?.title || '';
    const score = titleSimilarity(paper.title, candidateTitle);
    if (!best || score > best.score) {
      best = { candidate, score };
    }
  }
  if (!best) return null;
  if (normalizeTitle(paper.title) === normalizeTitle(best.candidate.attributes.title)) return best;
  if (best.score >= 0.82) return best;
  return null;
}

async function enrichPaper(paper) {
  let match = null;
  let strategy = 'none';

  if (paper.link) {
    const byId = await fetchPreprintById(paper.link);
    if (byId) {
      match = byId;
      strategy = 'link-id';
    }
  }

  if (!match) {
    const candidates = await searchCandidates(paper.title);
    const best = pickBestCandidate(paper, candidates);
    if (best) {
      match = best.candidate;
      strategy = normalizeTitle(paper.title) === normalizeTitle(best.candidate.attributes.title) ? 'title-exact' : 'title-fuzzy';
    }
  }

  if (!match) {
    return {
      paper,
      updated: null,
      strategy,
      resolved: false,
      reason: 'No confident PsyArXiv match'
    };
  }

  const contributors = await fetchContributors(match.id);
  const updated = {
    ...paper,
    link: `https://osf.io/${compactOsfId(match.id)}`,
    source_date: formatDate(match.attributes.date_created) || paper.source_date,
    authors: contributors.join(', ') || paper.authors
  };

  return {
    paper,
    updated,
    strategy,
    resolved: true,
    reason: ''
  };
}

async function main() {
  const raw = await readFile(DATA_PATH, 'utf8');
  const papers = JSON.parse(raw);
  const report = {
    scanned: papers.length,
    resolved: [],
    unresolved: []
  };

  const updatedPapers = [];
  for (const paper of papers) {
    const needsRepair = !paper.link || !paper.authors || paper.authors === 'Unknown';
    if (!needsRepair) {
      updatedPapers.push(paper);
      continue;
    }

    try {
      const result = await enrichPaper(paper);
      if (result.resolved) {
        updatedPapers.push(result.updated);
        report.resolved.push({
          number: paper.number,
          title: paper.title,
          strategy: result.strategy,
          link: result.updated.link,
          authors: result.updated.authors
        });
        if (verbose) {
          console.log(`resolved #${paper.number} via ${result.strategy}: ${result.updated.title}`);
        }
      } else {
        updatedPapers.push(paper);
        report.unresolved.push({
          number: paper.number,
          title: paper.title,
          reason: result.reason
        });
        if (verbose) {
          console.log(`unresolved #${paper.number}: ${paper.title}`);
        }
      }
    } catch (error) {
      updatedPapers.push(paper);
      report.unresolved.push({
        number: paper.number,
        title: paper.title,
        reason: error.message
      });
    }
  }

  await mkdir(path.dirname(REPORT_PATH), { recursive: true });
  await writeFile(REPORT_PATH, JSON.stringify(report, null, 2) + '\n', 'utf8');

  if (shouldWrite) {
    await writeFile(DATA_PATH, JSON.stringify(updatedPapers, null, 2) + '\n', 'utf8');
  }

  console.log(JSON.stringify({
    scanned: report.scanned,
    resolved: report.resolved.length,
    unresolved: report.unresolved.length,
    wroteData: shouldWrite,
    reportPath: path.relative(ROOT, REPORT_PATH)
  }));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
