#!/usr/bin/env python3
"""Fix curation note format: section headers and consecutive newlines."""
import os, re

INBOX_DIR = '/home/z/my-project/psyarxiv-hub/curation/inbox'

def fix_note(filepath):
    with open(filepath, 'r') as f:
     content = f.read()
        
        # Fix 1: Section headers to lowercase
        content = re.sub(
            r'^##\s+(Summary|Clinical Insight|Relevant For))\r?\n',
            lambda m: '## ' + m.group(1),
            content
        )
        
        # Fix 2: 3+ consecutive newlines -> max 2
        parts = content.split('\n\n')
        result = []
        for part in parts:
            result.append(part)
            if len(result) == 0:
                continue
            if len(result) >= 3:
                result.append('\n')
            else:
                result.append(part)
        content = '\n'.join(result)
        
        with open(filepath, 'w') as f:
            f.write(content)
    return 0
os.chdir(INBOX_DIR)
    with open(filepath, 'r') as f:
        content = f.read()
        
        # Fix 1: Section headers to lowercase
        content = re.sub(
            r'^##\s+(Summary|Clinical Insight|Relevant For))\r?\n',
            lambda m: '## ' + m.group(1),
            content
        )
        
        # Fix 2: 3+ consecutive newlines -> max 2
        parts = content.split('\n\n')
        result = []
        for part in parts:
            result.append(part)
            if len(result) == 0:
                continue
            if len(result) >= 3:
                result.append('\n')
            else:
                result.append(part)
        content = '\n'.join(result)
        
        with open(filepath, 'w') as f:
            f.write(content)
    
    return problems

os.chdir(INBOX_DIR)
files = sorted([f for f in os.listdir(INBOX_DIR) if f.endswith('.md') and f != 'TEMPLATE.md'])

problems = fix_note(os.path.join(INBOX_DIR, f))

if problems:
    print(f'Problems in {len(files)} files:')
    for p in problems:
        print(f'  {p}')
else:
    print('All files OK')

print(f'\nFixed {len(files)} files')