#!/usr/bin/env node
/**
 * Fetch contributors with embedded user data for candidate preprints.
 */
const API_BASE = 'https://api.osf.io/v2';
const PAUSE_MS = 300;

const IDS = [
  'ceu53_v1', '3ed7s_v1', '6ypwr_v6', 'pkwxy_v3', 'mgbq2_v1',
  '4nh62_v1', 'jxg3n_v3', '7ehdm_v2', 'he7rn_v1', 'kjerd_v2',
  '8j7n2_v1', 'fme25_v1', 'mwfah_v3', '4s9jk_v1', '2c8xf_v3',
  'uz3x5_v1', '7s2e9_v3'
];

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
    return null;
  }
}

async function main() {
  const results = {};
  
  for (const id of IDS) {
    console.error(`Fetching ${id}...`);
    try {
      const detailRes = await fetchJson(`${API_BASE}/preprints/${id}`);
      if (!detailRes || !detailRes.data) {
        console.error(`  Could not fetch preprint detail`);
        results[id] = [];
        continue;
      }
      
      const nodeId = detailRes.data.relationships?.node?.data?.id;
      if (!nodeId) {
        console.error(`  No node ID found`);
        results[id] = [];
        continue;
      }
      
      // Fetch contributors with embedded users
      const contribRes = await fetchJson(`${API_BASE}/nodes/${nodeId}/contributors/?page[size]=50&embed=users`);
      if (!contribRes || !contribRes.data) {
        console.error(`  Could not fetch contributors`);
        results[id] = [];
        continue;
      }
      
      const contributors = contribRes.data
        .filter(c => c.attributes?.bibliographic) // only bibliographic contributors
        .sort((a, b) => (a.attributes?.index || 0) - (b.attributes?.index || 0))
        .map(c => {
          const embed = c.embeds?.users?.data?.attributes;
          return embed?.full_name || 'Unknown';
        });
      
      results[id] = contributors;
      console.error(`  Got ${contributors.length}: ${contributors.slice(0, 3).join(', ')}`);
    } catch (e) {
      console.error(`  Error: ${e.message}`);
      results[id] = [];
    }
  }
  
  const fs = await import('fs');
  fs.writeFileSync('/home/z/my-project/scripts/contributors-batch3.json', JSON.stringify(results, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify({ fetched: Object.keys(results).length }, null, 2));
}

main().catch(err => { console.error(err); process.exitCode = 1; });
