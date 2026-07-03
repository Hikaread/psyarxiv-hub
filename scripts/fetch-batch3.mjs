#!/usr/bin/env node
/**
 * Fetch full details + contributors for candidate papers from OSF API.
 */
const API_BASE = 'https://api.osf.io/v2';
const PAUSE_MS = 300;

// Top clinically relevant candidates to fetch (compact IDs)
const CANDIDATES = [
  'ceu53',   // Psychosocial Wellbeing Assessment Tools for Children with CP
  '3ed7s',   // Resilience across pandemic phases in youth
  '6ypwr',   // Depressive Symptom Trajectories Around Retirement
  'pkwxy',   // Chronic Pain Processes Longitudinally (German)
  'mgbq2',   // Sensitive periods for childhood adversity
  '4nh62',   // Lost in aggregation: from score-based to representational mentalization
  'jxg3n',   // Intervention-Induced Neuroticism Change
  '7ehdm',   // Pre-Test Measurement of Alcohol Craving
  'he7rn',   // Delay discounting and nighttime drinking
  'kjerd',   // Recruiting Clinically-Relevant Stratified Samples
  '8j7n2',   // Coordinated Psychological Intervention Ensembles
  'fme25',   // Yoga psychology intervention, primal world beliefs
  'mwfah',   // Robustness of implicit evaluation updating
  '4s9jk',   // Positive Psychology intervention for high achievers
  '2c8xf',   // Dynamic networks, treatment selection, outcome prediction
  'uz3x5',   // Adolescent AI chatbot use
  '7s2e9',   // Trait Apathy and Fatigue, academic functioning
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
    throw new Error(`HTTP ${response.status} for ${url}`);
  }
}

async function main() {
  const results = {};
  
  for (const compactId of CANDIDATES) {
    console.error(`Fetching ${compactId}...`);
    try {
      // First get all versions to find the latest
      const preprintsRes = await fetchJson(`${API_BASE}/preprints/?filter[id]=${compactId}&filter[provider]=psyarxiv`);
      const items = preprintsRes.data || [];
      
      if (items.length === 0) {
        console.error(`  No preprint found for ${compactId}`);
        continue;
      }
      
      // Get the latest version
      const latest = items[0];
      const preprintId = latest.id; // This includes version like ceu53_v1
      const preprintUrl = `${API_BASE}/preprints/${preprintId}`;
      
      // Fetch full preprint details
      const detailRes = await fetchJson(preprintUrl);
      const detail = detailRes.data || {};
      
      // Fetch contributors
      let contributors = [];
      try {
        const contribUrl = detail.links?.contributors;
        if (contribUrl) {
          const contribRes = await fetchJson(contribUrl);
          contributors = (contribRes.data || []).map(c => {
            const attrs = c.attributes || {};
            return `${attrs.family_name || ''}, ${attrs.given_name || ''}`.trim().replace(/^, /, '');
          });
        }
      } catch (e) {
        console.error(`  Could not fetch contributors for ${compactId}: ${e.message}`);
      }
      
      results[compactId] = {
        id: preprintId,
        title: detail.attributes?.title || latest.attributes?.title || '',
        description: (detail.attributes?.description || latest.attributes?.description || '').substring(0, 3000),
        date_created: detail.attributes?.date_created || latest.attributes?.date_created || '',
        date_modified: detail.attributes?.date_modified || latest.attributes?.date_modified || '',
        date_published: detail.attributes?.date_published || '',
        doi: detail.attributes?.doi || latest.attributes?.doi || '',
        preprint_doi: detail.attributes?.preprint_doi || latest.attributes?.preprint_doi || '',
        subjects: (detail.attributes?.subjects || latest.attributes?.subjects || []).map(s => s.text || s),
        link: detail.links?.html || latest.links?.html || `https://osf.io/preprints/psyarxiv/${preprintId}`,
        contributors: contributors,
      };
      
      console.error(`  Got: ${results[compactId].title.substring(0, 80)}... (${contributors.length} contributors)`);
    } catch (e) {
      console.error(`  Error fetching ${compactId}: ${e.message}`);
    }
  }
  
  const fs = await import('fs');
  fs.writeFileSync('/home/z/my-project/scripts/fetched-candidates.json', JSON.stringify(results, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify({ fetched: Object.keys(results).length, ids: Object.keys(results) }, null, 2));
}

main().catch(err => { console.error(err); process.exitCode = 1; });
