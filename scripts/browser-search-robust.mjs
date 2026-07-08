#!/usr/bin/env node
/**
 * Robust browser-based search for missing osf_ids.
 * Uses eval() to interact with React components properly.
 * Processes papers one at a time, saves progress after each.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';

const PAPERS_JSON = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const PROGRESS_FILE = '/home/z/my-project/scripts/browser-search-progress.json';
const RESULTS_FILE = '/home/z/my-project/scripts/missing-osf-results.json';

const papers = JSON.parse(readFileSync(PAPERS_JSON, 'utf-8'));
const missing = papers.filter(p => !p.osf_id);

// Load progress
let progress = { found: {}, not_found: [], processed: [], logs: [] };
if (existsSync(PROGRESS_FILE)) {
  progress = JSON.parse(readFileSync(PROGRESS_FILE, 'utf-8'));
}

function saveProgress() {
  writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
}

function browserExec(cmd, timeout = 25000) {
  try {
    return execSync(`agent-browser ${cmd}`, {
      timeout, encoding: 'utf-8', maxBuffer: 1024 * 1024
    }).trim();
  } catch (e) {
    return '';
  }
}

function sleep(sec) { execSync(`sleep ${sec}`); }

function log(msg) {
  console.log(msg);
  progress.logs.push(msg);
}

// Search PsyArXiv and extract osf_ids from results
function searchPsyArXiv(query) {
  // Navigate to discover page fresh
  browserExec('open "https://osf.io/preprints/psyarxiv/discover" --timeout 20000');
  sleep(3);

  // Use eval to set the search input and trigger React's onChange
  const setSearch = browserExec(`eval "
    const input = document.querySelector('input[placeholder*=\"Search\"]');
    if (!input) return 'no input found';
    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    nativeSetter.call(input, '${query.replace(/'/g, "\\'").replace(/"/g, '\\"')}');
    input.dispatchEvent(new Event('input', {bubbles: true}));
    'input set';
  "`);

  if (setSearch.includes('no input')) {
    log('    ERROR: Could not find search input');
    return [];
  }

  sleep(1);

  // Trigger the search by pressing Enter via the input
  browserExec(`eval "
    const input = document.querySelector('input[placeholder*=\"Search\"]');
    input.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true, cancelable: true}));
    input.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true}));
    'enter dispatched';
  "`);

  // Wait for results to load
  browserExec('wait --load networkidle');
  sleep(3);

  // Extract all preprint links from the page
  const resultsJson = browserExec(`eval "
    const links = document.querySelectorAll('a[href*=\"preprints/psyarxiv/\"]');
    const results = [];
    const seen = new Set();
    for (const a of links) {
      const href = a.href || '';
      const match = href.match(/psyarxiv\\/([a-z0-9]{5})/i);
      if (match && !seen.has(match[1].toLowerCase())) {
        seen.add(match[1].toLowerCase());
        // Get the title from the closest heading
        const heading = a.closest('[class*=result], [class*=item], article, li, [class*=card]')?.querySelector('h2, h3, h4');
        const title = heading?.textContent?.trim() || a.textContent?.trim()?.substring(0, 100) || '';
        results.push({osf_id: match[1].toLowerCase(), title: title.substring(0, 120)});
      }
    }
    // Also check the result count
    const countEl = document.querySelector('h4');
    const count = countEl?.textContent?.match(/(\\d+)/)?.[1] || '?';
    JSON.stringify({count, results});
  "`);

  try {
    const parsed = JSON.parse(resultsJson);
    return parsed.results || [];
  } catch {
    return [];
  }
}

// Extract the most searchable terms from a paper
function getSearchTerms(paper) {
  const title = paper.title;
  const summary = paper.summary || '';
  const authors = paper.authors || 'Unknown';
  const terms = [];

  // Extract abbreviations (very specific)
  const abbrevs = title.match(/\b[A-Z]{2,}-?[A-Z]*\b/g) || [];
  terms.push(...abbrevs.map(a => a.toLowerCase()));

  // Extract hyphenated terms
  const hyphenated = title.match(/[a-zA-Z]+-[a-zA-Z]+/g) || [];
  terms.push(...hyphenated.map(h => h.toLowerCase()));

  // Extract long specific words from title (sorted by length, longest first)
  const stop = new Set(['therapeutic','approaches','approach','study','analysis','review','research','examination','based','using','between','among','into','clinical','framework','model','effects','effect','findings','systematic','implications','evaluation','assessment','disorder','disorders','predictors','outcomes']);
  const words = (title.match(/[a-zA-Z]+/g) || [])
    .filter(w => !stop.has(w.toLowerCase()) && w.length >= 5)
    .sort((a, b) => b.length - a.length);
  terms.push(...words.slice(0, 4));

  // If we have authors, add first author last name
  if (authors !== 'Unknown') {
    const lastName = authors.split(',')[0].trim().split(' ').pop();
    if (lastName) terms.unshift(lastName.toLowerCase());
  }

  return [...new Set(terms)];
}

// Check if a search result matches our paper
function checkMatch(paper, result) {
  const titleLower = paper.title.toLowerCase();
  const resultLower = result.title.toLowerCase();
  const terms = getSearchTerms(paper).filter(t => t.length >= 4);

  const matches = terms.filter(t => resultLower.includes(t.toLowerCase()));
  return {
    match: matches.length >= 1,
    matchedTerms: matches,
    totalTerms: terms.length,
    ratio: matches.length / Math.max(terms.length, 1),
  };
}

// Generate multiple search queries for a paper
function getQueries(paper) {
  const terms = getSearchTerms(paper);
  const authors = paper.authors || 'Unknown';
  const queries = [];

  // Query 1: Author + top 2 specific terms (if author known)
  if (authors !== 'Unknown') {
    const lastName = authors.split(',')[0].trim().split(' ').pop();
    const specific = terms.filter(t => t !== lastName.toLowerCase()).slice(0, 2);
    if (specific.length > 0) {
      queries.push(`${lastName} ${specific.join(' ')}`);
    }
  }

  // Query 2: Top 3-4 most specific terms
  const nonAuthor = terms.filter(t => {
    if (authors !== 'Unknown') {
      return t !== authors.split(',')[0].trim().split(' ').pop().toLowerCase();
    }
    return true;
  });
  queries.push(nonAuthor.slice(0, 4).join(' '));

  // Query 3: Try with a phrase from the summary
  const summary = paper.summary || '';
  if (summary.length > 50) {
    // Get the most unique phrase from summary (between commas or periods)
    const phrases = summary.split(/[.,]/).map(p => p.trim()).filter(p => p.length > 30 && p.length < 100);
    if (phrases.length > 0) {
      // Take first 5 words of the longest phrase
      const longest = phrases.sort((a, b) => b.length - a.length)[0];
      const phraseWords = longest.split(/\s+/).slice(0, 5).join(' ');
      queries.push(phraseWords);
    }
  }

  return [...new Set(queries)].slice(0, 3);
}

// Main
const toProcess = missing.filter(p => !progress.processed.includes(p.number));
log(`Progress: ${progress.processed.length}/${missing.length} processed, ${Object.keys(progress.found).length} found`);
log(`Remaining: ${toProcess.length}\n`);

// Ensure browser is open
browserExec('close');
sleep(1);

for (const paper of toProcess) {
  const { number, title } = paper;
  log(`\n#${number}: ${title}`);

  const queries = getQueries(paper);
  let foundId = null;

  for (let qi = 0; qi < queries.length && !foundId; qi++) {
    const query = queries[qi];
    log(`  [Q${qi + 1}] "${query}"`);

    const results = searchPsyArXiv(query);
    log(`  ${results.length} results on page`);

    for (const r of results) {
      log(`    ${r.osf_id}: ${r.title.substring(0, 70)}`);
    }

    // Check for matches
    for (const r of results) {
      const match = checkMatch(paper, r);
      if (match.match) {
        // Additional validation: the match should make sense
        if (match.ratio >= 0.2 || match.matchedTerms.length >= 2) {
          foundId = {
            osf_id: r.osf_id,
            api_title: r.title,
            link: `https://osf.io/preprints/psyarxiv/${r.osf_id}`,
            query_used: query,
            match_details: match,
          };
          log(`  ✅ MATCH: ${r.osf_id} (${match.matchedTerms.join(', ')})`);
          break;
        }
      }
    }

    if (!foundId && results.length === 0) {
      log(`  No results - paper may not be on PsyArXiv`);
      break; // No point trying more queries if first returns nothing
    }
  }

  if (foundId) {
    progress.found[String(number)] = { ...foundId, original_title: title };
  } else {
    progress.not_found.push(number);
  }
  progress.processed.push(number);
  saveProgress();
  log(`  Total: ${progress.processed.length}/${missing.length} (${Object.keys(progress.found).length} found)`);
}

// Save final results
const output = {
  found: progress.found,
  not_found_numbers: progress.not_found,
  total_missing: missing.length,
  total_found: Object.keys(progress.found).length,
};
writeFileSync(RESULTS_FILE, JSON.stringify(output, null, 2));

browserExec('close');

log(`\n${'='.repeat(50)}`);
log(`DONE: Found ${Object.keys(progress.found).length}/${missing.length}`);
log(`Results: ${RESULTS_FILE}`);