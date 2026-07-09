#!/usr/bin/env python3
"""
Download ALL PsyArXiv preprint IDs and titles from the OSF API,
then match them against the 59 papers missing osf_ids.
This is more reliable than search-based approaches.
"""
import json
import urllib.request
import urllib.parse
import time
import sys
import os
from difflib import SequenceMatcher

PAPERS_JSON = "/home/z/my-project/psyarxiv-hub/data/papers.json"
API_BASE = "https://api.osf.io/v2/preprints/"
PAGE_SIZE = 100
CACHE_FILE = "/home/z/my-project/scripts/psyarxiv-all-titles.json"
# How many pages to fetch (10000+ preprints / 100 per page = ~100+ pages)
MAX_PAGES = 150

def api_get(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible; PsyArXiv Matcher)"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  API error for {url}: {e}", file=sys.stderr)
                return None

def download_all_titles():
    """Download all PsyArXiv preprint titles."""
    if os.path.exists(CACHE_FILE):
        print(f"Loading cached titles from {CACHE_FILE}")
        with open(CACHE_FILE) as f:
            return json.load(f)
    
    print("Downloading all PsyArXiv preprint titles...")
    all_preprints = []
    
    for page in range(1, MAX_PAGES + 1):
        params = urllib.parse.urlencode({
            "filter[provider]": "psyarxiv",
            "page[size]": PAGE_SIZE,
            "page[number]": page,
            "sort": "-date_created",
        })
        url = f"{API_BASE}?{params}"
        data = api_get(url)
        if not data:
            print(f"  Failed at page {page}, stopping")
            break
        
        items = data.get("data", [])
        if not items:
            print(f"  No items at page {page}, stopping")
            break
        
        for item in items:
            attrs = item.get("attributes", {})
            all_preprints.append({
                "id": item["id"],
                "title": attrs.get("title", ""),
                "date_created": attrs.get("date_created", "")[:10],
            })
        
        total = data.get("meta", {}).get("total", "?")
        print(f"  Page {page}: fetched {len(items)} ({len(all_preprints)} total / {total})")
        
        # Check if there's a next page
        next_url = data.get("links", {}).get("next")
        if not next_url:
            print(f"  No next page, done at page {page}")
            break
        
        time.sleep(0.3)  # Rate limiting
    
    # Save cache
    with open(CACHE_FILE, "w") as f:
        json.dump(all_preprints, f)
    print(f"Saved {len(all_preprints)} preprints to {CACHE_FILE}")
    return all_preprints

def extract_key_phrases(short_title):
    """Extract key phrases/words from a short title for matching."""
    stop = {
        'a', 'an', 'the', 'and', 'or', 'of', 'for', 'in', 'on', 'to', 'with',
        'by', 'from', 'their', 'its', 'is', 'are', 'was', 'were', 'be', 'been',
        'that', 'this', 'these', 'those', 'not', 'no', 'but', 'at', 'if',
        'study', 'analysis', 'review', 'research', 'examination', 'based',
        'using', 'between', 'among', 'into', 'clinical', 'framework', 'model',
        'effects', 'effect', 'role', 'association', 'predictors', 'outcomes',
        'findings', 'evidence', 'overview', 'perspective', 'considerations',
        'evaluating', 'evaluation', 'assessment', 'versus', 'additional',
        'therapeutic', 'approaches', 'approach', 'systematic',
    }
    words = [w.lower() for w in __import__('re').findall(r'[a-zA-Z]+', short_title)]
    key_words = [w for w in words if w not in stop and len(w) >= 3]
    return key_words, words

def compute_match_score(short_title, api_title, paper_authors="Unknown"):
    """Compute a match score between a short title and an API title."""
    short_lower = short_title.lower()
    api_lower = api_title.lower()
    
    # 1. Fuzzy sequence similarity
    seq_sim = SequenceMatcher(None, short_lower, api_lower).ratio()
    
    # 2. Key word overlap
    key_words, all_words = extract_key_phrases(short_title)
    if not key_words:
        return 0, "no key words"
    
    key_hits = sum(1 for w in key_words if w in api_lower)
    key_ratio = key_hits / len(key_words)
    
    # 3. All word overlap (less strict)
    all_hits = sum(1 for w in all_words if w in api_lower)
    all_ratio = all_hits / len(all_words) if all_words else 0
    
    # 4. Check for rare/specific terms (longer words = more specific)
    rare_terms = [w for w in key_words if len(w) >= 7]
    rare_hits = sum(1 for w in rare_terms if w in api_lower)
    rare_ratio = rare_hits / len(rare_terms) if rare_terms else 0
    
    # Combined score
    # Rare term match is very strong signal
    if rare_ratio >= 0.5 and rare_terms:
        score = max(seq_sim, key_ratio * 0.95, 0.7)
    elif key_ratio >= 0.6:
        score = max(seq_sim, key_ratio * 0.9, 0.6)
    elif key_ratio >= 0.4 and seq_sim > 0.2:
        score = max(seq_sim * 0.8, key_ratio * 0.7)
    else:
        score = max(seq_sim, key_ratio * 0.6, all_ratio * 0.5)
    
    return score, f"seq={seq_sim:.2f} key={key_ratio:.2f} all={all_ratio:.2f} rare={rare_ratio:.2f}"

def find_matches(all_preprints, missing_papers):
    """Find the best match for each missing paper."""
    results = {}
    
    for paper in missing_papers:
        number = paper["number"]
        title = paper["title"]
        authors = paper.get("authors", "Unknown")
        
        best_match = None
        best_score = 0
        best_details = ""
        
        for preprint in all_preprints:
            score, details = compute_match_score(title, preprint["title"])
            if score > best_score:
                best_score = score
                best_match = preprint
                best_details = details
        
        if best_match and best_score >= 0.40:
            osf_id = best_match["id"].rsplit("_", 1)[0]
            print(f"  #{number} (score={best_score:.2f}): {title[:50]}")
            print(f"    -> {best_match['title'][:70]}")
            print(f"    osf_id={osf_id} | {best_details}")
            results[number] = {
                "osf_id": osf_id,
                "api_title": best_match["title"],
                "link": f"https://osf.io/preprints/psyarxiv/{osf_id}",
                "score": round(best_score, 3),
                "details": best_details,
            }
        else:
            print(f"  #{number} NO MATCH (best={best_score:.2f}): {title[:50]}")
            if best_match:
                print(f"    Best: {best_match['title'][:70]} | {best_details}")
            results[number] = None
    
    return results

def main():
    # Load papers
    with open(PAPERS_JSON) as f:
        papers = json.load(f)
    
    missing = [p for p in papers if not p.get("osf_id")]
    print(f"Found {len(missing)} papers missing osf_id\n")
    
    # Download all titles
    all_preprints = download_all_titles()
    print(f"\nMatching against {len(all_preprints)} PsyArXiv preprints...\n")
    
    # Find matches
    matches = find_matches(all_preprints, missing)
    
    # Summary
    found = {k: v for k, v in matches.items() if v is not None}
    not_found = [k for k, v in matches.items() if v is None]
    
    print(f"\n{'='*60}")
    print(f"RESULTS: Found {len(found)}/{len(missing)} matches")
    print(f"{'='*60}")
    
    # Save results
    output = {
        "found": found,
        "not_found_numbers": not_found,
        "total_missing": len(missing),
        "total_found": len(found),
    }
    out_path = "/home/z/my-project/scripts/missing-osf-results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")
    
    # Print found matches for review
    if found:
        print(f"\n--- FOUND MATCHES ---")
        for num, info in sorted(found.items()):
            p = next(p for p in papers if p["number"] == num)
            print(f"  #{num}: {p['title'][:60]}")
            print(f"    -> {info['api_title'][:70]}")
            print(f"    osf_id={info['osf_id']} score={info['score']}")
            print()

if __name__ == "__main__":
    main()