#!/usr/bin/env node

import { readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const ROOT = '/home/z/my-project/psyarxiv-hub';
const INBOX_DIR = path.join(ROOT, 'curation', 'inbox');
const DATA_PATH = path.join(ROOT, 'data', 'papers.json');
const shouldWrite = process.argv.includes('--write');

function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!match) {
    throw new Error('Missing frontmatter block');
  }

  const metadata = {};
  match[1].split(/\r?\n/).forEach((line) => {
    const separator = line.indexOf(':');
    if (separator === -1) return;
    const key = line.slice(0, separator).trim();
    const value = line.slice(separator + 1).trim();
    metadata[key] = value;
  });

  return {
    metadata,
    body: content.slice(match[0].length)
  };
}

function parseSections(body) {
  const sectionPattern = /^##\s+(.+)\r?\n([\s\S]*?)(?=^##\s+|$(?!\n))/gm;
  const sections = {};
  let match;

  while ((match = sectionPattern.exec(body)) !== null) {
    sections[match[1].trim().toLowerCase()] = match[2].trim();
  }

  return sections;
}

function normalizeCategories(value) {
  return String(value || '')
    .split('|')
    .map((item) => item.trim())
    .filter(Boolean);
}

function buildPaperRecord(parsed) {
  const metadata = parsed.metadata;
  const sections = parseSections(parsed.body);
  const requiredMetadata = ['number', 'title', 'authors', 'osf_id', 'date_posted', 'source_date', 'categories'];
  const requiredSections = ['summary', 'clinical insight', 'relevant for'];

  requiredMetadata.forEach((key) => {
    if (!metadata[key]) {
      throw new Error(`Missing metadata field: ${key}`);
    }
  });

  requiredSections.forEach((key) => {
    if (!sections[key]) {
      throw new Error(`Missing section: ${key}`);
    }
  });

  return {
    number: Number(metadata.number),
    title: metadata.title,
    authors: metadata.authors,
    osf_id: metadata.osf_id,
    date_posted: metadata.date_posted,
    source_date: metadata.source_date,
    categories: normalizeCategories(metadata.categories),
    summary: sections.summary,
    clinical_insight: sections['clinical insight'],
    methodology_note: sections['methodology note'] || null,
    relevant_for: sections['relevant for'],
    published: metadata.published || null,
    link: `https://osf.io/preprints/psyarxiv/${metadata.osf_id}`
  };
}

async function loadInboxRecords() {
  const files = await readdir(INBOX_DIR, { withFileTypes: true });
  const markdownFiles = files
    .filter((entry) => entry.isFile() && entry.name.toLowerCase().endsWith('.md') && entry.name !== 'TEMPLATE.md')
    .map((entry) => entry.name);

  const records = [];

  for (const fileName of markdownFiles) {
    const fullPath = path.join(INBOX_DIR, fileName);
    const content = await readFile(fullPath, 'utf8');
    const parsed = parseFrontmatter(content);
    const record = buildPaperRecord(parsed);
    records.push({ fileName, record });
  }

  return records;
}

function upsertPapers(existing, incoming) {
  const papers = existing.slice();
  const changes = [];

  incoming.forEach(({ fileName, record }) => {
    const index = papers.findIndex((paper) => paper.number === record.number || (paper.osf_id && paper.osf_id === record.osf_id));
    if (index >= 0) {
      papers[index] = { ...papers[index], ...record };
      changes.push({ type: 'updated', fileName, number: record.number, title: record.title });
    } else {
      papers.push(record);
      changes.push({ type: 'created', fileName, number: record.number, title: record.title });
    }
  });

  papers.sort((left, right) => left.number - right.number);
  return { papers, changes };
}

async function main() {
  const existing = JSON.parse(await readFile(DATA_PATH, 'utf8'));
  const incoming = await loadInboxRecords();
  const result = upsertPapers(existing, incoming);

  if (shouldWrite) {
    await writeFile(DATA_PATH, JSON.stringify(result.papers, null, 2) + '\n', 'utf8');
  }

  console.log(JSON.stringify({
    inboxFiles: incoming.length,
    changes: result.changes,
    wroteData: shouldWrite
  }, null, 2));
}

main().catch((error) => {
  console.error(error.message || error);
  process.exitCode = 1;
});
