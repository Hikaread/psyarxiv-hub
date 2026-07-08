import json, urllib.request, time

top = json.load(open("/home/z/my-project/psyarxiv-hub/data/top-papers-run3.json"))
print(f"Fetching abstracts one by one for {len(top)} papers...")

for i, c in enumerate(top):
    cid = c['compact_id']
    url = f"https://api.osf.io/v2/preprints/{cid}/?format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "PsyArXiv-Hub/1.0"})
    
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        attrs = data.get("data", {}).get("attributes", {})
        abstract = attrs.get("description", "").strip()
        c['abstract'] = abstract
        print(f"  [{i+1}/{len(top)}] [{cid}] OK ({len(abstract)} chars) | {c['title'][:80]}")
    except Exception as e:
        c['abstract'] = ""
        print(f"  [{i+1}/{len(top)}] [{cid}] ERROR: {e} | {c['title'][:80]}")
    
    time.sleep(0.8)

with open("/home/z/my-project/psyarxiv-hub/data/top-with-abstracts-run3.json", "w") as f:
    json.dump(top, f, indent=2, ensure_ascii=False)

print(f"\nDone.")