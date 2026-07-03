#!/usr/bin/env python3
"""Fetch full-text from PsyArXiv preprint PDFs via OSF API."""
import requests, json, sys, os
import pdfplumber

def fetch_fulltext(compact_id, output_file):
    # Find the preprint (try versions v5 down to v1)
    preprint_data = None
    for v in range(5, 0, -1):
        vid = f"{compact_id}_v{v}"
        r = requests.get(f'https://api.osf.io/v2/preprints/{vid}/',
                         params={'filter[provider]': 'psyarxiv'}, timeout=30)
        if r.status_code == 200 and r.json().get('data'):
            preprint_data = r.json()['data']
            break

    if not preprint_data:
        print(json.dumps({'error': 'preprint not found', 'compact_id': compact_id, 'source': 'failed'}))
        return False

    preprint_id = preprint_data['id']

    # List files in osfstorage
    r2 = requests.get(f'https://api.osf.io/v2/preprints/{preprint_id}/files/osfstorage/',
                      params={'page[size]': 20}, timeout=30)
    if r2.status_code != 200:
        print(json.dumps({'error': f'files API {r2.status_code}', 'compact_id': compact_id, 'source': 'failed'}))
        return False

    files = r2.json().get('data', [])
    pdf_download = None
    for f in files:
        name = f.get('attributes', {}).get('name', '')
        if name.lower().endswith('.pdf'):
            pdf_download = f.get('links', {}).get('download', '')
            break

    if not pdf_download:
        print(json.dumps({'error': 'no PDF found', 'compact_id': compact_id, 'source': 'abstract'}))
        return False

    # Download PDF
    r3 = requests.get(pdf_download, timeout=120)
    if r3.status_code != 200:
        print(json.dumps({'error': f'PDF download {r3.status_code}', 'compact_id': compact_id, 'source': 'failed'}))
        return False

    pdf_path = f'/tmp/{compact_id}.pdf'
    with open(pdf_path, 'wb') as f:
        f.write(r3.content)

    # Extract text with pdfplumber
    text = ''
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + '\n\n'

    with open(output_file, 'w') as f:
        f.write(text)

    print(json.dumps({'compact_id': compact_id, 'source': 'pdf',
                       'pages': len(pdf.pages), 'chars': len(text)}))
    os.remove(pdf_path)
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fetch-paper-fulltext.py <compact_id> [output_file]", file=sys.stderr)
        sys.exit(1)

    compact_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f'/tmp/{compact_id}_full.txt'
    fetch_fulltext(compact_id, output_file)