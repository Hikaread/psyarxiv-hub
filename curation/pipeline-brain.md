# Pipeline Brain

## Current State
- Papers: 765
- Seen IDs: 2933
- Last run: 2026-07-31 18:00

## Script Locations (CRITICAL)
- **evaluate-candidates.py**: `/home/z/my-project/psyarxiv-hub/scripts/evaluate-candidates.py` (git-tracked, survives wipes)
- **generate-og-pages.mjs**: `/home/z/my-project/psyarxiv-hub/scripts/generate-og-pages.mjs` (git-tracked)
- **discover-papers.mjs**: `/home/z/my-project/psyarxiv-hub/scripts/discover-papers.mjs` (git-tracked)
- **screen-papers.mjs**: `/home/z/my-project/psyarxiv-hub/scripts/screen-papers.mjs` (git-tracked)
- **screened-papers.json**: `/home/z/my-project/scripts/screened-papers.json` (volatile - wiped sometimes)
- **discovered-papers.json**: `/home/z/my-project/scripts/discovered-papers.json` (volatile)
- `/home/z/my-project/scripts/` is volatile and may be wiped between sessions
- `/tmp/my-project/scripts/` is a backup source but also volatile
- **Always use repo paths for .mjs/.py scripts** (git-tracked, survives wipes)

## Known Gotchas
- evaluate-candidates.py timeouts: run inline, 2-3 min batches, check count after each
- Background nohup produces empty logs — always use inline `python3 -B -u` directly
- pyc cache: always use `-B` flag to avoid stale bytecode
- docx support: fetch_fulltext() now accepts source in ('pdf','docx') — verified working
- Dupes: backfill can re-insert papers. Dedup by osf_id after each run if count jumps.
- screened-papers.json accumulates old candidates across runs — script handles via existing_osf_ids skip
- OG pages: check missing after eval, run generate-og-pages.mjs if count != paper count
- git filemode changes: paper/*.html flip between 644/755 on stash/pop — lots of noise in commits
- **Scripts in /home/z/my-project/scripts/ get wiped. Use repo copies.**
- **pipeline-brain.md now lives in the repo at curation/pipeline-brain.md** — survives wipes via git
- **Phantom entries**: timeouts during insert_paper_into_json can write partial entries (no osf_id). Dedup catches these.

## Patterns
- Backfill mode: discoverer jumps back ~57-225d, pulls large batches
- Accept rate: ~10-20% of screened candidates
- Common rejection reasons: basic cognitive psych, educational assessment, psycholinguistics, methodology papers
- Typical eval: ~2-5 min per paper (fetch + LLM call)

## Shifts Log
| Date | What | Why |
|------|------|-----|
| 07-22 | Fixed docx fetch | OSF accepts .docx, eval was rejecting as fetch_failed |
| 07-23 | Dedup papers.json | Backfill created 49 duplicate entries |
| 07-23 | Added pipeline-brain.md | Persistent context across cron sessions |
| 07-23 | Updated cron prompt | ADHD-style output rules, brain file reference |
| 07-23 | filemode noise | 631 files changed but only +74 insertions (mode changes) |
| 07-24 | Paragraph breaks in prompt | LLM prompt instructs \\n\\n for summary/clinical_insight |
| 07-25 | Strengthened bold in prompt | MANDATORY: 6+ bold items per summary, 2+ in clinical_insight |
| 07-25 | Updated Discord output format | Each paper on own line, full title |
| 07-30 | Checkpoint + reduced batch | eval-checkpoint.json persists progress across timeouts; --max=5 default; sleeps 3-5s |