---
Task ID: 2
Agent: Main agent
Task: Add markdown + LaTeX rendering to paper summaries on the website

Work Log:
- Added renderMd() function to app.js: parses **bold**, *italic*, - bullet lists, newlines→<br>, $...$ LaTeX
- Added renderKaTeXInContainer() for post-DOM KaTeX rendering
- Added KaTeX v0.16.11 via CDN (deferred load) to index.html
- Updated card view: replaced esc(truncate(...)) with renderMd(), added CSS line-clamp:3 for visual truncation
- Updated modal view: all 3 text fields (summary, clinical_insight, relevant_for) now use renderMd()
- XSS protection maintained: HTML escaped first, then whitelist sanitization (b, em, strong, br, ul, ol, li, p, span, sub, sup)
- Added .md-content CSS: styled bold/italic/lists/KaTeX for light/dark/purple themes
- Updated 10 most recent papers (492-501) with markdown formatting in papers.json

Stage Summary:
- Website now renders markdown in summaries: bold for key data, italic for caveats, bullet lists for relevant_for, LaTeX for statistical notation
- Cards show 3-line clamped formatted summaries; modals show full formatted content
- Future curation notes should use markdown formatting from day one
- Pushed to main, will deploy via GitHub Actions
---
Task ID: 1
Agent: main
Task: PsyArXiv curation pipeline (Job 252389, 2026-07-07)

Work Log:
- Step 1: Pulled latest from git (already up to date)
- Step 2: Discovered 42 unseen papers (21 days scanned back to 2026-06-16)
- Step 3: Screened 42 papers → 41 candidates (1 hard-excluded)
- Step 4: Two-pass evaluation → 9 accepted, 32 discarded
- Step 5: Fetched full PDF text for 7 papers; 2 papers (s4vzr, my6qw) had no PDF, used descriptions
- Step 6: Appended 32 discard entries to discarded-log.md
- Step 7: Created 9 curation notes in inbox (531-539)
- Step 8: Imported notes into papers.json (511→520 papers)
- Step 9: Incrementally updated seen-compact-ids.json (987→1028 IDs)
- Step 10: Verified all entries — fixed 3 papers with comma-separated categories
- Step 11: QA check — all failures were false positives (wrong path)
- Step 12: Committed and pushed to origin/main

Stage Summary:
- Discovered: 42, Screened: 41, Accepted: 9, Discarded: 33 (32 + 1 hard-excluded)
- Papers: 531 (Depressometer/MDD psychodynamic dataset), 532 (empathic disequilibrium/mindfulness), 533 (meditation systematic review), 534 (autism accessibility/wellbeing), 535 (ACT-RFT critical reanalysis), 536 (wise empathy/Instagram), 537 (listener engagement/emotional dynamics), 538 (social media evaluations/wellbeing), 539 (DESI-18 felt safety instrument)
- Total papers in hub: 520
- Commit: 00c2153 pushed to main
---
Task ID: 3
Agent: main
Task: PsyArXiv curation pipeline (Job 257322, 2026-07-08)

Work Log:
- Step 1: Pulled latest (already up to date)
- Step 2: Discovered 47 unseen papers (28 days scanned back to 2026-06-10)
- Step 3: Screened → 43 candidates (2 hard-excluded, 2 low-signal)
- Step 4: Two-pass evaluation → 12 accepted, 31 discarded
- Step 5: Fetched PDF text for 7 papers; 5 papers had no PDF, used descriptions/abstracts
- Step 6: Appended 32 discard entries to discarded-log.md
- Step 7: Created 12 curation notes in inbox (590-601)
- Step 8: Imported notes into papers.json (570→582 papers)
- Step 9: Incrementally updated seen-compact-ids.json (1246→1293 IDs)
- Step 10: Verified all 12 new entries — no errors
- Step 11: QA check — all failures false positives (wrong path)
- Step 12: Committed and pushed to origin/main

Stage Summary:
- Discovered: 47, Screened: 43, Accepted: 12, Discarded: 35 (31 + 2 hard-excluded + 2 low-signal)
- Papers: 590 (NLP verbal fluency/psychosis differential diagnosis), 591 (emotion coherence/depression outcomes), 592 (SEQ 3.0 Japanese/autism sensory), 593 (MAPS V2 brief parenting/IRT), 594 (PEP treatment/depression+anxiety), 595 (peer support/psychosis employment protocol), 596 (men + AI mental health/theoretical), 597 (group prevention PA+psychoeducation), 598 (men's MH service experiences/qualitative), 599 (families of self-harming youth/systematic review), 600 (EPQ-RN DIF/gender bias), 601 (LGBTQ+ acceptance/media)
- Total papers in hub: 582
- Commit: 5fd6dc8 pushed to main
---
Task ID: 1
Agent: main
Task: Run PsyArXiv curation pipeline Job 257322

Work Log:
- Pulled latest from main, cleaned up old manual run3 artifacts (8 deleted files)
- Discovered 42 unseen papers across 30 days (discover-papers.mjs)
- Screened to 36 candidates (screen-papers.mjs), 1 hard-excluded, 5 low-signal
- First-pass evaluation of screening-brief.json: accepted 10, then excluded qcm7n_v1 (child sample)
- Second-pass: read full descriptions for 9 accepted papers from screened-papers.json
- Fetched PDF full texts for 8/9 papers (qrpj6 abstract-only) via fetch-paper-fulltext.py
- Fetched author names via OSF preprints API with embed=contributors
- Created discard log with 27 entries (curation/discarded-log.md)
- Created 9 curation notes (602-610) in curation/inbox/
- Fixed missing frontmatter fields (number, date_posted, source_date)
- Imported via import-curation-notes.mjs --write: 9 created, 50 updated
- Incrementally updated seen-compact-ids.json: 1293 → 1329 (36 new IDs)
- Verified all 9 new entries: versioned OSF IDs, valid categories, correct links
- QA: only false positives (wrong working directory)
- Committed and pushed to GitHub

Stage Summary:
- Discovered: 42, Screened: 36, Accepted: 9, Discarded: 27
- Papers 602-610 added across categories: Neurodivergence (2), Trauma & Stressor-Related (1), Therapeutic Modalities (1), Couples Therapy & Sexology (1), Psychopathology & Assessment (3), Anxiety & OCD (1)
- Commit: d728264, pushed to main
