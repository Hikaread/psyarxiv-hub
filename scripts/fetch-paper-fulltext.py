#!/usr/bin/env python3
"""Fetch full-text from PsyArXiv preprint PDFs via OSF API.
Also handles .docx files (many authors upload Word docs to OSF)."""
import requests, json, sys, os
import pdfplumber
import docx


def extract_text_from_docx(docx_path):
    """Extract text from a .docx file."""
    doc = docx.Document(docx_path)
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    return '\n\n'.join(paragraphs)


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
    file_download = None
    file_ext = None
    for f in files:
        name = f.get('attributes', {}).get('name', '')
        lower_name = name.lower()
        # Prefer PDF, fall back to docx
        if lower_name.endswith('.pdf') and file_ext != 'pdf':
            file_download = f.get('links', {}).get('download', '')
            file_ext = 'pdf'
        elif lower_name.endswith('.docx') and file_ext is None:
            file_download = f.get('links', {}).get('download', '')
            file_ext = 'docx'

    if not file_download:
        print(json.dumps({'error': 'no PDF or DOCX found', 'compact_id': compact_id, 'source': 'abstract'}))
        return False

    # Download file
    r3 = requests.get(file_download, timeout=120)
    if r3.status_code != 200:
        print(json.dumps({'error': f'file download {r3.status_code}', 'compact_id': compact_id, 'source': 'failed'}))
        return False

    # Extract text based on file type
    if file_ext == 'pdf':
        pdf_path = f'/tmp/{compact_id}.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(r3.content)
        text = ''
        page_count = 0
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + '\n\n'
        os.remove(pdf_path)
        print(json.dumps({'compact_id': compact_id, 'source': 'pdf',
                           'pages': page_count, 'chars': len(text)}))
    elif file_ext == 'docx':
        docx_path = f'/tmp/{compact_id}.docx'
        with open(docx_path, 'wb') as f:
            f.write(r3.content)
        text = extract_text_from_docx(docx_path)
        os.remove(docx_path)
        page_count = text.count('\n\n')  # rough estimate
        print(json.dumps({'compact_id': compact_id, 'source': 'docx',
                           'pages': page_count, 'chars': len(text)}))
    else:
        print(json.dumps({'error': f'unsupported format: {file_ext}', 'compact_id': compact_id, 'source': 'failed'}))
        return False

    with open(output_file, 'w') as f:
        f.write(text)

    return bool(text.strip())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fetch-paper-fulltext.py <compact_id> [output_file]", file=sys.stderr)
        sys.exit(1)

    compact_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f'/tmp/{compact_id}_full.txt'
    fetch_fulltext(compact_id, output_file)
