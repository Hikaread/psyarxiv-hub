#!/usr/bin/env node

/**
 * Discover new PsyArXiv preprints from the OSF API.
 * Strategy: bulk-paginated sweep through ALL psyarxiv preprints,
 * checking each against seen-compact-ids.json.
 * Uses page[offset] to skip pages known to be fully seen (optimization).
 * Stops when MIN_UNSEEN unseen papers are collected OR MAX_PAGES reached.
 */

const API_BASE = 'https://api.osf.io/v2';
const PAUSE_MS = 0;
const MIN_UNSEEN = 15;
const MAX_PAGES = 15;
const SEEN_IDS_FILE = '/home/z/my-project/psyarxiv-hub/data/seen-compact-ids.json';
const OUTPUT_FILE = '/home/z/my-project/psyarxiv-hub/curation/discovered-papers.json';
const FRONTIER_FILE = '/home/z/my-project/psyarxiv-hub/curation/discover-frontier.json';

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

  // Load frontier (last page cursor we reached)
  let frontier = { page: 1, url: null };
  try {
    frontier = JSON.parse(fs.readFileSync(FRONTIER_FILE, 'utf8'));
    console.error(`Resuming from frontier page ${frontier.page}`);
  } catch {
    console.error('No frontier file, starting from page 1');
  }

  // Fetch first page (or resume from frontier)
  let pageUrl = frontier.url ||
    `${API_BASE}/preprints/?filter[provider]=psyarxiv&sort=-date_created&page[size]=100`;

  const allUnseen = [];
  const globalSeen = new Set();
  let pageNum = frontier.page - 1;
  let pagesAllSeen = 0;
  let stopReason = '';

  while (pageNum < frontier.page + MAX_PAGES) {
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

    // Save frontier for next run
    const nextUrl = payload.links?.next || null;
    fs.writeFileSync(FRONTIER_FILE, JSON.stringify({ page: pageNum + 1, url: nextUrl }) + '\n', 'utf8');

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
    pagesScanned: pageNum - (frontier.page - 1),
    currentPage: pageNum,
    totalUnseen: allUnseen.length,
    output: OUTPUT_FILE
  }, null, 2));
}

main().catch(err => { console.error(err); process.exitCode = 1; });
