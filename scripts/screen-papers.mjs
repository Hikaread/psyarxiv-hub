#!/usr/bin/env node

/**
 * Screen discovered papers against existing PsyHub data and exclusion rules.
 * Outputs candidates that need full evaluation.
 */

import { readFileSync, writeFileSync } from 'fs';

const DISCOVERED = JSON.parse(readFileSync('/home/z/my-project/scripts/discovered-papers.json', 'utf8'));
const EXISTING = JSON.parse(readFileSync('/home/z/my-project/psyarxiv-hub/data/papers.json', 'utf8'));

// Build existing OSF ID set (compact)
const existingOsfIds = new Set();
const existingTitles = new Set();
for (const p of EXISTING) {
  if (p.osf_id) existingOsfIds.add(p.osf_id.replace(/_v\d+$/i, '').toLowerCase());
  if (p.link) {
    const m = p.link.match(/osf\.io\/(?:preprints\/psyarxiv\/)?([a-z0-9]+)/i);
    if (m) existingOsfIds.add(m[1].toLowerCase());
  }
  // Normalize title for comparison
  const nt = (p.title || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (nt.length > 10) existingTitles.add(nt);
}

// Exclusion keywords (papers with these in title+abstract are likely not clinically relevant)
const HARD_EXCLUDE = [
  'psychedelic', 'lsd', 'psilocybin', 'mdma', 'ketamine', 'ayahuasca', 'dmt',
  'mescaline', 'ibogaine', 'cannabis-assisted', 'drug-assisted',
  'animal model', 'rat model', 'mouse model', 'rodent model',
  'registered report protocol', 'this is a protocol',
  'editorial', 'commentary on', 'reply to', 'correction to',
  'conference poster', 'slide deck'
];

// Clinical relevance keywords for initial positive signal
const CLINICAL_SIGNAL = [
  'psychotherapy', 'therapy', 'therapeutic', 'treatment', 'intervention',
  'cbt', 'cognitive behavioral', 'cognitive behavioural', 'dbt', 'dialectical behavior',
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
  'attachment', 'couple', 'couple therapy', 'intimacy', 'sexual dysfunction',
  'sexology', 'sex therapist', 'vaginismus', 'dyspareunia', 'sexual satisfaction', 'libido',
  'adhd', 'autism', 'autistic', 'neurodivergent', 'neurodivergence', 'neurodevelopmental',
  'transdiagnostic', 'comorbidity', 'differential diagnosis',
  'therapeutic alliance', 'rupture', 'dropout', 'nonresponse',
  'emotion regulation', 'cognitive reappraisal', 'exposure',
  'mindfulness', 'self-compassion', 'inner critic',
  'case formulation', 'clinical interview', 'psychopathology',
  'wellbeing', 'well-being', 'mental health', 'psychological distress',
  'resilience', 'coping', 'stress', 'burnout',
  'grief', 'bereavement', 'palliative', 'end-of-life',
  'parenting', 'caregiver', 'family therapy', 'systemic',
  'perfectionism', 'body image', 'weight concern',
  'sleep', 'insomnia', 'nightmare',
  'chronic pain', 'fibromyalgia', 'medically unexplained',
  'identity', 'gender', 'lgbt', 'minority stress',
  'stigma', 'discrimination', 'cultural', 'multicultural',
  'group therapy', 'interpersonal', 'relationship',
  'motivational interviewing', 'behavior change', 'behaviour change',
  'recovery', 'relapse', 'remission', 'outcome',
  'screening', 'detection', 'early intervention',
  'trauma-informed', 'trauma focused', 'trauma-focused',
  'working memory', 'executive function',
  'rumination', 'worry', 'intrusive thought',
  'social anxiety', 'phobia', 'panic', 'agoraphobia',
  'gaming disorder', 'internet addiction', 'problematic use',
  'hoarding', 'body dysmorphic',
  'dissociative', 'depersonalization', 'derealization',
  'bipolar', 'mania', 'hypomania',
  'adjustment disorder', 'acute stress',
  'older adult', 'aging', 'dementia',
  'refugee', 'asylum', 'migration',
  'peer support', 'lived experience', 'service user',
  'formulation', 'case conceptualization',
  'mentalization-based', 'mbt'
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

// Filter
const alreadyExisting = [];
const hardExcluded = [];
const lowSignal = [];
const candidates = [];

for (const paper of DISCOVERED) {
  const compactId = paper.osf_id.replace(/_v\d+$/i, '');
  
  // Check if already in PsyHub
  if (existingOsfIds.has(compactId.toLowerCase())) {
    alreadyExisting.push(paper);
    continue;
  }
  
  // Also check title match
  const nt = paper.title.toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
  let titleMatch = false;
  for (const et of existingTitles) {
    // Simple overlap check
    const tTokens = new Set(nt.split(' '));
    const eTokens = new Set(et.split(' '));
    let overlap = 0;
    for (const t of tTokens) { if (eTokens.has(t) && t.length > 3) overlap++; }
    if (overlap / Math.max(tTokens.size, eTokens.size) > 0.85) {
      titleMatch = true;
      break;
    }
  }
  if (titleMatch) {
    alreadyExisting.push(paper);
    continue;
  }
  
  const fullText = `${paper.title} ${paper.description}`;
  
  // Hard exclusions
  if (hasHardExclude(fullText)) {
    hardExcluded.push({ ...paper, exclude_reason: 'hard_exclude' });
    continue;
  }
  
  // Score clinical signal
  const signal = clinicalSignalScore(fullText);
  if (signal < 1) {
    lowSignal.push({ ...paper, signal_score: signal });
    continue;
  }
  
  candidates.push({ ...paper, signal_score: signal });
}

// Sort candidates by signal score descending
candidates.sort((a, b) => b.signal_score - a.signal_score);

const report = {
  discovered: DISCOVERED.length,
  alreadyExisting: alreadyExisting.length,
  hardExcluded: hardExcluded.length,
  lowSignal: lowSignal.length,
  candidates: candidates.length,
  candidates_list: candidates.map(c => ({
    osf_id: c.osf_id,
    title: c.title.substring(0, 120),
    date_created: c.date_created,
    signal_score: c.signal_score,
    description_preview: c.description.substring(0, 200)
  }))
};

writeFileSync('/home/z/my-project/scripts/screened-papers.json', JSON.stringify(candidates, null, 2) + '\n', 'utf8');
writeFileSync('/home/z/my-project/scripts/screening-brief.json', JSON.stringify(report, null, 2) + '\n', 'utf8');
console.log(JSON.stringify(report, null, 2));