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

Optional metadata:

- `published`

## Recommended workflow

1. Put raw discovered papers into `curation/inbox/`.
2. Fill in the summary, clinical insight, and relevant-for sections.
3. Run `node scripts/import-curation-notes.mjs --write`.
4. Review the diff in `data/papers.json`.
5. Push the repo.
