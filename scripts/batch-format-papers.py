#!/usr/bin/env python3
"""Batch formatting script for papers.json: add **bold** and bullet lists."""

import json
import re
import sys

VALID_CATEGORIES = {
    'Anxiety & OCD', 'Couples Therapy & Sexology', 'Neurodivergence', 'Mood Disorders',
    'Trauma & Stressor-Related', 'Personality Disorders', 'Therapeutic Modalities',
    'Psychopathology & Assessment', 'Eating Disorders', 'Somatic & Functional',
    'Suicidality & Self-Harm', 'Psychosis & Schizophrenia', 'Addiction & Substance Use',
    'Obsessive-Compulsive', 'Other Clinical'
}

# --- Bold term lists ---
MEASURES = sorted([
    'ADIS', 'AUDIT', 'BAS', 'BBS', 'BDI', 'BDI-II', 'BES', 'BFI', 'BMI', 'BPNS',
    'BSCS', 'BPRS', 'CAPS', 'CAR', 'CARS', 'CASI', 'CES-D', 'CFQ', 'CGI',
    'CLPS', 'CMS', 'COPE', 'CQ', 'CRS', 'CSI', 'CTQ', 'CWS', 'DAS', 'DASS',
    'DASS-21', 'DEQ', 'DES', 'DES-II', 'DLQI', 'DMQ', 'DRS', 'DERS', 'DSM',
    'DSM-5', 'DTS', 'EAT', 'EDE', 'EDE-Q', 'EEG', 'EMA', 'ERS', 'ESM', 'ETI',
    'FAD', 'FAS', 'FCR', 'FES-I', 'FFMQ', 'FNE', 'GAD-7', 'GAD-7', 'GRS',
    'HAM-A', 'HAM-D', 'HAMD', 'HRSD', 'HRV', 'IAS', 'ICD', 'ICD-10', 'ICD-11',
    'IES', 'IES-R', 'IIP', 'IPT', 'IRS', 'ISI', 'LAS', 'LEAS', 'LSAS', 'MAAS',
    'MADRS', 'MCQ', 'MDI', 'MEQ', 'MINI', 'MIND', 'MLR', 'MMPI', 'MOCI',
    'MPQ', 'MRNI', 'NAI', 'NCS', 'NEO', 'NEO-FFI', 'NFI', 'NPSI', 'OCI-R',
    'OQ-45', 'OPD', 'OPD-SQ', 'PADS', 'PANAS', 'PCL', 'PCL-5', 'PDQ', 'PHQ',
    'PHQ-9', 'PRFQ', 'PSQI', 'PSS', 'QoL', 'RAI', 'RAS', 'RSES', 'RSR',
    'SAD', 'SAS', 'SCID', 'SCID-5', 'SCL', 'SCL-90', 'SCL-90-R', 'SDS',
    'SES', 'SHAPS', 'SII', 'SNAP', 'SPIN', 'STAI', 'STAI-T', 'STAI-S',
    'STAXI', 'STOMP', 'SWLS', 'TCI', 'TEIQue', 'TMS', 'TRF', 'TUQ',
    'UP-CoF', 'VIA', 'WAIS', 'WAI', 'WEMWBS', 'WHO', 'WHO-5', 'WOI', 'Y-BOCS',
    'ZAN-BPD', 'ZKPQ',
], key=len, reverse=True)

THERAPIES = sorted([
    'acceptance and commitment therapy', 'ACT', 'assertiveness training',
    'behavioral activation', 'biofeedback', 'body-focused repetitive behavior therapy',
    'brief dynamic psychotherapy', 'CBT', 'cognitive behavioral therapy',
    'cognitive processing therapy', 'compassion-focused therapy', 'CFT',
    'contingency management', 'couples therapy', 'DBT', 'dialectical behavior therapy',
    'EMDR', 'emotion-focused therapy', 'EFT', 'exposure and response prevention',
    'ERP', 'exposure therapy', 'family therapy', 'GDT', 'gestalt therapy',
    'group therapy', 'habit reversal training', 'HRT', 'humanistic therapy',
    'imaginal exposure', 'interpersonal psychotherapy', 'IPT',
    'mentalization-based therapy', 'MBT', 'MBCT', 'MBSR', 'mindfulness',
    'mindfulness-based cognitive therapy', 'mindfulness-based stress reduction',
    'motivational interviewing', 'MI', 'narrative therapy', 'psychodynamic therapy',
    'psychoeducation', 'rational emotive behavior therapy', 'REBT',
    'schema therapy', 'solution-focused therapy', 'SFT', 'supportive-expressive',
    'systemic therapy', 'third-wave CBT', 'transference-focused psychotherapy',
    'trauma-focused CBT', 'TF-CBT',
], key=len, reverse=True)

DISORDERS = sorted([
    'ADHD', 'adjustment disorder', 'agoraphobia', 'alcohol use disorder',
    'anorexia nervosa', 'antisocial personality disorder', 'anxiety disorder',
    'autism spectrum disorder', 'ASD', 'binge eating disorder', 'BED',
    'bipolar disorder', 'body dysmorphic disorder', 'BDD', 'borderline personality disorder',
    'BPD', 'bulimia nervosa', 'claustrophobia', 'conduct disorder', 'delusional disorder',
    'dissociative identity disorder', 'DID', 'dyslexia', 'eating disorder',
    'generalized anxiety disorder', 'GAD', 'gender dysphoria', 'hoarding disorder',
    'intermittent explosive disorder', 'major depressive disorder', 'MDD',
    'narcissistic personality disorder', 'NPD', 'obsessive-compulsive disorder',
    'OCD', 'oppositional defiant disorder', 'ODD', 'panic disorder',
    'persistent depressive disorder', 'personality disorder', 'phobia',
    'post-traumatic stress disorder', 'PTSD', 'psychosis', 'schizophrenia',
    'separation anxiety disorder', 'social anxiety disorder', 'SAD',
    'somatization disorder', 'specific phobia', 'substance use disorder',
    'somatic symptom disorder', 'trichotillomania', 'avoidant personality disorder',
    'dependent personality disorder', 'histrionic personality disorder',
    'paranoid personality disorder', 'schizoaffective disorder',
    'schizotypal personality disorder', 'psychotic disorder',
], key=len, reverse=True)

STUDY_DESIGNS = sorted([
    'randomized controlled trial', 'RCT', 'preregistered study',
    'systematic review', 'meta-analysis', 'longitudinal study',
    'cross-sectional study', 'cohort study', 'case-control study',
    'ecological momentary assessment', 'EMA', 'experience sampling',
    'mixed-methods study', 'qualitative study', 'quantitative study',
    'multivariate analysis', 'multiverse analysis', 'network meta-analysis',
    'scoping review', 'rapid review', 'narrative review', 'umbrella review',
    'structural equation model', 'SEM', 'latent growth model',
    'multilevel model', 'mediation analysis', 'moderation analysis',
    'bayesian analysis', 'propensity score', 'factor analysis',
], key=len, reverse=True)


def bold_stats(text):
    """Bold statistical notations: N=, n=, p<, p=, d=, r=, β=, F(, t(, OR=, CI=, η²=, etc."""
    # Sample sizes
    text = re.sub(r'\b(N|n)\s*=\s*(\d[\d,]*)\b', r'**\1 = \2**', text)
    # p-values
    text = re.sub(r'\b(p)\s*([<>=])\s*([.\d]+)', r'**\1\2\3**', text)
    # Effect sizes
    for sym in ['d', 'r', 'g', 'f', 'β', 'η', 'b', 'OR', 'IRR', 'RR', 'HR', 'Cohen\'s d']:
        text = re.sub(r'(?<!\w)(' + re.escape(sym) + r')\s*=\s*([-\d.]+(?:\s*[-–]\s*[-\d.]+)?)', r'**\1 = \2**', text)
    # F and t statistics with parentheses
    text = re.sub(r'\b([Ft])\s*\(([^)]+)\)\s*=\s*([.\d]+)', r'**\1(\2) = \3**', text)
    # Percentages like (72%)
    text = re.sub(r'\((\d+(?:\.\d+)?%)\)', r'(**\1**)', text)
    # Confidence intervals
    text = re.sub(r'(\d+(?:\.\d+)?)\s*%\s*CI', r'**\1% CI**', text)
    # eta-squared / partial eta-squared
    text = re.sub(r'(?:partial )?(eta[\s-]*squared|η²?)\s*=\s*([.\d]+)', r'**\1 = \2**', text)
    # Odds ratios
    text = re.sub(r'\bAOR\s*=\s*([.\d]+)', r'**AOR = \1**', text)
    return text


def bold_terms(text, term_list):
    """Bold occurrences of specific terms."""
    for term in term_list:
        if len(term) < 3:
            continue
        if re.match(r'^[A-Z]+$', term) and len(term) <= 4:
            pattern = r'(?<![A-Za-z])' + re.escape(term) + r'(?![A-Za-z])'
        else:
            pattern = r'(?<!\w)' + re.escape(term) + r'(?!\w)'
        text = re.sub(pattern, lambda m: f'**{m.group()}**', text, flags=re.IGNORECASE)
    return text


def fix_relevant_for(rf):
    """Convert relevant_for to bullet list format."""
    if not rf:
        return '- No specific audience listed'
    rf = rf.strip()
    if rf.startswith('-'):
        return rf  # Already has bullets
    
    # Try splitting by semicolons
    if ';' in rf:
        items = [x.strip() for x in rf.split(';') if x.strip()]
    elif ',' in rf:
        # Check if it's a list of audiences (commas with "and" or "or")
        items = [x.strip() for x in rf.split(',') if x.strip()]
        # Merge short items that are likely part of one audience
        merged = []
        buf = ''
        for item in items:
            if len(item) < 30 and buf:
                buf = buf.rstrip('.') + ', ' + item
            else:
                if buf:
                    merged.append(buf)
                buf = item
        if buf:
            merged.append(buf)
        items = merged
    else:
        # Single sentence — try to split at "and" near the end
        m = re.match(r'^(.+?)\s+and\s+(.+)$', rf)
        if m and len(m.group(1)) > 20:
            items = [m.group(1).strip(), m.group(2).strip()]
        else:
            items = [rf]
    
    # Clean up trailing periods
    items = [x.rstrip('.').strip() for x in items]
    return '\n'.join(f'- {item}' for item in items if item)


def add_bold_to_text(text):
    """Add bold formatting to summary or clinical_insight text."""
    if not text or '**' in text:
        return text
    
    # 1. Bold statistical notations first (most reliable)
    text = bold_stats(text)
    
    # 2. Bold measure acronyms/names
    text = bold_terms(text, MEASURES)
    
    # 3. Bold therapy names
    text = bold_terms(text, THERAPIES)
    
    # 4. Bold disorder names
    text = bold_terms(text, DISORDERS)
    
    # 5. Bold study design terms
    text = bold_terms(text, STUDY_DESIGNS)
    
    # 6. Bold key clinical phrases
    key_phrases = [
        'therapeutic alliance', 'transdiagnostic', 'comorbidity', 'psychopathology',
        'effect size', 'statistically significant', 'clinical significance',
        'internalizing', 'externalizing', 'emotion regulation', 'cognitive reappraisal',
        'experiential avoidance', 'psychological flexibility', 'rumination',
        'self-compassion', 'mindfulness-based', 'evidence-based',
        'treatment outcome', 'treatment response', 'dropout',
        'remission', 'relapse', 'symptom reduction',
        'dose-response', 'moderator', 'mediator',
        'preregistered', 'replication',
    ]
    for phrase in key_phrases:
        pattern = re.escape(phrase)
        text = re.sub(pattern, f'**{phrase}**', text, flags=re.IGNORECASE)
    
    return text


def main():
    with open('data/papers.json', 'r') as f:
        papers = json.load(f)
    
    stats = {'bold_added': 0, 'bullets_fixed': 0, 'already_bold': 0, 'already_bullets': 0}
    
    for p in papers:
        changed = False
        
        # Fix summary bold
        s = p.get('summary', '')
        if s and '**' not in s:
            p['summary'] = add_bold_to_text(s)
            if '**' in p['summary']:
                stats['bold_added'] += 1
                changed = True
        elif '**' in s:
            stats['already_bold'] += 1
        
        # Fix clinical_insight bold
        ci = p.get('clinical_insight', '')
        if ci and '**' not in ci:
            p['clinical_insight'] = add_bold_to_text(ci)
            if '**' in p['clinical_insight']:
                changed = True
        elif '**' in ci:
            stats['already_bold'] += 1
        
        # Fix relevant_for bullets
        rf = p.get('relevant_for', '')
        if rf:
            if not rf.lstrip().startswith('-'):
                p['relevant_for'] = fix_relevant_for(rf)
                stats['bullets_fixed'] += 1
                changed = True
            else:
                stats['already_bullets'] += 1
    
    if changed:
        with open('data/papers.json', 'w') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
            f.write('\n')
    
    print(f"Bold added to: {stats['bold_added']} papers (already had bold: {stats['already_bold']})")
    print(f"Bullets fixed: {stats['bullets_fixed']} papers (already had bullets: {stats['already_bullets']})")
    print(f"Total papers: {len(papers)}")


if __name__ == '__main__':
    main()