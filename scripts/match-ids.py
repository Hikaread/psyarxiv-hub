#!/usr/bin/env python3
"""
Match 59 linkless papers to extra IDs in seen-compact-ids.json.
For each extra ID, fetch its title from OSF API and fuzzy-match against our papers.
"""
import json
import urllib.request
import time
import sys
import re

def fetch_title(base_id):
    url = f"https://api.osf.io/v2/preprints/{base_id}/"
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (compatible; PsyArXiv-Hub/1.0)'
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get('data', {}).get('attributes', {}).get('title', '')
    except:
        return ''

def word_overlap(t1, t2):
    """Count overlapping significant words between two titles."""
    stop = {'a','an','the','and','or','for','in','of','on','to','with','by','from',
            'as','is','are','was','were','be','been','that','this','these','those',
            'it','its','their','our','your','my','not','but','if','while','can',
            'will','just','also','about','how','what','which','between','into'}
    w1 = set(re.sub(r'[^a-z0-9\s]', ' ', t1.lower()).split()) - stop
    w2 = set(re.sub(r'[^a-z0-9\s]', ' ', t2.lower()).split()) - stop
    # Only count words > 3 chars for more reliable matching
    w1 = {w for w in w1 if len(w) > 3}
    w2 = {w for w in w2 if len(w) > 3}
    if not w1 or not w2:
        return 0, set()
    overlap = w1 & w2
    return len(overlap), overlap

# Load data
with open('/tmp/extra-ids.json') as f:
    extra_ids = json.load(f)
with open('/tmp/need-link-papers.json') as f:
    need_link = json.load(f)

print(f"Extra IDs: {len(extra_ids)}, Papers needing links: {len(need_link)}", flush=True)

# Pre-compute paper title words
paper_titles = [(p['number'], p['title']) for p in need_link]

# Fetch titles for all extra IDs and match
matches = {}  # paper_number -> osf_id
checked = 0

for i, eid in enumerate(extra_ids):
    base = eid.replace('_v', '_v').split('_v')[0] if '_v' in eid else eid
    
    title = fetch_title(base)
    checked += 1
    
    if not title:
        continue
    
    # Check against all 59 papers
    best_score = 0
    best_num = None
    best_overlap = set()
    
    for pnum, ptitle in paper_titles:
        if pnum in matches:
            continue  # already matched
        score, overlap = word_overlap(title, ptitle)
        if score > best_score:
            best_score = score
            best_num = pnum
            best_overlap = overlap
    
    # Require decent overlap
    if best_score >= 3:
        matches[best_num] = base
        ptitle = [t for n, t in paper_titles if n == best_num][0]
        print(f"  MATCH #{best_num} -> {base} (score={best_score}, words={best_overlap})", flush=True)
        print(f"    Paper: {ptitle[:70]}", flush=True)
        print(f"    OSF:   {title[:70]}", flush=True)
    
    # Progress
    if (i + 1) % 20 == 0:
        print(f"  Checked {i+1}/{len(extra_ids)} IDs, matched {len(matches)}/{len(need_link)}", flush=True)
    
    # Small delay
    if (i + 1) % 10 == 0:
        time.sleep(0.3)

print(f"\n=== Checked {checked} IDs, found {len(matches)} matches ===", flush=True)

if matches:
    # Save matches
    with open('/tmp/id-matches.json', 'w') as f:
        json.dump(matches, f, indent=2)
    
    # Show unmatched
    matched_nums = set(matches.keys())
    unmatched = [p for p in need_link if p['number'] not in matched_nums]
    print(f"\nStill unmatched ({len(unmatched)}):", flush=True)
    for p in unmatched:
        print(f"  #{p['number']}: {p['title']}", flush=True)
else:
    print("No matches found!", flush=True)