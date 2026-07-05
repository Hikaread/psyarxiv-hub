/**
 * Phase 1: Remove duplicates and clean up problematic papers
 * 
 * Removes:
 * 1. Papers that are confirmed duplicates (same osf_id)
 * 2. Papers with Google search placeholder links AND no osf_id (unverifiable)
 * 3. Papers with no link AND no osf_id AND no osf_id can be found (will be marked)
 * 
 * After removal, re-numbers all papers sequentially.
 */

import { readFileSync, writeFileSync } from 'fs';

const papersPath = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const papers = JSON.parse(readFileSync(papersPath, 'utf-8'));

// Step 1: Identify confirmed duplicates (same osf_id)
const osfIdMap = {};
for (const p of papers) {
  if (p.osf_id) {
    if (!osfIdMap[p.osf_id]) osfIdMap[p.osf_id] = [];
    osfIdMap[p.osf_id].push(p.number);
  }
}

const duplicateNumbers = new Set();
for (const [id, nums] of Object.entries(osfIdMap)) {
  if (nums.length > 1) {
    // Keep the first one, remove the rest
    console.log(`Duplicate osf_id ${id}: papers ${nums.join(', ')} — removing ${nums.slice(1).join(', ')}`);
    for (const n of nums.slice(1)) duplicateNumbers.add(n);
  }
}

// Step 2: Remove papers with Google placeholder links AND no osf_id
// These are unverifiable and link to Google searches
const googlePlaceholderNumbers = new Set();
for (const p of papers) {
  if (p.link && p.link.includes('google.com/search') && !p.osf_id) {
    googlePlaceholderNumbers.add(p.number);
  }
}
console.log(`\nGoogle placeholder links (no osf_id): ${googlePlaceholderNumbers.size} papers`);
for (const n of [...googlePlaceholderNumbers].sort((a,b) => a-b)) {
  const p = papers.find(x => x.number === n);
  console.log(`  #${n}: ${p.title}`);
}

// Step 3: Papers with no link AND no osf_id that aren't already caught
const noLinkNoOsf = new Set();
for (const p of papers) {
  if (!p.link && !p.osf_id && !duplicateNumbers.has(p.number) && !googlePlaceholderNumbers.has(p.number)) {
    noLinkNoOsf.add(p.number);
  }
}
console.log(`\nNo link AND no osf_id (remaining): ${noLinkNoOsf.size} papers`);
for (const n of [...noLinkNoOsf].sort((a,b) => a-b)) {
  const p = papers.find(x => x.number === n);
  console.log(`  #${n}: ${p.title}`);
}

// Combine all to remove
const allToRemove = new Set([...duplicateNumbers, ...googlePlaceholderNumbers, ...noLinkNoOsf]);
console.log(`\n=== TOTAL TO REMOVE: ${allToRemove.size} papers ===`);

// Check: what about google placeholder papers that DO have osf_ids?
const googleWithOsf = [];
for (const p of papers) {
  if (p.link && p.link.includes('google.com/search') && p.osf_id) {
    googleWithOsf.push(p);
  }
}
console.log(`\nGoogle placeholder links WITH osf_id (will fix link): ${googleWithOsf.length}`);
for (const p of googleWithOsf) {
  console.log(`  #${p.number}: ${p.title} (osf: ${p.osf_id})`);
}

// Actually perform the removal
const kept = papers.filter(p => !allToRemove.has(p.number));
console.log(`\nBefore: ${papers.length} papers`);
console.log(`After removal: ${kept.length} papers`);

// Re-number sequentially
for (let i = 0; i < kept.length; i++) {
  kept[i].number = i + 1;
}

// Fix Google placeholder links for papers that have osf_ids
for (const p of kept) {
  if (p.link && p.link.includes('google.com/search') && p.osf_id) {
    const baseId = p.osf_id.replace(/_v\d+$/, '');
    p.link = `https://osf.io/preprints/psyarxiv/${baseId}`;
    console.log(`Fixed link for #${p.number}: ${p.title} → ${p.link}`);
  }
}

// Save
writeFileSync(papersPath, JSON.stringify(kept, null, 2) + '\n');
console.log(`\nSaved ${kept.length} papers to ${papersPath}`);