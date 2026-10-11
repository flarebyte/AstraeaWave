#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
python3 scripts/validate_design_csv.py
"${FLYB:-flyb}" validate --config doc/design-meta
"${FLYB:-flyb}" generate markdown --config doc/design-meta
# Keep the generated artifact's ending consistent with git whitespace checks.
python3 -c 'from pathlib import Path; p = Path("doc/design/design.md"); p.write_text(p.read_text().rstrip("\n") + "\n")'
