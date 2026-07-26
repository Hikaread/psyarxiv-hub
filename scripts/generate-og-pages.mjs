#!/usr/bin/env node
// Generate per-paper OG meta tag pages for Discord/Twitter link previews.
// Each file is ~0.5KB — a minimal HTML page with OG tags + JS redirect to the SPA.
// Run after papers.json is updated. Only generates files that don't exist or are stale.

import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from 'fs';
import { join, resolve } from 'path';

const PAPERS_JSON = resolve('/home/z/my-project/psyarxiv-hub/data/papers.json');
const OUTPUT_DIR = resolve('/home/z/my-project/psyarxiv-hub/paper');
const BASE_URL = 'https://hikaread.github.io/psyarxiv-hub';

const TEMPLATE = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url={base}/#paper={number}">
<title>{title}</title>
<meta name="description" content="{summary_200}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{summary_200}">
<meta property="og:type" content="article">
<meta property="og:url" content="{base}/paper/{number}.html">
<meta property="og:site_name" content="PsyHub">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{summary_200}">
<style>body{margin:0;display:flex;justify-content:center;align-items:center;height:100vh;font-family:system-ui;color:#555}a{color:#3b82f6;text-decoration:none}</style>
</head>
<body><p>Redirecting to <a href="{base}/#paper={number}">{title}</a>…</p>
<script>location.replace('{base}/#paper={number}');</script>
</body>
</html>`;

function escHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function truncate(s, max = 200) {
  if (!s) return '';
  // Strip markdown
  s = s.replace(/\*\*([^*]+)\*\*/g, '$1').replace(/\*([^*]+)\*/g, '$1').replace(/<[^>]+>/g, '');
  if (s.length <= max) return s;
  return s.substring(0, max).replace(/\s+\S*$/, '') + '…';
}

const papers = JSON.parse(readFileSync(PAPERS_JSON, 'utf-8'));
mkdirSync(OUTPUT_DIR, { recursive: true });

let created = 0, skipped = 0;

for (const p of papers) {
  const outPath = join(OUTPUT_DIR, `${p.number}.html`);
  const html = TEMPLATE
    .replace(/{base}/g, BASE_URL)
    .replace(/{number}/g, p.number)
    .replace(/{title}/g, escHtml(p.title))
    .replace(/{summary_200}/g, escHtml(truncate(p.summary)));

  if (!existsSync(outPath)) {
    writeFileSync(outPath, html);
    created++;
  } else {
    skipped++;
  }
}

console.log(`Generated ${created} new OG pages, ${skipped} existing (total: ${papers.length} papers)`);