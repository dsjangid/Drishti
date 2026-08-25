#!/bin/bash
# ============================================================
# दृष्टि (Drishti) — AI Lab Launcher
# Starts the Streamlit YOLOv8 Pothole Detection interface
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "  दृष्टि (Drishti) · AI Video Pothole Detection Lab"
echo "  ════════════════════════════════════════════════════"
echo ""

# ── Check Python ──────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "  ❌ Python 3 not found. Please install Python 3.9+ first."
  exit 1
fi

# ── Check model weights ───────────────────────────────────
MODEL_PATHS=("$PROJECT_ROOT/models/drishti_potholedetect_v1.pt" "$PROJECT_ROOT/best (16).pt" "$PROJECT_ROOT/best.pt")
MODEL_FOUND=false

for mp in "${MODEL_PATHS[@]}"; do
  if [[ -f "$mp" ]]; then
    echo "  ✅ Model found: $(basename "$mp")"
    MODEL_FOUND=true
    break
  fi
done

if [[ "$MODEL_FOUND" == false ]]; then
  echo "  ⚠️  WARNING: Model weights not found in expected locations:"
  for mp in "${MODEL_PATHS[@]}"; do
    echo "     - $mp"
  done
  echo ""
  echo "  Please place drishti_potholedetect_v1.pt in the models/ directory."
  echo "  The UI will still launch but will show an error until the model is placed."
  echo ""
fi

# ── Check/Install dependencies ────────────────────────────
echo "  🔍 Checking Python dependencies..."

if ! python3 -c "import streamlit" 2>/dev/null; then
  echo "  📦 Installing requirements..."
  pip3 install -r "$PROJECT_ROOT/requirements.txt" --quiet
fi

# ── Launch ────────────────────────────────────────────────
echo ""
echo "  🚀 Launching AI Lab at http://localhost:8501"
echo "     Press Ctrl+C to stop."
echo ""

cd "$PROJECT_ROOT"
python3 -m streamlit run ui.py \
  --server.port 8501 \
  --server.headless false \
  --browser.gatherUsageStats false

