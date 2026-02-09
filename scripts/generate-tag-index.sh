#!/usr/bin/env python3
"""Generates tag-index.md from YAML frontmatter tags in facet/experience README.md files."""

import os
import re
from collections import defaultdict
from pathlib import Path

codex_root = Path(__file__).resolve().parent.parent
output = codex_root / "tag-index.md"

tag_map = defaultdict(list)

for subdir in ["facets", "experiences"]:
    base = codex_root / subdir
    if not base.exists():
        continue
    for entry in sorted(base.iterdir()):
        readme = entry / "README.md"
        if not readme.exists():
            continue

        content = readme.read_text()
        rel_path = f"{subdir}/{entry.name}/"

        title_match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
        tags_match = re.search(r"^tags:\s*\[(.+)\]$", content, re.MULTILINE)

        if not title_match or not tags_match:
            continue

        title = title_match.group(1).strip()
        tags = [t.strip() for t in tags_match.group(1).split(",")]

        for tag in tags:
            if tag:
                tag_map[tag].append((title, rel_path))

with open(output, "w") as f:
    f.write("# Tag Index\n\n")
    f.write("Auto-generated cross-reference of tags to facets and experiences. Regenerate with:\n\n")
    f.write("```bash\n")
    f.write("./scripts/generate-tag-index.sh\n")
    f.write("```\n\n")
    f.write("| Tag | Appears In |\n")
    f.write("|-----|------------|\n")

    for tag in sorted(tag_map.keys()):
        entries = ", ".join(f"[{title}]({path})" for title, path in tag_map[tag])
        f.write(f"| `{tag}` | {entries} |\n")

print(f"Generated {output} with {len(tag_map)} tags.")
