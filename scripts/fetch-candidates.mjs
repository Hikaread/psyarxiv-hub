#!/usr/bin/env node

/**
 * Fetch full details (contributors, PDF text) for shortlisted candidate papers.
 */

const API_BASE = 'https://api.osf.io/v2';
const PAUSE_MS = 300;

const CANDIDATES = [
  'edscr',  // Person-specific networks for chronic pain
  'qmz4v',  // Eating disorder network analysis
  'xfhek',  // Autistic fathers
  '5u67v',  // Emotion regulation quadratic patterns
  '4fkn2',  // Gaming disorder meta-synthesis
  'ntm9y',  // PTSD EMDR neural normalization
  'mgbq2',  // Childhood adversity sensitive periods
  'dr7um',  // Indigenous trauma-sensitive yoga
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

async function fetchPdfText(downloadUrl) {
  try {
    const resp = await fetch(downloadUrl);
    if (!resp.ok) return null;
    const buf = await resp.arrayBuffer();
    // Simple text extraction - look for text content in PDF
    const text = new TextDecoder('latin1').decode(buf);
    // Extract readable text between common PDF markers
    const textParts = [];
    const btRegex = /\(([^)]{10,})\)/g;
    let m;
    while ((m = btRegex.exec(text)) !== null) {
      const cleaned = m[1].replace(/[^a-zA-Z0-9\s.,;:!?'\-()]/g, ' ').replace(/\s+/g, ' ').trim();
      if (cleaned.length > 20) textParts.push(cleaned);
    }
    return textParts.join(' ').substring(0, 15000);
  } catch(e) {
    return null;
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
  // Find the latest version
  const url = `${API_BASE}/preprints/?filter[provider]=psyarxiv&filter[id]=${encodeURIComponent(compactId)}&page[size]=10`;
  const payload = await fetchJson(url);
  const items = (payload.data || []).filter(i => i.id.replace(/_v\d+$/i,'') === compactId.toLowerCase());
  if (!items.length) return null;
  
  // Get latest version
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
  
  // Find in discovered data
  const discPaper = discovered.find(p => p.osf_id.replace(/_v\d+$/i,'') === cid);
  if (!discPaper) { console.error(`  Not found in discovered data`); continue; }
  
  try {
    // Fetch full preprint record (latest version)
    const fullRecord = await fetchPreprintFull(cid);
    
    // Fetch contributors
    const latestId = fullRecord ? fullRecord.id : discPaper.osf_id;
    const authors = await fetchContributors(latestId);
    
    // Get PDF URL
    let pdfUrl = '';
    if (fullRecord?.links?.download) {
      pdfUrl = fullRecord.links.download;
    }
    
    // Try to get PDF text
    let pdfText = '';
    if (pdfUrl) {
      console.error(`  Fetching PDF for ${cid}...`);
      pdfText = await fetchPdfText(pdfUrl) || '';
    }
    
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
      link: discPaper.link || `https://osf.io/preprints/psyarxiv/${cid}`,
      pdf_url: pdfUrl,
      pdf_text_length: pdfText.length,
      pdf_text_sample: pdfText.substring(0, 8000),
      subjects: (fullRecord?.attributes?.subjects || discPaper.subjects || []).map(s => s.text || s),
    });
    
    console.error(`  Done: ${authors.length} authors, PDF text: ${pdfText.length} chars`);
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

fs.writeFileSync('/home/z/my-project/scripts/candidate-details.json', JSON.stringify(results, null, 2) + '\n', 'utf8');
console.log(JSON.stringify({ processed: CANDIDATES.length, succeeded: results.filter(r=>!r.error).length }, null, 2));