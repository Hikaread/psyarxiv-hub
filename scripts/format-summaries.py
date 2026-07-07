#!/usr/bin/env python3
"""Add markdown formatting to papers 492-501 in papers.json.

Formatting rules:
- **Bold** key data: sample sizes (N=...), effect sizes (d=..., r=..., OR=...),
  key findings, number of studies, statistical significance
- *Italic* for caveats, limitations, nuances, and emphasis
- Bullet lists with `- ` for relevant_for field
- LaTeX with $...$ for statistical notation
- Newlines between paragraphs in summary and clinical_insight
"""

import json
import re
import copy

DATA_PATH = "/home/z/my-project/psyarxiv-hub/data/papers.json"
TARGET_RANGE = range(492, 502)  # 492-501 inclusive


# ── 1. Paragraph breaks (applied FIRST, on clean text) ──────────────────────

def add_paragraph_breaks(text):
    """Insert double-newline paragraph breaks at natural topic boundaries."""
    # Only break before complete sentences (after a period followed by space+capital)
    break_points = [
        # Before "The study/paper/review/finding..." at sentence start
        r'(\.\s+)(The (?:study|paper|review|finding|author|trial|framework|model|intervention|protocol|use|analysis|identification|dissociation|tension|absence|emphasis|challenge|finding))',
        # Before "For clinicians/patients/participants/researchers..."
        r'(\.\s+)(For (?:clinicians|patients|participants|researchers|therapists|community|private practice))',
        # Before transition adverbs at sentence start
        r'(\.\s+)(However|Nonetheless|Additionally|Furthermore|Moreover|Importantly|Conversely|Specifically|Notably|Crucially|Finally|Ultimately|Overall|Qualitative|In contrast)\b',
        # Before "In both/longitudinal/cross-sectional..."
        r'(\.\s+)(In (?:both|longitudinal|cross-sectional|clinical|the|Study))',
        # Before "A notable/key/practical..."
        r'(\.\s+)(A (?:notable|key|important|practical|significant|critical|blind spot))',
        # Before "Clinicians should/note/remain..."
        r'(\.\s+)(Clinicians should)',
        # Before "Patients presenting..."
        r'(\.\s+)(Patients presenting)',
        # Before "Understanding these..."
        r'(\.\s+)(Understanding these)',
        # Before "The model bridges..."
        r'(\.\s+)(The model|The emphasis|The authors|Language analysis)',
        # Before "If efficacy..."
        r'(\.\s+)(If efficacy|If unemployed)',
        # Before "Cognitive reappraisal is..."
        r'(\.\s+)(Cognitive reappraisal)',
        # Before "These findings..."
        r'(\.\s+)(These findings)',
        # Before "With 27,258..."
        r'(\.\s+)(With \d)',
        # Before "TA-RPGs represent..."
        r'(\.\s+)(TA-RPGs)',
        # Before "The challenge-pattern..."
        r'(\.\s+)(The challenge-pattern)',
        # Before "An active control..."
        r'(\.\s+)(An active control)',
    ]
    
    for pattern in break_points:
        text = re.sub(pattern, r'\1\n\n\2', text)
    
    # Clean up excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── 2. LaTeX for statistical notation (applied SECOND, on clean text) ────────

def add_latex(text):
    """Wrap statistical notation in $...$."""
    # Effect sizes: d = 0.41, d=0.41
    text = re.sub(r'\b(d\s*=\s*[\d.\-]+)', r'$\1$', text)
    # Correlations: r = .66
    text = re.sub(r'\b(r\s*=\s*[\d.\-]+)', r'$\1$', text)
    # R-squared: R2=19.3%
    text = re.sub(r'\b(R2\s*=\s*[\d.\-]+%?)', r'$\1$', text)
    # Regression coefficients: b = 1.61
    text = re.sub(r'\b(b\s*=\s*[\d.\-]+)', r'$\1$', text)
    # Odds ratios: OR = X.XX
    text = re.sub(r'\b(OR\s*=\s*[\d.\-]+)', r'$\1$', text)
    # p-values: p < .001, p = .059, p < .01
    text = re.sub(r'\b(p\s*[<>=]\s*\.?\d+)', r'$\1$', text)
    # I-squared → I²
    text = re.sub(r'I-squared', r'$I^2$', text)
    return text


# ── 3. Bold key data (applied THIRD) ────────────────────────────────────────

def bold_key_data(text):
    """Bold sample sizes, effect sizes, key findings, number of studies, significance."""
    
    # Sample sizes: N = X,XXX (works for both bare and parenthesized)
    text = re.sub(
        r'\b(N\s*=\s*[\d,]+)\b',
        r'**\1**', text
    )
    # Also bold "total N across studies = X,XXX"
    text = re.sub(
        r'(total N (?:across studies )?=\s*[\d,]+)',
        r'**\1**', text
    )
    
    # Standalone large numbers with patients/participants/adults/people/studies
    text = re.sub(
        r'\b([\d,]+)\s+(patients|participants|adults|people)\b',
        r'**\1 \2**', text
    )
    
    # Number of studies/articles: "35 randomised controlled studies", "eight articles"
    text = re.sub(
        r'(\b\d+\s+randomised controlled studies)',
        r'**\1**', text
    )
    text = re.sub(
        r'(\b(eight|three|four|two)\s+articles)',
        r'**\1**', text
    )
    text = re.sub(
        r'(\bfour studies)',
        r'**\1**', text
    )
    text = re.sub(
        r'(\btwo online surveys)',
        r'**\1**', text
    )
    
    # Effect sizes (already in LaTeX) - bold the whole $...$ block
    text = re.sub(
        r'(\$(?:d|r|R2|b|OR)\s*=\s*[\d.\-]+%?\$)',
        r'**\1**', text
    )
    
    # Percentages representing key data
    text = re.sub(
        r'(\b\d+(?:\.\d+)?%\s+of\s+(?:variance|participants|patients|adults|studies))',
        r'**\1**', text
    )
    
    # Key phrases
    text = re.sub(
        r'(Key findings reveal)',
        r'**\1**', text
    )
    text = re.sub(
        r'(A key finding)',
        r'**\1**', text
    )
    text = re.sub(
        r'(unusually large sample)',
        r'**\1**', text
    )
    text = re.sub(
        r'(exceptional ecological validity)',
        r'**\1**', text
    )
    text = re.sub(
        r'(fundamentally different patterns)',
        r'**\1**', text
    )
    text = re.sub(
        r'(consistently rated higher)',
        r'**\1**', text
    )
    text = re.sub(
        r'(did not close the quality gap)',
        r'**\1**', text
    )
    text = re.sub(
        r'(meaningful changes)',
        r'**\1**', text
    )
    
    # Statistical significance
    text = re.sub(
        r'(improved significantly)',
        r'**\1**', text
    )
    text = re.sub(
        r'(increased significantly)',
        r'**\1**', text
    )
    text = re.sub(
        r'\b(remained significant predictors?)',
        r'**\1**', text
    )
    text = re.sub(
        r'(no significant effect)',
        r'**\1**', text
    )
    # 'significant predictors' NOT preceded by 'remained' (avoid double-bolding)
    text = re.sub(
        r'(?<!remained )(significant predictors?)\b',
        r'**\1**', text
    )
    
    # "three distinct NSSI clusters"
    text = re.sub(
        r'(three distinct NSSI clusters)',
        r'**\1**', text
    )
    
    return text


# ── 4. Italicize caveats/limitations (applied FOURTH) ───────────────────────

def italicize_caveats(text):
    """Italicize caveats, limitations, nuances, and emphasis."""
    
    # "A blind spot is/that..."
    text = re.sub(
        r'(A blind spot is that?)',
        r'*\1*', text
    )
    # "A notable blind spot is/..."
    text = re.sub(
        r'(A notable blind spot)',
        r'*\1*', text
    )
    
    # "However," at sentence/paragraph start
    text = re.sub(
        r'(\*?\bHowever\*?,?\s)',
        lambda m: '*However*, ' if not m.group(0).startswith('*') else m.group(0),
        text
    )
    
    # "Nonetheless,"
    text = re.sub(
        r'\b(Nonetheless)\b',
        r'*\1*', text
    )
    
    # "The authors emphasise/emphasize/note/propose/suggest"
    text = re.sub(
        r'\b(The authors (?:emphasise|emphasize|note|propose|suggest))\b',
        r'*\1*', text
    )
    
    # "The absence of"
    text = re.sub(
        r'\b(The absence of)\b',
        r'*\1*', text
    )
    
    # "may" when followed by common caveat verbs - use word boundary after
    text = re.sub(
        r'\b(may)\s+(be overlooked|be misattributed|be needed|not extend|represent|contribute|discount|limit|better guide|be disengaged|be particularly)',
        r'*\1* \2', text
    )
    
    # "potentially" (standalone adverb before verbs)
    text = re.sub(
        r'\b(potentially)\s+(inflating|improving)',
        r'*\1* \2', text
    )
    
    # "Clinicians should note/remain/routinely screen"
    text = re.sub(
        r'\b(Clinicians should (?:note|remain|broaden|routinely screen|consider))',
        r'*\1*', text
    )
    
    # Limitation patterns: "does not fully address", "lack of empirical validation"
    text = re.sub(
        r'(does not fully address)',
        r'*\1*', text
    )
    text = re.sub(
        r'(lack of empirical validation)',
        r'*\1*', text
    )
    text = re.sub(
        r'(awaits outcome trials)',
        r'*\1*', text
    )
    
    # "several cautions apply"
    text = re.sub(
        r'(several cautions apply)',
        r'*\1*', text
    )
    
    # "privacy concerns remain significant"
    text = re.sub(
        r'(privacy concerns remain significant)',
        r'*\1*', text
    )
    
    return text


# ── 5. Convert relevant_for to bullet list ──────────────────────────────────

def convert_relevant_to_bullets(text):
    """Convert prose relevant_for to bullet list, splitting on audience groups."""
    text = text.strip()
    # Remove trailing period
    if text.endswith('.'):
        text = text[:-1].strip()
    
    # Strategy: split on top-level separators between audience groups.
    # Audience groups typically start with: "Clinicians", "Therapists", "Researchers",
    # "Clinical psychologists", "CBT practitioners", "Health psychologists", "Those",
    # "Developers", etc.
    
    # First, try splitting on "; "
    if '; ' in text:
        parts = text.split('; ')
    else:
        # Split on ", and " to get the last item
        # Then split remaining on commas that precede audience-type nouns
        # Use maxsplit=1 to only split on the first ", and " (true audience boundary)
        and_split = re.split(r',\s+and\s+', text, maxsplit=1)
        
        if len(and_split) == 2:
            first_part = and_split[0]
            last_part = and_split[1]
            
            # Split first_part on commas that are followed by audience words
            # These commas separate different audience groups
            # Build audience-starting word pattern
            audience_words = [
                r'clinical researchers\b',  # must come before 'researchers'
                r'therapists\b', r'researchers\b', r'clinicians\b', 
                r'clinical psychologists\b', r'health psychologists\b',
                r'CBT practitioners\b', r'those\b', r'developers\b',
                r'mental health services\b',
            ]
            pattern = r',\s+(?=' + '|'.join(audience_words) + r')'
            
            if re.search(pattern, first_part):
                sub_parts = re.split(pattern, first_part)
                parts = sub_parts + [last_part]
            else:
                parts = and_split
        else:
            # Try splitting on commas before audience words
            audience_words = [
                r'clinical researchers\b',
                r'therapists\b', r'researchers\b', r'clinicians\b',
                r'clinical psychologists\b', r'health psychologists\b',
                r'CBT practitioners\b', r'those\b', r'developers\b',
                r'mental health services\b',
            ]
            pattern = r',\s+(?=' + '|'.join(audience_words) + r')'
            
            if re.search(pattern, text):
                parts = re.split(pattern, text)
            else:
                parts = [text]
    
    # Format each part as a bullet
    bullets = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Lowercase "and" at start if present
        if part.startswith('and '):
            part = part[4:]
        # Capitalize first letter
        if part and part[0].islower():
            part = part[0].upper() + part[1:]
        bullets.append(f"- {part}")
    
    return '\n'.join(bullets)


# ── Main pipeline ────────────────────────────────────────────────────────────

def format_paper_fields(paper):
    """Apply all markdown formatting to a paper's text fields."""
    result = copy.deepcopy(paper)
    
    for field in ('summary', 'clinical_insight'):
        if not result.get(field):
            continue
        text = result[field]
        # Order matters: paragraphs → LaTeX → bold → italic
        text = add_paragraph_breaks(text)
        text = add_latex(text)
        text = bold_key_data(text)
        text = italicize_caveats(text)
        result[field] = text
    
    if result.get('relevant_for'):
        result['relevant_for'] = convert_relevant_to_bullets(result['relevant_for'])
    
    return result


def main():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    updated_count = 0
    first_before_after = None
    
    for i, paper in enumerate(papers):
        if paper.get('number') in TARGET_RANGE:
            # Capture "before" for the first paper
            if first_before_after is None:
                first_before_after = {
                    'number': paper['number'],
                    'title': paper['title'],
                    'before_summary': paper.get('summary', ''),
                    'before_clinical': paper.get('clinical_insight', ''),
                    'before_relevant': paper.get('relevant_for', ''),
                }
            
            papers[i] = format_paper_fields(paper)
            updated_count += 1
            
            # Capture "after" for the first paper
            if first_before_after and first_before_after['number'] == paper['number']:
                first_before_after['after_summary'] = papers[i].get('summary', '')
                first_before_after['after_clinical'] = papers[i].get('clinical_insight', '')
                first_before_after['after_relevant'] = papers[i].get('relevant_for', '')
    
    # Show before/after for first paper
    if first_before_after:
        print("=" * 80)
        print(f"BEFORE/AFTER for Paper #{first_before_after['number']}")
        print(f"Title: {first_before_after['title']}")
        print("=" * 80)
        
        print(f"\n{'─'*40} SUMMARY BEFORE {'─'*40}")
        print(first_before_after['before_summary'])
        print(f"\n{'─'*40} SUMMARY AFTER {'─'*40}")
        print(first_before_after['after_summary'])
        
        print(f"\n{'─'*40} CLINICAL_INSIGHT BEFORE {'─'*40}")
        print(first_before_after['before_clinical'])
        print(f"\n{'─'*40} CLINICAL_INSIGHT AFTER {'─'*40}")
        print(first_before_after['after_clinical'])
        
        print(f"\n{'─'*40} RELEVANT_FOR BEFORE {'─'*40}")
        print(first_before_after['before_relevant'])
        print(f"\n{'─'*40} RELEVANT_FOR AFTER {'─'*40}")
        print(first_before_after['after_relevant'])
        print("=" * 80)
    
    # Write back
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {updated_count} papers (#{min(TARGET_RANGE)}-#{max(TARGET_RANGE)})")
    print(f"   Written to {DATA_PATH}")


if __name__ == '__main__':
    main()