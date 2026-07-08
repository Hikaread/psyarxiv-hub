#!/usr/bin/env node
/**
 * Fast batch search for missing osf_ids using web search.
 * More targeted queries, faster processing.
 */
import { execSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const PAPERS_PATH = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const PROGRESS_PATH = '/home/z/my-project/scripts/search-progress-v3.json';

const papers = JSON.parse(readFileSync(PAPERS_PATH, 'utf8'));
const missing = papers
  .map((p, i) => ({ ...p, idx: i }))
  .filter(p => !p.osf_id);

let progress = {};
if (existsSync(PROGRESS_PATH)) {
  progress = JSON.parse(readFileSync(PROGRESS_PATH, 'utf8'));
}

// More targeted search query generation
function getSearchQuery(paper) {
  const title = paper.title || '';
  const authors = paper.authors || '';
  const summary = (paper.summary || '');
  
  // Extract the most distinctive phrase from the title
  // Remove generic words
  const stopWords = new Set(['the','and','for','in','of','a','an','their','with','that','this',
    'study','review','analysis','examines','investigates','approaches','outcomes','effects',
    'treatment','disorder','disorders','clinical','therapeutic','systematic','meta',
    'between','among','during','into','from','using','based','which','what','when']);
  
  // For papers with known authors - use author + distinctive title terms
  if (authors && authors !== 'Unknown') {
    const lastName = authors.split(',')[0].trim().split(' ').pop();
    const terms = title.replace(/[:()]/g, ' ').split(/\s+/)
      .filter(w => w.length > 4 && !stopWords.has(w.toLowerCase()))
      .slice(0, 3);
    if (terms.length > 0) {
      return `site:osf.io/preprints/psyarxiv "${lastName}" "${terms.join(' ')}"`;
    }
    return `site:osf.io/preprints/psyarxiv "${lastName}"`;
  }
  
  // For papers with distinctive terms in title
  const allTerms = title.replace(/[:()]/g, ' ').split(/\s+/)
    .filter(w => w.length > 4 && !stopWords.has(w.toLowerCase()));
  
  // Look for very distinctive terms (abbreviations, hyphenated, capitalized, method names)
  const distinctive = title.match(/\b[A-Z]{2,}[\-]?[A-Z]*\b/g) || []; // Abbreviations like CBT-I, EMA, etc.
  
  if (distinctive.length > 0) {
    // Combine abbreviation with a content word
    const contentWords = allTerms.filter(w => !distinctive.map(d => d.toLowerCase()).includes(w.toLowerCase()));
    if (contentWords.length > 0) {
      return `site:osf.io/preprints/psyarxiv "${distinctive[0]}" "${contentWords[0]}"`;
    }
    return `site:osf.io/preprints/psyarxiv "${distinctive[0]}"`;
  }
  
  // For remaining papers, use 2 most distinctive words from title
  if (allTerms.length >= 2) {
    return `site:osf.io/preprints/psyarxiv "${allTerms[0]} ${allTerms[1]}"`;
  }
  
  return `site:osf.io/preprints/psyarxiv "${title}"`;
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function webSearch(query) {
  try {
    const escaped = JSON.stringify({ query, num: 5 });
    execSync(`z-ai function -n web_search -a '${escaped}' -o /tmp/ws-result.json`, { 
      timeout: 25000, encoding: 'utf8' 
    });
    if (existsSync('/tmp/ws-result.json')) {
      const data = JSON.parse(readFileSync('/tmp/ws-result.json', 'utf8'));
      if (Array.isArray(data)) return data;
    }
  } catch (e) {
    // Ignore
  }
  return [];
}

function extractOsfId(url) {
  const m = url.match(/osf\.io\/([a-z0-9]{4,6})(?:\/|$|_v)/i);
  return m ? m[1] : null;
}

function verifyOsfId(osfId) {
  try {
    const result = execSync(
      `curl -s 'https://api.osf.io/v2/preprints/${osfId}/'`,
      { timeout: 10000, encoding: 'utf8' }
    );
    const data = JSON.parse(result);
    const attrs = data.data?.attributes || {};
    const provider = data.data?.relationships?.provider?.data?.id;
    return {
      valid: true,
      title: attrs.title || '',
      provider,
      date: attrs.date_created?.substring(0, 10) || ''
    };
  } catch (e) {
    return { valid: false };
  }
}

async function main() {
  const toSearch = missing.filter(p => {
    const key = `${p.idx}`;
    return !progress[key] || progress[key].status !== 'found' && progress[key].status !== 'not_found';
  });
  
  // Also include papers that were "not_found" with a different query strategy
  const toRetry = missing.filter(p => {
    const key = `${p.idx}`;
    return progress[key]?.status === 'not_found';
  });
  
  console.log(`Fresh to search: ${toSearch.length}, Previously not found (to retry): ${toRetry.length}`);
  
  const allResults = [];
  const papersToProcess = [...toSearch]; // Don't retry yet
  
  for (const paper of papersToProcess) {
    const key = `${paper.idx}`;
    const query = getSearchQuery(paper);
    console.log(`#${paper.number} "${paper.title}"`);
    console.log(`  Query: ${query}`);
    
    const results = webSearch(query);
    let found = false;
    
    for (const r of results) {
      const osfId = extractOsfId(r.url);
      if (!osfId) continue;
      
      // Check if it looks like a psyarxiv link
      const isPsyarxiv = r.url.includes('psyarxiv') || r.snippet?.includes('PsyArXiv') || r.name?.includes('PsyArXiv');
      
      const verification = verifyOsfId(osfId);
      if (!verification.valid || verification.provider !== 'psyarxiv') continue;
      
      // Check word overlap
      const expectedWords = new Set(
        paper.title.toLowerCase().replace(/[^a-z0-9\s]/g, '').split(/\s+/).filter(w => w.length > 3)
      );
      const actualWords = new Set(
        verification.title.toLowerCase().replace(/[^a-z0-9\s]/g, '').split(/\s+/).filter(w => w.length > 3)
      );
      
      let overlap = 0;
      for (const w of expectedWords) {
        if (actualWords.has(w)) overlap++;
      }
      const score = overlap / Math.max(expectedWords.size, 1);
      
      console.log(`  → ${osfId} (score: ${score.toFixed(2)}) "${verification.title.substring(0, 80)}"`);
      
      if (score >= 0.15) {
        allResults.push({
          idx: paper.idx,
          number: paper.number,
          title: paper.title,
          osf_id: osfId,
          actual_title: verification.title,
          score
        });
        progress[key] = { status: 'found', osf_id: osfId, title: verification.title, score };
        found = true;
        break;
      }
    }
    
    if (!found) {
      progress[key] = { status: 'not_found', query };
      console.log('  ✗ Not found');
    }
    
    writeFileSync(PROGRESS_PATH, JSON.stringify(progress, null, 2));
    await sleep(8000); // 8s delay
  }
  
  console.log(`\n${'='.repeat(60)}`);
  console.log(`RESULTS: ${allResults.length} matches`);
  for (const r of allResults) {
    console.log(`#${r.number} → ${r.osf_id} (${r.score.toFixed(2)}) "${r.actual_title.substring(0, 80)}"`);
  }
  writeFileSync('/home/z/my-project/scripts/new-matches-v3.json', JSON.stringify(allResults, null, 2));
}

main().catch(e => console.error(e));