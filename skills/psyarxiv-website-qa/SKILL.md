---
name: psyarxiv-website-qa
description: "Comprehensive UI/UX quality assurance for the PsyArXiv Hub static website (https://hikaread.github.io/psyarxiv-hub/). Use this skill whenever making ANY changes to the website — editing HTML, CSS, JavaScript, or updating papers.json. Also trigger proactively after cron jobs add papers, after fixing bugs, or when the user says 'check the website', 'test the site', 'QA', 'verify', 'does it work', or reports visual/interaction issues. This skill catches z-index stacking bugs, missing DOM elements, broken references, data integrity issues, theme completeness, accessibility gaps, and responsive layout problems."
---

# PsyArXiv Hub Website QA

You are performing quality assurance on a static psychology preprint website
at `/home/z/my-project/website/`. The site uses vanilla HTML/CSS/JS (no framework),
three CSS themes (light/dark/purple), client-side JSON rendering, and is deployed
to GitHub Pages.

## Why This Matters

The site has a history of subtle breakage: overlays blocking clicks due to wrong
z-index, settings drawers becoming uncloseable, categories not mapping to filter IDs,
mobile layouts hiding content behind fixed headers, and data pipeline changes silently
breaking the UI. Each of these was caused by a small edit that seemed correct in
isolation. This skill exists to catch those regressions before they reach the user.

## Architecture

The website is a static site with these files:

```
website/
├── index.html          — Single page with header, sidebar, papers container, modals
├── css/style.css       — All styles including 3 themes, responsive breakpoints
├── js/app.js           — IIFE with fetch→render pipeline, settings, filters, sort
└── data/papers.json    — Array of paper objects rendered client-side
```

Key architectural decisions:
- **Three themes** via `data-theme` attribute on `<html>`: light, dark, purple
- **CSS custom properties** for all colors/shadows (never hard-coded colors in JS)
- **Settings persisted** in localStorage under key `psyarxiv-settings`
- **URL hash state** encodes search (`q`), disabled categories (`off`), and sort mode
- **15 category filters** mapped by `labelToId` in JS (label strings → short IDs)
- **Auto-hide header** using scroll direction + `requestAnimationFrame`
- **Slide-out drawers** for sidebar (mobile) and settings, each with a backdrop overlay
- **Paper cards** rendered via `createCard()`, modals via `openModal()`
- **Category sort mode** adds sticky dividers and quick-nav dots

## Step 1: Run the Automated Checker

Execute the bundled Python checker first — it catches structural issues:

```bash
python3 /home/z/my-project/skills/psyarxiv-website-qa/scripts/ux_checker.py
```

If it reports **any ERROR**, investigate and fix before proceeding. Warnings are
acceptable but note them.

## Step 2: Manual Code Review Checklist

Read each file and verify these items. This catches things the automated checker
cannot (logic bugs, interaction patterns, visual regressions).

### HTML (`index.html`)

- [ ] **Sort select** is in the `<header>` (inside `.header-right`), NOT in the sidebar
- [ ] **All 22 critical element IDs** exist: `site-header`, `sidebar`, `sidebar-toggle`,
  `search-input`, `settings-toggle`, `settings-drawer`, `settings-overlay`,
  `settings-close`, `sort-select`, `papers-container`, `papers-list`, `paper-modal`,
  `modal-close`, `modal-body`, `stats-bar`, `category-filters`, `quick-nav`,
  `load-more`, `no-results`, `btn-select-all`, `btn-clear-all`, `sidebar-overlay`
- [ ] **Settings drawer** has all 4 setting groups: theme, fontSize, dyslexic, pageSize
- [ ] Each setting group has `data-setting` attribute matching JS keys
- [ ] No orphaned elements (IDs not referenced in JS, or JS references with no matching ID)
- [ ] OpenDyslexic font is loaded with weight/style params:
  `?ital,wght@0,400;0,700;1,400`
- [ ] `<html>` has `lang="en"` and `data-theme="light"` (default theme)

### CSS (`css/style.css`)

- [ ] **Z-index stacking** is correct (this is the #1 source of bugs):
  - `#sidebar-overlay`: z-index 89
  - `#sidebar` (mobile): z-index 90
  - `#settings-overlay`: z-index 90 (MUST be < settings-drawer)
  - `#settings-drawer`: z-index 91
  - `.modal-overlay`: z-index 200
  - `#site-header`: z-index 100
  - `#stats-bar`: z-index 99
- [ ] **All three themes** define the SAME set of CSS custom properties:
  `--bg-body`, `--bg-card`, `--bg-sidebar`, `--bg-stats`, `--bg-drawer`,
  `--bg-modal-bg`, `--text-primary`, `--text-secondary`, `--text-muted`,
  `--text-on-accent`, `--border`, `--border-card`, `--accent`, `--accent-hover`,
  `--accent-subtle`, `--accent-subtle2`, `--header-bg`, `--shadow-sm`, `--shadow-md`,
  `--shadow-lg`
- [ ] **`.open` rules exist** for both overlays:
  `#sidebar-overlay.open { display: block; }` and
  `#settings-overlay.open { display: block; }`
- [ ] **Main layout padding-top** >= 72px (header 48px + stats ~24px)
- [ ] **Mobile breakpoint** at 900px and 600px both exist
- [ ] At 900px: `#sidebar-toggle { display: flex }` (not `display: none`)
- [ ] At 900px: sidebar transforms off-screen and `.open` brings it back
- [ ] At 600px: search input and sort select shrink appropriately
- [ ] **No `no-detail` class** on `.paper-title` (removed — all papers should look equal)
- [ ] `#sort-select` has styling for the header (semi-transparent background,
  white text, compact padding) — NOT the sidebar card styling
- [ ] Badge colors exist for all 15 categories

### JavaScript (`js/app.js`)

- [ ] **IIFE wrapper** — entire file is `(function() { ... })();`
- [ ] **15 categories** in CATEGORIES array with matching IDs and labels
- [ ] **`labelToId` map** is built from CATEGORIES (reverses label→id)
- [ ] **Category filter** uses `labelToId[c]` to convert paper category labels
  to IDs before checking `activeCats` (the #1 historical bug)
- [ ] **`createCard()`** gives ALL titles `has-modal` class (not `no-detail`)
- [ ] **`createCard()`** always attaches a click listener that calls `openModal(p)`
- [ ] **`openModal()`** always shows the Summary section (full text, not truncated)
  even for papers without `clinical_insight`
- [ ] **`openModal()`** checks `p.clinical_insight`, `p.relevant_for`, `p.published`
  individually (each wrapped in its own `if`)
- [ ] **Settings** load from `psyarxiv-settings` in localStorage on startup
- [ ] **`applySettings()`** sets `data-theme`, `data-fontsize`, `data-dyslexic` on
  `<html>` element
- [ ] **Auto-hide header** compares `scrollY > lastScrollY` with threshold of 60px
- [ ] **Hash state** encodes/decodes `q`, `off`, `sort` parameters
- [ ] **`esc()` function** creates a textNode and reads innerHTML (XSS prevention)
- [ ] **No `console.log`** left in production code
- [ ] **Sort select listener** is on `#sort-select` (works regardless of where
  the element is in the DOM)

### Data (`data/papers.json`)

- [ ] File is valid JSON (parseable)
- [ ] Root is an array
- [ ] Every paper has: `number`, `title`, `authors`, `categories`, `summary`
- [ ] `categories` values match the 15 valid category labels exactly
- [ ] No duplicate `number` values
- [ ] All `link` values (if present) start with `https://`
- [ ] `osf_id` matches the ID in the link (e.g., osf_id `abc12` → link `https://osf.io/abc12`)

## Step 3: Interaction Pattern Verification

These are the interaction flows that have broken repeatedly. For each one,
trace through the code to verify the chain of events works:

### Settings drawer open/close
1. User clicks ⚙ → `openSettings()` fires
2. `settingsDrawer.classList.add('open')` — drawer slides in from right
3. `settingsOverlay.classList.add('open')` — overlay appears (z-index 90, BELOW drawer at 91)
4. User clicks a theme button → `applySettings()` updates `data-theme`
5. User clicks × or overlay → `closeSettings()` fires
6. Both `.open` classes removed, `body.style.overflow` restored

**Common failure**: overlay z-index ≥ drawer z-index → clicks can't reach drawer buttons.

### Mobile sidebar open/close
1. User clicks ☰ → `openSidebar()` fires
2. `sidebar.classList.add('open')` — sidebar slides in from left
3. `sidebarOverlay.classList.add('open')` — overlay appears
4. User checks/unchecks a category → filter updates, sidebar STAYS open
5. User clicks overlay or ☰ → `closeSidebar()` fires

**Common failure**: category change auto-closes sidebar, or hamburger CSS `display:none`
overrides the mobile `display:flex`.

### Paper card click → modal
1. User clicks any paper title → `openModal(p)` fires
2. Modal shows: title, authors, date, badges, **summary** (always), clinical_insight
  (if present), relevant_for (if present), published (if present), link (if present)
3. User clicks ×, overlay, or Escape → `closeModal()` fires
4. Modal hidden, scroll restored

**Common failure**: papers without `clinical_insight` get `no-detail` class → title
not clickable, or modal is empty because summary isn't shown.

### Auto-hide header on scroll
1. User scrolls down → header slides up via `transform: translateY(-100%)`
2. User scrolls up → header slides back
3. Stats bar follows the same pattern

**Common failure**: header is `position:fixed` but content padding-top is too small,
causing the first card to hide behind the header.

### Category sort with dividers
1. User selects "By category" sort
2. Papers grouped by first category
3. Sticky dividers appear between groups
4. Quick-nav dots appear on the right edge

**Common failure**: `lastRenderedCat` not reset between filter changes → dividers
appear in wrong positions.

## Step 4: Cross-Theme Verification

For each of the 3 themes (light, dark, purple), verify:

1. **Header gradient** is visible and uses theme-appropriate colors
2. **Card backgrounds** contrast with body background (not invisible)
3. **Text is readable** (primary text on card background has sufficient contrast)
4. **Accent color** is visible on badges and buttons
5. **Modal backdrop** is dark enough to see the modal card
6. **Settings drawer** background matches the theme
7. **Links** are visible (accent color, not blending into background)
8. **Search input** text is visible (white text on dark header background)

## Step 5: Responsive Verification

### Desktop (>900px)
- Sidebar is visible as a sticky column on the left
- Sort select is in the header
- Cards have left padding for number alignment
- Quick-nav dots appear in category sort mode

### Tablet (600-900px)
- Sidebar is hidden, hamburger button visible
- Cards have no left padding (padding-left: 0)
- Quick-nav is hidden

### Mobile (<600px)
- Header elements are compact (smaller search, smaller sort)
- Cards are touch-friendly (adequate tap targets)
- Modal has appropriate padding

## Step 6: Report

After completing all checks, report:

1. **PASS/FAIL** for each check
2. **Any errors found** with specific file, line, and fix recommendation
3. **Any warnings** (non-critical but worth noting)
4. **Overall status**: ✅ Ready to deploy / ⚠️ Has warnings / ❌ Has errors

If errors were found and fixed, re-run the automated checker to confirm the fix.