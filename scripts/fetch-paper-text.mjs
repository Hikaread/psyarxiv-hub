#!/usr/bin/env node

/**
 * Fetch full paper text from OSF preprint via PDF download + pdftotext.
 * Usage: node fetch-paper-text.mjs <compact_id> [output_file]
 * Outputs plain text of the paper to stdout or file.
 */

import { execSync } from 'child_process';
import { writeFileSync } from 'fs';

const OSF_API = 'https://api.osf.io/v2';
const args = process.argv.slice(2);

if (args.length < 1) {
  console.error('Usage: node fetch-paper-text.mjs <compact_id> [output_file]');
  process.exit(1);
}

const compactId = args[0].replace(/_v\d+$/i, '');
const outputFile = args[1] || null;

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function fetchJson(url) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const r = await fetch(url, { headers: { 'Accept': 'application/vnd.api+json' } });
    if (r.ok) { await sleep(200); return r.json(); }
    if (r.status === 429 && attempt < 2) { await sleep(3000); continue; }
    throw new Error(`HTTP ${r.status} for ${url}`);
  }
}

async function findDownloadUrl(preprintId) {
  // Use ?include=primary_file to get the main PDF directly
  const data = await fetchJson(`${OSF_API}/preprints/${preprintId}/?include=primary_file`);
  const rel = data.data?.relationships?.primary_file?.links?.related?.href;
  if (!rel) return null;
  const fileData = await fetchJson(rel);
  if (fileData.data?.links?.download) {
    return { name: fileData.data.attributes?.name, url: fileData.data.links.download };
  }
  return null;
}

async function main() {
  let downloadUrl = null;
  let fileName = null;

  // Try versions in reverse order (newest first)
  for (let v = 5; v >= 1; v--) {
    const preprintId = `${compactId}_v${v}`;
    try {
      const result = await findDownloadUrl(preprintId);
      if (result) {
        downloadUrl = result.url;
        fileName = result.name;
        process.stderr.write(`Found file via ${preprintId}: ${fileName}\n`);
        break;
      }
    } catch (e) { /* try next version */ }
  }

  // Also try without version
  if (!downloadUrl) {
    try {
      const result = await findDownloadUrl(compactId);
      if (result) {
        downloadUrl = result.url;
        fileName = result.name;
        process.stderr.write(`Found file via ${compactId}: ${fileName}\n`);
      }
    } catch (e) { /* no luck */ }
  }

  if (!downloadUrl) {
    console.error(`No downloadable file found for ${compactId}`);
    process.exit(1);
  }

  // Download PDF
  const pdfPath = `/tmp/${compactId}_paper.pdf`;
  process.stderr.write(`Downloading PDF...\n`);
  execSync(`curl -sL "${downloadUrl}" -o "${pdfPath}"`);

  // Check it's actually a PDF
  const fileType = execSync(`file -b "${pdfPath}"`).toString().trim();
  if (!fileType.startsWith('PDF')) {
    // Some OSF files might be docx or other formats
    if (fileType.includes('Microsoft') || fileType.includes('Word') || fileType.includes('DOCX')) {
      process.stderr.write(`File is ${fileType}, attempting docx extraction...\n`);
      try {
        const text = execSync(`python3 -c "
from docx import Document
doc = Document('${pdfPath}')
print('\\n'.join([p.text for p in doc.paragraphs]))
" 2>/dev/null`).toString();
        if (text.trim().length > 100) {
          output(text);
          return;
        }
      } catch (e) { /* fallback to abstract */ }
    }
    console.error(`Downloaded file is not PDF: ${fileType}`);
    process.exit(1);
  }

  // Extract text with pdftotext
  process.stderr.write(`Extracting text...\n`);
  try {
    const text = execSync(`pdftotext "${pdfPath}" - 2>/dev/null`).toString();
    output(text);
  } catch (e) {
    console.error('pdftotext failed. Is poppler-utils installed?');
    process.exit(1);
  }
}

function output(text) {
  if (outputFile) {
    writeFileSync(outputFile, text, 'utf8');
    process.stderr.write(`Wrote ${text.split(/\s+/).length} words to ${outputFile}\n`);
  } else {
    process.stdout.write(text);
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });