#!/usr/bin/env node
/**
 * Find missing osf_ids one paper at a time with long delays.
 * Searches Google for key terms + "psyarxiv" (no site: filter).
 * Saves progress after each paper.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';

const PAPERS_JSON = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const PROGRESS_FILE = '/home/z/my-project/scripts/find-ids-progress.json';

const papers = JSON.parse(readFileSync(PAPERS_JSON, 'utf-8'));
const missing = papers.filter(p => !p.osf_id);

// Load progress
let progress = { found: {}, not_found: [], processed: [], results_log: [] };
if (existsSync(PROGRESS_FILE)) {
  const saved = JSON.parse(readFileSync(PROGRESS_FILE, 'utf-8'));
  progress = { ...progress, ...saved };
}

function saveProgress() {
  writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
}

function webSearch(query) {
  const args = JSON.stringify({ query, num: 10 });
  try {
    const result = execSync(
      `z-ai function -n web_search -a '${args.replace(/'/g, "'\\''")}' 2>/dev/null`,
      { timeout: 30000, encoding: 'utf-8', maxBuffer: 2 * 1024 * 1024 }
    );
    return JSON.parse(result);
  } catch (e) {
    return null;
  }
}

function extractOsfId(url) {
  // Match osf.io/preprints/psyarxiv/XXXXX or just osf.io/XXXXX
  const match = url.match(/osf\.io\/(?:preprints\/psyarxiv\/)?([a-z0-9]{5})/i);
  return match ? match[1].toLowerCase() : null;
}

function getSearchQueries(paper) {
  const title = paper.title;
  const authors = paper.authors || 'Unknown';
  const queries = [];

  // Strategy: search for the most unique/specific terms + "psyarxiv"
  const stop = new Set(['a','an','the','and','or','of','for','in','on','to','with','by','from','their','its','is','are','was','were','be','been','that','this','these','those','not','no','but','at','if','study','analysis','review','research','examination','based','using','between','among','into','clinical','framework','model','effects','effect','role','association','predictors','outcomes','findings','evidence','overview','perspective','considerations','evaluating','evaluation','assessment','versus','therapeutic','approaches','approach','systematic','additional','implications','disorder','disorders']);

  // Extract unique terms
  const abbrevs = (title.match(/\b[A-Z]{2,}-?[A-Z]*\b/g) || []).map(a => a.toLowerCase());
  const hyphenated = (title.match(/[a-zA-Z]+-[a-zA-Z]+/g) || []).map(h => h.toLowerCase());
  const words = (title.match(/[a-zA-Z]+/g) || [])
    .filter(w => !stop.has(w.toLowerCase()) && w.length >= 5)
    .sort((a, b) => b.length - a.length);

  // Build 2-3 search queries
  const specific = [...new Set([...abbrevs, ...hyphenated, ...words.slice(0, 3)])].slice(0, 4);

  if (authors !== 'Unknown') {
    const lastNames = authors.split(',').map(a => a.trim().split(' ').pop());
    queries.push(`${lastNames[0]} ${specific.slice(0, 2).join(' ')} psyarxiv`.trim());
  }
  queries.push(`${specific.join(' ')} psyarxiv`);

  // Also try without psyarxiv, just the most unique terms
  if (specific.length >= 2) {
    queries.push(`"${specific[0]}" "${specific[1]}" preprint`);
  }

  return [...new Set(queries)].slice(0, 2);
}

function isValidMatch(paper, result) {
  const titleLower = paper.title.toLowerCase();
  const nameLower = (result.name || '').toLowerCase();
  const snippetLower = (result.snippet || '').toLowerCase();
  const combined = nameLower + ' ' + snippetLower;

  // Get key words from paper title (long words)
  const keyWords = titleLower.split(/\s+/).filter(w => w.length >= 5);
  const matchWords = keyWords.filter(w => combined.includes(w));

  // Also check abbreviations
  const abbrevs = (paper.title.match(/\b[A-Z]{2,}-?[A-Z]*\b/g) || []).map(a => a.toLowerCase());
  const matchAbbrevs = abbrevs.filter(a => combined.includes(a));

  // Also check hyphenated terms
  const hyphenated = (paper.title.match(/[a-zA-Z]+-[a-zA-Z]+/g) || []).map(h => h.toLowerCase());
  const matchHyphenated = hyphenated.filter(h => combined.includes(h));

  const totalSpecific = [...new Set([...keyWords, ...abbrevs, ...hyphenated])];
  const totalMatches = [...new Set([...matchWords, ...matchAbbrevs, ...matchHyphenated])];

  return {
    isMatch: totalMatches.length >= 1 || (totalSpecific.length <= 2 && totalMatches.length >= 1),
    matchCount: totalMatches.length,
    totalSpecific: totalSpecific.length,
    matchedTerms: totalMatches,
  };
}

// Main loop - process one at a time
const toProcess = missing.filter(p => !progress.processed.includes(p.number));
console.log(`Already: ${progress.processed.length} processed, ${Object.keys(progress.found).length} found, ${progress.not_found.length} not found`);
console.log(`Remaining: ${toProcess.length}\n`);

for (const paper of toProcess) {
  const { number, title, authors } = paper;
  console.log(`#${number}: ${title}`);
  console.log(`  Authors: ${authors}`);

  const queries = getSearchQueries(paper);
  let foundResult = null;

  for (const query of queries) {
    console.log(`  Searching: "${query}"`);
    const results = webSearch(query);

    if (!results || !Array.isArray(results)) {
      console.log(`  No results (API error or rate limit)`);
      execSync('sleep 15');
      continue;
    }

    // Log results for debugging
    for (const r of results.slice(0, 3)) {
      console.log(`    [${r.host_name}] ${r.name?.substring(0, 70)}`);
    }

    // Look for osf.io URLs
    for (const r of results) {
      const osfId = extractOsfId(r.url);
      if (!osfId) continue;

      const validation = isValidMatch(paper, r);
      if (validation.isMatch) {
        foundResult = {
          osf_id: osfId,
          api_title: r.name,
          url: r.url,
          link: `https://osf.io/preprints/psyarxiv/${osfId}`,
          snippet: (r.snippet || '').substring(0, 200),
          query_used: query,
          match_details: validation,
        };
        console.log(`  ✅ FOUND: ${osfId} (${validation.matchCount}/${validation.totalSpecific} terms: ${validation.matchedTerms.join(', ')})`);
        console.log(`     ${r.name?.substring(0, 80)}`);
        break;
      } else {
        console.log(`  ⏭️  Skipped ${osfId} (${validation.matchCount}/${validation.totalSpecific} terms match)`);
      }
    }

    if (foundResult) break;
    execSync('sleep 12');
  }

  if (foundResult) {
    progress.found[String(number)] = { ...foundResult, original_title: title };
  } else {
    progress.not_found.push(number);
    console.log(`  ❌ NOT FOUND`);
  }

  progress.processed.push(number);
  saveProgress();
  console.log(`  Progress: ${progress.processed.length}/${missing.length}\n`);

  execSync('sleep 12');
}

// Summary
const output = {
  found: progress.found,
  not_found_numbers: progress.not_found,
  total_missing: missing.length,
  total_found: Object.keys(progress.found).length,
};
writeFileSync('/home/z/my-project/scripts/missing-osf-results.json', JSON.stringify(output, null, 2));

console.log(`${'='.repeat(60)}`);
console.log(`FINAL: Found ${Object.keys(progress.found).length}/${missing.length}`);
console.log(`Results: /home/z/my-project/scripts/missing-osf-results.json`);