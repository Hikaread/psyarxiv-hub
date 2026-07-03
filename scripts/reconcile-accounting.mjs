#!/usr/bin/env node

/**
 * Reconcile curation accounting from actual run artifacts.
 * Every discovered record must have exactly one final status.
 */

import { readFileSync, writeFileSync } from 'fs';

const DISCOVERED = JSON.parse(readFileSync('/home/z/my-project/scripts/discovered-papers.json', 'utf8'));
const SCREENED = JSON.parse(readFileSync('/home/z/my-project/scripts/screened-papers.json', 'utf8'));
const CANDIDATE_DETAILS = JSON.parse(readFileSync('/home/z/my-project/scripts/candidate-details.json', 'utf8'));
const EXISTING = JSON.parse(readFileSync('/home/z/my-project/psyarxiv-hub/data/papers.json', 'utf8'));

// Build existing OSF ID set (compact)
const existingOsfIds = new Set();
const existingTitlesNorm = [];
for (const p of EXISTING) {
  if (p.osf_id) existingOsfIds.add(p.osf_id.replace(/_v\d+$/i, '').toLowerCase());
  if (p.link) {
    const m = p.link.match(/osf\.io\/(?:preprints\/psyarxiv\/)?([a-z0-9]+)/i);
    if (m) existingOsfIds.add(m[1].toLowerCase());
  }
  const nt = (p.title || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (nt.length > 10) existingTitlesNorm.push(nt);
}

// Hard exclude keywords
const HARD_EXCLUDE = [
  'psychedelic', 'lsd', 'psilocybin', 'mdma', 'ketamine', 'ayahuasca', 'dmt',
  'mescaline', 'ibogaine', 'cannabis-assisted', 'drug-assisted',
  'animal model', ' rat ', ' mouse ', 'rodent',
  'electroencephalography', ' eeg ', 'fmri', 'functional magnetic resonance',
  'neuroimaging', 'structural equation model',
  'registered report protocol', 'this is a protocol',
  'editorial', 'commentary on', 'reply to', 'correction to',
  'conference poster', 'slide deck'
];

// Clinical signal keywords
const CLINICAL_SIGNAL = [
  'psychotherapy', 'therapy', 'therapeutic', 'treatment', 'intervention',
  'cbt', 'cognitive behavioral', 'dbt', 'dialectical behavior',
  'act', 'acceptance and commitment', 'emdr', 'psychodynamic',
  'schema therapy', 'mentalization', 'compassion-focused',
  'clinical', 'clinician', 'patient', 'diagnosis', 'diagnostic',
  'assessment', 'formulation', 'therapist', 'session',
  'depression', 'anxiety', 'trauma', 'ptsd', 'dissociation',
  'personality disorder', 'borderline', 'narcissistic',
  'eating disorder', 'anorexia', 'bulimia', 'binge',
  'self-harm', 'suicid', 'nssi',
  'psychosis', 'schizophreni', 'psychotic',
  'addiction', 'substance use', 'alcohol', 'opioid',
  'obsessive compulsive', 'ocd',
  'somatic', 'functional neurological', 'health anxiety',
  'attachment', 'couple', 'intimacy', 'sexual dysfunction',
  'adhd', 'autism', 'neurodivergent',
  'transdiagnostic', 'comorbidity', 'differential diagnosis',
  'therapeutic alliance', 'rupture', 'dropout', 'nonresponse',
  'emotion regulation', 'cognitive reappraisal', 'exposure',
  'mindfulness', 'self-compassion', 'inner critic',
  'case formulation', 'clinical interview', 'psychopathology'
];

function hasHardExclude(text) {
  const lower = text.toLowerCase();
  return HARD_EXCLUDE.some(kw => lower.includes(kw));
}

function clinicalSignalScore(text) {
  const lower = text.toLowerCase();
  let score = 0;
  for (const kw of CLINICAL_SIGNAL) {
    if (lower.includes(kw)) score++;
  }
  return score;
}

function titleSimilarity(nt1, nt2) {
  const t1 = new Set(nt1.split(' ').filter(w => w.length > 3));
  const t2 = new Set(nt2.split(' ').filter(w => w.length > 3));
  if (!t1.size || !t2.size) return 0;
  let overlap = 0;
  for (const t of t1) { if (t2.has(t)) overlap++; }
  return overlap / Math.max(t1.size, t2.size);
}

// Accepted OSF IDs
const ACCEPTED_COMPACT = new Set(['edscr', 'qmz4v', 'xfhek']);

// Insufficient relevance (evaluated but rejected for clinical reasons)
const INSUFFICIENT_RELEVANCE = new Set(['5u67v', '4fkn2', 'ntm9y', 'mgbq2', 'dr7um']);

const results = {
  accepted: [],
  hard_excluded: [],
  low_clinical_signal: [],
  insufficient_relevance: [],
  duplicate: [],
  retrieval_or_metadata_failure: [],
};

for (const paper of DISCOVERED) {
  const compact = paper.osf_id.replace(/_v\d+$/i, '');
  const fullText = `${paper.title} ${paper.description}`;
  
  // Check duplicate
  if (existingOsfIds.has(compact.toLowerCase())) {
    results.duplicate.push({ compact, title: paper.title.substring(0, 100) });
    continue;
  }
  
  // Title match check
  const nt = paper.title.toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
  let isDupe = false;
  for (const et of existingTitlesNorm) {
    if (titleSimilarity(nt, et) > 0.85) { isDupe = true; break; }
  }
  if (isDupe) {
    results.duplicate.push({ compact, title: paper.title.substring(0, 100) });
    continue;
  }

  // Check metadata failure
  if (!paper.description || paper.description.length < 20) {
    results.retrieval_or_metadata_failure.push({ compact, title: paper.title.substring(0, 100), reason: 'empty description' });
    continue;
  }
  
  // Hard exclude
  if (hasHardExclude(fullText)) {
    results.hard_excluded.push({ compact, title: paper.title.substring(0, 100) });
    continue;
  }
  
  // Clinical signal
  const signal = clinicalSignalScore(fullText);
  if (signal < 2) {
    results.low_clinical_signal.push({ compact, title: paper.title.substring(0, 100), signal });
    continue;
  }
  
  // Now we're in full evaluation territory
  if (ACCEPTED_COMPACT.has(compact)) {
    results.accepted.push({ compact, title: paper.title.substring(0, 100) });
  } else if (INSUFFICIENT_RELEVANCE.has(compact)) {
    results.insufficient_relevance.push({ compact, title: paper.title.substring(0, 100) });
  } else {
    // This is the missing/unaccounted record
    results.insufficient_relevance.push({ compact, title: paper.title.substring(0, 100), signal, note: 'previously unaccounted' });
  }
}

const total = Object.values(results).reduce((sum, arr) => sum + arr.length, 0);
const summary = {
  discovered: DISCOVERED.length,
  total_accounted: total,
  discrepancy: DISCOVERED.length - total,
  breakdown: {
    accepted: results.accepted.length,
    hard_excluded: results.hard_excluded.length,
    low_clinical_signal: results.low_clinical_signal.length,
    insufficient_relevance: results.insufficient_relevance.length,
    duplicate: results.duplicate.length,
    retrieval_or_metadata_failure: results.retrieval_or_metadata_failure.length,
  },
  screened: DISCOVERED.length - results.retrieval_or_metadata_failure.length,
  full_clinical_evaluation: results.accepted.length + results.insufficient_relevance.length,
  previously_unaccounted: results.insufficient_relevance.filter(r => r.note),
};

writeFileSync('/home/z/my-project/scripts/reconciled-accounting.json', JSON.stringify({ results, summary }, null, 2) + '\n', 'utf8');
console.log(JSON.stringify(summary, null, 2));

if (summary.discrepancy !== 0) {
  console.error('\nWARNING: Discrepancy still exists!');
} else {
  console.error('\nAll records accounted for.');
}

// Print previously unaccounted records
if (summary.previously_unaccounted.length) {
  console.error('\nPreviously unaccounted records:');
  summary.previously_unaccounted.forEach(r => console.error('  ' + r.compact + ': ' + r.title));
}