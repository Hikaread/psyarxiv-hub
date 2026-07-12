#!/usr/bin/env node

/**
 * Discover new PsyArXiv preprints from the OSF API.
 * Scans day-by-day from today backwards, checking against seen-compact-ids.json.
 * Stops when ≥ MIN_UNSEEN unseen papers are found.
 * Scans until it reaches a day where ALL papers are already seen (the true frontier),
 *   or hits MAX_LOOKBACK_DAYS as a safety net.
 */

const API_BASE = 'https://api.osf.io/v2';
const PAUSE_MS = 300;
const MIN_UNSEEN = 15;           // stop when this many unseen papers collected
const MAX_LOOKBACK_DAYS = 730;  // safety net: don't scan more than 2 years back
const SEEN_IDS_FILE = '/home/z/my-project/psyarxiv-hub/data/seen-compact-ids.json';
const OUTPUT_FILE = '/home/z/my-project/scripts/discovered-papers.json';

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchJson(url) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const response = await fetch(url, {
      headers: { 'Accept': 'application/vnd.api+json' }
    });
    if (response.ok) {
      if (PAUSE_MS > 0) await sleep(PAUSE_MS);
      return response.json();
    }
    if (response.status === 429 && attempt < 2) {
      await sleep((attempt + 1) * 3000);
      continue;
    }
    throw new Error(`HTTP ${response.status} for ${url}`);
  }
}

function toDateStr(d) {
  return d.toISOString().split('T')[0]; // YYYY-MM-DD
}

function stripVersion(osfId) {
  return (osfId || '').replace(/_v\d+$/i, '');
}

async function main() {
  const fs = await import('fs');

  // Load already-seen compact IDs
  let seenIds = new Set();
  try {
    const raw = JSON.parse(fs.readFileSync(SEEN_IDS_FILE, 'utf8'));
    for (const id of raw) seenIds.add(id.toLowerCase());
    console.error(`Loaded ${seenIds.size} seen IDs`);
  } catch {
    console.error('No seen-IDs file found, starting fresh');
  }

  const allPapers = [];
  let dayOffset = 0;
  let daysWithNewPapers = 0;
  let daysFullyScanned = 0;
  let stopReason = '';

  // Scan day-by-day from today backwards
  while (true) {
    const scanDate = new Date();
    scanDate.setUTCDate(scanDate.getUTCDate() - dayOffset);
    const dateStr = toDateStr(scanDate);
    const nextDateStr = toDateStr(new Date(scanDate.getTime() + 86400000));

    console.error(`\n--- Day ${dayOffset}: scanning ${dateStr} ---`);

    // Fetch papers created on this specific day
    const url = `${API_BASE}/preprints/?filter[provider]=psyarxiv&sort=date_created&filter[date_created][gte]=${dateStr}T00:00:00&filter[date_created][lt]=${nextDateStr}T00:00:00&page[size]=100`;

    let dayPapers = [];
    let pageUrl = url;
    let pageCount = 0;

    while (pageUrl) {
      pageCount++;
      const payload = await fetchJson(pageUrl);
      const items = payload.data || [];

      for (const item of items) {
        dayPapers.push({
          osf_id: item.id,
          title: item.attributes?.title || '',
          date_created: item.attributes?.date_created || '',
          date_modified: item.attributes?.date_modified || '',
          description: (item.attributes?.description || '').substring(0, 2000),
          doi: item.attributes?.doi || '',
          preprint_doi: item.attributes?.preprint_doi || '',
          subjects: (item.attributes?.subjects || []).map(s => s.text || s),
          link: item.links?.html || '',
        });
      }

      pageUrl = payload.links?.next || null;
      if (items.length < 100) break;
    }

    console.error(`  Fetched ${dayPapers.length} papers (${pageCount} pages)`);

    // Deduplicate within this day
    const daySeen = new Set();
    dayPapers = dayPapers.filter(p => {
      const compact = stripVersion(p.osf_id).toLowerCase();
      if (daySeen.has(compact)) return false;
      daySeen.add(compact);
      return true;
    });

    // Filter to unseen only
    let unseenDayPapers = dayPapers.filter(p => {
      const compact = stripVersion(p.osf_id).toLowerCase();
      return !seenIds.has(compact);
    });

    console.error(`  Unseen: ${unseenDayPapers.length} / ${dayPapers.length}`);

    if (unseenDayPapers.length > 0) {
      daysWithNewPapers++;
      allPapers.push(...unseenDayPapers);
      console.error(`  Total unseen collected so far: ${allPapers.length}`);

      if (allPapers.length >= MIN_UNSEEN) {
        stopReason = `Reached ${MIN_UNSEEN} unseen papers after ${dayOffset} days`;
        console.error(`  ✓ ${stopReason}`);
        break;
      }
    } else {
      daysFullyScanned++;
      // If every paper on this day was already seen, we may have reached the frontier.
      // Require CONSECUTIVE_FULLY_SEEN days of 100% seen to confirm we've passed the frontier.
      const CONSECUTIVE_FULLY_SEEN = 3;
      if (daysFullyScanned >= CONSECUTIVE_FULLY_SEEN && dayPapers.length > 0 && unseenDayPapers.length === 0) {
        stopReason = `All papers seen for ${daysFullyScanned} consecutive days — reached seen-ID frontier at ${dateStr}`;
        console.error(`  ✓ ${stopReason}`);
        break;
      }
    }

    // Safety net: don't scan more than MAX_LOOKBACK_DAYS
    if (dayOffset + 1 >= MAX_LOOKBACK_DAYS) {
      stopReason = `Reached max lookback of ${MAX_LOOKBACK_DAYS} days`;
      console.error(`  ✓ ${stopReason}`);
      break;
    }

    dayOffset++;
  }

  // Final dedup across all days
  const finalSeen = new Set();
  const deduped = allPapers.filter(p => {
    const compact = stripVersion(p.osf_id).toLowerCase();
    if (finalSeen.has(compact)) return false;
    finalSeen.add(compact);
    return true;
  });

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(deduped, null, 2) + '\n', 'utf8');

  const report = {
    stopReason,
    daysScanned: dayOffset + 1,
    daysWithNewPapers,
    totalFetched: deduped.length,
    totalUnseen: deduped.length,
    output: OUTPUT_FILE
  };

  console.log(JSON.stringify(report, null, 2));
}

main().catch(err => { console.error(err); process.exitCode = 1; });