/**
 * Restore removed papers from git history.
 * Re-inserts them into papers.json, re-numbers, and saves.
 * Papers without osf_ids will have null values (links to be found later).
 */

import { readFileSync, writeFileSync } from 'fs';

const before = JSON.parse(readFileSync('/tmp/papers-before-revamp.json', 'utf-8'));
const current = JSON.parse(readFileSync('/home/z/my-project/psyarxiv-hub/data/papers.json', 'utf-8'));

// True duplicates to permanently remove (same osf_id as a kept paper)
const dupOsfIds = new Set(['5aqxg', 'f53wp']);

// Find papers that were removed
const currentTitles = new Set(current.map(p => p.title.toLowerCase().trim()));

const toRestore = before.filter(p => {
  // Not in current by title
  if (currentTitles.has(p.title.toLowerCase().trim())) return false;
  // Not a true duplicate
  if (p.osf_id && dupOsfIds.has(p.osf_id.replace(/_v\d+$/, ''))) return false;
  return true;
});

console.log(`Papers to restore: ${toRestore.length}`);

// Clean up restored papers: remove Google placeholder links, set proper fields
for (const p of toRestore) {
  // Remove Google placeholder links
  if (p.link && p.link.includes('google.com/search')) {
    p.link = null;
  }
  // Remove published field if it's null
  if (p.published === null) {
    delete p.published;
  }
  // Ensure categories is array
  if (typeof p.categories === 'string') {
    p.categories = [p.categories];
  }
}

// Merge: current papers + restored papers, sorted by original number
// First, create a map of original number -> paper for restored ones
const restoredByOrigNum = new Map();
for (const p of toRestore) {
  restoredByOrigNum.set(p.number, p);
}

// We need to interleave the restored papers back into the correct positions
// The current papers were renumbered sequentially after removal.
// We need to figure out where each restored paper fits.

// Strategy: create a list of all papers (current + restored) with their 
// "approximate original position", sort by that, then re-number.

// For current papers, we need to figure out their approximate original position.
// Since 61 papers were removed and current has 425, the original had 486.
// Current #1 was originally #2 (since original #1 was removed)
// This is complex. Let me use a simpler approach:
// Merge all papers, sort by a combination of date_posted and original number,
// then re-number.

const allPapers = [...current, ...toRestore];

// Sort by: date_posted (desc), then by some original ordering hint
allPapers.sort((a, b) => {
  // Primary: date_posted descending (newest first)
  const dateA = a.date_posted || '0000-00-00';
  const dateB = b.date_posted || '0000-00-00';
  if (dateA !== dateB) return dateB.localeCompare(dateA);
  
  // Secondary: for same date, use original number as tiebreaker (lower = first)
  return (a.number || 9999) - (b.number || 9999);
});

// Re-number
for (let i = 0; i < allPapers.length; i++) {
  allPapers[i].number = i + 1;
}

console.log(`Total papers after restore: ${allPapers.length}`);

// Verify
const titles = new Set(allPapers.map(p => p.title.toLowerCase().trim()));
console.log(`Unique titles: ${titles.size} (should equal ${allPapers.length})`);
if (titles.size !== allPapers.length) {
  console.error('WARNING: Duplicate titles detected!');
}

writeFileSync(
  '/home/z/my-project/psyarxiv-hub/data/papers.json',
  JSON.stringify(allPapers, null, 2) + '\n'
);
console.log('Saved to papers.json');

// Report papers still needing links
const noLink = allPapers.filter(p => !p.link && !p.osf_id);
console.log(`\nPapers still needing osf_id/link: ${noLink.length}`);
for (const p of noLink) {
  console.log(`  #${p.number}: ${p.title}`);
}