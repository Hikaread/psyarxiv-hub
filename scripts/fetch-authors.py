#!/usr/bin/env python3
"""Fetch authors from OSF API for papers with missing author data."""
import urllib.request
import json
import time
import sys

USER_CACHE = {}  # cache user_id -> name

def fetch_json(url):
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (compatible; PsyArXiv-Hub/1.0)'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def get_user_name(user_id):
    if user_id in USER_CACHE:
        return USER_CACHE[user_id]
    try:
        data = fetch_json(f"https://api.osf.io/v2/users/{user_id}/")
        name = data.get('data', {}).get('attributes', {}).get('full_name', '').strip()
        USER_CACHE[user_id] = name
        return name
    except:
        return None

def fetch_authors_for_preprint(base_id):
    """Fetch all contributor names for a preprint."""
    url = f"https://api.osf.io/v2/preprints/{base_id}/contributors/?page[size]=50"
    try:
        data = fetch_json(url)
        contributors = data.get('data', [])
        
        # Build list of (index, user_id) pairs
        contrib_list = []
        for c in contributors:
            user_data = c.get('relationships', {}).get('users', {}).get('data', {})
            if isinstance(user_data, dict) and user_data.get('id'):
                index = c.get('attributes', {}).get('index', 999)
                contrib_list.append((index, user_data['id']))
        
        # Sort by index
        contrib_list.sort(key=lambda x: x[0])
        
        # Fetch names
        names = []
        for idx, uid in contrib_list:
            name = get_user_name(uid)
            if name:
                names.append(name)
            time.sleep(0.15)  # rate limit
        
        result = ', '.join(names[:10])
        if len(names) > 10:
            result += ', et al.'
        return result if result else None
    except Exception as e:
        print(f"  API error for {base_id}: {e}", flush=True)
        return None

# Read papers
papers_path = '/home/z/my-project/psyarxiv-hub/data/papers.json'
with open(papers_path, 'r') as f:
    papers = json.load(f)

need_authors = [p for p in papers if p.get('osf_id') and (not p.get('authors') or p['authors'] == 'Unknown')]
print(f"Papers needing authors: {len(need_authors)}", flush=True)

fetched = 0
failed = 0
results = {}

for i, paper in enumerate(need_authors):
    osf_id = paper['osf_id']
    base_id = osf_id.split('_v')[0] if '_v' in osf_id else osf_id
    
    sys.stdout.write(f"#{paper['number']} ({base_id})... ")
    sys.stdout.flush()
    
    authors = fetch_authors_for_preprint(base_id)
    if authors:
        results[paper['number']] = authors
        display = authors[:55] + '...' if len(authors) > 55 else authors
        print(f"✓ {display}", flush=True)
        fetched += 1
    else:
        print("✗ not found", flush=True)
        failed += 1
    
    # Extra delay between papers
    if (i + 1) < len(need_authors):
        time.sleep(0.5)

print(f"\n=== Fetched {fetched}, Failed {failed} ===", flush=True)

# Apply updates
for p in papers:
    if p['number'] in results:
        p['authors'] = results[p['number']]

with open(papers_path, 'w') as f:
    json.dump(papers, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f"Saved {len(papers)} papers", flush=True)