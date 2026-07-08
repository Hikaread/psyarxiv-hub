import json, urllib.request, time

accepted = json.load(open("/home/z/my-project/psyarxiv-hub/data/accepted-run3.json"))
print(f"Fetching PDF links for {len(accepted)} papers...")

for i, c in enumerate(accepted):
    cid = c['compact_id']
    try:
        # Step 1: Get preprint to find files link
        url = f"https://api.osf.io/v2/preprints/{cid}/"
        req = urllib.request.Request(url, headers={"User-Agent": "PsyArXiv-Hub/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        
        files_rel = data.get("data", {}).get("relationships", {}).get("files", {}).get("links", {}).get("related", {})
        if isinstance(files_rel, dict):
            files_url = files_rel.get("href", "")
        else:
            files_url = files_rel
        
        pdf_link = ""
        if files_url:
            # Step 2: List files in osfstorage
            storage_url = files_url + "osfstorage/"
            req2 = urllib.request.Request(storage_url, headers={"User-Agent": "PsyArXiv-Hub/1.0"})
            resp2 = urllib.request.urlopen(req2, timeout=15)
            files_data = json.loads(resp2.read())
            
            for f in files_data.get("data", []):
                name = f.get("attributes", {}).get("name", "").lower()
                if name.endswith(".pdf"):
                    dl = f.get("links", {}).get("download", "")
                    if isinstance(dl, dict):
                        dl = dl.get("href", "")
                    pdf_link = dl
                    break
        
        c['pdf_link'] = pdf_link
        status = "PDF" if pdf_link else "NO PDF"
        print(f"  [{i+1}/{len(accepted)}] [{cid}] {status} | {c['title'][:70]}")
    except Exception as e:
        c['pdf_link'] = ""
        print(f"  [{i+1}/{len(accepted)}] [{cid}] ERROR: {e}")
    
    time.sleep(1)

with open("/home/z/my-project/psyarxiv-hub/data/accepted-run3.json", "w") as f:
    json.dump(accepted, f, indent=2, ensure_ascii=False)

pdf_count = sum(1 for c in accepted if c.get('pdf_link'))
print(f"\nPapers with PDF links: {pdf_count}/{len(accepted)}")
PYEOF