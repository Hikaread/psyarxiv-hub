#!/usr/bin/env python3
"""
PsyArXiv Paper Discovery & Clinical Screening Pipeline

Two-stage screening:
  1. Title-based keyword scoring (fast, no downloads)
     - score >= 2: auto-accept (clearly clinical)
     - score 0: auto-discard (clearly non-clinical)
     - score 1: borderline → stage 2
  2. PDF download + text extraction (for borderline papers only)
     - Download first 3 pages of PDF
     - Re-score with keywords on extracted text
     - score >= 2: accept
     - score < 2: discard
     - Delete PDFs after extraction

Output:
  - screening-brief.json: all candidates with scores
  - screened-papers.json: accepted papers (for full curation)
  - discarded-log.md: discarded paper IDs with reasons
"""

import json
import os
import re
import sys
import time
import datetime
import subprocess
import requests

# ─── Config ───────────────────────────────────────────────────────────────────
PSYARXIV_HUB = os.path.expanduser("~/my-project/psyarxiv-hub")
PAPERS_JSON = os.path.join(PSYARXIV_HUB, "data", "papers.json")
SCREENING_BRIEF = os.path.join(PSYARXIV_HUB, "scripts", "screening-brief.json")
SCREENED_PAPERS = os.path.join(PSYARXIV_HUB, "scripts", "screened-papers.json")
DISCARDED_LOG = os.path.join(PSYARXIV_HUB, "curation", "discarded-log.md")
FETCH_SCRIPT = os.path.expanduser("~/my-project/scripts/fetch-paper-fulltext.py")
TMP_DIR = "/tmp/psyarxiv-screening"

VALID_CATEGORIES = [
    "Anxiety & OCD", "Couples Therapy & Sexology", "Neurodivergence",
    "Mood Disorders", "Trauma & Stressor-Related", "Personality Disorders",
    "Therapeutic Modalities", "Psychopathology & Assessment", "Eating Disorders",
    "Somatic & Functional", "Suicidality & Self-Harm", "Psychosis & Schizophrenia",
    "Addiction & Substance Use", "Obsessive-Compulsive", "Other Clinical",
]

# ─── Keywords ─────────────────────────────────────────────────────────────────
CLINICAL_KEYWORDS = [
    # Core clinical
    "depress", "anxiety", "trauma", "ptsd", "therap", "treatment", "intervention",
    "disorder", "clinical", "psychopath", "symptom", "mental health",
    # Modalities
    "cbt", "cognitive behavioral", "cognitive reappraisal", "reappraisal",
    "psychotherapy", "counseling", "mindfulness",
    "acceptance", "commitment", "dialectical behavior", "dbt", "schema therapy",
    "psychodynamic", "emdr", "exposure therapy", "compassion-focused",
    # Specific conditions
    "suicid", "self-harm", "eating disorder", "anorexia", "bulimia", "binge",
    "addiction", "substance", "alcohol", "drug abuse", "ocd", "obsessive",
    "compulsive", "panic", "phobia", "social anxiety", "psychosis",
    "schizophreni", "bipolar", "personality disorder", "borderline",
    "narcissist", "psychopath", "amnesia",
    # Neurodivergence
    "autism", "autistic", "adhd", "neurodiverg", "aspberger",
    "dyslexi", "learning disabil", "coordination disorder", "neurodevelopmental",
    # Somatic & functional
    "somatic", "pain", "chronic", "insomnia", "sleep disorder",
    "interoceptive", "interoception",
    # Coping & regulation
    "resilience", "coping", "emotion regulation", "rumination", "worry",
    "stress", "burnout", "grief", "bereavement",
    # Assessment & research
    "psychometric", "assessment", "scale", "validation", "comorbidity",
    "prevalence", "risk factor", "randomized", "clinical trial", "rct",
    "evidence-based", "diagnosis", "diagnostic", "screening tool",
    # Other clinical
    "couples", "sex therap", "paraphilia", "body image", "dissociat",
    "forensic", "offender", "violence", "aggression", "abuse",
    "maltreatment", "domestic violence", "self-esteem", "self-compassion",
    "shame", "well-being", "wellbeing", "rehabilitation",
    "health psychology", "behavioral medicine", "crisis",
    # Behavioral/addictive
    "smartphone", "impulsiv", "executive function", "gambling",
    "hypersexuality", "self-control", "self-regulation",
    # Additional terms found during discard re-scan
    "fear", "phobic", "caregiver", "carer", "patient", "clinical practice",
    "hallucinogen", "psychedel", "salvia",
    "empathetic", "empathy", "chatbot", "ai-assist", "digital twin",
    "social skill", "social functioning", "social disconn",
    "eeg", "neuroimag", "functional connectivity",
    "workplace well", "occupational health",
    "moral injury", "secondary traum",
    "psychological flexib", "transdiagnostic",
    "mechanism", "mainten", "relapse",
    "impairment", "stream of consciousness", "thought disorder",
    "orgasm", "sexual satisfaction",
    "co-design", "lived experience", "service user",
]

HARD_EXCLUDE = [
    r"animal personality", r"rat model", r"mouse model", r"non-human animal",
    r"brightness perception", r"light-source position", r"transparency in brightness",
    r"temporal interval judgment", r"neural language model",
    r"evaluative conditioning response to de houwer",
    r"comments on.*animal personality",
    r"paddle effect.*visual-context bias",
    r"quantum of silence",  # philosophical, not clinical
]

CLINICAL_COMPILED = [re.compile(kw, re.IGNORECASE) for kw in CLINICAL_KEYWORDS]
EXCLUDE_COMPILED = [re.compile(kw, re.IGNORECASE) for kw in HARD_EXCLUDE]

# ─── Functions ────────────────────────────────────────────────────────────────

def load_existing_ids():
    """Load known OSF base IDs from papers.json and seen-compact-ids.json."""
    with open(PAPERS_JSON) as f:
        papers = json.load(f)
    ids = set()
    for p in papers:
        oid = p.get("osf_id")
        if oid:
            ids.add(oid.split("_v")[0])
    # Also load previously seen IDs (including discarded papers)
    seen_file = os.path.join(PSYARXIV_HUB, "data", "seen-compact-ids.json")
    if os.path.exists(seen_file):
        with open(seen_file) as f:
            ids.update(json.load(f))
    return ids, len(papers)


def discover_papers(days_back=3):
    """Fetch papers from OSF API using the fixed date filter."""
    today = datetime.date.today()
    from_date = today - datetime.timedelta(days=days_back)

    all_results = []
    page = 1
    while True:
        params = {
            "filter[provider]": "psyarxiv",
            "filter[date_created][gt]": from_date.isoformat(),
            "page[size]": 100,
            "page": page,
        }
        r = requests.get(
            "https://api.osf.io/v2/preprints/",
            params=params, timeout=30
        )
        if r.status_code != 200:
            print(f"  API error on page {page}: {r.status_code}")
            break
        data = r.json()
        results = data.get("data", [])
        all_results.extend(results)
        if not results or not data.get("links", {}).get("next"):
            break
        page += 1

    # Dedupe by base ID
    seen = {}
    for p in all_results:
        base = p["id"].split("_v")[0]
        if base not in seen:
            seen[base] = p

    return list(seen.values())


def score_text(text):
    """Score clinical relevance based on keyword matches. Returns (score, matched_keywords)."""
    lower = text.lower()
    hits = []
    for pat in CLINICAL_COMPILED:
        m = pat.search(lower)
        if m:
            hits.append(m.group())
    # Deduplicate by lowercase
    unique = list(dict.fromkeys(h.lower() for h in hits))
    return len(unique), unique


def is_hard_excluded(text):
    """Check if paper should be hard-excluded based on title/content."""
    lower = text.lower()
    for pat in EXCLUDE_COMPILED:
        if pat.search(lower):
            return True
    return False


def extract_pdf_abstract(compact_id, max_pages=3):
    """Download PDF or DOCX and extract text for screening."""
    tmp_file = os.path.join(TMP_DIR, f"{compact_id}_screen.txt")
    try:
        # First try the dedicated fetch script (PDF only)
        result = subprocess.run(
            [sys.executable, FETCH_SCRIPT, compact_id, tmp_file],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            with open(tmp_file) as f:
                text = f.read()
            if text.strip():
                return text[:3000]

        # If PDF failed, try fetching DOCX directly
        import requests as req
        for v in range(5, 0, -1):
            vid = f"{compact_id}_v{v}"
            r = req.get(f"https://api.osf.io/v2/preprints/{vid}/",
                        params={"filter[provider]": "psyarxiv"}, timeout=30)
            if r.status_code != 200 or not r.json().get("data"):
                continue
            preprint_id = r.json()["data"]["id"]
            r2 = req.get(f"https://api.osf.io/v2/preprints/{preprint_id}/files/osfstorage/",
                         params={"page[size]": 20}, timeout=30)
            if r2.status_code != 200:
                continue
            for f_info in r2.json().get("data", []):
                name = f_info.get("attributes", {}).get("name", "")
                dl = f_info.get("links", {}).get("download", "")
                if not dl:
                    continue
                if name.lower().endswith((".docx", ".pdf")):
                    r3 = req.get(dl, timeout=120)
                    if r3.status_code != 200:
                        continue
                    tmp_doc = os.path.join(TMP_DIR, f"{compact_id}.{name.split('.')[-1]}")
                    with open(tmp_doc, "wb") as out:
                        out.write(r3.content)
                    try:
                        if name.lower().endswith(".docx"):
                            from docx import Document
                            doc = Document(tmp_doc)
                            text = "\n".join(p.text for p in doc.paragraphs)
                        else:
                            import pdfplumber
                            text = ""
                            with pdfplumber.open(tmp_doc) as pdf:
                                for page in pdf.pages:
                                    t = page.extract_text()
                                    if t:
                                        text += t + "\n\n"
                        if tmp_doc != tmp_file:
                            os.remove(tmp_doc)
                        if text.strip():
                            return text[:3000]
                    except Exception:
                        if os.path.exists(tmp_doc) and tmp_doc != tmp_file:
                            os.remove(tmp_doc)
                    break
            break
        return ""
    except Exception as e:
        print(f"    Extraction failed for {compact_id}: {e}")
        return ""


def cleanup_tmp():
    """Delete temporary screening files."""
    if os.path.exists(TMP_DIR):
        for f in os.listdir(TMP_DIR):
            os.remove(os.path.join(TMP_DIR, f))
        os.rmdir(TMP_DIR)


def categorize_from_text(text, title):
    """Suggest category based on keywords in text."""
    lower = (title + " " + text).lower()
    category_map = {
        "Anxiety & OCD": ["anxiety", "ocd", "obsessive", "compulsive", "panic", "phobia", "social anxiety", "worry", "fear", "phobic"],
        "Couples Therapy & Sexology": ["couples", "sex therap", "paraphilia", "sexual", "intimate relationship", "romantic", "orgasm", "sexual satisfaction"],
        "Neurodivergence": ["autism", "autistic", "adhd", "neurodiverg", "asperger", "neurodevelopmental", "dyslexi", "learning disabil", "coordination disorder"],
        "Mood Disorders": ["depress", "bipolar", "manic", "mood", "dysthym"],
        "Trauma & Stressor-Related": ["trauma", "ptsd", "posttraumatic", "stressor", "ace", "adverse childhood", "moral injury", "abuse", "secondary traum"],
        "Personality Disorders": ["personality disorder", "borderline", "narcissist", "antisocial", "cluster b", "personality functioning"],
        "Therapeutic Modalities": ["cbt", "psychotherapy", "mindfulness", "acceptance and commitment", "dbt", "schema therapy", "emdr", "exposure therapy", "cognitive reappraisal", "intervention", "compassion-focused", "chatbot", "empathetic"],
        "Psychopathology & Assessment": ["psychopath", "assessment", "psychometric", "scale", "validation", "diagnosis", "diagnostic", "screening tool", "digital twin", "amnesia"],
        "Eating Disorders": ["eating disorder", "anorexia", "bulimia", "binge", "body image", "weight"],
        "Somatic & Functional": ["somatic", "chronic pain", "functional", "conversion", "medically unexplained", "interoceptive", "interoception"],
        "Suicidality & Self-Harm": ["suicid", "self-harm", "nonsuicidal", "self-injur"],
        "Psychosis & Schizophrenia": ["psychosis", "schizophreni", "delusion", "hallucinat", "psychotic", "psychotic-like", "thought disorder", "stream of consciousness"],
        "Addiction & Substance Use": ["addiction", "substance", "alcohol", "drug", "opiate", "cannabis", "gambling", "salvia", "hallucinogen", "psychedel"],
        "Obsessive-Compulsive": ["obsessive-compulsive", "hoarding", "body-focused repetitive"],
    }
    best_cat = "Other Clinical"
    best_score = 0
    for cat, keywords in category_map.items():
        score = sum(1 for kw in keywords if kw in lower)
        if score > best_score:
            best_score = score
            best_cat = cat
    return best_cat


def assign_number():
    """Get the next paper number."""
    with open(PAPERS_JSON) as f:
        papers = json.load(f)
    return max(p["number"] for p in papers) + 1 if papers else 1


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def main():
    os.makedirs(TMP_DIR, exist_ok=True)
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    print(f"=== PsyArXiv Discovery & Screening Pipeline ===")
    print(f"Looking back {days_back} days")

    # 1. Load existing
    known_ids, total_existing = load_existing_ids()
    print(f"Existing papers: {total_existing}, known OSF IDs: {len(known_ids)}")

    # 2. Discover
    print(f"\n--- Discovering ---")
    candidates = discover_papers(days_back)
    print(f"Discovered: {len(candidates)} (deduped)")

    # 3. Filter unseen
    unseen = []
    for c in candidates:
        base = c["id"].split("_v")[0]
        if base not in known_ids:
            unseen.append(c)
    print(f"Already known: {len(candidates) - len(unseen)}")
    print(f"Unseen: {len(unseen)}")

    # 4. Stage 1: Title-based screening
    print(f"\n--- Stage 1: Title-based screening ---")
    auto_accept = []
    auto_discard = []
    borderline = []  # score = 1 or title unclear

    for c in unseen:
        title = c["attributes"]["title"]
        compact_id = c["id"].split("_v")[0]

        if is_hard_excluded(title):
            auto_discard.append((compact_id, c["id"], title, "Hard excluded (non-clinical topic)"))
            continue

        score, hits = score_text(title)

        entry = {
            "compact_id": compact_id,
            "osf_id": c["id"],
            "title": title,
            "date_created": c["attributes"].get("date_created", ""),
            "link": c.get("links", {}).get("html", f"https://osf.io/preprints/psyarxiv/{compact_id}"),
            "stage1_score": score,
            "stage1_hits": hits[:5],
        }

        if score >= 2:
            entry["source"] = "title"
            entry["final_score"] = score
            auto_accept.append(entry)
        elif score == 0:
            auto_discard.append((compact_id, c["id"], title, f"Score 0 (no clinical keywords)"))
        else:
            borderline.append(entry)

    print(f"Auto-accept (score >= 2): {len(auto_accept)}")
    print(f"Borderline (score = 1):  {len(borderline)}")
    print(f"Auto-discard (score = 0): {len(auto_discard)}")

    # 5. Stage 2: PDF-based screening for borderline
    print(f"\n--- Stage 2: PDF screening for {len(borderline)} borderline papers ---")
    pdf_accepted = []
    pdf_discarded = []

    for i, entry in enumerate(borderline):
        cid = entry["compact_id"]
        print(f"  [{i+1}/{len(borderline)}] Fetching PDF for {cid}...", end=" ", flush=True)
        text = extract_pdf_abstract(cid)
        if text:
            full_text = entry["title"] + " " + text
            score, hits = score_text(full_text)
            entry["stage2_score"] = score
            entry["stage2_hits"] = hits[:5]
            entry["source"] = "pdf"
            entry["final_score"] = score
            if score >= 2:
                pdf_accepted.append(entry)
                print(f"ACCEPT (score {score}: {hits[:3]})")
            else:
                pdf_discarded.append((cid, entry["osf_id"], entry["title"], f"PDF score {score} (insufficient)"))
                print(f"discard (score {score})")
        else:
            pdf_discarded.append((cid, entry["osf_id"], entry["title"], "PDF extraction failed"))
            print("FAILED (no text)")
        time.sleep(0.5)  # Be polite

    # 6. Combine results
    all_accepted = auto_accept + pdf_accepted
    all_discarded = auto_discard + pdf_discarded

    print(f"\n=== RESULTS ===")
    print(f"Accepted: {len(all_accepted)}")
    print(f"  From title screening: {len(auto_accept)}")
    print(f"  From PDF screening:   {len(pdf_accepted)}")
    print(f"Discarded: {len(all_discarded)}")

    for a in all_accepted:
        print(f"  ✓ {a['compact_id']:8s} [{a['final_score']}] {a['title'][:65]}")

    # 7. Save outputs
    # Save accepted to screened-papers.json
    with open(SCREENED_PAPERS, "w") as f:
        json.dump(all_accepted, f, indent=2, ensure_ascii=False)

    # Save all candidates with scores to screening-brief.json
    brief = []
    for a in all_accepted:
        brief.append({
            "compact_id": a["compact_id"],
            "osf_id": a["osf_id"],
            "title": a["title"],
            "description": f"Score: {a['final_score']} via {a.get('source','title')}",
            "date_created": a.get("date_created", ""),
            "link": a.get("link", ""),
            "status": "accepted",
            "score": a["final_score"],
            "source": a.get("source", "title"),
        })
    for cid, oid, title, reason in all_discarded:
        brief.append({
            "compact_id": cid,
            "osf_id": oid,
            "title": title,
            "description": reason,
            "date_created": "",
            "link": "",
            "status": "discarded",
            "score": 0,
            "source": "title",
        })
    with open(SCREENING_BRIEF, "w") as f:
        json.dump(brief, f, indent=2, ensure_ascii=False)

    # Append to discard log
    today_str = datetime.date.today().isoformat()
    with open(DISCARDED_LOG, "a") as f:
        f.write(f"\n## {today_str} — Pipeline run\n\n")
        for cid, oid, title, reason in all_discarded:
            f.write(f"- ~~{cid}~~ {title[:80]} — *{reason}*\n")
        f.write(f"\n### Accepted ({len(all_accepted)})\n\n")
        for a in all_accepted:
            f.write(f"- {a['compact_id']} {a['title'][:80]} (score {a['final_score']}, via {a.get('source','title')})\n")

    # 8. Update seen-compact-ids.json with all encountered IDs
    seen_file = os.path.join(PSYARXIV_HUB, "data", "seen-compact-ids.json")
    existing_seen = set()
    if os.path.exists(seen_file):
        with open(seen_file) as f:
            existing_seen = set(json.load(f))
    # Add all candidates from this run
    for a in all_accepted:
        existing_seen.add(a["compact_id"])
    for cid, oid, title, reason in all_discarded:
        existing_seen.add(cid)
    # Also add unseen IDs that scored 0 (auto-discarded by title)
    with open(seen_file, "w") as f:
        json.dump(sorted(existing_seen), f, indent=2)

    # 9. Cleanup temp files
    cleanup_tmp()

    print(f"\nOutputs:")
    print(f"  {SCREENED_PAPERS} ({len(all_accepted)} accepted)")
    print(f"  {SCREENING_BRIEF} ({len(brief)} total)")
    print(f"  {DISCARDED_LOG} (appended)")
    print(f"  {seen_file} ({len(existing_seen)} tracked IDs)")
    print(f"  Temp PDFs cleaned up")


if __name__ == "__main__":
    main()