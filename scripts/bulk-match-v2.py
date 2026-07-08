#!/usr/bin/env python3
"""Simplified bulk match - download & match in one pass."""
import json, re, time, urllib.request, urllib.parse, sys

PAPERS_PATH = '/home/z/my-project/psyarxiv-hub/data/papers.json'
CACHE_PATH = '/home/z/my-project/scripts/psyarxiv-titles-cache.json'

with open(PAPERS_PATH) as f:
    papers = json.load(f)
missing = [(i, p) for i, p in enumerate(papers) if not p.get('osf_id')]
print(f"Missing: {len(missing)}", flush=True)

# Prepare search terms
stop = {'the','and','for','in','of','a','an','their','with','that','this',
        'study','review','analysis','examines','investigates','approaches','outcomes',
        'effects','treatment','disorder','disorders','clinical','therapeutic','systematic',
        'between','among','during','into','from','using','based','which','what',
        'when','where','have','been','were','will','would','could','should',
        'also','may','can','about','such','than','other','more','most',
        'however','although','while','findings','results','participants','sample',
        'methods','measures','measured','assessed','found','showed','showing',
        'significant','significantly','associated','association','relationship',
        'paper','research','examining','proposes','introduces','describes',
        'explores','tests','reports','develops','details','discusses'}

paper_data = []
for idx, p in missing:
    title = (p.get('title') or '').lower()
    summary = ((p.get('summary') or '')[:300]).lower()
    text = f"{title} {summary}"
    words = set(w for w in re.findall(r'[a-z]+', text) if len(w) > 3 and w not in stop)
    abbrevs = set(a.lower() for a in re.findall(r'\b[A-Z]{2,}[\-]?[A-Z0-9]*\b', p.get('title','') + ' ' + (p.get('summary','')[:300])))
    authors = set()
    if p.get('authors') and p['authors'] != 'Unknown':
        for name in p['authors'].split(','):
            parts = name.strip().split()
            if parts:
                authors.add(parts[-1].lower())
    paper_data.append({'words': words, 'abbrevs': abbrevs, 'authors': authors, 'number': p['number'], 'title': p['title']})

# Load existing cache
cache = {}
try:
    with open(CACHE_PATH) as f:
        cache = json.load(f)
    print(f"Loaded {len(cache)} cached pages", flush=True)
except:
    pass

matches = []
checked = 0

for page_num in range(1, 201):
    if str(page_num) in cache:
        preprints = cache[str(page_num)]
    else:
        try:
            params = urllib.parse.urlencode({
                'filter[provider]': 'psyarxiv',
                'page[size]': 100,
                'page': page_num
            })
            url = f'https://api.osf.io/v2/preprints/?{params}'
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
            preprints = []
            for item in data.get('data', []):
                pid = item['id'].split('_v')[0]
                preprints.append({
                    'id': pid,
                    'title': item['attributes'].get('title', ''),
                    'date': item['attributes'].get('date_created', '')[:10]
                })
            cache[str(page_num)] = preprints
            time.sleep(0.3)
        except Exception as e:
            print(f"Error page {page_num}: {e}", flush=True)
            time.sleep(2)
            continue
    
    for pp in preprints:
        checked += 1
        pp_lower = pp['title'].lower()
        pp_words = set(re.findall(r'[a-z]+', pp_lower))
        pp_abbrevs = set(a.lower() for a in re.findall(r'\b[A-Z]{2,}[\-]?[A-Z0-9]*\b', pp['title']))
        
        for pd in paper_data:
            if pd.get('_matched'):
                continue
            
            word_overlap = len(pd['words'] & pp_words)
            abbrev_overlap = len(pd['abbrevs'] & pp_abbrevs)
            author_match = sum(1 for a in pd['authors'] if a in pp_lower)
            
            if word_overlap == 0 and abbrev_overlap == 0 and author_match == 0:
                continue
            
            word_score = word_overlap / max(len(pd['words']), 1)
            abbrev_score = 1.0 if abbrev_overlap > 0 else 0.0
            auth_score = author_match / max(len(pd['authors']), 1)
            score = word_score * 0.5 + abbrev_score * 0.3 + auth_score * 0.2
            
            if score >= 0.2:
                m = {
                    'paper_number': pd['number'],
                    'paper_title': pd['title'],
                    'osf_id': pp['id'],
                    'preprint_title': pp['title'],
                    'score': round(score, 3),
                    'word_overlap': word_overlap,
                    'abbrev_overlap': abbrev_overlap,
                    'author_match': author_match,
                    'date': pp['date']
                }
                matches.append(m)
                print(f"  MATCH #{pd['number']} -> {pp['id']} ({score:.3f}) w={word_overlap} a={abbrev_overlap} auth={author_match}", flush=True)
                print(f"    {pp['title'][:90]}", flush=True)
                if score >= 0.35:
                    pd['_matched'] = True
    
    if page_num % 10 == 0:
        with open(CACHE_PATH, 'w') as f:
            json.dump(cache, f)
        print(f"Page {page_num}/200 | Checked {checked} | Matches: {len(matches)}", flush=True)

# Save
with open(CACHE_PATH, 'w') as f:
    json.dump(cache, f)

matches.sort(key=lambda m: m['score'], reverse=True)
with open('/home/z/my-project/scripts/bulk-match-results.json', 'w') as f:
    json.dump(matches, f, indent=2)

print(f"\nDone. Checked {checked} preprints, found {len(matches)} potential matches.", flush=True)
for m in matches:
    flag = 'Y' if m['score'] >= 0.35 else '~' if m['score'] >= 0.25 else '?'
    print(f"  {flag} #{m['paper_number']} -> {m['osf_id']} ({m['score']:.3f}) {m['preprint_title'][:80]}")