#!/usr/bin/env python3
"""Add line breaks after sentences in summary, clinical_insight, and relevant_for fields.
Only processes papers where these fields have no newlines already."""

import json
import re

ABBREVIATIONS = {
    'etc.', 'e.g.', 'i.e.', 'vs.', 'Dr.', 'cf.', 'vol.', 'ed.', 'pp.',
    'Fig.', 'N.', 'M.', 'SD.', 'SE.', 'CI.', 'HRSD.', 'BDI-II.',
    'RCT.', 'MBSR.', 'MBCT.', 'DBT.', 'CFT.', 'ACT.', 'RFT.',
    'OSF.', 'ABCD.', 'CBCL.', 'OQ-45.', 'HSCL.', 'IRI.', 'MINI.',
    'PRISMA.', 'EMA.', 'ESM.', 'LLM.', 'PBS.', 'HDL.', 'CBC.',
    'ADHD.', 'ASD.', 'MDD.', 'WBC.', 'RBC.', 'MCV.', 'MCH.',
}

def has_abbreviation(text, pos):
    """Check if the period at pos is part of an abbreviation."""
    for abbr in ABBREVIATIONS:
        abbr_start = pos - len(abbr) + 1
        if abbr_start >= 0 and text[abbr_start:pos+1] == abbr:
            return True
    return False

def add_line_breaks(text):
    """Add \n after sentence-ending periods, respecting abbreviations."""
    if '\n' in text:
        return text  # Already has line breaks, don't touch
    
    result = []
    i = 0
    while i < len(text):
        if text[i] == '.' and i + 1 < len(text) and text[i+1] == ' ':
            # Check if this is a sentence-ending period
            if not has_abbreviation(text, i):
                # Check if it's preceded by a letter (not a number like "3.5")
                if i > 0 and text[i-1].isalpha():
                    result.append('.')
                    result.append('\n')
                    i += 2
                    continue
        result.append(text[i])
        i += 1
    
    return ''.join(result)

def process_paper(paper):
    """Add line breaks to summary, clinical_insight, relevant_for if needed."""
    changed = False
    
    for field in ['summary', 'clinical_insight', 'relevant_for']:
        text = paper.get(field, '')
        if text and '\n' not in text:
            new_text = add_line_breaks(text)
            if new_text != text:
                paper[field] = new_text
                changed = True
    
    return changed

# Load papers
with open('data/papers.json') as f:
    papers = json.load(f)

fixed = 0
for p in papers:
    if process_paper(p):
        fixed += 1

print(f'Fixed {fixed} papers')

# Save
with open('data/papers.json', 'w') as f:
    json.dump(papers, f, indent=2, ensure_ascii=False)

print('Saved.')