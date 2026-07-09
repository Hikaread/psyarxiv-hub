#!/usr/bin/env python3
"""
Bulk download PsyArXiv preprint titles via OSF API and fuzzy match
against papers missing osf_ids.
"""
import json
import os
import re
import time
import urllib.request
import urllib.parse
import sys

PAPERS_PATH = '/home/z/my-project/psyarxiv-hub/data/papers.json'
CACHE_PATH = '/home/z/my-project/scripts/psyarxiv-titles-cache.json'
RESULTS_PATH = '/home/z/my-project/scripts/bulk-match-results.json'

# Load missing papers
with open(PAPERS_PATH) as f:
    papers = json.load(f)

missing = [(i, p) for i, p in enumerate(papers) if not p.get('osf_id')]
print(f"Missing osf_id: {len(missing)} papers")

# Prepare search terms for each missing paper
def get_search_terms(paper):
    """Extract key terms from title and summary for matching."""
    title = paper.get('title', '')
    summary = (paper.get('summary', '') or '')[:300]
    authors = paper.get('authors', '')
    
    # All text to match against
    text = f"{title} {summary}".lower()
    
    # Extract meaningful words (>3 chars, not generic)
    stop = {'the', 'and', 'for', 'in', 'of', 'a', 'an', 'their', 'with', 'that', 'this',
            'study', 'review', 'analysis', 'examines', 'investigates', 'approaches', 'outcomes',
            'effects', 'treatment', 'disorder', 'disorders', 'clinical', 'therapeutic', 'systematic',
            'between', 'among', 'during', 'into', 'from', 'using', 'based', 'which', 'what',
            'when', 'where', 'have', 'been', 'were', 'will', 'would', 'could', 'should',
            'also', 'may', 'can', 'about', 'such', 'than', 'other', 'more', 'most',
            'however', 'although', 'while', 'findings', 'results', 'participants', 'sample',
            'methods', 'measures', 'measured', 'assessed', 'found', 'showed', 'showing',
            'significant', 'significantly', 'associated', 'association', 'relationship'}
    
    words = re.findall(r'[a-z]+', text)
    meaningful = [w for w in words if len(w) > 3 and w not in stop]
    
    # Also extract abbreviations and hyphenated terms
    abbrevs = re.findall(r'\b[A-Z]{2,}[\-]?[A-Z0-9]*\b', f"{title} {summary}")
    
    return {
        'words': set(meaningful),
        'abbrevs': set(a.lower() for a in abbrevs),
        'author_lastnames': set(),
        'title_lower': title.lower()
    }

paper_terms = []
for idx, p in missing:
    terms = get_search_terms(p)
    # Add author last names if known
    if p.get('authors') and p['authors'] != 'Unknown':
        for author in p['authors'].split(','):
            name = author.strip().split()
            if name:
                terms['author_lastnames'].add(name[-1].lower())
    paper_terms.append(terms)

def score_match(pt, preprint_title):
    """Score how well a preprint title matches a paper's search terms."""
    pt_lower = preprint_title.lower()
    pt_words = set(re.findall(r'[a-z]+', pt_lower))
    pt_abbrevs = set(a.lower() for a in re.findall(r'\b[A-Z]{2,}[\-]?[A-Z0-9]*\b', preprint_title))
    
    # Word overlap
    word_overlap = len(pt['words'] & pt_words)
    word_score = word_overlap / max(len(pt['words']), 1)
    
    # Abbreviation match (very strong signal)
    abbrev_overlap = len(pt['abbrevs'] & pt_abbrevs)
    
    # Author match (strong signal)
    author_match = 0
    for author in pt['author_lastnames']:
        if author in pt_lower:
            author_match += 1
    author_score = author_match / max(len(pt['author_lastnames']), 1)
    
    # Combined score
    score = word_score * 0.5 + (1.0 if abbrev_overlap > 0 else 0.0) * 0.3 + author_score * 0.2
    
    return score, word_overlap, abbrev_overlap, author_match

# Download preprint titles from API
def fetch_page(page_num, page_size=100):
    params = urllib.parse.urlencode({
        'filter[provider]': 'psyarxiv',
        'page[size]': page_size,
        'page': page_num,
        'sort': '-date_created'
    })
    url = f'https://api.osf.io/v2/preprints/?{params}'
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}", file=sys.stderr)
        return None

# Load cache
cache = {}
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH) as f:
        cache = json.load(f)
    print(f"Loaded {len(cache)} cached preprints")

# Download and match
total_pages = 608  # 60790 / 100
matches = []
checked = 0
start_time = time.time()

# Check recent pages first (most likely to contain our papers)
# Our papers are from 2025-2026, so start from page 1 (most recent)
for page_num in range(1, total_pages + 1):
    if str(page_num) in cache:
        preprints = cache[str(page_num)]
    else:
        data = fetch_page(page_num)
        if data is None:
            time.sleep(2)
            continue
        
        preprints = []
        for item in data.get('data', []):
            attrs = item.get('attributes', {})
            preprint_id = item.get('id', '').replace('_v1', '').replace('_v2', '')
            if '_v' in preprint_id:
                preprint_id = preprint_id.split('_v')[0]
            preprints.append({
                'id': preprint_id,
                'title': attrs.get('title', ''),
                'date': attrs.get('date_created', '')[:10]
            })
        
        cache[str(page_num)] = preprints
        time.sleep(0.5)  # Rate limit
    
    # Check each preprint against missing papers
    for pp in preprints:
        checked += 1
        for i, (idx, paper) in enumerate(missing):
            if paper.get('_matched'):
                continue
            
            score, word_overlap, abbrev_overlap, author_match = score_match(paper_terms[i], pp['title'])
            
            # Threshold for reporting
            if score >= 0.25 or abbrev_overlap > 0 or (author_match > 0 and word_overlap >= 2):
                match_info = {
                    'paper_number': paper['number'],
                    'paper_title': paper['title'],
                    'osf_id': pp['id'],
                    'preprint_title': pp['title'],
                    'score': round(score, 3),
                    'word_overlap': word_overlap,
                    'abbrev_overlap': abbrev_overlap,
                    'author_match': author_match,
                    'preprint_date': pp['date']
                }
                matches.append(match_info)
                print(f"\n  MATCH #{paper['number']} → {pp['id']} (score: {score:.3f})")
                print(f"    Paper: {paper['title'][:80]}")
                print(f"    Found: {pp['title'][:80]}")
    
    # Save cache periodically
    if page_num % 20 == 0:
        with open(CACHE_PATH, 'w') as f:
            json.dump(cache, f)
        
        elapsed = time.time() - start_time
        print(f"\nPage {page_num}/{total_pages} | Checked {checked} preprints | {len(matches)} matches | {elapsed:.0f}s")
        
        # Stop after 200 pages if no matches (unlikely to find more)
        if page_num >= 200 and len(matches) == 0:
            print("No matches after 200 pages, stopping.")
            break

# Save results
with open(CACHE_PATH, 'w') as f:
    json.dump(cache, f)

# Sort matches by score
matches.sort(key=lambda m: m['score'], reverse=True)

with open(RESULTS_PATH, 'w') as f:
    json.dump(matches, f, indent=2)

print(f"\n{'='*60}")
print(f"Checked {checked} preprints across {page_num} pages")
print(f"Found {len(matches)} potential matches")
print(f"{'='*60}")
for m in matches:
    flag = '✓' if m['score'] >= 0.35 else '~' if m['score'] >= 0.25 else '?'
    print(f"  {flag} #{m['paper_number']} → {m['osf_id']} ({m['score']:.3f})")
    print(f"    {m['preprint_title'][:80]}")