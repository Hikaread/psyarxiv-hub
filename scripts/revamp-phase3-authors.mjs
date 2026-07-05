/**
 * Fetch authors from OSF API for papers with Unknown authors
 * Uses concurrent fetching with Node.js fetch
 */

import { readFileSync, writeFileSync } from 'fs';

const papersPath = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const papers = JSON.parse(readFileSync(papersPath, 'utf-8'));

const needAuthors = papers.filter(p => p.osf_id && (!p.authors || p.authors === 'Unknown'));
console.log(`Papers needing authors: ${needAuthors.length}`);

if (needAuthors.length === 0) process.exit(0);

const userCache = new Map();

async function fetchJSON(url) {
  const resp = await fetch(url, {
    headers: { 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0' },
    signal: AbortSignal.timeout(10000)
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

async function getUserName(userId) {
  if (userCache.has(userId)) return userCache.get(userId);
  try {
    const data = await fetchJSON(`https://api.osf.io/v2/users/${userId}/`);
    const name = data.data?.attributes?.full_name?.trim();
    if (name) userCache.set(userId, name);
    return name;
  } catch {
    return null;
  }
}

async function fetchAuthors(osfId) {
  const baseId = osfId.replace(/_v\d+$/, '');
  
  // First get contributor list
  let contribData;
  try {
    contribData = await fetchJSON(
      `https://api.osf.io/v2/preprints/${baseId}/contributors/?page[size]=50`
    );
  } catch (e) {
    return null;
  }
  
  const contributors = contribData.data || [];
  if (contributors.length === 0) return null;
  
  // Build (index, userId) pairs
  const pairs = contributors
    .map(c => ({
      index: c.attributes?.index ?? 999,
      userId: c.relationships?.users?.data?.id
    }))
    .filter(p => p.userId);
  
  pairs.sort((a, b) => a.index - b.index);
  
  // Fetch names concurrently (max 5 at a time)
  const names = [];
  const CONCURRENCY = 5;
  
  for (let i = 0; i < pairs.length; i += CONCURRENCY) {
    const batch = pairs.slice(i, i + CONCURRENCY);
    const results = await Promise.all(
      batch.map(p => getUserName(p.userId))
    );
    for (const name of results) {
      if (name) names.push(name);
    }
  }
  
  if (names.length === 0) return null;
  
  let result = names.slice(0, 10).join(', ');
  if (names.length > 10) result += ', et al.';
  return result;
}

// Process papers concurrently (max 3 at a time)
const CONCURRENCY = 3;
let fetched = 0, failed = 0;
const results = new Map();

for (let i = 0; i < needAuthors.length; i += CONCURRENCY) {
  const batch = needAuthors.slice(i, i + CONCURRENCY);
  
  const outcomes = await Promise.allSettled(
    batch.map(async (paper) => {
      const authors = await fetchAuthors(paper.osf_id);
      return { paper, authors };
    })
  );
  
  for (const outcome of outcomes) {
    if (outcome.status === 'fulfilled' && outcome.value.authors) {
      results.set(outcome.value.paper.number, outcome.value.authors);
      fetched++;
      const d = outcome.value.authors.length > 55 ? outcome.value.authors.slice(0, 55) + '...' : outcome.value.authors;
      console.log(`✓ #${outcome.value.paper.number}: ${d}`);
    } else {
      failed++;
      const num = outcome.status === 'fulfilled' ? outcome.value.paper.number : '?';
      console.log(`✗ #${num}`);
    }
  }
  
  // Small delay between batches
  if (i + CONCURRENCY < needAuthors.length) {
    await new Promise(r => setTimeout(r, 300));
  }
}

console.log(`\n=== Fetched ${fetched}, Failed ${failed} ===`);

// Apply updates
for (const p of papers) {
  if (results.has(p.number)) {
    p.authors = results.get(p.number);
  }
}

writeFileSync(papersPath, JSON.stringify(papers, null, 2) + '\n');
console.log(`Saved ${papers.length} papers`);