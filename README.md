# PsyArXiv Therapist Hub

Curated psychology preprints for clinical practice. Papers are sourced from [PsyArXiv](https://osf.io/preprints/psyarxiv/) and selected for clinical relevance to therapists working in adult mental health.

## Categories

- Couples Therapy & Sexology
- Neurodivergence (ADHD, Autism)
- Mood Disorders (Depression, Anxiety, OCD)
- Trauma & Stressor-Related Disorders
- Personality Disorders
- Therapeutic Modalities (CBT, DBT, ACT, EMDR, Psychodynamic, Schema Therapy)
- Psychopathology & Clinical Assessment
- Eating Disorders
- Somatic & Functional Disorders
- Suicidality & Self-Harm
- Psychosis & Schizophrenia
- Addiction & Substance Use

## About

This site is automatically updated with newly curated papers from the PsyArXiv hourly pipeline. Each paper includes a clinical summary, clinical insight, and relevance tags for practitioners.

## Data repair

Run `node scripts/repair-papers.mjs` to audit missing PsyArXiv links and author metadata against the official OSF API.

Run `node scripts/repair-papers.mjs --write` to write back only confident matches to `data/papers.json`.

The audit report is saved to `data/papers-repair-report.json`.
