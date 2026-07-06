/**
 * Phase 2: Search PsyArXiv API for papers missing osf_ids
 * If found → add osf_id and link
 * If not found → remove paper
 */

import { readFileSync, writeFileSync } from 'fs';

const papersPath = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const papers = JSON.parse(readFileSync(papersPath, 'utf-8'));

// Find papers with no osf_id and no valid link
const missingPapers = papers.filter(p => !p.osf_id && (!p.link || !p.link.includes('osf.io')));
console.log(`Papers missing osf_id: ${missingPapers.length}`);
for (const p of missingPapers) {
  console.log(`  #${p.number}: ${p.title}`);
}

if (missingPapers.length === 0) {
  console.log('Nothing to do!');
  process.exit(0);
}

// Extract key search terms from title (remove common filler words)
function extractSearchTerms(title) {
  const stopWords = new Set(['a', 'an', 'the', 'and', 'or', 'for', 'in', 'of', 'on', 'to', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'that', 'this', 'these', 'those', 'it', 'its', 'their', 'our', 'your', 'my', 'his', 'her', 'we', 'they', 'you', 'i', 'me', 'us', 'at', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now', 'also', 'about', 'up', 'do', 'does', 'did', 'but', 'if', 'while', 'which']);
  return title.toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2 && !stopWords.has(w))
    .slice(0, 6);
}

async function searchPsyArXiv(title) {
  const terms = extractSearchTerms(title);
  if (terms.length < 2) return null;
  
  // Search using the first 3-4 most distinctive terms
  const searchQuery = terms.slice(0, 4).join(' ');
  const url = `https://api.osf.io/v2/preprints/?filter[title_contains]=${encodeURIComponent(searchQuery)}&filter[provider]=psyarxiv&page[size]=5`;
  
  try {
    const resp = await fetch(url, {
      headers: { 'Accept': 'application/json' }
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    
    if (!data.data || data.data.length === 0) return null;
    
    // Find the best match by comparing titles
    const titleLower = title.toLowerCase();
    let bestMatch = null;
    let bestScore = 0;
    
    for (const item of data.data) {
      const itemTitle = (item.attributes.title || '').toLowerCase();
      // Count how many of our search terms appear in the result title
      let score = 0;
      for (const term of terms) {
        if (itemTitle.includes(term)) score++;
      }
      // Also check if the original title words appear
      const origWords = titleLower.split(/\s+/).filter(w => w.length > 3);
      for (const word of origWords) {
        if (itemTitle.includes(word)) score += 2;
      }
      
      if (score > bestScore) {
        bestScore = score;
        bestMatch = item;
      }
    }
    
    // Only return if we have a reasonably good match
    if (bestScore >= 3 && bestMatch) {
      const id = bestMatch.id; // This is the preprint node ID
      const attributes = bestMatch.attributes;
      // The OSF ID is in the links or we need to derive it
      // The preprint ID in the URL is usually in attributes or links
      const links = bestMatch.links || {};
      // Try to get the OSF ID from the self link
      const selfLink = links.self || '';
      const osfMatch = selfLink.match(/preprints\/([a-z0-9]{5,})/);
      const osfId = osfMatch ? osfMatch[1] : id;
      
      return {
        osf_id: osfId,
        apiTitle: bestMatch.attributes.title,
        score: bestScore,
        datePosted: bestMatch.attributes.date_created
      };
    }
    return null;
  } catch (e) {
    console.error(`  Search error for "${searchQuery}": ${e.message}`);
    return null;
  }
}

// Process in batches of 5 with delay
const BATCH_SIZE = 5;
const DELAY_MS = 1000;
let found = 0;
let notFound = 0;
const toRemove = new Set();
const toUpdate = [];

for (let i = 0; i < missingPapers.length; i += BATCH_SIZE) {
  const batch = missingPapers.slice(i, i + BATCH_SIZE);
  
  const results = await Promise.all(
    batch.map(p => searchPsyArXiv(p.title).then(r => ({ paper: p, result: r })))
  );
  
  for (const { paper, result } of results) {
    if (result) {
      found++;
      toUpdate.push({ number: paper.number, ...result });
      console.log(`✓ #${paper.number}: "${paper.title}" → ${result.osf_id} (${result.apiTitle.substring(0, 60)}...)`);
    } else {
      notFound++;
      toRemove.add(paper.number);
      console.log(`✗ #${paper.number}: "${paper.title}" → NOT FOUND`);
    }
  }
  
  if (i + BATCH_SIZE < missingPapers.length) {
    console.log(`  Waiting ${DELAY_MS}ms...`);
    await new Promise(r => setTimeout(r, DELAY_MS));
  }
}

console.log(`\n=== Results: Found ${found}, Not found ${notFound} ===`);

// Apply updates
for (const paper of papers) {
  const update = toUpdate.find(u => u.number === paper.number);
  if (update) {
    paper.osf_id = update.osf_id;
    const baseId = update.osf_id.replace(/_v\d+$/, '');
    paper.link = `https://osf.io/preprints/psyarxiv/${baseId}`;
  }
}

// Remove not-found papers
const kept = papers.filter(p => !toRemove.has(p.number));
console.log(`Before: ${papers.length}, After: ${kept.length}`);

// Re-number
for (let i = 0; i < kept.length; i++) {
  kept[i].number = i + 1;
}

writeFileSync(papersPath, JSON.stringify(kept, null, 2) + '\n');
console.log(`Saved ${kept.length} papers to ${papersPath}`);