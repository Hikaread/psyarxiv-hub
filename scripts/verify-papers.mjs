#!/usr/bin/env node
/**
 * Verify all papers with osf_id against the OSF API.
 * Check title match, fix links, fetch missing authors.
 */
const API = 'https://api.osf.io/v2/preprints/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const fs = require('fs');
const papers = require('/home/z/my-project/psyarxiv-hub/data/papers.json');

async function verifyPaper(p) {
  const osfId = p.osf_id;
  if (!osfId) return { num: p.number, status: 'no_id' };

  try {
    const res = await fetch(API + osfId);
    if (res.status === 429) { await sleep(3000); return verifyPaper(p); }
    if (res.status === 404) return { num: p.number, status: 'not_found', osf_id: osfId };
    
    const data = await res.json();
    const apiTitle = data.data?.attributes?.title;
    const apiDesc = data.data?.attributes?.description || '';
    
    // Check title match (loose - check if key words overlap)
    const ourWords = p.title.toLowerCase().split(/\s+/).filter(w => w.length > 4);
    const apiWords = (apiTitle || '').toLowerCase().split(/\s+/).filter(w => w.length > 4);
    const overlap = ourWords.filter(w => apiWords.includes(w)).length;
    const matchScore = ourWords.length > 0 ? overlap / ourWords.length : 0;
    
    // Also get node ID for contributor fetch
    const nodeId = data.data?.relationships?.node?.data?.id;
    
    return {
      num: p.number,
      status: matchScore > 0.3 ? 'ok' : 'mismatch',
      osf_id: osfId,
      our_title: p.title,
      api_title: apiTitle,
      match_score: matchScore,
      nodeId: nodeId,
      has_link: !!p.link,
      has_authors: !!p.authors && p.authors !== 'Author metadata unavailable'
    };
  } catch (e) {
    return { num: p.number, status: 'error', error: e.message, osf_id: osfId };
  }
}

async function main() {
  const toCheck = papers.filter(p => p.osf_id);
  console.log('Verifying', toCheck.length, 'papers with osf_id against OSF API...');
  
  const results = [];
  for (let i = 0; i < toCheck.length; i++) {
    const r = await verifyPaper(toCheck[i]);
    results.push(r);
    if (r.status === 'mismatch' || r.status === 'not_found') {
      console.log(`#${r.num} [${r.status}] score=${r.match_score?.toFixed(2) || '-'} our="${(r.our_title||'').substring(0,50)}" api="${(r.api_title||'').substring(0,50)}"`);
    }
    if ((i + 1) % 20 === 0) console.log(`  ...${i+1}/${toCheck.length}`);
    await sleep(350);
  }
  
  const mismatches = results.filter(r => r.status === 'mismatch');
  const notFound = results.filter(r => r.status === 'not_found');
  const noLink = results.filter(r => r.status === 'ok' && !r.has_link);
  const noAuthor = results.filter(r => r.status === 'ok' && !r.has_authors);
  
  console.log('\n=== SUMMARY ===');
  console.log('OK:', results.filter(r => r.status === 'ok').length);
  console.log('MISMATCH:', mismatches.length);
  console.log('NOT FOUND:', notFound.length);
  console.log('ERRORS:', results.filter(r => r.status === 'error').length);
  console.log('OK but missing link:', noLink.length);
  console.log('OK but missing authors:', noAuthor.length);
  
  // Save full results for repair script
  fs.writeFileSync('/tmp/paper-verify-results.json', JSON.stringify(results, null, 2));
  console.log('\nFull results saved to /tmp/paper-verify-results.json');
}

main().catch(console.error);