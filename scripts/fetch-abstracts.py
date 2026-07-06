#!/usr/bin/env python3
"""
Fetch abstracts from OSF API for papers with short summaries.
Outputs a JSON mapping of paper number -> abstract text.
"""
import urllib.request
import json
import time
import sys

def fetch_json(url):
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (compatible; PsyArXiv-Hub/1.0)'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

# Read short papers list
papers_path = '/home/z/my-project/psyarxiv-hub/data/papers.json'
with open(papers_path, 'r') as f:
    all_papers = json.load(f)

# Papers needing summary enrichment (first 200 only, summary < 150 chars)
need_abstracts = [
    p for p in all_papers 
    if p['number'] <= 200 and p.get('osf_id') and p.get('summary') and len(p['summary']) < 150
]

print(f"Papers needing abstracts: {len(need_abstracts)}", flush=True)

abstracts = {}
failed = 0

for i, paper in enumerate(need_abstracts):
    osf_id = paper['osf_id']
    base_id = osf_id.split('_v')[0] if '_v' in osf_id else osf_id
    
    sys.stdout.write(f"#{paper['number']} ({base_id})... ")
    sys.stdout.flush()
    
    try:
        data = fetch_json(f"https://api.osf.io/v2/preprints/{base_id}/")
        attrs = data.get('data', {}).get('attributes', {})
        abstract = attrs.get('abstract') or attrs.get('description', '')
        if abstract and len(abstract) > 50:
            abstracts[paper['number']] = abstract
            print(f"✓ ({len(abstract)} chars)", flush=True)
        else:
            print(f"✗ empty/short abstract", flush=True)
            failed += 1
    except Exception as e:
        print(f"✗ {e}", flush=True)
        failed += 1
    
    if (i + 1) % 5 == 0 and (i + 1) < len(need_abstracts):
        time.sleep(0.3)

print(f"\n=== Got {len(abstracts)} abstracts, {failed} failed ===", flush=True)

# Save abstracts to a temp file for the enrichment script
with open('/tmp/paper-abstracts.json', 'w') as f:
    json.dump(abstracts, f, indent=2, ensure_ascii=False)

print("Saved to /tmp/paper-abstracts.json", flush=True)