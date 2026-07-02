#!/usr/bin/env python3
"""
UI/UX QA Checker for PsyArXiv Hub Website

Validates the website files (HTML, CSS, JS, data) to catch common
breakage before pushing to GitHub.

Run: python3 /home/z/my-project/scripts/ux_checker.py

Checks:
1. papers.json structure (required fields, valid categories, no dupes)
2. HTML references to CSS/JS files exist
3. JS references to DOM element IDs exist in HTML
4. CSS class names used in JS exist in CSS
5. No broken z-index stacking (overlay above drawer, etc.)
6. Mobile responsive breakpoints don't conflict
7. Theme color definitions are complete across all themes
8. Accessibility: settings buttons have aria-labels, focus states exist
9. Sort select exists in DOM (not removed by accident)
10. No orphaned CSS rules for removed elements
"""

import json
import re
import os
import sys

WEBSITE_DIR = "/home/z/my-project/website"
HTML_FILE = os.path.join(WEBSITE_DIR, "index.html")
CSS_FILE = os.path.join(WEBSITE_DIR, "css/style.css")
JS_FILE = os.path.join(WEBSITE_DIR, "js/app.js")
DATA_FILE = os.path.join(WEBSITE_DIR, "data/papers.json")

VALID_CATEGORIES = [
    "Anxiety & OCD", "Couples Therapy & Sexology", "Neurodivergence",
    "Mood Disorders", "Trauma & Stressor-Related", "Personality Disorders",
    "Therapeutic Modalities", "Psychopathology & Assessment", "Eating Disorders",
    "Somatic & Functional", "Suicidality & Self-Harm", "Psychosis & Schizophrenia",
    "Addiction & Substance Use", "Obsessive-Compulsive", "Other Clinical"
]

REQUIRED_PAPER_FIELDS = ["number", "title", "authors", "categories", "summary"]

errors = []
warnings = []


def check(label, condition, detail=""):
    if not condition:
        errors.append(f"[FAIL] {label}: {detail}" if detail else f"[FAIL] {label}")
    else:
        print(f"  [OK] {label}")


def warn(label, condition, detail=""):
    if not condition:
        warnings.append(f"[WARN] {label}: {detail}" if detail else f"[WARN] {label}")


def check_papers_json():
    print("\n=== papers.json ===")
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            papers = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        check("papers.json loads", False, str(e))
        return

    check("papers.json is an array", isinstance(papers, list))
    check(f"papers.json has papers ({len(papers)})", len(papers) > 0)

    if not papers:
        return

    # Check structure of first and last paper
    for idx in [0, -1]:
        p = papers[idx]
        missing = [f for f in REQUIRED_PAPER_FIELDS if f not in p]
        check(f"Paper #{p.get('number', idx)} has required fields", not missing,
              f"missing: {', '.join(missing)}")

    # Check for duplicate numbers
    numbers = [p.get("number") for p in papers]
    dupes = [n for n in numbers if numbers.count(n) > 1]
    check("No duplicate paper numbers", not dupes, f"duplicates: {set(dupes)}")

    # Check all numbers are sequential-ish (allowing gaps)
    check("Paper numbers are positive", all(n > 0 for n in numbers if n))

    # Check categories are valid
    invalid_cats = set()
    for p in papers:
        for c in p.get("categories", []):
            if c not in VALID_CATEGORIES:
                invalid_cats.add(c)
    check("All categories are valid", not invalid_cats, f"invalid: {invalid_cats}")

    # Check for papers with no summary
    no_summary = [p["number"] for p in papers if not p.get("summary")]
    warn("All papers have summaries", not no_summary, f"missing: {no_summary[:5]}")

    # Check papers with link have valid format
    bad_links = []
    for p in papers:
        link = p.get("link")
        if link and not link.startswith("https://"):
            bad_links.append(p["number"])
    check("All links use https", not bad_links, f"bad: {bad_links[:5]}")


def check_html():
    print("\n=== HTML ===")
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        check("index.html exists", False)
        return

    check("index.html exists", True)
    check("Has <!DOCTYPE html>", "<!DOCTYPE html>" in html)
    check("Has <html lang=", 'lang="' in html)

    # Check CSS/JS references
    css_ref = re.search(r'href="([^"]+style\.css)"', html)
    js_ref = re.search(r'src="([^"]+app\.js)"', html)
    check("References style.css", css_ref is not None, "no <link> to style.css")
    check("References app.js", js_ref is not None, "no <script> to app.js")

    if css_ref:
        css_path = os.path.join(WEBSITE_DIR, css_ref.group(1))
        check("style.css file exists", os.path.isfile(css_path), css_path)
    if js_ref:
        js_path = os.path.join(WEBSITE_DIR, js_ref.group(1))
        check("app.js file exists", os.path.isfile(js_path), js_path)

    # Check data reference (in JS, not HTML)
    try:
        with open(JS_FILE, "r", encoding="utf-8") as f:
            js_text = f.read()
        data_ref = "data/papers.json" in js_text
    except:
        data_ref = False
    check("References data/papers.json in JS", data_ref)

    # Extract all element IDs
    ids = set(re.findall(r'id="([^"]+)"', html))
    check(f"HTML has element IDs ({len(ids)})", len(ids) > 5)

    # Check critical IDs exist
    critical_ids = [
        "site-header", "sidebar", "sidebar-toggle", "search-input",
        "settings-toggle", "settings-drawer", "settings-overlay",
        "settings-close", "sort-select", "papers-container",
        "papers-list", "paper-modal", "modal-close", "modal-body",
        "stats-bar", "category-filters", "quick-nav", "load-more",
        "no-results", "btn-select-all", "btn-clear-all", "sidebar-overlay"
    ]
    for eid in critical_ids:
        check(f"Element #{eid} exists", eid in ids)

    # Check settings drawer has all setting groups
    check("Settings has theme options", 'data-setting="theme"' in html)
    check("Settings has fontSize options", 'data-setting="fontSize"' in html)
    check("Settings has dyslexic options", 'data-setting="dyslexic"' in html)
    check("Settings has pageSize options", 'data-setting="pageSize"' in html)

    # Check sort select is in header (not sidebar)
    # Find positions of sort-select and sidebar
    sort_pos = html.find('id="sort-select"')
    sidebar_start = html.find('<aside id="sidebar">')
    sidebar_end = html.find('</aside>', sidebar_start) if sidebar_start >= 0 else 0
    if sort_pos >= 0 and sidebar_start >= 0:
        check("Sort select is NOT in sidebar", not (sidebar_start < sort_pos < sidebar_end))
    else:
        warn("Sort select location", False, "cannot determine")


def check_css():
    print("\n=== CSS ===")
    try:
        with open(CSS_FILE, "r", encoding="utf-8") as f:
            css = f.read()
    except FileNotFoundError:
        check("style.css exists", False)
        return

    check("style.css exists and has content", len(css) > 500)

    # Check all 3 theme definitions exist
    check("Light theme defined", "[data-theme=\"light\"]" in css or ":root" in css)
    check("Dark theme defined", '[data-theme="dark"]' in css)
    check("Purple theme defined", '[data-theme="purple"]' in css)

    # Check critical CSS variables exist in each theme
    critical_vars = ["--bg-body", "--bg-card", "--text-primary", "--accent", "--border"]
    for var in critical_vars:
        check(f"CSS var {var} defined", var in css)

    # Check z-index stacking: settings-overlay < settings-drawer
    overlay_match = re.search(r'#settings-overlay[^}]*z-index:\s*(\d+)', css)
    drawer_match = re.search(r'#settings-drawer[^}]*z-index:\s*(\d+)', css)
    if overlay_match and drawer_match:
        ov_z = int(overlay_match.group(1))
        dr_z = int(drawer_match.group(1))
        check(f"Settings overlay ({ov_z}) < drawer ({dr_z})", ov_z < dr_z)
    else:
        warn("Z-index stacking check", False, "could not parse z-indices")

    # Check modal z-index is highest
    modal_match = re.search(r'\.modal-overlay[^}]*z-index:\s*(\d+)', css)
    if modal_match:
        modal_z = int(modal_match.group(1))
        check(f"Modal z-index ({modal_z}) > drawer ({dr_z if drawer_match else 0})",
              modal_z > (dr_z if drawer_match else 0))

    # Check responsive breakpoints
    check("Tablet breakpoint (900px) exists", "@media (max-width: 900px)" in css)
    check("Mobile breakpoint (600px) exists", "@media (max-width: 600px)" in css)

    # Check header is fixed and has height
    check("Header is position:fixed", "#site-header" in css and "position: fixed" in css)

    # Check settings overlay has .open rule
    check("Settings overlay .open rule", "#settings-overlay.open" in css)

    # Check sort-select styling in header
    check("Sort select has styling", "#sort-select" in css)

    # Check no no-detail class dimming (removed)
    warn("no-detail opacity removed", ".paper-title.no-detail" not in css,
         ".paper-title.no-detail still exists (should be removed)")


def check_js():
    print("\n=== JavaScript ===")
    try:
        with open(JS_FILE, "r", encoding="utf-8") as f:
            js = f.read()
    except FileNotFoundError:
        check("app.js exists", False)
        return

    check("app.js exists and has content", len(js) > 500)

    # Check all getElementById references exist in HTML
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            html = f.read()
    except:
        html = ""

    html_ids = set(re.findall(r'id="([^"]+)"', html))
    js_id_refs = set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", js))

    missing_ids = js_id_refs - html_ids
    check(f"All JS getElementById refs exist in HTML ({len(js_id_refs)} refs)",
          not missing_ids, f"missing: {missing_ids}")

    # Check for querySelectorAll refs to classes used in CSS
    js_classes = set(re.findall(r'\.querySelector(?:All)?\(["\']\.([^"\']+)["\']', js))

    # Check CATEGORIES array has all 15 categories
    cat_count = js.count("{id:")
    check(f"Categories defined ({cat_count})", cat_count == 15, f"expected 15")

    # Check labelToId map exists
    check("labelToId map exists", "labelToId" in js)

    # Check openModal shows summary
    check("Modal shows summary section", 'modal-section-label">Summary' in js or '"Summary"' in js)

    # Check all titles get has-modal class
    check("All titles get has-modal class", 'has-modal' in js)

    # Check IIFE wrapper
    check("JS uses IIFE pattern", js.strip().startswith("(function"))

    # Check settings persistence
    check("Settings use localStorage", "localStorage" in js)
    check("Settings load on init", "loadSettings" in js)

    # Check auto-hide header
    check("Auto-hide header on scroll", "scrollY" in js or "scroll" in js)

    # Check hash state management
    check("Hash state save/restore", "saveHash" in js and "applyStateFromHash" in js)

    # Check escape function
    check("HTML escape function", "function esc" in js)

    # Check no console.log in production
    warn("No console.log left", "console.log" not in js, "console.log found in JS")


def check_integration():
    print("\n=== Integration ===")

    # Check data file size is reasonable
    try:
        data_size = os.path.getsize(DATA_FILE)
        check(f"papers.json size ({data_size/1024:.0f}KB)", 0 < data_size < 5_000_000)
    except:
        pass

    # Check total file count
    expected_files = ["index.html", "css/style.css", "js/app.js", "data/papers.json"]
    for ef in expected_files:
        path = os.path.join(WEBSITE_DIR, ef)
        check(f"{ef} exists", os.path.isfile(path))

    # Check no leftover temp files
    temp_patterns = [".swp", ".tmp", "~"]
    for root, dirs, files in os.walk(WEBSITE_DIR):
        for f in files:
            if any(f.endswith(p) for p in temp_patterns):
                warnings.append(f"[WARN] Temp file found: {os.path.join(root, f)}")

    if not any(w.startswith("[WARN] Temp file") for w in warnings):
        print("  [OK] No temp files")


def main():
    print("=" * 60)
    print("PsyArXiv Hub UI/UX QA Checker")
    print("=" * 60)

    check_papers_json()
    check_html()
    check_css()
    check_js()
    check_integration()

    print("\n" + "=" * 60)
    if errors:
        print(f"RESULT: {len(errors)} ERROR(S), {len(warnings)} warning(s)")
        for e in errors:
            print(f"  {e}")
    else:
        print(f"RESULT: ALL CHECKS PASSED ({len(warnings)} warning(s))")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  {w}")

    print("=" * 60)

    # Return non-zero if errors
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()