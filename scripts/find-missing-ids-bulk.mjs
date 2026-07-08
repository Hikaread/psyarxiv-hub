#!/usr/bin/env node
/**
 * Bulk download ALL PsyArXiv preprint IDs+titles from OSF API (concurrent),
 * then match against the 59 papers missing osf_ids.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';

const API_BASE = 'https://api.osf.io/v2/preprints/';
const PAPERS_JSON = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const CACHE_FILE = '/home/z/my-project/scripts/psyarxiv-all-titles.json';
const OUTPUT_FILE = '/home/z/my-project/scripts/missing-osf-results.json';
const CONCURRENCY = 5;  // parallel API requests
const PAGE_SIZE = 100;
const MAX_PAGES = 200;  // safety limit

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function fetchJson(url, retries = 3) {
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const resp = await fetch(url, {
        headers: { 'Accept': 'application/vnd.api+json' }
      });
      if (resp.ok) {
        return await resp.json();
      }
      if (resp.status === 429 && attempt < retries - 1) {
        await sleep((attempt + 1) * 3000);
        continue;
      }
      throw new Error(`HTTP ${resp.status}`);
    } catch (e) {
      if (attempt < retries - 1) {
        await sleep(1000 * (attempt + 1));
        continue;
      }
      throw e;
    }
  }
}

async function downloadAllTitles() {
  if (existsSync(CACHE_FILE)) {
    console.log(`Loading cached titles from ${CACHE_FILE}`);
    const cached = JSON.parse(readFileSync(CACHE_FILE, 'utf-8'));
    console.log(`Loaded ${cached.length} cached preprints`);
    return cached;
  }

  console.log('Downloading all PsyArXiv preprint titles...');

  // First, get the total count
  const firstPage = await fetchJson(
    `${API_BASE}?filter%5Bprovider%5D=psyarxiv&page%5Bsize%5D=1&sort=-date_created`
  );
  const total = firstPage.meta?.total || 10000;
  const totalPages = Math.ceil(total / PAGE_SIZE);
  console.log(`Total PsyArXiv preprints: ${total} (~${totalPages} pages)`);

  // Fetch all pages concurrently with rate limiting
  const allPreprints = [];
  let pagesFetched = 0;
  let activeRequests = 0;
  let pageQueue = [];

  for (let p = 1; p <= Math.min(totalPages, MAX_PAGES); p++) {
    pageQueue.push(p);
  }

  async function processPage(pageNum) {
    const url = `${API_BASE}?filter%5Bprovider%5D=psyarxiv&page%5Bsize%5D=${PAGE_SIZE}&page%5Bnumber%5D=${pageNum}&sort=-date_created`;
    const data = await fetchJson(url);
    const items = data.data || [];

    for (const item of items) {
      allPreprints.push({
        id: item.id,
        title: item.attributes?.title || '',
        date_created: (item.attributes?.date_created || '').substring(0, 10),
      });
    }

    pagesFetched++;
    if (pagesFetched % 10 === 0 || pagesFetched === pageQueue.length) {
      console.log(`  Progress: ${pagesFetched}/${pageQueue.length} pages, ${allPreprints.length} preprints`);
    }
  }

  // Process with concurrency limit
  while (pageQueue.length > 0 || activeRequests > 0) {
    while (activeRequests < CONCURRENCY && pageQueue.length > 0) {
      const page = pageQueue.shift();
      activeRequests++;
      processPage(page).catch(e => {
        console.error(`  Error on page ${page}: ${e.message}`);
      }).finally(() => {
        activeRequests--;
      });
    }
    if (pageQueue.length > 0 || activeRequests > 0) {
      await sleep(100);
    }
  }

  // Wait for any remaining requests
  await sleep(2000);

  // Save cache
  writeFileSync(CACHE_FILE, JSON.stringify(allPreprints, null, 2));
  console.log(`\nSaved ${allPreprints.length} preprints to ${CACHE_FILE}`);
  return allPreprints;
}

// Extract key words from a short title
function extractKeywords(shortTitle) {
  const stop = new Set([
    'a','an','the','and','or','of','for','in','on','to','with','by','from',
    'their','its','is','are','was','were','be','been','that','this','these',
    'those','not','no','but','at','if','study','analysis','review','research',
    'examination','based','using','between','among','into','clinical',
    'framework','model','effects','effect','role','association','predictors',
    'outcomes','findings','evidence','overview','perspective','considerations',
    'evaluating','evaluation','assessment','versus','therapeutic','approaches',
    'approach','systematic','additional','implications'
  ]);
  const words = shortTitle.match(/[a-zA-Z]+/g) || [];
  return words.filter(w => !stop.has(w.toLowerCase()) && w.length >= 3);
}

// Compute match score
function matchScore(shortTitle, apiTitle) {
  const sLower = shortTitle.toLowerCase();
  const aLower = apiTitle.toLowerCase();
  const keywords = extractKeywords(shortTitle);

  if (keywords.length === 0) return 0;

  // Key word hits
  const keyHits = keywords.filter(w => aLower.includes(w.toLowerCase())).length;
  const keyRatio = keyHits / keywords.length;

  // All word overlap
  const sWords = new Set(sLower.split(/\s+/));
  const aWords = new Set(aLower.split(/\s+/));
  const wordOverlap = [...sWords].filter(w => aWords.has(w) && w.length >= 3).length / sWords.size;

  // Rare term matching (words >= 7 chars are very specific)
  const rareTerms = keywords.filter(w => w.length >= 7);
  let rareBonus = 0;
  if (rareTerms.length > 0) {
    const rareHits = rareTerms.filter(w => aLower.includes(w.toLowerCase())).length;
    rareBonus = rareHits / rareTerms.length;
  }

  // Substring matching for specific phrases (e.g., "PEP therapy", "CBM-I")
  const phrases = shortTitle.match(/"[^"]+"|\([^)]+\)|[\w]+-[\w]+/g) || [];
  let phraseHits = 0;
  for (const phrase of phrases) {
    if (aLower.includes(phrase.toLowerCase().replace(/['"]/g, ''))) phraseHits++;
  }
  const phraseRatio = phrases.length > 0 ? phraseHits / phrases.length : 0;

  // Combined score
  let score;
  if (rareBonus >= 0.5 && rareTerms.length >= 2) {
    score = Math.max(keyRatio * 0.95, wordOverlap * 0.8, 0.65);
    score += rareBonus * 0.15;
  } else if (keyRatio >= 0.5) {
    score = Math.max(keyRatio * 0.9, wordOverlap * 0.7, phraseRatio * 0.8);
  } else if (keyRatio >= 0.3 && (wordOverlap > 0.3 || phraseRatio > 0)) {
    score = Math.max(keyRatio * 0.8, wordOverlap * 0.5, phraseRatio * 0.7);
  } else {
    score = Math.max(keyRatio * 0.7, wordOverlap * 0.4);
  }

  return Math.min(score, 1.0);
}

async function main() {
  const papers = JSON.parse(readFileSync(PAPERS_JSON, 'utf-8'));
  const missing = papers.filter(p => !p.osf_id);
  console.log(`Found ${missing.length} papers missing osf_id\n`);

  // Download all titles
  const allPreprints = await downloadAllTitles();
  console.log(`\nMatching against ${allPreprints.length} PsyArXiv preprints...\n`);

  const found = {};
  const notFound = [];

  for (const paper of missing) {
    const { number, title } = paper;
    let bestMatch = null;
    let bestScore = 0;

    for (const preprint of allPreprints) {
      const score = matchScore(title, preprint.title);
      if (score > bestScore) {
        bestScore = score;
        bestMatch = preprint;
      }
    }

    if (bestMatch && bestScore >= 0.35) {
      // Validate: at least one keyword must be in the API title
      const keywords = extractKeywords(title);
      const validHits = keywords.filter(w => bestMatch.title.toLowerCase().includes(w.toLowerCase())).length;
      if (validHits === 0 && keywords.length >= 2) {
        console.log(`#${number} REJECTED (no keywords match, score=${bestScore.toFixed(2)}): ${title.substring(0, 55)}`);
        console.log(`  Best: ${bestMatch.title.substring(0, 70)}`);
        notFound.push(number);
        continue;
      }

      const osfId = bestMatch.id.replace(/_v\d+$/i, '');
      console.log(`#${number} MATCH (${bestScore.toFixed(2)}): ${title.substring(0, 55)}`);
      console.log(`  -> ${bestMatch.title.substring(0, 70)}`);
      console.log(`  osf_id=${osfId}`);
      found[number] = {
        osf_id: osfId,
        api_title: bestMatch.title,
        link: `https://osf.io/preprints/psyarxiv/${osfId}`,
        score: +bestScore.toFixed(3),
        original_title: title,
      };
    } else {
      console.log(`#${number} NO MATCH (best=${bestScore.toFixed(2)}): ${title.substring(0, 55)}`);
      if (bestMatch) console.log(`  Best: ${bestMatch.title.substring(0, 70)}`);
      notFound.push(number);
    }
  }

  console.log(`\n${'='.repeat(60)}`);
  console.log(`RESULTS: Found ${Object.keys(found).length}/${missing.length} matches`);
  console.log(`${'='.repeat(60)}`);

  if (Object.keys(found).length > 0) {
    console.log(`\n--- FOUND ---`);
    for (const [num, info] of Object.entries(found).sort((a, b) => +a[0] - +b[0])) {
      console.log(`  #${num}: ${info.original_title.substring(0, 60)}`);
      console.log(`    -> ${info.api_title.substring(0, 70)}`);
      console.log(`    osf_id=${info.osf_id} score=${info.score}`);
    }
  }

  if (notFound.length > 0) {
    console.log(`\n--- NOT FOUND (${notFound.length}) ---`);
    for (const num of notFound) {
      const p = missing.find(m => m.number === num);
      console.log(`  #${num}: ${p.title}`);
    }
  }

  const output = {
    found,
    not_found_numbers: notFound,
    total_missing: missing.length,
    total_found: Object.keys(found).length,
  };
  writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
  console.log(`\nResults saved to ${OUTPUT_FILE}`);
}

main().catch(err => { console.error(err); process.exit(1); });