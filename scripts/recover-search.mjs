/**
 * Search PsyArXiv API to find real osf_ids for removed papers.
 * For each paper, search by title keywords and find the best match.
 */

import { readFileSync, writeFileSync } from 'fs';

const before = JSON.parse(readFileSync('/tmp/papers-before-revamp.json', 'utf-8'));
const after = JSON.parse(readFileSync('/home/z/my-project/psyarxiv-hub/data/papers.json', 'utf-8'));

// True duplicates to skip
const dupOsfIds = new Set(['5aqxg', 'f53wp']);

// Papers to recover (not true duplicates, not in 'after')
const afterTitles = new Set(after.map(p => p.title.toLowerCase().trim()));
const toRecover = before.filter(p => 
  !afterTitles.has(p.title.toLowerCase().trim()) && 
  !(p.osf_id && dupOsfIds.has(p.osf_id.replace(/_v\d+$/, '')))
);

console.log(`Papers to find: ${toRecover.length}`);

function extractSearchTerms(title) {
  const stopWords = new Set(['a','an','the','and','or','for','in','of','on','to','with','by','from','as','is','are','was','were','be','been','being','that','this','these','those','it','its','their','our','your','my','his','her','we','they','you','i','me','us','at','into','through','during','before','after','above','below','between','out','off','over','under','again','further','then','once','here','there','when','where','why','how','all','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','can','will','just','should','now','also','about','up','do','does','did','but','if','while','which']);
  return title.toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2 && !stopWords.has(w))
    .slice(0, 8);
}

async function searchPsyArXiv(title) {
  const terms = extractSearchTerms(title);
  if (terms.length < 2) return null;
  
  // Use the most distinctive terms (longer words first)
  const sorted = [...terms].sort((a, b) => b.length - a.length);
  const searchTerms = sorted.slice(0, 4);
  const searchQuery = searchTerms.join(' ');
  
  const url = `https://api.osf.io/v2/preprints/?filter[title_contains]=${encodeURIComponent(searchQuery)}&filter[provider]=psyarxiv&page[size]=10`;
  
  try {
    const resp = await fetch(url, {
      headers: { 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0' },
      signal: AbortSignal.timeout(15000)
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    if (!data.data || data.data.length === 0) return null;
    
    const titleLower = title.toLowerCase();
    let bestMatch = null;
    let bestScore = 0;
    
    for (const item of data.data) {
      const itemTitle = (item.attributes.title || '').toLowerCase();
      let score = 0;
      
      // Score: count matching words from our title
      const origWords = titleLower.split(/\s+/).filter(w => w.length > 3);
      for (const word of origWords) {
        if (itemTitle.includes(word)) score += 2;
      }
      // Bonus for length similarity
      const lenRatio = Math.min(itemTitle.length, titleLower.length) / Math.max(itemTitle.length, titleLower.length);
      score += lenRatio * 5;
      
      if (score > bestScore) {
        bestScore = score;
        bestMatch = item;
      }
    }
    
    if (bestScore >= 5 && bestMatch) {
      const links = bestMatch.links || {};
      const selfLink = links.self || '';
      // Extract OSF ID from the preprint node ID
      const nodeId = bestMatch.id; // e.g., "r8hpk_v1"
      // Or try from self link
      const linkMatch = selfLink.match(/preprints\/([a-z0-9]{5,}(?:_v\d+)*)/);
      const osfId = linkMatch ? linkMatch[1] : nodeId;
      
      return {
        osf_id: osfId,
        apiTitle: bestMatch.attributes.title,
        score: bestScore
      };
    }
    return null;
  } catch (e) {
    return null;
  }
}

// Process in batches
const BATCH_SIZE = 3;
const DELAY_MS = 600;
const results = new Map();
let found = 0, notFound = 0;
const notFoundList = [];

for (let i = 0; i < toRecover.length; i += BATCH_SIZE) {
  const batch = toRecover.slice(i, i + BATCH_SIZE);
  
  const outcomes = await Promise.allSettled(
    batch.map(async (paper) => {
      const result = await searchPsyArXiv(paper.title);
      return { paper, result };
    })
  );
  
  for (const outcome of outcomes) {
    if (outcome.status === 'fulfilled' && outcome.value.result) {
      const { paper, result } = outcome.value;
      results.set(paper.number, { ...result, paper });
      found++;
      console.log(`✓ #${paper.number}: ${paper.title}`);
      console.log(`  → ${result.osf_id} (${result.apiTitle.substring(0, 80)}...)`);
    } else {
      const paper = outcome.status === 'fulfilled' ? outcome.value.paper : null;
      notFound++;
      if (paper) {
        notFoundList.push(paper);
        console.log(`✗ #${paper.number}: ${paper.title}`);
      }
    }
  }
  
  if (i + BATCH_SIZE < toRecover.length) {
    await new Promise(r => setTimeout(r, DELAY_MS));
  }
}

console.log(`\n=== Found ${found}, Not found ${notFound} ===`);

// Save results for next step
writeFileSync('/tmp/recovery-results.json', JSON.stringify({
  found: [...results.entries()].map(([num, data]) => ({ originalNumber: num, ...data })),
  notFound: notFoundList.map(p => ({ originalNumber: p.number, title: p.title }))
}, null, 2));

console.log('Saved to /tmp/recovery-results.json');