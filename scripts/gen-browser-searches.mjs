#!/usr/bin/env node
/**
 * Use agent-browser to search PsyArXiv for each missing paper.
 * Outputs browser commands to search and extract results.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { execSync } from 'child_process';

const PAPERS_JSON = '/home/z/my-project/psyarxiv-hub/data/papers.json';
const PROGRESS_FILE = '/home/z/my-project/scripts/browser-search-progress.json';

const papers = JSON.parse(readFileSync(PAPERS_JSON, 'utf-8'));
const missing = papers.filter(p => !p.osf_id);

// Search terms extraction - be very specific
function getSearchTerms(paper) {
  const title = paper.title;
  const authors = paper.authors || 'Unknown';
  
  // For papers with known authors, use author last name + most specific topic word
  if (authors !== 'Unknown') {
    const lastNames = authors.split(',').map(a => {
      const parts = a.trim().split(' ');
      return parts[parts.length - 1];
    });
    // Get most specific words from title
    const stop = new Set(['therapeutic','approaches','approach','study','analysis','review','clinical','framework','model','effects','findings','systematic','implications']);
    const words = title.match(/[a-zA-Z]+/g)?.filter(w => !stop.has(w.toLowerCase()) && w.length >= 5) || [];
    words.sort((a, b) => b.length - a.length);
    return `${lastNames[0]} ${words.slice(0, 2).join(' ')}`;
  }
  
  // For papers without authors, use the 3 most specific/unique terms
  const stop = new Set(['a','an','the','and','or','of','for','in','on','to','with','by','from','their','its','is','are','was','were','be','been','that','this','these','those','not','no','but','at','if','study','analysis','review','research','examination','based','using','between','among','into','clinical','framework','model','effects','effect','role','association','predictors','outcomes','findings','evidence','overview','perspective','considerations','evaluating','evaluation','assessment','versus','therapeutic','approaches','approach','systematic','additional','implications','disorder','disorders']);
  
  // Prioritize: abbreviations (CBT, EMA, etc.), hyphenated terms, then longest words
  const abbrevs = title.match(/\b[A-Z]{2,}-?[A-Z]*\b/g) || [];
  const hyphenated = title.match(/[a-zA-Z]+-[a-zA-Z]+/g) || [];
  const words = title.match(/[a-zA-Z]+/g)?.filter(w => !stop.has(w.toLowerCase()) && w.length >= 4) || [];
  words.sort((a, b) => b.length - a.length);
  
  // Combine: abbreviations first, then hyphenated, then top words
  const specific = [...abbrevs.map(a => a.toLowerCase()), ...hyphenated.map(h => h.toLowerCase()), ...words.slice(0, 3)];
  return [...new Set(specific)].slice(0, 4).join(' ');
}

// Build search commands for all missing papers
const commands = [];
for (const paper of missing) {
  const terms = getSearchTerms(paper);
  commands.push({
    number: paper.number,
    title: paper.title,
    search_terms: terms,
  });
}

console.log(`Generated ${commands.length} search commands\n`);

// Print the first 10 as a test
for (const cmd of commands.slice(0, 10)) {
  console.log(`#${cmd.number}: ${cmd.title}`);
  console.log(`  Search: ${cmd.search_terms}`);
  console.log();
}

// Save all commands
writeFileSync('/home/z/my-project/scripts/browser-search-commands.json', JSON.stringify(commands, null, 2));
console.log(`\nAll commands saved to browser-search-commands.json`);