#!/usr/bin/env python3
"""Quick bulk match - pages 101-200 only, writes results incrementally."""
import json, re, time, urllib.request, urllib.parse, os, sys

PAPERS_PATH = '/home/z/my-project/psyarxiv-hub/data/papers.json'
CACHE_PATH = '/home/z/my-project/scripts/psyarxiv-titles-cache.json'
RESULTS_PATH = '/home/z/my-project/scripts/bulk-match-results.json'

with open(PAPERS_PATH) as f:
    papers = json.load(f)
missing = [(i, p) for i, p in enumerate(papers) if not p.get('osf_id')]

stop = set('the and for in of a an their with that this study review analysis examines investigates approaches outcomes effects treatment disorder disorders clinical therapeutic systematic between among during into from using based which what when where have been were will would could should also may can about such than other more most however although while findings results participants sample methods measures measured assessed found showed showing significant significantly associated association relationship paper research examining proposes introduces describes explores tests reports develops details discusses does examined investigated reviewed tested reported developed novel new used including included specifically suggests suggesting indicates indicating reveals revealing highlights highlighting demonstrates demonstrating provides providing offers offering presents presenting considers perspective framework model models understanding important implications implication evidence current recent year years data overall potential role specific general possible likely need needs well within across through various several many much each both these those first second third one two three'.split())

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
    paper_data.append({'words': words, 'abbrevs': abbrevs, 'authors': authors, 'number': p['number'], '_matched': False})

cache = {}
try:
    with open(CACHE_PATH) as f:
        cache = json.load(f)
except: pass

print(f"Missing papers: {len(missing)}, Cached: {len(cache)} pages", flush=True)

# Process pages 101-200
matches = []
checked = 0

for page_num in range(101, 201):
    if str(page_num) in cache:
        preprints = cache[str(page_num)]
    else:
        try:
            params = urllib.parse.urlencode({'filter[provider]': 'psyarxiv', 'page[size]': 100, 'page': page_num})
            req = urllib.request.Request(f'https://api.osf.io/v2/preprints/?{params}')
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read())
            preprints = [{'id': item['id'].split('_v')[0], 'title': item['attributes'].get('title', '')} for item in data.get('data', [])]
            cache[str(page_num)] = preprints
        except Exception as e:
            print(f"ERR {page_num}: {e}", flush=True)
            continue
    
    for pp in preprints:
        checked += 1
        pp_words = set(re.findall(r'[a-z]+', pp['title'].lower()))
        pp_abbrevs = set(a.lower() for a in re.findall(r'\b[A-Z]{2,}[\-]?[A-Z0-9]*\b', pp['title']))
        
        for pd in paper_data:
            if pd['_matched']: continue
            wo = len(pd['words'] & pp_words)
            ao = len(pd['abbrevs'] & pp_abbrevs)
            am = sum(1 for a in pd['authors'] if a in pp['title'].lower())
            if wo == 0 and ao == 0 and am == 0: continue
            ws = wo / max(len(pd['words']), 1)
            score = ws * 0.5 + (1.0 if ao > 0 else 0.0) * 0.3 + am / max(len(pd['authors']), 1) * 0.2
            if score >= 0.3:
                matches.append({'paper_number': pd['number'], 'osf_id': pp['id'], 'preprint_title': pp['title'], 'score': round(score, 3), 'wo': wo, 'ao': ao, 'am': am})
                print(f"  #{pd['number']} -> {pp['id']} ({score:.3f}) {pp['title'][:80]}", flush=True)
    
    time.sleep(0.2)
    if page_num % 20 == 0:
        with open(CACHE_PATH, 'w') as f: json.dump(cache, f)
        print(f"Page {page_num} | {checked} | matches: {len(matches)}", flush=True)

with open(CACHE_PATH, 'w') as f: json.dump(cache, f)
matches.sort(key=lambda m: m['score'], reverse=True)
with open(RESULTS_PATH, 'w') as f: json.dump(matches, f, indent=2)
print(f"\nDone. {checked} checked, {len(matches)} matches.", flush=True)
for m in matches:
    print(f"  #{m['paper_number']} -> {m['osf_id']} ({m['score']:.3f}) {m['preprint_title'][:80]}")