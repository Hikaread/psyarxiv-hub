#!/usr/bin/env node
/**
 * Batch search PsyArXiv using agent-browser.
 * For each paper: search, extract osf_ids from results, save progress.
 * Uses eval() to extract links directly from the DOM.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';

const PAPERS_JSON = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const PROGRESS_FILE = '/home/z/my-project/scripts/browser-search-progress.json';
const OUTPUT_FILE = '/home/z/my-project/scripts/missing-osf-results.json';

const papers = JSON.parse(readFileSync(PAPERS_JSON, 'utf-8'));
const missing = papers.filter(p => !p.osf_id);

// Load progress
let progress = { found: {}, not_found: [], processed: [] };
if (existsSync(PROGRESS_FILE)) {
  progress = JSON.parse(readFileSync(PROGRESS_FILE, 'utf-8'));
}

function saveProgress() {
  writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
}

function browserExec(cmd) {
  try {
    return execSync(`agent-browser ${cmd} 2>/dev/null`, {
      timeout: 30000, encoding: 'utf-8', maxBuffer: 1024 * 1024
    }).trim();
  } catch (e) {
    return '';
  }
}

function sleep(ms) { execSync(`sleep ${ms/1000}`); }

function getSearchQuery(paper) {
  const title = paper.title;
  const authors = paper.authors || 'Unknown';
  
  const stop = new Set(['a','an','the','and','or','of','for','in','on','to','with','by','from','their','its','is','are','was','were','be','been','that','this','these','those','not','no','but','at','if','study','analysis','review','research','examination','based','using','between','among','into','clinical','framework','model','effects','effect','role','association','predictors','outcomes','findings','evidence','overview','perspective','considerations','evaluating','evaluation','assessment','versus','therapeutic','approaches','approach','systematic','additional','implications']);
  
  // Extract key terms
  const abbrevs = (title.match(/\b[A-Z]{2,}-?[A-Z]*\b/g) || []).map(a => a.toLowerCase());
  const hyphenated = (title.match(/[a-zA-Z]+-[a-zA-Z]+/g) || []).map(h => h.toLowerCase());
  const words = (title.match(/[a-zA-Z]+/g) || [])
    .filter(w => !stop.has(w.toLowerCase()) && w.length >= 5)
    .sort((a, b) => b.length - a.length);
  
  // For author papers, include first author last name
  let authorTerm = '';
  if (authors !== 'Unknown') {
    const parts = authors.split(',')[0].trim().split(' ');
    authorTerm = parts[parts.length - 1];
  }
  
  // Build query: most specific terms first
  const terms = [...abbrevs, ...hyphenated, ...words.slice(0, 3)];
  const unique = [...new Set(terms)];
  
  if (authorTerm) {
    return `${authorTerm} ${unique.slice(0, 3).join(' ')}`.trim();
  }
  return unique.slice(0, 4).join(' ');
}

function searchAndExtract(query) {
  // Fill search box
  browserExec(`fill @e41 "${query.replace(/"/g, '\\"')}"`);
  sleep(300);
  browserExec('press Enter');
  browserExec('wait --load networkidle');
  sleep(1000);
  
  // Extract all osf_ids from result links using JavaScript
  const jsResult = browserExec(`eval "
    const links = document.querySelectorAll('a[href*=\"preprints/psyarxiv/\"]');
    const results = [];
    const seen = new Set();
    links.forEach(a => {
      const href = a.href || '';
      const match = href.match(/psyarxiv\\/([a-z0-9]{5})/i);
      if (match && !seen.has(match[1].toLowerCase())) {
        seen.add(match[1].toLowerCase());
        results.push({
          osf_id: match[1].toLowerCase(),
          title: a.textContent?.trim()?.substring(0, 100) || '',
          url: href
        });
      }
    });
    JSON.stringify(results);
  "`);
  
  try {
    return JSON.parse(jsResult);
  } catch {
    return [];
  }
}

function checkMatch(paper, results) {
  const titleLower = paper.title.toLowerCase();
  const words = titleLower.split(/\s+/).filter(w => w.length >= 4);
  const keyWords = words.filter(w => !['therapeutic','approaches','approach','study','analysis','review','systematic','clinical','framework','model','effects','findings','implications','evaluation','assessment'].includes(w));
  
  for (const r of results) {
    const rLower = r.title.toLowerCase();
    const matchWords = keyWords.filter(w => rLower.includes(w));
    const matchRatio = matchWords.length / Math.max(keyWords.length, 1);
    
    if (matchRatio >= 0.3 || (matchWords.length >= 2 && keyWords.length <= 5)) {
      return r;
    }
  }
  return null;
}

// Main
const toProcess = missing.filter(p => !progress.processed.includes(p.number));
console.log(`Already processed: ${progress.processed.length}, Remaining: ${toProcess.length}`);

// Open the discover page once
browserExec('open "https://osf.io/preprints/psyarxiv/discover" --timeout 30000');
sleep(3000);

for (const paper of toProcess) {
  const { number, title } = paper;
  console.log(`\n#${number}: ${title}`);
  
  const query = getSearchQuery(paper);
  console.log(`  Query: ${query}`);
  
  const results = searchAndExtract(query);
  console.log(`  Found ${results.length} results on page`);
  
  if (results.length > 0) {
    const match = checkMatch(paper, results);
    if (match) {
      console.log(`  MATCH: ${match.osf_id} - ${match.title.substring(0, 70)}`);
      progress.found[String(number)] = {
        osf_id: match.osf_id,
        api_title: match.title,
        link: `https://osf.io/preprints/psyarxiv/${match.osf_id}`,
        original_title: title,
        query_used: query,
      };
    } else {
      console.log(`  No matching result`);
      for (const r of results.slice(0, 3)) {
        console.log(`    - ${r.osf_id}: ${r.title.substring(0, 60)}`);
      }
      progress.not_found.push(number);
    }
  } else {
    console.log(`  0 results`);
    progress.not_found.push(number);
  }
  
  progress.processed.push(number);
  saveProgress();
  
  // Go back to discover page for next search
  browserExec('open "https://osf.io/preprints/psyarxiv/discover" --timeout 15000');
  sleep(2000);
}

const output = {
  found: progress.found,
  not_found_numbers: progress.not_found,
  total_missing: missing.length,
  total_found: Object.keys(progress.found).length,
};
writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));

console.log(`\n${'='.repeat(60)}`);
console.log(`DONE: Found ${Object.keys(progress.found).length}/${missing.length}`);
console.log(`Results: ${OUTPUT_FILE}`);

browserExec('close');