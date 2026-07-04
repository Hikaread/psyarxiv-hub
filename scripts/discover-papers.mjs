#!/usr/bin/env node

/**
 * Discover new PsyArXiv preprints from the OSF API - lightweight version.
 * Fetches paper metadata without contributors for initial screening.
 */

const API_BASE = 'https://api.osf.io/v2';
const PAUSE_MS = 300;
const LATEST_PROCESSED = '2026-07-01';
const OUTPUT_FILE = '/home/z/my-project/scripts/discovered-papers.json';

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

async function main() {
  console.error(`Discovering PsyArXiv preprints since ${LATEST_PROCESSED}...`);
  
  const allPapers = [];
  let url = `${API_BASE}/preprints/?filter[provider]=psyarxiv&sort=date_created&filter[date_created][gt]=${LATEST_PROCESSED}T00:00:00&page[size]=100`;
  
  let page = 0;
  while (url) {
    page++;
    console.error(`Fetching page ${page}...`);
    const payload = await fetchJson(url);
    const items = payload.data || [];
    
    for (const item of items) {
      allPapers.push({
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
    
    url = payload.links?.next || null;
    if (items.length < 100) break;
  }
  
  // Deduplicate by compact OSF ID
  const seen = new Set();
  const deduped = allPapers.filter(p => {
    const compact = p.osf_id.replace(/_v\d+$/i, '');
    if (seen.has(compact)) return false;
    seen.add(compact);
    return true;
  });
  
  const fs = await import('fs');
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(deduped, null, 2) + '\n', 'utf8');
  
  console.log(JSON.stringify({
    discovered: allPapers.length,
    deduplicated: deduped.length,
    output: OUTPUT_FILE
  }, null, 2));
}

main().catch(err => { console.error(err); process.exitCode = 1; });