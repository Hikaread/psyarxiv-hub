#!/usr/bin/env python3
"""Clean up papers.json: remove stubs, deduplicate, renumber."""
import json

INPUT = '/home/z/my-project/psyarxiv-hub/data/papers.json'
OUTPUT = '/home/z/my-project/psyarxiv-hub/data/papers.json'

d = json.load(open(INPUT))
print(f"Input: {len(d)} entries")

# --- Step 1: Remove completely stub papers ---
def is_stub(p):
    no_authors = not p.get('authors') or p['authors'] in (
        'Unknown', 'Author metadata unavailable',
        'Authors unavailable (embargoed preprint)', 'Pending'
    )
    no_summary = not p.get('summary') or 'pending full-text extraction' in str(p.get('summary', '')).lower()
    no_insight = not p.get('clinical_insight') or 'to be completed' in str(p.get('clinical_insight', '')).lower()
    return no_authors and no_summary and no_insight

before = len(d)
d = [p for p in d if not is_stub(p)]
print(f"Removed {before - len(d)} stub papers")

# --- Step 2: Remove adolescent/child-focused papers ---
ADOLESCENT_TITLES = {
    'from retreat to reality: a qualitative study of how adolescents apply mindfulness',
    'securing adolescent mental health by training need crafting',
    'psychotic-like experiences and neurobehavioral reward processing in ad',
    'supporting children on therapy waitlists',
}

before2 = len(d)
d = [p for p in d if p.get('title', '').lower().strip('"\'')[:70] not in ADOLESCENT_TITLES]
print(f"Removed {before2 - len(d)} adolescent/child-focused papers")

# --- Step 3: Deduplicate by osf_id (exact same paper imported twice) ---
seen_osf = set()
deduped = []
for p in d:
    oid = p.get('osf_id', '')
    if oid and oid in seen_osf:
        continue
    if oid:
        seen_osf.add(oid)
    deduped.append(p)
d = deduped
print(f"After osf_id dedup: {len(d)} entries")

# --- Step 4: Deduplicate by title (exact same paper with different osf_id) ---
seen_titles = set()
deduped2 = []
for p in d:
    norm = p.get('title', '').lower().strip()
    if norm in seen_titles:
        continue
    seen_titles.add(norm)
    deduped2.append(p)
d = deduped2
print(f"After title dedup: {len(d)} entries")

# --- Step 5: Renumber sequentially (fixes all duplicate numbers) ---
for i, p in enumerate(d):
    p['number'] = i + 1

# --- Step 6: Fix categories that are strings instead of arrays ---
for p in d:
    if isinstance(p.get('categories'), str):
        p['categories'] = [p['categories']]

print(f"\nFinal: {len(d)} papers, numbered 1-{len(d)}")

# --- Step 7: Validate ---
required = ['number', 'title', 'authors', 'date_posted', 'categories', 'summary', 'link']
issues = []
for i, p in enumerate(d):
    for k in required:
        if k not in p or not p[k]:
            issues.append(f"#{p['number']} missing/empty: {k}")
    if not isinstance(p.get('categories'), list):
        issues.append(f"#{p['number']} categories is {type(p['categories']).__name__}")

if issues:
    print(f"\nWARNING: {len(issues)} validation issues:")
    for iss in issues[:20]:
        print(f"  {iss}")
else:
    print("Validation: OK")

# --- Save ---
with open(OUTPUT, 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print(f"Saved to {OUTPUT}")