#!/bin/bash
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
# Rebuild the animated diagrams in assets/ from the descriptions in this folder.
#
# The generator, make-diagram.py, is not part of this repository. Point MAKE_DIAGRAM at a copy:
#   MAKE_DIAGRAM=/path/to/make-diagram.py assets/diagrams/build.sh
#
# The generator plays an animation a fixed number of times. These diagrams loop instead, so the
# last step here rewrites the play count. Each file is still complete as a still image.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$(dirname "$HERE")"
MAKE_DIAGRAM="${MAKE_DIAGRAM:-$HOME/.claude/skills/animated-svg/make-diagram.py}"
[ -f "$MAKE_DIAGRAM" ] || {
    echo "generator not found: $MAKE_DIAGRAM (set MAKE_DIAGRAM)" >&2
    exit 1
}

python3 "$MAKE_DIAGRAM" --out "$OUT" "$HERE"/*.txt

for txt in "$HERE"/*.txt; do
    svg="$OUT/$(basename "${txt%.txt}").svg"
    python3 - "$svg" <<'EOF'
import re
import sys

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
text, count = re.subn(r"(animation: [^;}]*? ease-in-out) \d+", r"\1 infinite", text)
if not count:
    sys.exit(f"{path}: no play count found to change")
notice = "<!-- Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE. -->"
if notice not in text:
    end = text.index(">", text.index("<svg")) + 1
    text = text[:end] + "\n" + notice + text[end:]
open(path, "w", encoding="utf-8").write(text)
print(f"{path.rsplit('/', 1)[-1]}: {count} animations set to loop")
EOF
done
