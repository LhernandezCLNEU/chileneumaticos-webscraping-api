#!/usr/bin/env bash
set -euo pipefail

echo "Setup Selenium helper script"

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
  echo "Activating virtualenv .venv"
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "Upgrading pip and installing Python packages: selenium, webdriver-manager"
pip install --upgrade pip
pip install selenium webdriver-manager

if command -v brew >/dev/null 2>&1; then
  echo "Homebrew detected. Installing Chrome (or Chromium)"
  # prefer google-chrome; fall back to chromium
  if brew list --cask google-chrome >/dev/null 2>&1; then
    echo "google-chrome already installed"
  else
    brew install --cask google-chrome || brew install --cask chromium || true
  fi
else
  echo "Homebrew not found. Please install Chrome/Chromium manually for Selenium testing."
fi

echo "Done. To run the example scraper (dry-run):"
echo "  python scripts/run_example_scraper.py --url https://example.com/ --dry-run"
