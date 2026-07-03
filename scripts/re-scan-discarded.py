#!/usr/bin/env python3
"""
Re-scan discarded papers using PDF extraction (since OSF API returns empty abstracts
and PsyArXiv pages are JS-rendered so Scrapling can't get content either).

For each candidate: download PDF, extract text, score for clinical relevance,
then delete the PDF. Only log IDs, not files.
"""

import json
import os
import re
import subprocess
import sys
import time

# ─── Config ───────────────────────────────────────────────────────────────────
PSYARXIV_HUB = os.path.expanduser("~/my-project/psyarxiv-hub")
PAPERS_JSON = os.path.join(PSYARXIV_HUB, "data", "papers.json")
FETCH_SCRIPT = os.path.expanduser("~/my-project/scripts/fetch-paper-fulltext.py")
TMP_DIR = "/tmp/psyarxiv-rescan"

CLINICAL_KEYWORDS = [
    "depress", "anxiety", "trauma", "ptsd", "therap", "treatment", "intervention",
    "disorder", "clinical", "psychopath", "symptom", "mental health",
    "cbt", "cognitive behavioral", "psychotherapy", "counseling", "mindfulness",
    "acceptance", "commitment", "dialectical behavior", "dbt", "schema therapy",
    "psychodynamic", "emdr", "exposure therapy",
    "suicid", "self-harm", "eating disorder", "anorexia", "bulimia", "binge",
    "addiction", "substance", "alcohol", "drug abuse", "ocd", "obsessive",
    "compulsive", "panic", "phobia", "social anxiety", "psychosis",
    "schizophreni", "bipolar", "personality disorder", "borderline",
    "narcissist", "psychopath",
    "autism", "autistic", "adhd", "neurodiverg", "asperger",
    "somatic", "pain", "chronic", "insomnia", "sleep disorder",
    "resilience", "coping", "emotion regulation", "rumination", "worry",
    "stress", "burnout", "grief", "bereavement",
    "psychometric", "assessment", "scale", "validation", "comorbidity",
    "prevalence", "risk factor", "randomized", "clinical trial", "rct",
    "evidence-based",
    "couples", "sex therap", "paraphilia", "body image", "dissociat",
    "forensic", "offender", "violence", "aggression", "abuse",
    "maltreatment", "domestic violence", "self-esteem", "self-compassion",
    "shame", "well-being", "wellbeing", "rehabilitation",
    "health psychology", "behavioral medicine", "crisis",
    "smartphone", "impulsiv", "executive function", "gambling",
    "hypersexuality",
    # Additional keywords for things the title-only scan missed
    "fear", "phobic", "caregiver", "carer", "patient", "clinical practice",
    "diagnosis", "diagnostic", "screening tool", "neurodevelopmental",
    "dyslexi", "learning disabil", "coordination disorder", "impairment",
    "salvia", "hallucinogen", "psychedel",
    "empathetic", "empathy", "compassion-focused",
    "self-control", "self-regulation", "impulse control",
    "social skill", "social functioning", "social disconn",
    "interoceptive", "interoception",
    "urgen", "triage", "crisis intervention",
    "stream of consciousness", "thought disorder",
    "eeg", "neuroimag", "functional connectivity",
    "digital twin", "chatbot", "ai-assist",
    "workplace well", "occupational health",
    "moral injury", "secondary traum",
    "resilience", "psychological flexib",
    "transdiagnostic", "mechanism", "mainten", "relapse",
]

CLINICAL_COMPILED = [re.compile(kw, re.IGNORECASE) for kw in CLINICAL_KEYWORDS]


def score_text(text):
    lower = text.lower()
    hits = []
    for pat in CLINICAL_COMPILED:
        m = pat.search(lower)
        if m:
            hits.append(m.group())
    unique = list(dict.fromkeys(h.lower() for h in hits))
    return len(unique), unique


def categorize_from_text(text, title):
    lower = (title + " " + text).lower()
    category_map = {
        "Anxiety & OCD": ["anxiety", "ocd", "obsessive", "compulsive", "panic", "phobia", "social anxiety", "worry", "fear", "phobic"],
        "Couples Therapy & Sexology": ["couples", "sex therap", "paraphilia", "sexual", "intimate relationship", "romantic", "orgasm"],
        "Neurodivergence": ["autism", "autistic", "adhd", "neurodiverg", "asperger", "neurodevelopmental", "dyslexi", "learning disabil", "coordination disorder"],
        "Mood Disorders": ["depress", "bipolar", "manic", "mood", "dysthym"],
        "Trauma & Stressor-Related": ["trauma", "ptsd", "posttraumatic", "stressor", "ace", "adverse childhood", "moral injury", "abuse", "secondary traum"],
        "Personality Disorders": ["personality disorder", "borderline", "narcissist", "antisocial", "cluster b", "personality functioning"],
        "Therapeutic Modalities": ["cbt", "psychotherapy", "mindfulness", "acceptance and commitment", "dbt", "schema therapy", "emdr", "exposure therapy", "cognitive reappraisal", "intervention", "compassion-focused"],
        "Psychopathology & Assessment": ["psychopath", "assessment", "psychometric", "scale", "validation", "diagnosis", "diagnostic", "screening tool"],
        "Eating Disorders": ["eating disorder", "anorexia", "bulimia", "binge", "body image", "weight"],
        "Somatic & Functional": ["somatic", "chronic pain", "functional", "conversion", "medically unexplained", "interoceptive", "interoception"],
        "Suicidality & Self-Harm": ["suicid", "self-harm", "nonsuicidal", "self-injur"],
        "Psychosis & Schizophrenia": ["psychosis", "schizophreni", "delusion", "hallucinat", "psychotic", "psychotic-like", "thought disorder", "stream of consciousness"],
        "Addiction & Substance Use": ["addiction", "substance", "alcohol", "drug", "opiate", "cannabis", "gambling", "salvia", "hallucinogen", "psychedel"],
    }
    best_cat = "Other Clinical"
    best_score = 0
    for cat, keywords in category_map.items():
        score = sum(1 for kw in keywords if kw in lower)
        if score > best_score:
            best_score = score
            best_cat = cat
    return best_cat


def fetch_pdf_text(compact_id):
    """Download PDF and extract first ~3000 chars for screening."""
    os.makedirs(TMP_DIR, exist_ok=True)
    tmp_file = os.path.join(TMP_DIR, f"{compact_id}_rescan.txt")
    try:
        result = subprocess.run(
            [sys.executable, FETCH_SCRIPT, compact_id, tmp_file],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return None
        with open(tmp_file) as f:
            text = f.read()
        return text[:4000]  # First ~3-4 pages
    except Exception as e:
        return None
    finally:
        # Clean up temp file
        if os.path.exists(tmp_file):
            os.remove(tmp_file)


def load_existing_ids():
    with open(PAPERS_JSON) as f:
        papers = json.load(f)
    ids = set()
    for p in papers:
        oid = p.get("osf_id")
        if oid:
            ids.add(oid.split("_v")[0])
    return ids, len(papers)


def main():
    known_ids, total_existing = load_existing_ids()
    print(f"Existing papers: {total_existing}")

    # All candidates: PDF failures + suspicious score-0 discards
    candidates = {
        # PDF extraction failures (borderline, never properly screened)
        "fhvnz": "Current distress does not moderate the efficacy of cognitive reappraisal",
        "e87ft": "Exploring diagnosis of Developmental Coordination Disorder and Specific Develop",
        "2kbtm": "Factors Shaping Autistic Adults' Experiences and Perceived Benefits of a Co-Design",
        "gxrha": "Construct validity evidence for a Workplace Well-Being Questionnaire Battery",
        "n9gfq": "Subjective Effects and Characteristics of Salvia Divinorum Use from a Retrospect",
        "f5kbv": "Telling Stories of Resistance - Calling to Ancestral Strength",
        "m2vw4": "Regulation Without Regulating? Misalignment Between Self-Reported Emotion Regulation",
        "xpfjz": "Identification of mental illness in maternity settings and care pathways",
        "djkcz": "Self-reports of personality functioning and depression are practically fungible",
        "zdm4c": "Anxiety modulates sensitivity and response bias in the AX CPT task",
        "zbwsx": "What do people believe about AI chatbots for mental health",
        "965yg": "Psychometric Comparability of LLM-Based Digital Twins",
        
        # Score-0 discards with clinical-sounding titles
        "r29tv": "Memory-Based Learning Disabilities: A Syndrome Without a Pigeonhole",
        "xpm7e": "Neural discrimination in dyslexic and typical readers",
        "5rea9": "Subjective Experience of Stream of Consciousness Impairment in Three Patients",
        "a26je": "EEG study in informal caregivers of patients",
        "ebawx": "The Fearbase: a dynamically growing database for fear research",
        "3q9dk": "From backlog to blind spots: neurodevelopmental pathway reform",
        "pvyfm": "The Role of Interoceptive Awareness and Relationship Satisfaction in Female Orgasm",
        "g7ktm": "Social Disconnection is Associated with Impaired Social Skills",
        "nctgh": "Predicting Effects of a Computational Empathetic Bot",
        "4jpwn": "Identifying safety risks in an Integrated Urgent Care telephone triage",
        "sp4k7": "Believe It, Achieve It? Self-Control Beliefs in Predicting Life Outcomes",
        "rsmun": "Psychotic-like experiences and neurobehavioral reward processing in adolescents",
    }

    # Filter out already-known
    to_scan = {cid: title for cid, title in candidates.items() if cid not in known_ids}
    print(f"Candidates to re-scan: {len(to_scan)} (out of {len(candidates)}, {len(candidates) - len(to_scan)} already known)")

    results = []
    recovered = []

    for i, (cid, stored_title) in enumerate(to_scan.items()):
        print(f"\n[{i+1}/{len(to_scan)}] {cid}: {stored_title}")
        
        # Score title first with expanded keywords
        title_score, title_hits = score_text(stored_title)
        print(f"  Title score: {title_score} ({title_hits[:5]})")
        
        if title_score >= 2:
            # Title alone is enough with expanded keywords
            category = categorize_from_text("", stored_title)
            result = {
                "compact_id": cid,
                "title": stored_title,
                "abstract_found": False,
                "text_source": "title_expanded",
                "score": title_score,
                "hits": title_hits[:10],
                "category": category,
                "link": f"https://osf.io/preprints/psyarxiv/{cid}",
            }
            results.append(result)
            recovered.append(result)
            print(f"  => RECOVER via expanded title keywords! Score: {title_score} | Cat: {category}")
            continue
        
        # Need PDF
        print(f"  Fetching PDF...", end=" ", flush=True)
        text = fetch_pdf_text(cid)
        
        if text:
            full_text = stored_title + " " + text
            score, hits = score_text(full_text)
            category = categorize_from_text(full_text, stored_title)
            
            result = {
                "compact_id": cid,
                "title": stored_title,
                "abstract_found": True,
                "text_preview": text[:200],
                "text_source": "pdf",
                "score": score,
                "hits": hits[:10],
                "category": category,
                "link": f"https://osf.io/preprints/psyarxiv/{cid}",
            }
            results.append(result)
            
            if score >= 2:
                recovered.append(result)
                print(f"RECOVER! Score: {score} | Cat: {category} | Hits: {hits[:5]}")
            else:
                print(f"Score: {score} | still discard")
        else:
            print(f"PDF fetch failed")
            results.append({
                "compact_id": cid,
                "title": stored_title,
                "abstract_found": False,
                "text_source": "failed",
                "score": title_score,
                "hits": title_hits,
                "category": "Unknown",
                "link": f"https://osf.io/preprints/psyarxiv/{cid}",
            })
        
        time.sleep(0.5)

    # Cleanup
    if os.path.exists(TMP_DIR):
        for f in os.listdir(TMP_DIR):
            os.remove(os.path.join(TMP_DIR, f))
        os.rmdir(TMP_DIR)

    # Save
    output = os.path.join(PSYARXIV_HUB, "scripts", "re-scan-results.json")
    with open(output, "w") as f:
        json.dump({"results": results, "recovered": recovered}, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"RE-SCAN COMPLETE")
    print(f"Total scanned: {len(results)}")
    print(f"Recovered (score >= 2): {len(recovered)}")
    for r in recovered:
        print(f"  + {r['compact_id']:8s} [{r['score']}] {r['title'][:65]}")
        print(f"    Category: {r['category']} | Source: {r.get('text_source','')} | Hits: {r['hits'][:5]}")
    
    print(f"\nResults saved to: {output}")
    return recovered


if __name__ == "__main__":
    recovered = main()
    if recovered:
        print(f"\n=== RECOVERED PAPERS ({len(recovered)}) ===")
        for r in recovered:
            print(json.dumps(r, ensure_ascii=False))