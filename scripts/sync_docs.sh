#!/bin/bash
# ============================================================
# दृष्टि (Drishti) — Sync root HTML files to docs/ for GitHub Pages
# Run this after every edit to any root-level .html file
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "  दृष्टि (Drishti) · Syncing HTML to docs/"
echo "  ═══════════════════════════════════════════"

HTML_FILES=(
  "index.html"
  "dashboard.html"
  "how_it_works.html"
  "features.html"
  "ai_demo.html"
)

for f in "${HTML_FILES[@]}"; do
  if [[ -f "$PROJECT_ROOT/$f" ]]; then
    cp "$PROJECT_ROOT/$f" "$PROJECT_ROOT/docs/$f"
    echo "  ✅ Synced: $f → docs/$f"
  else
    echo "  ⚠️  Not found: $f (skipping)"
  fi
done

echo ""
echo "  🎉 All HTML files synced to docs/ successfully."
echo "  Commit and push to deploy to GitHub Pages."
echo ""

