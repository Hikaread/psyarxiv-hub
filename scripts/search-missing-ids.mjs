#!/usr/bin/env node
/**
 * Batch search for missing osf_ids using web search.
 * Strategy: Search for distinctive phrases + "psyarxiv" or "osf.io"
 * Then verify any found links.
 */
import { execSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const PAPERS_PATH = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const PROGRESS_PATH = '/home/z/my-project/scripts/search-progress-v2.json';

// Load papers
const papers = JSON.parse(readFileSync(PAPERS_PATH, 'utf8'));
const missing = papers
  .map((p, i) => ({ ...p, idx: i }))
  .filter(p => !p.osf_id);

console.log(`Total missing: ${missing.length}`);

// Load progress
let progress = {};
if (existsSync(PROGRESS_PATH)) {
  progress = JSON.parse(readFileSync(PROGRESS_PATH, 'utf8'));
}

// Generate search queries for each paper
function getSearchQueries(paper) {
  const queries = [];
  const title = paper.title || '';
  const authors = paper.authors || '';
  const summary = (paper.summary || '').substring(0, 200);
  
  // Strategy 1: For papers with known authors, search author + topic
  if (authors && authors !== 'Unknown') {
    const firstAuthor = authors.split(',')[0].trim().split(' ').slice(-1)[0]; // last name
    // Extract 2-3 key terms from title
    const keyTerms = title.split(/[:()]/)[0].trim().split(/\s+/).filter(w => 
      w.length > 4 && !['therapeutic', 'clinical', 'study', 'examines', 'investigates', 'analysis'].includes(w.toLowerCase())
    ).slice(0, 3).join(' ');
    queries.push(`"${firstAuthor}" ${keyTerms} psyarxiv`);
  }
  
  // Strategy 2: Extract highly distinctive phrases from title
  // Quoted phrases work best
  const phrases = title.match(/"([^"]+)"|([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)/g) || [];
  if (phrases.length > 0) {
    const phrase = phrases[0].replace(/"/g, '');
    queries.push(`"${phrase}" psyarxiv`);
  }
  
  // Strategy 3: Most distinctive 3-4 word sequence from title
  const words = title.replace(/[:()]/g, ' ').split(/\s+/).filter(w => w.length > 3);
  // Find the most distinctive bigram/trigram
  const stopWords = new Set(['therapeutic', 'clinical', 'study', 'examines', 'investigates', 
    'analysis', 'review', 'systematic', 'meta', 'their', 'with', 'for', 'and', 'the', 'treatment',
    'disorder', 'disorders', 'approach', 'approaches', 'outcome', 'outcomes', 'effects', 'effect',
    'between', 'among', 'during', 'into', 'from', 'using', 'based', 'that', 'this', 'which',
    'what', 'when', 'where', 'have', 'been', 'were', 'will', 'would', 'could', 'should']);
  
  const meaningful = words.filter(w => !stopWords.has(w.toLowerCase()));
  if (meaningful.length >= 2) {
    const distinctive = meaningful.slice(0, 3).join(' ');
    queries.push(`"${distinctive}" psyarxiv osf.io`);
  }
  
  // Strategy 4: From summary, extract specific methodological terms
  const summaryTerms = summary.match(/(?:RCT|EMA|IPA|CBT-I|DBT|ACT|N-of-1|CBM-I|MTIIF|PEP|NSSI|CPTSD|BPD|OXTR|IMV|ROM)/g);
  if (summaryTerms && summaryTerms.length > 0) {
    const term = summaryTerms[0];
    // Combine with a content word from title
    const contentWord = words.find(w => !stopWords.has(w.toLowerCase()) && w.length > 4);
    if (contentWord) {
      queries.push(`"${term}" "${contentWord}" psyarxiv`);
    }
  }
  
  // Deduplicate and return
  return [...new Set(queries)].slice(0, 3);
}

// Web search with rate limiting
async function webSearch(query, numResults = 5) {
  try {
    const result = execSync(
      `z-ai function -n web_search -a '${JSON.stringify({ query, num: numResults })}' -o /tmp/search-result.json`,
      { timeout: 30000, encoding: 'utf8' }
    );
    if (existsSync('/tmp/search-result.json')) {
      const data = JSON.parse(readFileSync('/tmp/search-result.json', 'utf8'));
      if (Array.isArray(data) && data.length > 0) {
        return data;
      }
    }
    return [];
  } catch (e) {
    console.error(`  Search error: ${e.message.substring(0, 100)}`);
    return [];
  }
}

// Extract osf_id from a URL
function extractOsfId(url) {
  const m = url.match(/osf\.io\/([a-z0-9]+)/i);
  return m ? m[1] : null;
}

// Check if search result is a PsyArXiv link
function isPsyarxivResult(result) {
  const url = result.url || '';
  const snippet = (result.snippet || '') + (result.name || '');
  return url.includes('osf.io/preprints/psyarxiv') || 
         url.includes('psyarxiv') ||
         snippet.includes('PsyArXiv') ||
         snippet.includes('osf.io/preprints');
}

// Verify an osf_id actually exists and matches
async function verifyOsfId(osfId, expectedTitle) {
  try {
    const result = execSync(
      `curl -s 'https://api.osf.io/v2/preprints/${osfId}/'`,
      { timeout: 15000, encoding: 'utf8' }
    );
    const data = JSON.parse(result);
    const attrs = data.data?.attributes || {};
    const actualTitle = attrs.title || '';
    
    // Check word overlap
    const expectedWords = new Set(expectedTitle.toLowerCase().split(/\s+/).filter(w => w.length > 3));
    const actualWords = new Set(actualTitle.toLowerCase().split(/\s+/).filter(w => w.length > 3));
    let overlap = 0;
    for (const w of expectedWords) {
      if (actualWords.has(w)) overlap++;
    }
    const score = overlap / Math.max(expectedWords.size, 1);
    
    return {
      valid: true,
      title: actualTitle,
      provider: data.data?.relationships?.provider?.data?.id,
      overlap,
      score
    };
  } catch (e) {
    return { valid: false, error: e.message.substring(0, 100) };
  }
}

// Process papers in batches
async function processBatch(paperBatch) {
  const results = [];
  
  for (const paper of paperBatch) {
    const key = `${paper.idx}`;
    if (progress[key]?.status === 'found') continue;
    
    const queries = getSearchQueries(paper);
    console.log(`\n#${paper.number} "${paper.title}"`);
    console.log(`  Queries: ${queries.join(' | ')}`);
    
    let found = false;
    
    for (const query of queries) {
      if (found) break;
      
      console.log(`  Searching: "${query}"`);
      const searchResults = await webSearch(query, 5);
      
      if (searchResults.length === 0) {
        console.log('  No results');
        continue;
      }
      
      // Check each result for psyarxiv links
      for (const sr of searchResults) {
        const osfId = extractOsfId(sr.url);
        if (osfId && isPsyarxivResult(sr)) {
          console.log(`  Found potential: ${osfId} - "${sr.name?.substring(0, 80)}"`);
          
          // Verify
          const verification = await verifyOsfId(osfId, paper.title);
          if (verification.valid && verification.provider === 'psyarxiv') {
            console.log(`  ✓ VERIFIED: ${osfId} - "${verification.title.substring(0, 80)}" (score: ${verification.score.toFixed(2)})`);
            
            if (verification.score >= 0.15) {
              results.push({
                idx: paper.idx,
                number: paper.number,
                title: paper.title,
                osf_id: osfId,
                actual_title: verification.title,
                score: verification.score
              });
              progress[key] = { status: 'found', osf_id: osfId, title: verification.title, score: verification.score };
              found = true;
              break;
            } else {
              console.log(`  ✗ Score too low (${verification.score.toFixed(2)})`);
            }
          } else if (verification.valid) {
            console.log(`  ✗ Provider: ${verification.provider}, not psyarxiv`);
          }
        }
      }
      
      // Also check snippets for osf.io links
      if (!found) {
        for (const sr of searchResults) {
          const snippetMatch = (sr.snippet || '').match(/osf\.io\/([a-z0-9]+)/i);
          if (snippetMatch) {
            const osfId = snippetMatch[1];
            console.log(`  Found in snippet: ${osfId}`);
            const verification = await verifyOsfId(osfId, paper.title);
            if (verification.valid && verification.provider === 'psyarxiv' && verification.score >= 0.15) {
              console.log(`  ✓ VERIFIED (from snippet): ${osfId} - "${verification.title.substring(0, 80)}"`);
              results.push({
                idx: paper.idx,
                number: paper.number,
                title: paper.title,
                osf_id: osfId,
                actual_title: verification.title,
                score: verification.score
              });
              progress[key] = { status: 'found', osf_id: osfId, title: verification.title, score: verification.score };
              found = true;
              break;
            }
          }
        }
      }
      
      // Rate limit
      await new Promise(r => setTimeout(r, 13000));
    }
    
    if (!found) {
      progress[key] = { status: 'not_found', queries };
      console.log('  ✗ Not found');
    }
    
    // Save progress after each paper
    writeFileSync(PROGRESS_PATH, JSON.stringify(progress, null, 2));
  }
  
  return results;
}

// Main
async function main() {
  // Filter out already found
  const toSearch = missing.filter(p => {
    const key = `${p.idx}`;
    return !progress[key] || progress[key].status !== 'found';
  });
  
  console.log(`Papers to search: ${toSearch.length} (already found: ${missing.length - toSearch.length})`);
  
  // Process in batches of 5
  const BATCH_SIZE = 5;
  const allResults = [];
  
  for (let i = 0; i < toSearch.length; i += BATCH_SIZE) {
    const batch = toSearch.slice(i, i + BATCH_SIZE);
    console.log(`\n${'='.repeat(60)}`);
    console.log(`BATCH ${Math.floor(i/BATCH_SIZE) + 1}: Papers #${batch.map(p => p.number).join(', #')}`);
    console.log(`${'='.repeat(60)}`);
    
    const results = await processBatch(batch);
    allResults.push(...results);
  }
  
  console.log(`\n${'='.repeat(60)}`);
  console.log(`FINAL RESULTS: ${allResults.length} new matches found`);
  console.log(`${'='.repeat(60)}`);
  
  for (const r of allResults) {
    console.log(`#${r.number} → ${r.osf_id} (score: ${r.score.toFixed(2)}) "${r.actual_title.substring(0, 80)}"`);
  }
  
  // Output as JSON for easy processing
  writeFileSync('/home/z/my-project/scripts/new-matches.json', JSON.stringify(allResults, null, 2));
  console.log(`\nSaved to new-matches.json`);
}

main().catch(e => console.error(e));