#!/usr/bin/env python3
"""Validates internal markdown links across the Engineering Codex.

Checks relative file links, directory links, and anchor references.
Reports broken links with file, line number, and issue description.

Usage:
    python3 scripts/validate-links.py [directory]

If no directory is specified, scans the entire codex.
"""

import os
import re
import sys
from pathlib import Path

codex_root = Path(__file__).resolve().parent.parent

LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
HEADING_PATTERN = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)


def slugify_heading(heading: str) -> str:
    heading = heading.strip()
    heading = re.sub(r'\*\*(.+?)\*\*', r'\1', heading)
    heading = re.sub(r'\*(.+?)\*', r'\1', heading)
    heading = re.sub(r'`(.+?)`', r'\1', heading)
    heading = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', heading)
    heading = heading.lower()
    heading = re.sub(r'[^\w\s-]', '', heading)
    heading = re.sub(r'[\s]+', '-', heading)
    heading = heading.strip('-')
    return heading


def extract_anchors(filepath: Path) -> set:
    try:
        content = filepath.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return set()

    anchors = set()
    for match in HEADING_PATTERN.finditer(content):
        slug = slugify_heading(match.group(1))
        if slug:
            anchors.add(slug)
    return anchors


def validate_file(filepath: Path, scan_root: Path) -> list:
    issues = []

    try:
        content = filepath.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return issues

    lines = content.split('\n')

    for line_num, line in enumerate(lines, start=1):
        if line.strip().startswith('```'):
            continue

        for match in LINK_PATTERN.finditer(line):
            link_text = match.group(1)
            link_target = match.group(2)

            if link_target.startswith(('http://', 'https://', 'mailto:')):
                continue

            if link_target.startswith('#'):
                anchor = link_target[1:]
                file_anchors = extract_anchors(filepath)
                if anchor not in file_anchors:
                    issues.append({
                        'file': str(filepath.relative_to(codex_root)),
                        'line': line_num,
                        'link': link_target,
                        'issue': f'Anchor not found in file'
                    })
                continue

            if '#' in link_target:
                file_part, anchor_part = link_target.split('#', 1)
            else:
                file_part = link_target
                anchor_part = None

            resolved = (filepath.parent / file_part).resolve()

            if not resolved.exists():
                suggestion = ''
                parent = resolved.parent
                name = resolved.name
                if parent.exists():
                    siblings = [p.name for p in parent.iterdir()]
                    for sib in siblings:
                        if name in sib or sib in name:
                            suggestion = f' (did you mean `{sib}`?)'
                            break

                issues.append({
                    'file': str(filepath.relative_to(codex_root)),
                    'line': line_num,
                    'link': link_target,
                    'issue': f'{"Directory" if file_part.endswith("/") else "File"} not found{suggestion}'
                })
                continue

            if anchor_part and resolved.is_file():
                file_anchors = extract_anchors(resolved)
                if anchor_part not in file_anchors:
                    issues.append({
                        'file': str(filepath.relative_to(codex_root)),
                        'line': line_num,
                        'link': link_target,
                        'issue': f'Anchor `#{anchor_part}` not found in target file'
                    })

    return issues


def main():
    scan_dir = codex_root
    if len(sys.argv) > 1:
        scan_dir = codex_root / sys.argv[1]
        if not scan_dir.exists():
            print(f"Error: Directory '{sys.argv[1]}' not found")
            sys.exit(1)

    md_files = sorted(scan_dir.rglob('*.md'))
    md_files = [f for f in md_files if '.git' not in f.parts]

    all_issues = []
    link_count = 0

    for filepath in md_files:
        try:
            content = filepath.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue

        links = LINK_PATTERN.findall(content)
        internal_links = [l for l in links if not l[1].startswith(('http://', 'https://', 'mailto:'))]
        link_count += len(internal_links)

        issues = validate_file(filepath, scan_dir)
        all_issues.extend(issues)

    print(f"\nLink Validation Report")
    print(f"{'=' * 50}")
    print(f"Files scanned: {len(md_files)}")
    print(f"Internal links checked: {link_count}")
    print(f"Broken links: {len(all_issues)}")

    if not all_issues:
        print(f"\nAll links valid.")
    else:
        print(f"\nBroken Links:")
        print(f"{'-' * 50}")
        for issue in all_issues:
            print(f"  {issue['file']}:{issue['line']}")
            print(f"    Link: {issue['link']}")
            print(f"    Issue: {issue['issue']}")
            print()

    sys.exit(1 if all_issues else 0)


if __name__ == '__main__':
    main()
