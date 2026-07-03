#!/usr/bin/env node

/**
 * Fetch full details for the second batch of accepted papers.
 */

const API_BASE = 'https://api.osf.io/v2';
const PAUSE_MS = 300;

const CANDIDATES = [
  'w8j2d',  // Therapy waitlist single-session intervention RCT
  'q2v5k',  // Dyslexia mental health intervention (Clever Kids)
  'c86da',  // Mindfulness dose-response RCT
  'zxt3g',  // CBT for bipolar re-analysis
  '4fkn2',  // Gaming disorder meta-synthesis
  'dr7um',  // Trauma-sensitive yoga indigenous perspectives
  '5u67v',  // Emotion regulation quadratic patterns
];

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function fetchJson(url) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const resp = await fetch(url, { headers: { 'Accept': 'application/vnd.api+json' } });
    if (resp.ok) { if (PAUSE_MS > 0) await sleep(PAUSE_MS); return resp.json(); }
    if (resp.status === 429 && attempt < 2) { await sleep((attempt+1) * 3000); continue; }
    throw new Error(`HTTP ${resp.status} for ${url}`);
  }
}

async function fetchContributors(preprintId) {
  const url = `${API_BASE}/preprints/${encodeURIComponent(preprintId)}/contributors/?page[size]=50&embed=users`;
  const payload = await fetchJson(url);
  return (payload.data || [])
    .filter(item => item?.attributes?.bibliographic !== false)
    .map(item => item?.embeds?.users?.data?.attributes?.full_name)
    .filter(Boolean);
}

async function fetchPreprintFull(compactId) {
  const url = `${API_BASE}/preprints/?filter[provider]=psyarxiv&filter[id]=${encodeURIComponent(compactId)}&page[size]=10`;
  const payload = await fetchJson(url);
  const items = (payload.data || []).filter(i => i.id.replace(/_v\d+$/i,'') === compactId.toLowerCase());
  if (!items.length) return null;
  items.sort((a,b) => {
    const va = parseInt(a.id.split('_v')[1] || '0');
    const vb = parseInt(b.id.split('_v')[1] || '0');
    return vb - va;
  });
  return items[0];
}

const fs = await import('fs');
const discovered = JSON.parse(fs.readFileSync('/home/z/my-project/scripts/discovered-papers.json', 'utf8'));
const results = [];

for (const cid of CANDIDATES) {
  console.error(`Processing ${cid}...`);
  const discPaper = discovered.find(p => p.osf_id.replace(/_v\d+$/i,'') === cid);
  if (!discPaper) { console.error(`  Not found in discovered data`); continue; }
  
  try {
    const fullRecord = await fetchPreprintFull(cid);
    const latestId = fullRecord ? fullRecord.id : discPaper.osf_id;
    const authors = await fetchContributors(latestId);
    
    results.push({
      osf_id: latestId,
      compact_id: cid,
      title: fullRecord?.attributes?.title || discPaper.title,
      authors: authors.join(', '),
      date_created: fullRecord?.attributes?.date_created || discPaper.date_created,
      date_modified: fullRecord?.attributes?.date_modified || '',
      description: fullRecord?.attributes?.description || discPaper.description,
      doi: fullRecord?.attributes?.doi || discPaper.doi,
      preprint_doi: fullRecord?.attributes?.preprint_doi || discPaper.preprint_doi,
      subjects: (fullRecord?.attributes?.subjects || discPaper.subjects || []).map(s => s.text || s),
    });
    
    console.error(`  Done: ${authors.length} authors`);
  } catch(e) {
    console.error(`  Error: ${e.message}`);
    results.push({
      osf_id: discPaper.osf_id,
      compact_id: cid,
      title: discPaper.title,
      authors: '',
      date_created: discPaper.date_created,
      description: discPaper.description,
      error: e.message
    });
  }
}

fs.writeFileSync('/home/z/my-project/scripts/batch2-details.json', JSON.stringify(results, null, 2) + '\n', 'utf8');
console.log(JSON.stringify({ processed: CANDIDATES.length, succeeded: results.filter(r=>!r.error).length }, null, 2));