#!/usr/bin/env python3
"""Minimal batch formatter: add **bold** and bullet lists to papers.json."""
import json, re

# Term lists for bolding
STATS_PATTERN = [
    (r'\b(N|n)\s*=\s*(\d[\d,]*)\b', r'**\1 = \2**'),
    (r'\b(p)\s*([<>=])\s*([.\d]+)', r'**\1\2\3**'),
]

MEASURES = [
    'ADIS','AUDIT','BDI','BDI-II','BES','BFI','BMI','BPNS','BSCS','BPRS','CAPS',
    'CAR','CARS','CASI','CES-D','CFQ','CGI','CLPS','CMS','COPE','CQ','CRS',
    'CSI','CTQ','CWS','DAS','DASS','DASS-21','DEQ','DES','DES-II','DLQI','DMQ',
    'DRS','DERS','DSM','DSM-5','DTS','EAT','EDE','EDE-Q','EEG','EMA','ERS',
    'ESM','ETI','FAD','FAS','FCR','FES-I','FFMQ','FNE','GAD-7','GRS','HAM-A',
    'HAM-D','HAMD','HRSD','HRV','IAS','ICD','ICD-10','ICD-11','IES','IES-R','IIP',
    'IPT','IRS','ISI','LAS','LEAS','LSAS','MAAS','MADRS','MCQ','MDI','MEQ',
    'MINI','MIND','MMPI','MOCI','MPQ','MRNI','NAI','NCS','NEO','NEO-FFI','NFI',
    'NPSI','OCI-R','OQ-45','OPD','OPD-SQ','PADS','PANAS','PCL','PCL-5','PDQ',
    'PHQ','PHQ-9','PRFQ','PSQI','PSS','QoL','RAI','RAS','RSES','RSR','SAD',
    'SAS','SCID','SCID-5','SCL','SCL-90','SCL-90-R','SDS','SES','SHAPS','SII',
    'SNAP','SPIN','STAI','STAI-T','STAI-S','STAXI','STOMP','SWLS','TCI',
    'TEIQue','TMS','TRF','TUQ','UP-CoF','VIA','WAIS','WAI','WEMWBS','WHO',
    'WHO-5','WOI','Y-BOCS','ZAN-BPD','ZKPQ',
]

DISORDERS = [
    'ADHD','adjustment disorder','agoraphobia','alcohol use disorder',
    'anorexia nervosa','antisocial personality disorder','anxiety disorder',
    'autism spectrum disorder','ASD','binge eating disorder','BED',
    'bipolar disorder','body dysmorphic disorder','BDD','borderline personality disorder',
    'BPD','bulimia nervosa','conduct disorder','delusional disorder',
    'dissociative identity disorder','DID','dyslexia','eating disorder',
    'generalized anxiety disorder','GAD','gender dysphoria','hoarding disorder',
    'intermittent explosive disorder','major depressive disorder','MDD',
    'narcissistic personality disorder','NPD','obsessive-compulsive disorder',
    'OCD','oppositional defiant disorder','ODD','panic disorder',
    'persistent depressive disorder','personality disorder','phobia',
    'post-traumatic stress disorder','PTSD','psychosis','schizophrenia',
    'separation anxiety disorder','social anxiety disorder','SAD',
    'somatization disorder','specific phobia','substance use disorder',
    'somatic symptom disorder','trichotillomania','avoidant personality disorder',
    'dependent personality disorder','histrionic personality disorder',
    'paranoid personality disorder','schizoaffective disorder',
    'schizotypal personality disorder','psychotic disorder',
]

THERAPIES = [
    'acceptance and commitment therapy','ACT','assertiveness training',
    'behavioral activation','biofeedback','body-focused repetitive behavior therapy',
    'brief dynamic psychotherapy','CBT','cognitive behavioral therapy',
    'cognitive processing therapy','compassion-focused therapy','CFT',
    'contingency management','couples therapy','DBT','dialectical behavior therapy',
    'EMDR','emotion-focused therapy','EFT','exposure and response prevention',
    'ERP','exposure therapy','family therapy','GDT','gestalt therapy',
    'group therapy','habit reversal training','HRT','humanistic therapy',
    'imaginal exposure','interpersonal psychotherapy','IPT',
    'mentalization-based therapy','MBT','MBCT','MBSR','mindfulness',
    'mindfulness-based cognitive therapy','mindfulness-based stress reduction',
    'motivational interviewing','MI','narrative therapy','psychodynamic therapy',
    'psychoeducation','rational emotive behavior therapy','REBT',
    'schema therapy','solution-focused therapy','SFT','supportive-expressive',
    'systemic therapy','third-wave CBT','transference-focused psychotherapy',
    'trauma-focused CBT','TF-CBT',
]

STUDY_DESIGNS = [
    'randomized controlled trial','RCT','preregistered study',
    'systematic review','meta-analysis','longitudinal study',
    'cross-sectional study','cohort study','case-control study',
    'ecological momentary assessment','EMA','experience sampling',
    'mixed-methods study','qualitative study','quantitative study',
    'multiverse analysis','network meta-analysis','scoping review',
    'rapid review','narrative review','umbrella review',
    'structural equation model','SEM','latent growth model',
    'multilevel model','mediation analysis','moderation analysis',
    'bayesian analysis','propensity score','factor analysis',
]

KEY_PHRASES = [
    'therapeutic alliance','transdiagnostic','comorbidity','psychopathology',
    'effect size','clinical significance','internalizing','externalizing',
    'emotion regulation','cognitive reappraisal','experiential avoidance',
    'psychological flexibility','rumination','self-compassion','evidence-based',
    'treatment outcome','treatment response','remission','relapse',
    'symptom reduction','dose-response','preregistered','replication',
    'therapeutic alliance','mentalizing','reflective functioning',
    'affect regulation','interoceptive','somatic','psychometric',
]

ALL_TERMS = sorted(MEASURES + DISORDERS + THERAPIES + STUDY_DESIGNS + KEY_PHRASES, key=len, reverse=True)


def make_pattern(term):
    if re.match(r'^[A-Z]+$', term) and len(term) <= 4:
        return r'(?<![A-Za-z])' + re.escape(term) + r'(?![A-Za-z])'
    return r'(?<!\w)' + re.escape(term) + r'(?!\w)'


def add_bold(text):
    if not text or '**' in text:
        return text
    for pat, repl in STATS_PATTERN:
        text = re.sub(pat, repl, text)
    for term in ALL_TERMS:
        pat = make_pattern(term)
        # Find all match positions, skip any inside existing **...** spans
        bold_spans = [(m.start(), m.end()) for m in re.finditer(r'\*\*[^*]+\*\*', text)]
        def should_bold(m):
            for bs, be in bold_spans:
                if bs <= m.start() < be:
                    return m.group()  # Inside existing bold, skip
            return f'**{m.group()}**'
        text = re.sub(pat, should_bold, text, flags=re.IGNORECASE)
        # Update bold_spans for next iteration
        bold_spans = [(m.start(), m.end()) for m in re.finditer(r'\*\*[^*]+\*\*', text)]
    # Safety: fix any residual broken patterns
    text = re.sub(r'\*{4,}', '**', text)
    return text


def fix_bullets(rf):
    if not rf or rf.lstrip().startswith('-'):
        return rf
    if ';' in rf:
        items = [x.strip() for x in rf.split(';') if x.strip()]
    elif ',' in rf:
        items = [x.strip() for x in rf.split(',') if x.strip()]
        merged, buf = [], ''
        for item in items:
            if len(item) < 30 and buf:
                buf = buf.rstrip('.') + ', ' + item
            else:
                if buf: merged.append(buf)
                buf = item
        if buf: merged.append(buf)
        items = merged
    else:
        m = re.match(r'^(.+?)\s+and\s+(.+)$', rf)
        items = [m.group(1).strip(), m.group(2).strip()] if m and len(m.group(1)) > 20 else [rf]
    items = [x.rstrip('.').strip() for x in items]
    return '\n'.join(f'- {item}' for item in items if item)


def main():
    with open('data/papers.json') as f:
        papers = json.load(f)

    bold_count = 0
    bullet_count = 0
    for p in papers:
        s = p.get('summary', '')
        ci = p.get('clinical_insight', '')
        rf = p.get('relevant_for', '')

        new_s = add_bold(s)
        new_ci = add_bold(ci)
        new_rf = fix_bullets(rf)

        p['summary'] = new_s
        p['clinical_insight'] = new_ci
        p['relevant_for'] = new_rf

        if '**' in new_s and '**' not in s:
            bold_count += 1
        if '**' in new_ci and '**' not in ci:
            bold_count += 1
        if new_rf != rf:
            bullet_count += 1

    with open('data/papers.json', 'w') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"Bold added: {bold_count} sections, Bullets fixed: {bullet_count} papers, Total: {len(papers)}")


if __name__ == '__main__':
    main()