#!/usr/bin/env node
/**
 * Find missing osf_ids by searching Google for each paper on osf.io
 */
import { readFileSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';

const PAPERS_JSON = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const OUTPUT = '/home/z/my-project/scripts/missing-osf-results.json';

const papers = JSON.parse(readFileSync(PAPERS_JSON, 'utf-8'));
const missing = papers.filter(p => !p.osf_id);

console.log(`Found ${missing.length} papers missing osf_id`);

// Extract search-friendly terms from short titles
function getSearchQuery(paper) {
  const title = paper.title;
  const authors = paper.authors || 'Unknown';
  
  // If we have known authors, use them
  if (authors !== 'Unknown') {
    const lastNames = authors.split(',').map(a => a.trim().split(' ').pop()).join(' ');
    return `site:osf.io/preprints/psyarxiv "${lastNames.split(' ')[0]}" ${title.split(':')[0].split('(')[0].trim().split(' ').slice(-3).join(' ')}`;
  }
  
  // Otherwise use the most specific terms from the title
  const stop = new Set(['a','an','the','and','or','of','for','in','on','to','with','by','from','their','its','is','are','was','were','be','been','that','this','these','those','not','no','but','at','if','study','analysis','review','research','examination','based','using','between','among','into','clinical','framework','model','effects','effect','role','association','predictors','outcomes','findings','evidence','overview','perspective','considerations','evaluating','evaluation','assessment','versus','therapeutic','approaches','approach','systematic']);
  
  // Get the most unique/specific part of the title
  // Strategy: use words after colon, or longest words
  let searchTerms;
  if (title.includes(':')) {
    searchTerms = title.split(':')[1].trim();
  } else {
    const words = title.split(/\s+/).filter(w => !stop.has(w.toLowerCase()) && w.length >= 4);
    // Pick the 3 longest/most specific words
    words.sort((a, b) => b.length - a.length);
    searchTerms = words.slice(0, 3).join(' ');
  }
  
  return `site:osf.io/preprints/psyarxiv ${searchTerms}`;
}

function extractOsfId(url) {
  // Match patterns like osf.io/preprints/psyarxiv/abc123
  const match = url.match(/psyarxiv\/([a-z0-9]{5})/i);
  if (match) return match[1];
  return null;
}

async function searchPaper(paper) {
  const query = getSearchQuery(paper);
  console.log(`\n#${paper.number}: ${paper.title}`);
  console.log(`  Query: ${query}`);
  
  try {
    const result = execSync(
      `z-ai function -n web_search -a '${JSON.stringify({ query, num: 5 })}' 2>/dev/null`,
      { timeout: 30000, encoding: 'utf-8', maxBuffer: 1024 * 1024 }
    );
    
    const results = JSON.parse(result);
    
    if (!Array.isArray(results) || results.length === 0) {
      console.log('  No results');
      return null;
    }
    
    // Look for osf.io URLs in results
    for (const r of results) {
      const osfId = extractOsfId(r.url);
      if (osfId) {
        console.log(`  FOUND: ${osfId} -> ${r.url}`);
        console.log(`  Title: ${r.name?.substring(0, 80)}`);
        return {
          osf_id: osfId,
          api_title: r.name,
          url: r.url,
          link: `https://osf.io/preprints/psyarxiv/${osfId}`,
          snippet: r.snippet?.substring(0, 150),
        };
      }
    }
    
    // Check snippet/title for osf.io references
    for (const r of results) {
      if (r.snippet?.includes('osf.io') || r.name?.includes('PsyArXiv')) {
        console.log(`  Possible: ${r.url}`);
        console.log(`  Title: ${r.name?.substring(0, 80)}`);
      }
    }
    
    console.log(`  No osf.io URLs found in ${results.length} results`);
    console.log(`  Top result: ${results[0]?.url}`);
    return null;
    
  } catch (err) {
    console.log(`  Search error: ${err.message?.substring(0, 100)}`);
    return null;
  }
}

async function main() {
  const found = {};
  const notFound = [];
  
  // Process in batches of 5 with delays
  for (let i = 0; i < missing.length; i += 5) {
    const batch = missing.slice(i, i + 5);
    const promises = batch.map(p => searchPaper(p));
    const results = await Promise.all(promises);
    
    for (let j = 0; j < batch.length; j++) {
      if (results[j]) {
        found[batch[j].number] = { ...results[j], original_title: batch[j].title };
      } else {
        notFound.push(batch[j].number);
      }
    }
    
    // Delay between batches
    if (i + 5 < missing.length) {
      console.log('\n  --- batch pause ---');
      await new Promise(r => setTimeout(r, 2000));
    }
  }
  
  console.log(`\n${'='.repeat(60)}`);
  console.log(`RESULTS: Found ${Object.keys(found).length}/${missing.length} osf_ids`);
  console.log(`${'='.repeat(60)}`);
  
  const output = {
    found,
    not_found_numbers: notFound,
    total_missing: missing.length,
    total_found: Object.keys(found).length,
  };
  
  writeFileSync(OUTPUT, JSON.stringify(output, null, 2));
  console.log(`\nResults saved to ${OUTPUT}`);
}

main().catch(console.error);