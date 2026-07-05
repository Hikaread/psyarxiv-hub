#!/usr/bin/env python3
"""
Search for removed papers on PsyArXiv using web search.
Outputs a mapping of paper title -> osf_id.
"""
import subprocess
import json
import re
import time
import sys

# The 59 papers to find (from before-revamp)
before = json.load(open('/tmp/papers-before-revamp.json'))
after = json.load(open('/home/z/my-project/psyarxiv-hub/data/papers.json'))
after_titles = set(p['title'].lower().strip() for p in after)

# Skip true duplicates
dup_osf = {'5aqxg', 'f53wp'}
to_find = [
    p for p in before
    if p['title'].lower().strip() not in after_titles
    and not (p.get('osf_id') and p['osf_id'].replace('_v','').split('_v')[0] in dup_osf)
]

print(f"Papers to find: {len(to_find)}", flush=True)

results = {}

for i, paper in enumerate(to_find):
    title = paper['title']
    # Extract key search terms
    # Remove parenthetical content for cleaner search
    clean_title = re.sub(r'\(.*?\)', '', title).strip()
    # Take first few meaningful words
    words = clean_title.split()[:6]
    query = ' '.join(words) + ' psyarxiv'
    
    sys.stdout.write(f"#{paper['number']}: {title[:50]}... ")
    sys.stdout.flush()
    
    try:
        result = subprocess.run(
            ['z-ai', 'function', '-n', 'web_search', '-a', json.dumps({"query": query, "num": 5})],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            search_results = json.loads(result.stdout.strip())
            
            # Look for osf.io links in results
            osf_id = None
            for r in search_results:
                url = r.get('url', '')
                # Match osf.io/preprints/psyarxiv/XXXXX
                m = re.search(r'osf\.io/([a-z0-9]{5}(?:_v\d+)*)', url)
                if m:
                    osf_id = m.group(1)
                    # Also check if result title matches our paper
                    result_title = r.get('name', '').lower()
                    paper_title_lower = title.lower()
                    # Check word overlap
                    paper_words = set(w for w in paper_title_lower.split() if len(w) > 3)
                    result_words = set(w for w in result_title.split() if len(w) > 3)
                    overlap = len(paper_words & result_words)
                    if overlap >= 2:
                        break
                    else:
                        osf_id = None  # Not a good match
            
            if osf_id:
                results[paper['number']] = {
                    'title': title,
                    'osf_id': osf_id,
                    'original_data': paper
                }
                print(f"✓ {osf_id}", flush=True)
            else:
                print("✗ no osf.io link found", flush=True)
        else:
            print(f"✗ search error", flush=True)
    except subprocess.TimeoutExpired:
        print("✗ timeout", flush=True)
    except Exception as e:
        print(f"✗ {e}", flush=True)
    
    # Rate limit
    if (i + 1) < len(to_find) and (i + 1) % 10 == 0:
        print(f"  Pausing... ({i+1}/{len(to_find)})", flush=True)
        time.sleep(2)

print(f"\n=== Found {len(results)} / {len(to_find)} ===", flush=True)

# Save results
with open('/tmp/recovery-search-results.json', 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Show what we found
for num, data in sorted(results.items()):
    print(f"  #{num}: {data['osf_id']} - {data['title'][:60]}")

# Show what we didn't find
found_nums = set(results.keys())
not_found = [p for p in to_find if p['number'] not in found_nums]
print(f"\nNot found ({len(not_found)}):")
for p in not_found:
    print(f"  #{p['number']}: {p['title'][:70]}")