#!/usr/bin/env node
/**
 * Repair papers.json:
 * 1. Null out wrong osf_ids for mismatched early papers
 * 2. Add proper links for papers that have correct osf_ids but null link
 * 3. Try to fetch missing authors for papers with correct osf_ids
 */
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');

const papersPath = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const papers = JSON.parse(fs.readFileSync(papersPath, 'utf8'));

// Papers verified as having WRONG osf_ids (title doesn't match OSF)
const wrongIds = new Set([
  1, 10, 12, 18, 36, 39, 41, 44, 51, 53, 54, 61, 63, 66, 72,
  118, 121, 133, 138, 139, 142, 143, 144, 145, 147, 148, 149, 150, 151, 154, 157
]);

const API = 'https://api.osf.io/v2';
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function fetchAuthors(osfId) {
  // Get preprint to find node
  const preRes = await fetch(API + '/preprints/' + osfId);
  if (preRes.status === 429) { await sleep(3000); return fetchAuthors(osfId); }
  const preData = await preRes.json();
  const nodeId = preData.data?.relationships?.node?.data?.id;
  
  let url;
  if (nodeId) {
    url = API + '/nodes/' + nodeId + '/contributors/?page[size]=50&embed=users';
  } else {
    url = API + '/preprints/' + osfId + '/contributors/?embed=users';
  }
  
  let res = await fetch(url);
  if (res.status === 429) { await sleep(3000); res = await fetch(url); }
  let data = await res.json();
  
  if (data.errors || !data.data) {
    url = API + '/preprints/' + osfId + '/contributors/?embed=users';
    res = await fetch(url);
    if (res.status === 429) { await sleep(3000); res = await fetch(url); }
    data = await res.json();
  }
  
  const contribData = data.data || [];
  const bibs = contribData.filter(c => c.attributes.bibliographic).sort((a,b) => a.attributes.index - b.attributes.index);
  const names = [];
  
  for (const c of bibs) {
    const embedUser = c.embeds?.users;
    if (embedUser) {
      const userData = Array.isArray(embedUser.data) ? embedUser.data[0] : embedUser.data;
      if (userData?.attributes?.full_name) {
        names.push(userData.attributes.full_name);
        continue;
      }
    }
    const userLink = c.relationships?.users?.links?.related?.href;
    if (userLink) {
      try {
        const uRes = await fetch(userLink);
        if (uRes.status !== 429) {
          const uData = await uRes.json();
          names.push(uData.data.attributes.full_name);
        }
      } catch(e) {}
      await sleep(300);
    }
  }
  return names.join(', ');
}

async function main() {
  let fixed = 0;
  
  // Step 1: Null out wrong osf_ids
  for (const p of papers) {
    if (wrongIds.has(p.number) && p.osf_id) {
      console.log(`#${p.number}: Nulling wrong osf_id ${p.osf_id} (was: "${p.title.substring(0,50)}")`);
      p.osf_id = null;
      p.link = null;
      fixed++;
    }
  }
  
  // Step 2: Add links for papers with correct osf_ids but null link
  for (const p of papers) {
    if (p.osf_id && !p.link) {
      const link = 'https://osf.io/preprints/psyarxiv/' + p.osf_id;
      console.log(`#${p.number}: Adding link ${link}`);
      p.link = link;
      fixed++;
    }
  }
  
  // Step 3: Fetch authors for papers with correct osf_ids and missing/bad authors
  const needsAuthors = papers.filter(p => 
    p.osf_id && 
    (!p.authors || p.authors === 'Author metadata unavailable' || p.authors.trim() === '')
  );
  console.log(`\nFetching authors for ${needsAuthors.length} papers...`);
  
  for (const p of needsAuthors) {
    try {
      const authors = await fetchAuthors(p.osf_id);
      if (authors) {
        console.log(`#${p.number}: ${authors.substring(0,60)}...`);
        p.authors = authors;
        fixed++;
      }
      await sleep(350);
    } catch(e) {
      console.log(`#${p.number}: Error fetching authors: ${e.message}`);
    }
  }
  
  // Write updated papers.json
  fs.writeFileSync(papersPath, JSON.stringify(papers, null, 2));
  console.log(`\nDone. Fixed ${fixed} issues.`);
}

main().catch(console.error);