# Validate Links Command

Scans all markdown files in the Engineering Codex for broken internal links and anchor references. Reports any that don't resolve.

## Usage

```
Validate codex links
```

Or:
```
Check for broken links in the codex
```

Or scoped:
```
Validate links in facets/security/
```

## Behavior

1. Determine scope:
   - If no scope specified, scan all `.md` files in the codex
   - If a directory is specified, scan only within that directory
2. For each markdown file, find all links:
   - **Relative file links**: `[text](../path/to/file.md)` — verify the target file exists
   - **Relative directory links**: `[text](../facets/security/)` — verify the directory exists
   - **Anchor links**: `[text](#section-name)` — verify the anchor exists in the current file
   - **Cross-file anchors**: `[text](../file.md#section)` — verify both the file and anchor exist
3. Skip external links (http/https) — these require network access and are out of scope
4. Report findings

## Output Format

### All Links Valid

```
Link validation complete. Checked [X] links across [Y] files. All links valid.
```

### Broken Links Found

```markdown
## Broken Links Report

**Files scanned:** [Y]
**Links checked:** [X]
**Broken:** [Z]

### Broken Links

| File | Line | Link | Issue |
|------|------|------|-------|
| facets/security/README.md | 15 | `../developer-experience/` | Directory not found |
| facets/api-design/options.md | 42 | `#hateoas-assessment` | Anchor not found in file |
| experiences/onboarding/product.md | 78 | `../../facets/refactoring/best-practices.md` | File not found (did you mean `refactoring-and-extraction`?) |

### Suggestions

- For renamed directories, update the link to the new path
- For missing anchors, check if the heading was renamed
- Run `validate-links` again after fixes to confirm resolution
```

## Automated Alternative

For CI or scripted use, run the Python validation script directly:

```bash
python3 scripts/validate-links.py
```

This produces the same report as the command but can be integrated into a pre-commit hook or CI pipeline.

## Related Resources

- [Content Freshness Audit](../skills/content-freshness-audit/SKILL.md) — Broader content health check
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Link conventions
