#!/usr/bin/env python3
"""Robust bulk match - incremental results, error handling."""
import json, re, time, urllib.request, urllib.parse, os, signal, sys

PAPERS_PATH = '/home/z/my-project/psyarxiv-hub/data/papers.json'
CACHE_PATH = '/home/z/my-project/scripts/psyarxiv-titles-cache.json'
RESULTS_PATH = '/home/z/my-project/scripts/bulk-match-results.json'
LOG_PATH = '/tmp/bulk-v4.log'

def log(msg):
    with open(LOG_PATH, 'a') as f:
        f.write(msg + '\n')
    print(msg, flush=True)

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
    paper_data.append({'words': words, 'abbrevs': abbrevs, 'authors': authors, 'number': p['number'], 'title': p['title'], '_matched': False})

# Load state
cache = {}
try:
    with open(CACHE_PATH) as f:
        cache = json.load(f)
except: pass

existing_results = []
try:
    with open(RESULTS_PATH) as f:
        existing_results = json.load(f)
except: pass

start_page = max((int(k) for k in cache.keys() if k.isdigit()), default=0) + 1
log(f"Start: page {start_page}, {len(cache)} cached, {len(existing_results)} existing matches")

# Mark already matched papers
for er in existing_results:
    if er['score'] >= 0.4:
        for pd in paper_data:
            if pd['number'] == er['paper_number']:
                pd['_matched'] = True

matches = list(existing_results)
checked = 0
start_time = time.time()
errors = 0

for page_num in range(start_page, 608):
    for attempt in range(3):
        try:
            params = urllib.parse.urlencode({'filter[provider]': 'psyarxiv', 'page[size]': 100, 'page': page_num})
            req = urllib.request.Request(f'https://api.osf.io/v2/preprints/?{params}')
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            cache[str(page_num)] = [{'id': item['id'].split('_v')[0], 'title': item['attributes'].get('title', '')} for item in data.get('data', [])]
            break
        except Exception as e:
            errors += 1
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
            else:
                log(f"ERR page {page_num}: {e}")
    
    for pp in cache.get(str(page_num), []):
        checked += 1
        pp_lower = pp['title'].lower()
        pp_words = set(re.findall(r'[a-z]+', pp_lower))
        pp_abbrevs = set(a.lower() for a in re.findall(r'\b[A-Z]{2,}[\-]?[A-Z0-9]*\b', pp['title']))
        
        for pd in paper_data:
            if pd['_matched']: continue
            wo = len(pd['words'] & pp_words)
            ao = len(pd['abbrevs'] & pp_abbrevs)
            am = sum(1 for a in pd['authors'] if a in pp_lower)
            if wo == 0 and ao == 0 and am == 0: continue
            ws = wo / max(len(pd['words']), 1)
            score = ws * 0.5 + (1.0 if ao > 0 else 0.0) * 0.3 + am / max(len(pd['authors']), 1) * 0.2
            if score >= 0.3:
                m = {'paper_number': pd['number'], 'osf_id': pp['id'], 'preprint_title': pp['title'], 'score': round(score, 3), 'wo': wo, 'ao': ao, 'am': am}
                matches.append(m)
                log(f"  #{pd['number']} -> {pp['id']} ({score:.3f}) w={wo} a={ao} auth={am} | {pp['title'][:80]}")
                if score >= 0.4: pd['_matched'] = True
    
    time.sleep(0.2)
    
    if page_num % 20 == 0:
        with open(CACHE_PATH, 'w') as f: json.dump(cache, f)
        matches.sort(key=lambda m: m['score'], reverse=True)
        with open(RESULTS_PATH, 'w') as f: json.dump(matches, f, indent=2)
        log(f"P{page_num} | {checked} checked | {len(matches)} matches | {time.time()-start_time:.0f}s | err={errors}")

# Final save
with open(CACHE_PATH, 'w') as f: json.dump(cache, f)
matches.sort(key=lambda m: m['score'], reverse=True)
with open(RESULTS_PATH, 'w') as f: json.dump(matches, f, indent=2)
log(f"Done. {checked} checked, {len(matches)} matches, {errors} errors, {time.time()-start_time:.0f}s")
