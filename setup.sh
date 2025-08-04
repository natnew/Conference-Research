#!/bin/sh
# Setup script to ensure Playwright browsers are available for crawl4ai
# Run during Streamlit build step

set -e

# Download required browser for crawl4ai
type crawl4ai-setup >/dev/null 2>&1 && crawl4ai-setup || python -m playwright install chromium
