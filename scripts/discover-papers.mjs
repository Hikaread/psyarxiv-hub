#!/usr/bin/env node

/**
 * Discover new PsyArXiv preprints from the OSF API.
 * Scans newest pages first, checks against seen-compact-ids.json.
 * Stops when MIN_UNSEEN unseen papers are collected OR MAX_PAGES reached.
 */

const API_BASE = 'https://api.osf.io/v2';
const PAUSE_MS = 0;
const MIN_UNSEEN = 5;
const MAX_PAGES = 3;
const SEEN_IDS_FILE = '/home/z/my-project/psyarxiv-hub/data/seen-compact-ids.json';
const OUTPUT_FILE = '/home/z/my-project/psyarxiv-hub/curation/discovered-papers.json';
// FRONTIER_FILE removed — always start from page 1 (newest)

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchJson(url) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const response = await fetch(url, {
      headers: { 'Accept': 'application/vnd.api+json' }
    });
    if (response.ok) {
      if (PAUSE_MS > 0) await sleep(PAUSE_MS);
      return response.json();
    }
    if (response.status === 429 && attempt < 2) {
      await sleep((attempt + 1) * 3000);
      continue;
    }
    throw new Error(`HTTP ${response.status} for ${url}`);
  }
}

function stripVersion(osfId) {
  return (osfId || '').replace(/_v\d+$/i, '');
}

async function main() {
  const fs = await import('fs');

  // Load already-seen compact IDs
  let seenIds = new Set();
  try {
    const raw = JSON.parse(fs.readFileSync(SEEN_IDS_FILE, 'utf8'));
    for (const id of raw) seenIds.add(id.toLowerCase());
    console.error(`Loaded ${seenIds.size} seen IDs`);
  } catch {
    console.error('No seen-IDs file found, starting fresh');
  }

  // Always start from newest (page 1) — seen-compact-ids handles dedup
  let pageUrl =
    `${API_BASE}/preprints/?filter[provider]=psyarxiv&sort=-date_created&page[size]=100`;

  const allUnseen = [];
  const globalSeen = new Set();
  let pageNum = 0;
  let pagesAllSeen = 0;
  let stopReason = '';

  while (pageNum < MAX_PAGES) {
    pageNum++;
    console.error(`Page ${pageNum} — unseen so far: ${allUnseen.length}`);

    const payload = await fetchJson(pageUrl);
    const items = payload.data || [];
    let pageUnseen = 0;

    for (const item of items) {
      const compact = stripVersion(item.id).toLowerCase();
      if (globalSeen.has(compact)) continue;
      globalSeen.add(compact);
      if (seenIds.has(compact)) continue;
      pageUnseen++;
      allUnseen.push({
        osf_id: item.id,
        title: item.attributes?.title || '',
        date_created: item.attributes?.date_created || '',
        date_modified: item.attributes?.date_modified || '',
        description: (item.attributes?.description || '').substring(0, 2000),
        doi: item.attributes?.doi || '',
        preprint_doi: item.attributes?.preprint_doi || '',
        subjects: (item.attributes?.subjects || []).map(s => s.text || s),
        link: item.links?.html || '',
      });
    }

    console.error(`  ${pageUnseen} unseen / ${items.length} total`);

    if (pageUnseen > 0) {
      pagesAllSeen = 0;
    } else {
      pagesAllSeen++;
    }

    const nextUrl = payload.links?.next || null;

    if (!nextUrl) {
      stopReason = `Reached end of all pages (page ${pageNum})`;
      console.error(`  ✓ ${stopReason}`);
      break;
    }

    if (allUnseen.length >= MIN_UNSEEN) {
      stopReason = `Collected ${allUnseen.length} unseen papers`;
      console.error(`  ✓ ${stopReason}`);
      break;
    }

    pageUrl = nextUrl;
  }

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(allUnseen, null, 2) + '\n', 'utf8');

  console.log(JSON.stringify({
    stopReason,
    pagesScanned: pageNum,
    currentPage: pageNum,
    totalUnseen: allUnseen.length,
    output: OUTPUT_FILE
  }, null, 2));
}

main().catch(err => { console.error(err); process.exitCode = 1; });
