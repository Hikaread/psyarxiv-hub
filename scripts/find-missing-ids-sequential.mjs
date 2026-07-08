#!/usr/bin/env node
/**
 * Find missing osf_ids one paper at a time using web search.
 * Saves progress after each paper to be resilient to timeouts.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';

const PAPERS_JSON = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const PROGRESS_FILE = '/home/z/my-project/scripts/find-ids-progress.json';
const OUTPUT_FILE = '/home/z/my-project/scripts/missing-osf-results.json';
const DELAY_MS = 8000; // 8 seconds between searches to avoid rate limiting

const papers = JSON.parse(readFileSync(PAPERS_JSON, 'utf-8'));
const missing = papers.filter(p => !p.osf_id);
console.log(`Found ${missing.length} papers missing osf_id`);

// Load progress
let progress = { found: {}, not_found: [], processed: [] };
if (existsSync(PROGRESS_FILE)) {
  progress = JSON.parse(readFileSync(PROGRESS_FILE, 'utf-8'));
  console.log(`Loaded progress: ${Object.keys(progress.found).length} found, ${progress.not_found.length} not found, ${progress.processed.length} processed`);
}

function saveProgress() {
  writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
}

function extractOsfId(url) {
  const match = url.match(/psyarxiv\/([a-z0-9]{5})/i);
  return match ? match[1].toLowerCase() : null;
}

function getSearchQueries(paper) {
  const title = paper.title;
  const authors = paper.authors || 'Unknown';
  const queries = [];

  // Query 1: Most specific terms from title
  const stop = new Set(['a','an','the','and','or','of','for','in','on','to','with','by','from','their','its','is','are','was','were','be','been','that','this','these','those','not','no','but','at','if','study','analysis','review','research','examination','based','using','between','among','into','clinical','framework','model','effects','effect','role','association','predictors','outcomes','findings','evidence','overview','perspective','considerations','evaluating','evaluation','assessment','versus','therapeutic','approaches','approach','systematic','additional','implications']);

  // Extract key terms (longest/most specific)
  const words = title.match(/[a-zA-Z]+/g) || [];
  const keyWords = words.filter(w => !stop.has(w.toLowerCase()) && w.length >= 4);
  keyWords.sort((a, b) => b.length - a.length);

  // Query with top 3 specific words
  if (keyWords.length >= 2) {
    queries.push(`site:osf.io/preprints/psyarxiv "${keyWords[0]}" "${keyWords[1]}"`);
  }
  if (keyWords.length >= 3) {
    queries.push(`site:osf.io/preprints/psyarxiv ${keyWords.slice(0, 3).join(' ')}`);
  }

  // If there's a colon, use the part after colon (usually more specific)
  if (title.includes(':')) {
    const afterColon = title.split(':').pop().trim();
    const acWords = afterColon.split(/\s+/).filter(w => !stop.has(w.toLowerCase()) && w.length >= 4);
    if (acWords.length >= 2) {
      queries.push(`site:osf.io/preprints/psyarxiv "${acWords.slice(0, 2).join('" "')}"`);
    }
  }

  // If we have authors, add an author-based query
  if (authors !== 'Unknown') {
    const lastNames = authors.split(',').map(a => a.trim().split(' ').pop());
    if (lastNames.length >= 1) {
      queries.push(`site:osf.io/preprints/psyarxiv ${lastNames[0]} ${keyWords[0] || ''}`.trim());
    }
  }

  // Fallback: just search the full title in quotes
  queries.push(`site:osf.io/preprints/psyarxiv "${title.substring(0, 60)}"`);

  return [...new Set(queries)].slice(0, 3); // max 3 queries per paper
}

function search(query) {
  try {
    const args = JSON.stringify({ query, num: 5 });
    const result = execSync(
      `z-ai function -n web_search -a '${args.replace(/'/g, "'\\''")}' 2>/dev/null`,
      { timeout: 30000, encoding: 'utf-8', maxBuffer: 1024 * 1024 }
    );
    return JSON.parse(result);
  } catch (e) {
    if (e.message?.includes('429')) {
      console.log('    Rate limited, waiting longer...');
      execSync('sleep 15');
      return null;
    }
    return null;
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  const toProcess = missing.filter(p => !progress.processed.includes(p.number));

  console.log(`Already processed: ${progress.processed.length}, Remaining: ${toProcess.length}\n`);

  for (const paper of toProcess) {
    const { number, title } = paper;
    console.log(`\n#${number}: ${title}`);

    if (progress.found[String(number)]) {
      console.log('  Already found, skipping');
      continue;
    }

    const queries = getSearchQueries(paper);
    let foundId = null;

    for (let qi = 0; qi < queries.length && !foundId; qi++) {
      const query = queries[qi];
      console.log(`  Query ${qi + 1}: ${query.substring(0, 80)}`);

      const results = search(query);
      if (!results || !Array.isArray(results)) continue;

      for (const r of results) {
        const osfId = extractOsfId(r.url);
        if (osfId) {
          // Check if this looks like a real match
          const titleLower = title.toLowerCase();
          const nameLower = (r.name || '').toLowerCase();
          const snippetLower = (r.snippet || '').toLowerCase();

          const titleWords = titleLower.split(/\s+/).filter(w => w.length >= 4);
          const matchWords = titleWords.filter(w =>
            nameLower.includes(w) || snippetLower.includes(w)
          );

          if (matchWords.length >= 1 || titleWords.length <= 2) {
            foundId = {
              osf_id: osfId,
              api_title: r.name,
              url: r.url,
              link: `https://osf.io/preprints/psyarxiv/${osfId}`,
              snippet: (r.snippet || '').substring(0, 200),
              match_words: matchWords.length,
              query_used: query,
            };
            console.log(`  FOUND: ${osfId} (${matchWords.length} word matches)`);
            console.log(`  Title: ${r.name?.substring(0, 80)}`);
            break;
          } else {
            console.log(`  Skipped ${osfId} (only ${matchWords.length}/${titleWords.length} word matches)`);
          }
        }
      }

      // Delay between queries
      if (qi < queries.length - 1) await sleep(DELAY_MS);
    }

    if (foundId) {
      progress.found[String(number)] = { ...foundId, original_title: title };
    } else {
      progress.not_found.push(number);
      console.log('  NOT FOUND');
    }
    progress.processed.push(number);
    saveProgress();

    // Delay between papers
    await sleep(DELAY_MS);
  }

  // Write final output
  const output = {
    found: progress.found,
    not_found_numbers: progress.not_found,
    total_missing: missing.length,
    total_found: Object.keys(progress.found).length,
  };
  writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));

  console.log(`\n${'='.repeat(60)}`);
  console.log(`FINAL: Found ${Object.keys(progress.found).length}/${missing.length} osf_ids`);
  console.log(`Results saved to ${OUTPUT_FILE}`);
}

main().catch(err => { console.error(err); saveProgress(); process.exit(1); });