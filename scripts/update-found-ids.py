#!/usr/bin/env python3
"""Update papers.json with found osf_ids."""
import json

PAPERS_JSON = "/home/z/my-project/psyarxiv-hub/data/papers.json"

# Verified matches: paper number -> osf_id
FOUND = {
    192: "kn95m",
    193: "rge42",
    196: "rc39w",
    199: "9zk54",
    201: "ps54j",
    202: "btge4",
    205: "2bv3x",
    241: "r3cgf",
}

with open(PAPERS_JSON) as f:
    papers = json.load(f)

updated = 0
for paper in papers:
    num = paper.get("number")
    if num in FOUND:
        osf_id = FOUND[num]
        paper["osf_id"] = osf_id
        paper["link"] = f"https://osf.io/preprints/psyarxiv/{osf_id}"
        updated += 1
        print(f"  Updated #{num}: {osf_id} - {paper['title'][:60]}")

with open(PAPERS_JSON, "w") as f:
    json.dump(papers, f, indent=2, ensure_ascii=False)

print(f"\nUpdated {updated} papers in {PAPERS_JSON}")