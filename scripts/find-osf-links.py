#!/usr/bin/env python3
"""Find osf_ids for 59 papers using web search with proper rate limiting."""
import subprocess, json, re, time, sys, os

PAPERS_PATH = '/home/z/my-project/psyarxiv-hub/data/papers.json'
RESULTS_PATH = '/tmp/osf-links-results.json'

def load_results():
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            return json.load(f)
    return {}

def save_results(results):
    with open(RESULTS_PATH, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def search(title):
    """Search for paper and extract osf.io/preprints/psyarxiv/ ID from results."""
    # Try multiple search strategies
    queries = [
        f'"{title}" site:osf.io preprints psyarxiv',
        f'{title} psyarxiv preprint osf.io',
    ]
    
    for q in queries[:1]:  # Just use the first (most specific) query
        try:
            result = subprocess.run(
                ['z-ai', 'function', '-n', 'web_search', '-a', 
                 json.dumps({"query": q, "num": 5})],
                capture_output=True, text=True, timeout=25
            )
            if result.returncode != 0:
                continue
            
            # Parse JSON from output (skip the emoji lines)
            lines = result.stdout.strip().split('\n')
            json_start = None
            for i, line in enumerate(lines):
                if line.strip().startswith('['):
                    json_start = i
                    break
            if json_start is None:
                continue
            
            json_str = '\n'.join(lines[json_start:])
            search_results = json.loads(json_str)
            
            for r in search_results:
                url = r.get('url', '')
                # Look for osf.io/preprints/psyarxiv/XXXXX pattern
                m = re.search(r'osf\.io/(?:preprints/psyarxiv/)?([a-z0-9]{5}(?:_v\d+)*)', url)
                if m:
                    osf_id = m.group(1)
                    # Verify the result title matches reasonably
                    result_title = r.get('name', '').lower()
                    paper_lower = title.lower()
                    # Check for key word overlap
                    paper_words = set(w for w in paper_lower.split() if len(w) > 3)
                    result_words = set(w for w in result_title.split() if len(w) > 3)
                    overlap = len(paper_words & result_words)
                    if overlap >= 1:
                        return osf_id, r.get('name', '')[:80]
        except:
            continue
    return None, None

# Load data
with open(PAPERS_PATH) as f:
    papers = json.load(f)

need = [p for p in papers if not p.get('link') and not p.get('osf_id')]
print(f"Papers needing links: {len(need)}", flush=True)

results = load_results()
already = set(int(k) for k in results.keys())
remaining = [p for p in need if p['number'] not in already]
print(f"Already found: {len(already)}, Remaining: {len(remaining)}", flush=True)

for i, p in enumerate(remaining):
    sys.stdout.write(f"#{p['number']}: {p['title'][:50]:50s} → ")
    sys.stdout.flush()
    
    osf_id, match_title = search(p['title'])
    if osf_id:
        results[str(p['number'])] = {'osf_id': osf_id, 'matched_title': match_title}
        save_results(results)
        print(f"✓ {osf_id}", flush=True)
    else:
        print("✗", flush=True)
    
    # Rate limit: 3 seconds between searches
    if i + 1 < len(remaining):
        time.sleep(3)

print(f"\n=== Found {len(results)}/{len(need)} ===", flush=True)

# Show all results
for num_str, data in sorted(results.items(), key=lambda x: int(x[0])):
    print(f"  #{num_str}: {data['osf_id']} - {data.get('matched_title', '?')[:60]}")

# Show unmatched
matched = set(int(k) for k in results.keys())
unmatched = [p for p in need if p['number'] not in matched]
print(f"\nUnmatched ({len(unmatched)}):")
for p in unmatched:
    print(f"  #{p['number']}: {p['title']}")