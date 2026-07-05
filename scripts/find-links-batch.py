#!/usr/bin/env python3
"""Search for papers needing links, 10 at a time. Resumable."""
import subprocess
import json
import re
import time
import sys
import os

PAPERS_PATH = '/home/z/my-project/psyarxiv-hub/data/papers.json'
RESULTS_PATH = '/tmp/link-results.json'

def load_results():
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            return json.load(f)
    return {}

def save_results(results):
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def search_paper(title):
    """Search for a paper on PsyArXiv and return osf_id if found."""
    clean = re.sub(r'\(.*?\)', '', title).strip()
    words = clean.split()[:5]
    query = ' '.join(words) + ' site:osf.io psyarxiv'
    
    try:
        result = subprocess.run(
            ['z-ai', 'function', '-n', 'web_search', '-a', 
             json.dumps({"query": query, "num": 5})],
            capture_output=True, text=True, timeout=25
        )
        if result.returncode != 0:
            return None
        
        search_results = json.loads(result.stdout.strip())
        
        for r in search_results:
            url = r.get('url', '')
            m = re.search(r'osf\.io/([a-z0-9]{5}(?:_v\d+)*)', url)
            if m:
                osf_id = m.group(1)
                # Verify title match
                result_title = r.get('name', '').lower()
                paper_words = set(w for w in title.lower().split() if len(w) > 3)
                result_words = set(w for w in result_title.split() if len(w) > 3)
                overlap = len(paper_words & result_words)
                if overlap >= 2:
                    return osf_id
        return None
    except:
        return None

# Load data
with open(PAPERS_PATH) as f:
    papers = json.load(f)

need_links = [p for p in papers if not p.get('link') and not p.get('osf_id')]
print(f"Papers needing links: {len(need_links)}", flush=True)

# Load previous results
results = load_results()
already_found = set(int(k) for k in results.keys())
print(f"Already found: {len(already_found)}", flush=True)

# Process remaining
remaining = [p for p in need_links if p["number"] not in already_found]
print(f"Remaining to search: {len(remaining)}", flush=True)

BATCH = 10
for i in range(0, len(remaining), BATCH):
    batch = remaining[i:i+BATCH]
    print(f"\nBatch {i//BATCH + 1} ({len(batch)} papers):", flush=True)
    
    for p in batch:
        sys.stdout.write(f"  #{p["number"]}: {p["title"][:45]}... ")
        sys.stdout.flush()
        
        osf_id = search_paper(p["title"])
        if osf_id:
            results[str(p["number"])] = osf_id
            save_results(results)  # save incrementally
            print(f"✓ {osf_id}", flush=True)
        else:
            print("✗", flush=True)
        
        time.sleep(0.5)
    
    if i + BATCH < len(remaining):
        print(f"  Pausing 3s...", flush=True)
        time.sleep(3)

print(f"\n=== Total found: {len(results)} / {len(need_links)} ===", flush=True)
for num, osf_id in sorted(results.items(), key=lambda x: int(x[0])):
    print(f"  #{num}: {osf_id}")

not_found = [p for p in need_links if str(p["number"]) not in results]
print(f"\nStill missing ({len(not_found)}):")
for p in not_found:
    print(f"  #{p["number"]}: {p["title"]}")