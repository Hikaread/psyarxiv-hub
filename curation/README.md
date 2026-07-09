# Curation Inbox

This folder is the handoff layer between paper discovery and website publishing.

Instead of asking an agent to search from scratch, add one Markdown file per paper into `curation/inbox/`, then run:

`node scripts/import-curation-notes.mjs --write`

The importer will:

- validate required fields
- build the OSF/PsyArXiv link from `osf_id`
- update an existing paper when `number` or `osf_id` already exists
- append a new paper when it does not exist yet

## File format

Use `curation/inbox/TEMPLATE.md` as the template.

Required metadata:

- `number`
- `title`
- `authors`
- `osf_id`
- `date_posted`
- `source_date`
- `categories`

Required sections:

- `## Summary`
- `## Clinical Insight`
- `## Relevant For`

Recommended sections:

- `## Methodology Note` — honest methodology assessment based on the full text. No length limits — write as much or as little as the paper warrants. Bold key terms with `**`. Use `__Sub-labels__` (e.g. `__Strengths__:`, `__Limitation__:`) for structure. See the 7-dimension framework below.

Optional metadata:

- `published`

## Recommended workflow

1. Put raw discovered papers into `curation/inbox/`.
2. Fill in the summary, clinical insight, methodology note, and relevant-for sections.
3. Run `node scripts/import-curation-notes.mjs --write`.
4. Review the diff in `data/papers.json`.
5. Push the repo.

## Methodology Note — 7-Dimension Framework

First identify the **paper type**, then evaluate applicable dimensions:

| Paper Type | Skip Dimensions |
|-----------|----------------|
| `quantitative_experimental` | None (all 7 apply) |
| `meta_analysis` | 1, 5, 7 |
| `qualitative` | 1, 3, 4 |
| `psychometric/validation` | 1, 3 |
| `mixed_methods` | Apply dims per section |
| `other` | Rate all 7, expect many unevaluable |

**Dimensions:**

1. **Sample Size & Power** — a priori power analysis? explicit effect size? or underpowered / no justification?
2. **Preregistration** — linked registration before data collection? deviations justified?
3. **Effect Size Reporting** — effect sizes with CIs for all primary tests? or p-values only?
4. **Statistical Rigor** — multiple comparison corrections? assumption checks? or uncorrected tests, p-hacking signals?
5. **Measurement Validity** — established instruments with psychometric properties + in-sample reliability? or ad-hoc measures?
6. **Open Science Practices** — data/materials/code publicly linked? or nothing shared?
7. **Participant Transparency** — recruitment, inclusion/exclusion, demographics, attrition all reported? or vague?

Write the note as plain-language prose (not a scored checklist). Use `__Strengths__:` and `__Limitation__:` sub-labels where helpful. Be honest — if a paper has 5 strengths, say so. If it has none, say so.
