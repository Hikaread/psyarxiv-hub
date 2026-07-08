#!/usr/bin/env python3
"""
Find missing osf_ids for papers in papers.json by searching the OSF API.
Strategy: For each paper, extract key terms and search the PsyArXiv preprint API.
Use fuzzy matching on titles to find the best match.
"""
import json
import urllib.request
import urllib.parse
import re
import time
import sys
from difflib import SequenceMatcher

PAPERS_JSON = "/home/z/my-project/psyarxiv-hub/data/papers.json"
API_BASE = "https://api.osf.io/v2/preprints/"
PAGE_SIZE = 100
# Minimum similarity score to consider a match
MIN_SIMILARITY = 0.45
# For papers with known authors, lower threshold since we can verify
AUTHOR_SIMILARITY = 0.30

def api_get(url, retries=3):
    """Make API request with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  API error: {e}", file=sys.stderr)
                return None

def similarity(a, b):
    """Fuzzy similarity between two strings."""
    a = a.lower().strip()
    b = b.lower().strip()
    return SequenceMatcher(None, a, b).ratio()

def extract_search_terms(title):
    """Extract key search terms from a shortened title."""
    # Remove common stop words and keep meaningful terms
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'of', 'for', 'in', 'on', 'to', 'with',
        'by', 'from', 'their', 'its', 'is', 'are', 'was', 'were', 'be', 'been',
        'that', 'this', 'these', 'those', 'not', 'no', 'but', 'at', 'if',
        'therapeutic', 'approaches', 'approach', 'study', 'analysis', 'review',
        'systematic', 'meta-analysis', 'research', 'examination', 'investigation',
        'exploring', 'exploring', 'based', 'using', 'between', 'among', 'into',
        'clinical', 'implications', 'implications', 'framework', 'model',
        'effects', 'effect', 'role', 'association', 'associations', 'relationship',
        'relationships', 'predictors', 'outcomes', 'outcome', 'results',
        'findings', 'evidence', 'overview', 'perspective', 'considerations',
        'understanding', 'understanding', 'evaluating', 'evaluation', 'assessment',
        'comparative', 'comparison', 'comparison', 'versus', 'vs'
    }
    # Split on colons, dashes, parentheses
    words = re.findall(r'[a-zA-Z]+', title)
    # Keep words that aren't stop words and are >= 4 chars (for specificity)
    # But also keep 3-char words if they're very specific (e.g., OCD, RCT, EMA)
    terms = []
    for w in words:
        wl = w.lower()
        if wl not in stop_words and (len(w) >= 4 or wl in {'rct', 'ema', 'cbt', 'dbt', 'ocd', 'mri', 'ptd', 'nss', 'mti', 'pep', 'cbm', 'rom'}):
            terms.append(wl)
    return terms

def search_psyarxiv(query, max_results=20):
    """Search PsyArXiv using the OSF API q parameter."""
    params = urllib.parse.urlencode({
        "filter[provider]": "psyarxiv",
        "q": query,
        "page[size]": min(max_results, 50),
    })
    url = f"{API_BASE}?{params}"
    data = api_get(url)
    if not data:
        return []
    results = []
    for item in data.get("data", []):
        attrs = item.get("attributes", {})
        results.append({
            "id": item["id"],
            "title": attrs.get("title", ""),
            "description": attrs.get("description", "")[:200],
            "date_created": attrs.get("date_created", ""),
            "date_published": attrs.get("date_published", ""),
        })
    return results

def search_by_date_range(start_date, end_date, page=1):
    """Fetch preprints by date range."""
    params = urllib.parse.urlencode({
        "filter[provider]": "psyarxiv",
        "filter[date_created][gte]": start_date,
        "filter[date_created][lte]": end_date,
        "page[size]": PAGE_SIZE,
        "page[number]": page,
        "sort": "-date_created",
    })
    url = f"{API_BASE}?{params}"
    data = api_get(url)
    if not data:
        return [], None
    results = []
    for item in data.get("data", []):
        attrs = item.get("attributes", {})
        results.append({
            "id": item["id"],
            "title": attrs.get("title", ""),
            "description": attrs.get("description", "")[:500],
            "date_created": attrs.get("date_created", ""),
            "date_published": attrs.get("date_published", ""),
        })
    next_url = data.get("links", {}).get("next")
    return results, next_url

def get_preprint_contributors(preprint_id):
    """Get contributors (authors) for a preprint."""
    vid = preprint_id.rsplit("_", 1)[0]  # strip version
    url = f"https://api.osf.io/v2/preprints/{vid}/bibliographic_contributors/?embed=users&limit=20"
    data = api_get(url)
    if not data:
        return []
    authors = []
    try:
        for item in data.get("data", []):
            embeds = item.get("embeds", {})
            users_data = embeds.get("users", {}).get("data", [])
            if users_data and isinstance(users_data, list) and len(users_data) > 0:
                # users_data might be a list of user objects or a dict
                if isinstance(users_data[0], dict):
                    name = users_data[0].get("attributes", {}).get("full_name", "")
                else:
                    name = str(users_data[0])
                if name:
                    authors.append(name.lower())
    except (KeyError, IndexError, TypeError) as e:
        print(f"    [contributor parse error: {e}]", file=sys.stderr)
    return authors

def check_author_match(paper_authors, api_authors):
    """Check if any author from the paper matches the API authors."""
    if not paper_authors or paper_authors == "Unknown":
        return False, 0
    paper_author_list = [a.strip().lower().split()[-1] for a in paper_authors.split(",") if a.strip()]
    matches = 0
    for pa in paper_author_list:
        for aa in api_authors:
            # Check last name match
            aa_last = aa.split()[-1] if aa.split() else ""
            if pa in aa or aa_last in pa or pa in aa_last:
                matches += 1
                break
    return matches > 0, matches / max(len(paper_author_list), 1)

def find_match_for_paper(paper):
    """Try to find a matching PsyArXiv preprint for a paper."""
    title = paper["title"]
    authors = paper.get("authors", "Unknown")
    number = paper["number"]
    
    print(f"\n  #{number}: {title}")
    
    # Strategy 1: If we have known authors, search by author name
    if authors and authors != "Unknown":
        author_names = [a.strip().split()[-1] for a in authors.split(",") if a.strip()]
        # Use first 2 author last names for search
        search_query = " ".join(author_names[:2])
        print(f"    Searching by author: {search_query}")
        results = search_psyarxiv(search_query, max_results=20)
        
        best_match = None
        best_score = 0
        best_details = ""
        
        for r in results:
            # Check author match first
            api_authors = get_preprint_contributors(r["id"])
            author_match, author_score = check_author_match(authors, api_authors)
            
            # Also check title similarity
            sim = similarity(title, r["title"])
            # Also check if key terms from short title appear in the API title
            terms = extract_search_terms(title)
            term_hits = sum(1 for t in terms if t in r["title"].lower())
            term_ratio = term_hits / max(len(terms), 1)
            
            # Combined score: title similarity + term matching + author bonus
            combined = max(sim, term_ratio * 0.8) + (0.3 if author_match else 0)
            
            details = f"  sim={sim:.2f} terms={term_ratio:.2f} authors={author_score:.2f} -> {combined:.2f}"
            
            if combined > best_score:
                best_score = combined
                best_match = r
                best_details = details
        
        if best_match and best_score >= AUTHOR_SIMILARITY:
            osf_id = best_match["id"].rsplit("_", 1)[0]
            print(f"    MATCH (score={best_score:.2f}): {best_match['title'][:80]}")
            print(f"    osf_id={osf_id}")
            print(f"    {best_details}")
            return osf_id, best_match["title"]
    
    # Strategy 2: Search by key terms from the short title
    terms = extract_search_terms(title)
    if not terms:
        print(f"    No useful search terms extracted")
        return None, None
    
    # Use top 3 most specific terms (longest words tend to be most specific)
    terms_sorted = sorted(terms, key=len, reverse=True)
    search_query = " ".join(terms_sorted[:3])
    print(f"    Searching by terms: {search_query}")
    results = search_psyarxiv(search_query, max_results=20)
    
    best_match = None
    best_score = 0
    best_details = ""
    
    for r in results:
        # Check title similarity
        sim = similarity(title, r["title"])
        
        # Check term matching
        term_hits = sum(1 for t in terms if t in r["title"].lower())
        term_ratio = term_hits / max(len(terms), 1)
        
        # Check if short title's key phrases appear in the long title or description
        title_words = set(title.lower().split())
        api_title_lower = r["title"].lower()
        word_overlap = len(title_words & set(api_title_lower.split())) / max(len(title_words), 1)
        
        # Combined score
        combined = max(sim, term_ratio * 0.9, word_overlap * 0.7)
        
        details = f"  sim={sim:.2f} terms={term_ratio:.2f} words={word_overlap:.2f} -> {combined:.2f}"
        
        if combined > best_score:
            best_score = combined
            best_match = r
            best_details = details
    
    if best_match and best_score >= MIN_SIMILARITY:
        # Extra validation: at least one key term must be in the title
        terms_in_title = sum(1 for t in terms if t in best_match["title"].lower())
        if terms_in_title == 0 and len(terms) >= 2:
            print(f"    REJECTED (no key terms in title): {best_match['title'][:80]}")
            print(f"    {best_details}")
            return None, None
        osf_id = best_match["id"].rsplit("_", 1)[0]
        print(f"    MATCH (score={best_score:.2f}): {best_match['title'][:80]}")
        print(f"    osf_id={osf_id}")
        print(f"    {best_details}")
        return osf_id, best_match["title"]

    if best_match:
        print(f"    Best candidate (below threshold {best_score:.2f}): {best_match['title'][:80]}")
        print(f"    {best_details}")
    
    print(f"    NO MATCH FOUND")
    return None, None

def main():
    # Load papers
    with open(PAPERS_JSON) as f:
        papers = json.load(f)
    
    # Find papers missing osf_id
    missing = [p for p in papers if not p.get("osf_id")]
    print(f"Found {len(missing)} papers missing osf_id")
    
    found = {}
    not_found = []
    
    for paper in missing:
        osf_id, api_title = find_match_for_paper(paper)
        if osf_id:
            found[paper["number"]] = {
                "osf_id": osf_id,
                "original_title": paper["title"],
                "api_title": api_title,
                "link": f"https://osf.io/preprints/psyarxiv/{osf_id}",
            }
        else:
            not_found.append(paper["number"])
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"RESULTS: Found {len(found)}/{len(missing)} osf_ids")
    print(f"{'='*60}")
    
    if found:
        print(f"\nFound matches:")
        for num, info in sorted(found.items()):
            print(f"  #{num}: {info['osf_id']}")
            print(f"    Short: {info['original_title'][:60]}")
            print(f"    API:   {info['api_title'][:60]}")
    
    if not_found:
        print(f"\nStill missing ({len(not_found)}):")
        for num in not_found:
            p = next(p for p in papers if p["number"] == num)
            print(f"  #{num}: {p['title']}")
    
    # Save results to a JSON file for review
    output = {
        "found": found,
        "not_found": not_found,
        "total_missing": len(missing),
        "total_found": len(found),
    }
    with open("/home/z/my-project/scripts/missing-osf-results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to /home/z/my-project/scripts/missing-osf-results.json")

if __name__ == "__main__":
    main()