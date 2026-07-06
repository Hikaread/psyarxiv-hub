/**
 * Fast matching: fetch titles for extra seen-IDs using concurrent Node.js requests
 * and match against 59 papers needing links.
 */

import { readFileSync, writeFileSync } from 'fs';

const seenIds = JSON.parse(readFileSync('/home/z/my-project/psyarxiv-hub/data/seen-compact-ids.json', 'utf-8'));
const papers = JSON.parse(readFileSync('/home/z/my-project/psyarxiv-hub/data/papers.json', 'utf-8'));

// Current osf_ids in papers
const currentIds = new Set();
for (const p of papers) {
  if (p.osf_id) currentIds.add(p.osf_id.replace(/_v\d+$/, ''));
}

// Extra IDs not in current papers
const extraIds = seenIds.filter(id => !currentIds.has(id.replace(/_v\d+$/, '')));

// Papers needing links
const needLink = papers.filter(p => !p.link && !p.osf_id);
const needTitles = new Map(needLink.map(p => [p.number, p.title.toLowerCase()]));

console.log(`Extra IDs: ${extraIds.length}, Papers needing links: ${needLink.length}`);

const stopWords = new Set('a an the and or for in of on to with by from as is are was were be been that this these those it its their our your my not but if while can will just also about how what which between into'.split(' '));

function getWords(title) {
  return new Set(
    title.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').split(/\s+/)
      .filter(w => w.length > 3 && !stopWords.has(w))
  );
}

async function fetchTitle(baseId) {
  try {
    const resp = await fetch(`https://api.osf.io/v2/preprints/${baseId}/`, {
      headers: { 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0' },
      signal: AbortSignal.timeout(8000)
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    return data.data?.attributes?.title || null;
  } catch {
    return null;
  }
}

function scoreMatch(apiTitle, paperTitle) {
  const apiWords = getWords(apiTitle);
  const paperWords = getWords(paperTitle);
  if (apiWords.size === 0 || paperWords.size === 0) return 0;
  let overlap = 0;
  for (const w of paperWords) {
    if (apiWords.has(w)) overlap++;
  }
  return overlap;
}

// Process in concurrent batches
const CONCURRENCY = 20;
const matches = new Map(); // paper_number -> osf_id
let checked = 0;

for (let i = 0; i < extraIds.length; i += CONCURRENCY) {
  const batch = extraIds.slice(i, i + CONCURRENCY);
  
  const results = await Promise.all(
    batch.map(async (id) => {
      const base = id.replace(/_v\d+$/, '');
      const title = await fetchTitle(base);
      return { id: base, title };
    })
  );
  
  for (const { id, title } of results) {
    checked++;
    if (!title) continue;
    
    let bestScore = 0;
    let bestNum = null;
    
    for (const [num, ptitle] of needTitles) {
      if (matches.has(num)) continue;
      const score = scoreMatch(title, ptitle);
      if (score > bestScore) {
        bestScore = score;
        bestNum = num;
      }
    }
    
    if (bestScore >= 3 && bestNum !== null) {
      matches.set(bestNum, id);
      const ptitle = needTitles.get(bestNum);
      console.log(`✓ #${bestNum} → ${id} (score=${bestScore})`);
      console.log(`  Paper: ${ptitle.substring(0, 65)}`);
      console.log(`  OSF:   ${title.substring(0, 65)}`);
    }
  }
  
  if (matches.size === needLink.length) {
    console.log(`\nAll ${needLink.length} papers matched!`);
    break;
  }
  
  if ((i + CONCURRENCY) % 100 === 0) {
    console.log(`  Progress: ${checked}/${extraIds.length} IDs checked, ${matches.size}/${needLink.length} matched`);
  }
  
  await new Promise(r => setTimeout(r, 150));
}

console.log(`\n=== Checked ${checked} IDs, matched ${matches.size}/${needLink.length} ===`);

// Save matches
writeFileSync('/tmp/id-matches.json', JSON.stringify(Object.fromEntries(matches), null, 2));

// Show unmatched
const matchedNums = new Set(matches.keys());
const unmatched = needLink.filter(p => !matchedNums.has(p.number));
if (unmatched.length > 0) {
  console.log(`\nUnmatched (${unmatched.length}):`);
  for (const p of unmatched) {
    console.log(`  #${p.number}: ${p.title}`);
  }
}