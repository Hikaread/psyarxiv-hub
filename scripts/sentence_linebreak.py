#!/usr/bin/env python3
"""Add line breaks after sentence-ending periods in methodology notes (and optionally summary/clinical_insight).

Rule: end of sentence (period followed by space and uppercase or end of string) → newline.
Exceptions: abbreviations like etc., e.g., i.e., vs., Dr., Mr., vol., p., pp., ed., approx., cf., U.S., U.K., N., No.
"""

import json
import re
import sys

ABBREVIATIONS = {
    'etc', 'e.g', 'i.e', 'vs', 'dr', 'mr', 'mrs', 'ms', 'prof',
    'vol', 'p', 'pp', 'ed', 'approx', 'cf', 'nos', 'v', 'fig',
    'al', 'no', 'srh', 'ema', 'mrt', 'osf', 'bdi', 'pcl', 'ctq',
    'ders', 'erq', 'mdq', 'mmat', 'vif', 'r',
}

# Regex: match a period followed by a space and an uppercase letter, or period at end of string
# But NOT if the word before the period is a known abbreviation
SENTENCE_END = re.compile(r'(?<=[a-z\]])\.(?:\s+([A-Z])|$)')


def should_break(pre_context: str) -> bool:
    """Check if the word before the period is an abbreviation."""
    # Extract the last word before the period
    match = re.search(r'([a-zA-Z]+)\.$', pre_context)
    if match:
        word = match.group(1).lower()
        if word in ABBREVIATIONS:
            return False
    return True


def add_sentence_breaks(text: str) -> str:
    """Add newline after each sentence-ending period."""
    if not text:
        return text

    result = []
    i = 0
    while i < len(text):
        # Check for period pattern
        if text[i] == '.' and i > 0:
            pre = text[:i+1]
            rest = text[i+1:]

            # Check if this is a sentence end
            # Case 1: period followed by space + uppercase letter
            m = re.match(r'^(\s+)([A-Z])', rest)
            if m and should_break(pre):
                result.append('.')
                result.append('\n')  # line break after sentence
                result.append(m.group(2))  # keep the uppercase letter
                i += 1 + len(m.group(0))
                continue

            # Case 2: period at end of string
            if rest == '' or rest.strip() == '':
                if should_break(pre):
                    result.append('.')
                    if rest:
                        result.append(rest)
                    break

        result.append(text[i])
        i += 1

    return ''.join(result)


def process_papers(json_path: str, paper_range: tuple = None, fields: list = None):
    """Process papers.json to add sentence line breaks."""
    if fields is None:
        fields = ['methodology_note']

    with open(json_path, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    changed = 0
    for paper in papers:
        num = paper.get('number')
        if paper_range and (num is None or not (paper_range[0] <= num <= paper_range[1])):
            continue

        for field in fields:
            text = paper.get(field)
            if not text or not isinstance(text, str):
                continue

            new_text = add_sentence_breaks(text)
            if new_text != text:
                paper[field] = new_text
                changed += 1
                print(f"Paper {num} ({field}): updated")

    if changed:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        print(f"\nTotal fields updated: {changed}")
    else:
        print("No changes needed.")


if __name__ == '__main__':
    process_papers(
        '/home/z/my-project/psyarxiv-hub/data/papers.json',
        paper_range=(632, 636),
        fields=['methodology_note']
    )