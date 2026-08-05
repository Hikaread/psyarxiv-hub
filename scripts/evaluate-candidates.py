#!/usr/bin/env python3
"""
Unified PsyArXiv evaluation pipeline.
Reads screened-papers.json, fetches PDFs, evaluates via LLM (single merged call),
inserts accepted papers into papers.json, logs discards, updates seen IDs, and
generates OG pages. No agent reasoning needed — just run and commit.

Usage:
  python3 evaluate-candidates.py [--max N] [--dry-run]
"""
import json, sys, os, subprocess, re, time, glob, shutil, urllib.request
from datetime import datetime, timezone

# Volatile paths (may be wiped) with git-tracked fallbacks
SCREENED_PATH = '/home/z/my-project/psyarxiv-hub/curation/screened-papers.json'
DISCOVERED_PATH = '/home/z/my-project/psyarxiv-hub/curation/discovered-papers.json'
RESULTS_PATH = '/home/z/my-project/psyarxiv-hub/curation/evaluation-results.json'
PAPERS_JSON = '/home/z/my-project/psyarxiv-hub/data/papers.json'
SEEN_IDS_PATH = '/home/z/my-project/psyarxiv-hub/data/seen-compact-ids.json'
DISCARD_LOG = '/home/z/my-project/psyarxiv-hub/curation/discarded-log.md'
OG_SCRIPT = '/home/z/my-project/psyarxiv-hub/scripts/generate-og-pages.mjs'
FETCH_SCRIPT = '/home/z/my-project/psyarxiv-hub/scripts/fetch-paper-fulltext.py'
INBOX_DIR = '/home/z/my-project/psyarxiv-hub/curation/inbox'
CHECKPOINT_PATH = '/home/z/my-project/psyarxiv-hub/curation/eval-checkpoint.json'

# All scripts and data now live in the git-tracked repo — no volatile copies needed

# Checkpoint: persists eval progress so timeouts don't lose work
def load_checkpoint():
    try:
        with open(CHECKPOINT_PATH, 'r') as f:
            cp = json.load(f)
        # Stale if older than 4 hours
        if time.time() - cp.get('ts', 0) > 14400:
            os.remove(CHECKPOINT_PATH)
            return set()
        return set(cp.get('done_ids', []))
    except:
        return set()

def save_checkpoint(done_ids):
    with open(CHECKPOINT_PATH, 'w') as f:
        json.dump({'ts': time.time(), 'done_ids': list(done_ids)}, f)
        f.write('\n')

def clear_checkpoint():
    try:
        os.remove(CHECKPOINT_PATH)
    except:
        pass

# Merged prompt: accept/reject AND curation in one call
MERGED_SYSTEM = """You are a clinical psychology preprint evaluator and curator for PsyArXiv Hub.

STEP 1 — Evaluate for clinical psychology practice relevance.

ACCEPT if the paper relates to:
- Therapy, assessment, diagnosis, psychopathology, mental health interventions, neuropsychology
- Clinical utility for practicing therapists, psychologists, or psychiatrists

REJECT if the paper is:
- Basic cognitive/social/developmental psychology without clinical application
- Education, linguistics, neuroscience methods, AI/tech, political psychology
- Forensic/criminal, sports, music, philosophy
- Focused on children/adolescents/infants (unless direct adult clinical implications)
- Animal models, psychedelics, registered report protocols, editorials/commentaries

STEP 2 — If ACCEPT, write curation content.

Category options:
Therapeutic Modalities, Psychopathology & Assessment, Mood Disorders, Trauma & Stressor-Related,
Neurodivergence, Anxiety & OCD, Personality Disorders, Other Clinical, Somatic & Functional,
Suicidality & Self-Harm, Addiction & Substance Use, Eating Disorders, Psychosis & Schizophrenia,
Couples Therapy & Sexology, Obsessive-Compulsive, Neuropsychology & Aging, Digital Mental Health

Respond with ONLY a JSON object, no other text.

If REJECT:
{"decision": "reject", "reason": "brief reason"}

If ACCEPT:
{"decision": "accept", "reason": "brief reason", "category": "ONE category", "summary": "150+ words, factual, include specific data (N, effect sizes, statistics). MANDATORY: wrap EVERY key term, finding, and statistic in **bold** markdown (at least 6 bold items per summary). Use \\\\n\\\\n (double newline) to separate into 2-3 paragraphs: context/aim, methods/key findings, implications/interpretation.", "clinical_insight": "2-4 sentences, concrete clinical utility. MANDATORY: wrap at least 2 key terms in **bold**. Use \\\\n\\\\n (double newline) to separate into 2 short paragraphs.", "relevant_for": "Bullet list with - prefix describing which clinicians/settings", "notes": "Limitations, caveats", "methodology_note": "Sample size, design type, key measures, analysis approach, preregistration status. Use \\\\n\\\\n to separate logical sections."}"""


def run_zai_chat(prompt, system, timeout=180, max_retries=3):
    for attempt in range(max_retries):
        out_file = f'/tmp/zai_eval_{os.getpid()}_{int(time.time())}.json'
        try:
            cmd = ['z-ai', 'chat', '-p', prompt, '-s', system, '-o', out_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode != 0:
                stderr = result.stderr or ''
                if '429' in stderr or 'Too many requests' in stderr or 'concurrency limit' in stderr:
                    wait = 60 * (attempt + 1)
                    print(f"  -> Rate limited (attempt {attempt+1}), waiting {wait}s...", file=sys.stderr)
                    time.sleep(wait)
                    continue
                print(f"  -> CLI error: {stderr[:100]}", file=sys.stderr)
                return None
            with open(out_file, 'r') as f:
                data = json.load(f)
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            print(f"  -> No JSON in response", file=sys.stderr)
            return None
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"  -> Exception: {type(e).__name__}: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(30)
                continue
            return None
        finally:
            if os.path.exists(out_file):
                os.remove(out_file)
    return None


def fetch_fulltext(osf_id):
    compact = re.sub(r'_v\d+$', '', osf_id)
    output = f'/tmp/{compact}_full.txt'
    try:
        result = subprocess.run(
            ['python3', FETCH_SCRIPT, compact, output],
            capture_output=True, text=True, timeout=180
        )
        for line in (result.stdout + result.stderr).strip().split('\n'):
            line = line.strip()
            if line.startswith('{'):
                info = json.loads(line)
                if info.get('source') in ('pdf', 'docx') and os.path.exists(output):
                    with open(output, 'r') as f:
                        text = f.read()
                    return text, info.get('source', 'pdf')
                elif info.get('source') == 'abstract':
                    return None, 'no_pdf'
                else:
                    return None, info.get('error', 'fetch_failed')
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    except Exception as e:
        return None, str(e)
    return None, 'unknown'


def get_next_number():
    try:
        with open(PAPERS_JSON, 'r') as f:
            papers = json.load(f)
        if papers:
            return max(p.get('number', 0) for p in papers) + 1
    except:
        pass
    return 1


def extract_sections(text, max_chars=8000):
    sections = {}
    current_section = 'preamble'
    current_text = []
    for line in text.split('\n'):
        lower = line.strip().lower()
        if lower in ['abstract', 'introduction', 'methods', 'method', 'methodology',
                      'results', 'discussion', 'conclusion', 'conclusions',
                      'references', 'bibliography', 'acknowledg']:
            if current_text:
                sections[current_section] = '\n'.join(current_text)
            current_section = lower
            current_text = []
        else:
            current_text.append(line)
    if current_text:
        sections[current_section] = '\n'.join(current_text)
    parts = []
    for key in ['abstract', 'methods', 'method', 'methodology', 'results', 'discussion']:
        if key in sections:
            parts.append(f'### {key.upper()}\n{sections[key]}')
    combined = '\n\n'.join(parts)
    if len(combined) > max_chars:
        combined = combined[:max_chars] + '\n...[truncated]'
    if not combined:
        combined = text[:max_chars]
    return combined


def fetch_authors(osf_id):
    """Fetch author names from OSF contributors API (public, no auth needed)."""
    try:
        base_id = osf_id.split('_v')[0] if '_v' in osf_id else osf_id
        url = f"https://api.osf.io/v2/preprints/{base_id}/contributors/?page[size]=50"
        req = urllib.request.Request(url, headers={
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; PsyArXiv-Hub/1.0)'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        contrib_list = []
        for c in data.get('data', []):
            user_data = c.get('relationships', {}).get('users', {}).get('data', {})
            if isinstance(user_data, dict) and user_data.get('id'):
                index = c.get('attributes', {}).get('index', 999)
                contrib_list.append((index, user_data['id']))
        contrib_list.sort(key=lambda x: x[0])
        names = []
        for _, uid in contrib_list[:10]:
            try:
                ureq = urllib.request.Request(
                    f"https://api.osf.io/v2/users/{uid}/",
                    headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0 (compatible; PsyArXiv-Hub/1.0)'}
                )
                with urllib.request.urlopen(ureq, timeout=10) as uresp:
                    udata = json.loads(uresp.read().decode())
                    name = udata.get('data', {}).get('attributes', {}).get('full_name', '').strip()
                    if name:
                        names.append(name)
                time.sleep(0.15)
            except Exception:
                pass
        if names:
            return '; '.join(names)
    except Exception as e:
        print(f"  -> Author fetch failed: {e}", file=sys.stderr)
    return None


def format_source_date(date_str):
    """Convert YYYY-MM-DD to DD.MM.YYYY."""
    try:
        dt = date_str.replace('T', ' ').split('.')[0].split(' ')[0]
        parts = dt.split('-')
        return f"{parts[2]}.{parts[1]}.{parts[0]}"
    except Exception:
        return date_str


def fix_relevant_for(rf):
    """Fix relevant_for: if LLM returns JSON array (string or list), convert to markdown bullets."""
    if not rf:
        return ''
    if isinstance(rf, list):
        return '\n'.join(f'- {item}' for item in rf)
    rf_str = str(rf).strip()
    if rf_str.startswith('[') and rf_str.endswith(']'):
        try:
            items = json.loads(rf_str)
            if isinstance(items, list):
                return '\n'.join(f'- {item}' for item in items)
        except json.JSONDecodeError:
            pass
    lines = rf_str.split('\n')
    fixed = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('- '):
            fixed.append(f'- {stripped}')
        else:
            fixed.append(stripped)
    return '\n'.join(fixed)


def insert_paper_into_json(paper_entry, number, authors, category, curation, date_posted, osf_id):
    """Insert a new paper directly into papers.json."""
    with open(PAPERS_JSON, 'r') as f:
        papers = json.load(f)
    compact_id = re.sub(r'_v\d+$', '', osf_id)
    source_date = format_source_date(date_posted)
    entry = {
        "number": number,
        "title": paper_entry['title'],
        "authors": authors or "Unknown",
        "osf_id": osf_id,
        "date_posted": date_posted[:10],
        "source_date": source_date,
        "categories": [category],
        "summary": curation.get('summary', ''),
        "clinical_insight": curation.get('clinical_insight', ''),
        "relevant_for": fix_relevant_for(curation.get('relevant_for', '')),
        "published": None,
        "link": f"https://osf.io/preprints/psyarxiv/{osf_id}",
        "methodology_note": curation.get('methodology_note', '')
    }
    papers.append(entry)
    papers.sort(key=lambda p: p.get('number', 0))
    with open(PAPERS_JSON, 'w') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
        f.write('\n')
    return entry


def append_discard_log(osf_id, signal_score, title, reason):
    """Append a discard entry to the log."""
    with open(DISCARD_LOG, 'a') as f:
        f.write(f"- {osf_id} | {signal_score} | {title} — {reason}\n")


def update_seen_ids():
    """Add all compact IDs from discovered-papers.json to seen-compact-ids.json (incremental)."""
    with open(DISCOVERED_PATH, 'r') as f:
        discovered = json.load(f)
    new_compact = set()
    for p in discovered:
        cid = re.sub(r'_v\d+$', '', p['osf_id']).lower()
        new_compact.add(cid)
    with open(SEEN_IDS_PATH, 'r') as f:
        existing = set(json.load(f))
    added = new_compact - existing
    if added:
        merged = sorted(existing | new_compact)
        with open(SEEN_IDS_PATH, 'w') as f:
            json.dump(merged, f, indent=2)
            f.write('\n')
        print(f"Seen IDs: +{len(added)} new (total: {len(merged)})", file=sys.stderr)
    else:
        print(f"Seen IDs: no new IDs to add", file=sys.stderr)
    return len(added)


# Read discarded IDs to skip already-evaluated papers across runs
def load_discarded_ids():
    discarded = set()
    try:
        with open(DISCARD_LOG, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('- '):
                    parts = line.split(' | ')
                    if parts:
                        discarded.add(parts[0][2:])  # strip "- "
    except:
        pass
    # Also load from evaluation-results.json
    try:
        with open(RESULTS_PATH, 'r') as f:
            res = json.load(f)
        for r in res.get('results', []):
            if r['decision'] in ('reject', 'error'):
                discarded.add(r['osf_id'])
    except:
        pass
    return discarded


def generate_og_pages():
    """Run the OG page generator."""
    result = subprocess.run(['node', OG_SCRIPT], capture_output=True, text=True, timeout=60)
    print(result.stdout.strip(), file=sys.stderr)
    if result.returncode != 0:
        print(f"OG generation warning: {result.stderr[:100]}", file=sys.stderr)


def main():
    max_papers = 15
    dry_run = False
    for arg in sys.argv[1:]:
        if arg == '--dry-run':
            dry_run = True
        elif arg.startswith('--max='):
            max_papers = int(arg.split('=')[1])
        elif arg.startswith('--max'):
            max_papers = int(sys.argv[sys.argv.index(arg) + 1])

    with open(SCREENED_PATH, 'r') as f:
        candidates = json.load(f)
    if not candidates:
        print(json.dumps({'evaluated': 0, 'accepted': 0, 'rejected': 0, 'errors': 0, 'results': []}))
        update_seen_ids()
        return

    discarded_ids = load_discarded_ids()
    checkpoint_ids = load_checkpoint()
    eval_done_ids = discarded_ids | checkpoint_ids

    existing_osf_ids = set()
    try:
        with open(PAPERS_JSON, 'r') as f:
            for p in json.load(f):
                if p.get('osf_id'):
                    existing_osf_ids.add(p['osf_id'])
    except:
        pass

    skip_ids = existing_osf_ids | eval_done_ids

    to_eval = [c for c in candidates if c['osf_id'] not in skip_ids]
    print(f"Evaluating {len(candidates)} candidates (max {max_papers}, {len(skip_ids & set(c['osf_id'] for c in candidates))} skipped, {len(to_eval)} to eval)...", file=sys.stderr)
    results = []
    accepted_papers = []
    accepted = 0
    rejected = 0
    errors = 0
    skipped = 0
    base_number = get_next_number()

    for i, paper in enumerate(candidates):
        osf_id = paper['osf_id']
        if osf_id in skip_ids:
            results.append({'osf_id': osf_id, 'title': paper['title'][:80], 'decision': 'skipped', 'reason': 'already in papers.json'})
            skipped += 1
            continue

        evaluated_count = accepted + rejected + errors
        if evaluated_count >= max_papers:
            results.append({'osf_id': osf_id, 'title': paper['title'][:80], 'decision': 'deferred', 'reason': 'max_papers limit reached'})
            continue

        signal = paper.get('signal_score', 0)
        print(f"[{i+1}/{min(len(candidates), max_papers)}] {osf_id}: {paper['title'][:60]}... (signal={signal})", file=sys.stderr)

        if signal <= 1:
            results.append({'osf_id': osf_id, 'title': paper['title'][:80], 'decision': 'reject', 'reason': f'low signal score ({signal})', 'category': None})
            rejected += 1
            checkpoint_ids.add(osf_id)
            save_checkpoint(checkpoint_ids)
            continue

        fulltext, source = fetch_fulltext(osf_id)
        print(f'  FETCH: source={source}, text_len={len(fulltext) if fulltext else 0}', file=sys.stderr)
        if fulltext is None:
            results.append({'osf_id': osf_id, 'title': paper['title'][:80], 'decision': 'reject', 'reason': f'no PDF ({source})', 'category': None})
            rejected += 1
            checkpoint_ids.add(osf_id)
            save_checkpoint(checkpoint_ids)
            print(f"  -> REJECT: {source}", file=sys.stderr)
            continue

        focused_text = extract_sections(fulltext, max_chars=8000)
        prompt = f"""Title: {paper['title']}
Signal score: {signal}
Description: {paper.get('description_preview', paper.get('description', ''))[:500]}

Full text (sections):
{focused_text}

Evaluate this paper for the PsyArXiv clinical psychology hub. If accepted, include full curation content."""

        result = run_zai_chat(prompt, MERGED_SYSTEM, timeout=180)
        if result is None:
            results.append({'osf_id': osf_id, 'title': paper['title'][:80], 'decision': 'error', 'reason': 'LLM call failed'})
            errors += 1
            checkpoint_ids.add(osf_id)
            save_checkpoint(checkpoint_ids)
            time.sleep(5)
            continue

        decision = result.get('decision', 'reject')
        reason = result.get('reason', 'no reason given')

        if decision.lower() == 'reject':
            results.append({'osf_id': osf_id, 'title': paper['title'][:80], 'decision': 'reject', 'reason': reason, 'category': result.get('category')})
            rejected += 1
            print(f"  -> REJECT: {reason[:80]}", file=sys.stderr)
            checkpoint_ids.add(osf_id)
            save_checkpoint(checkpoint_ids)
            time.sleep(3)
            continue

        category = result.get('category', 'Other Clinical')
        print(f"  -> ACCEPT: {reason[:80]}", file=sys.stderr)

        if dry_run:
            results.append({'osf_id': osf_id, 'title': paper['title'][:80], 'decision': 'accept', 'reason': reason, 'category': category, 'curated': False})
            accepted += 1
            time.sleep(8)
            continue

        number = base_number + accepted
        date_posted = paper.get('date_created', paper.get('date_posted', '2026-01-01'))[:10]
        authors = fetch_authors(osf_id)
        if not authors:
            authors = "Unknown"
        entry = insert_paper_into_json(paper, number, authors, category, result, date_posted, osf_id)
        accepted_papers.append(entry)
        results.append({
            'osf_id': osf_id, 'title': paper['title'][:80],
            'decision': 'accept', 'reason': reason, 'category': category,
            'number': number, 'authors': authors, 'curated': True
        })
        accepted += 1
        print(f"  -> CURATED: #{number} — {paper['title'][:50]}...", file=sys.stderr)
        checkpoint_ids.add(osf_id)
        save_checkpoint(checkpoint_ids)
        time.sleep(3)

    output = {
        'evaluated': accepted + rejected + errors, 'accepted': accepted, 'rejected': rejected, 'errors': errors,
        'skipped': skipped,
        'deferred': max(0, len(candidates) - accepted - rejected - errors - skipped),
        'results': results
    }
    with open(RESULTS_PATH, 'w') as f:
        json.dump(output, f, indent=2)
        f.write('\n')

    if not dry_run:
        discard_count = 0
        for r in results:
            if r['decision'] in ('reject', 'error'):
                signal = next((c.get('signal_score', 0) for c in candidates if c['osf_id'] == r['osf_id']), 0)
                append_discard_log(r['osf_id'], signal, r['title'], r['reason'])
                discard_count += 1
        print(f"Logged {discard_count} discards", file=sys.stderr)
        if accepted > 0:
            generate_og_pages()
        seen_added = update_seen_ids()
        # Clear checkpoint after successful completion
        remaining = [c for c in candidates if c['osf_id'] not in skip_ids and c['osf_id'] not in checkpoint_ids]
        if not remaining:
            clear_checkpoint()
            print("Checkpoint cleared: all candidates processed", file=sys.stderr)
        for f in glob.glob(os.path.join(INBOX_DIR, '*.md')):
            if os.path.basename(f) != 'TEMPLATE.md':
                try:
                    os.remove(f)
                except:
                    pass

    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
