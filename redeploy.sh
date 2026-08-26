#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Fetching origin/master..."
git fetch origin
echo "Resetting to origin/master (discards local commits, keeps untracked bin/ etc)..."
git reset --hard origin/master
echo "Now at: $(git log --oneline -1)"
echo "Done. Restart your radio daemon if needed (e.g. sudo systemctl restart radio)."
