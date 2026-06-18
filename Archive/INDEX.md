# Archive — INDEX

Map of superseded, historical, and frozen documentation.

**Purpose:** Archive holds the complete history of BlackRoad OS decisions, iterations, and abandoned approaches. Nothing is deleted — superseded items are archived here instead.

## Archive Organization

| Category | Content | Retention |
|----------|---------|-----------|
| Superseded docs | Old versions of canon/spec docs | indefinite |
| Abandoned features | Features not shipped | indefinite |
| Decision reversals | Decisions overturned with new reasoning | indefinite |
| Historical research | Research not pursued | indefinite |
| Incident post-mortems | Resolved incidents (also in Receipts/) | indefinite |

## Archiving Practice

When a document or approach is superseded:

1. Move file to Archive/ with date suffix: `ORIGINAL-NAME-archived-YYYY-MM-DD.md`
2. Keep original location's link to archived version in NEXT.md or INDEX.md
3. Add cross-reference header in archived file pointing to new version (if applicable)
4. Commit archive move separately from new work

Example:
- Old: `Docs/ARCHITECTURE.md` (v1)
- Archived: `Archive/ARCHITECTURE-archived-2026-06-18.md`
- New: `Docs/ARCHITECTURE.md` (v2)
- Archive file includes: "Superseded by `Docs/ARCHITECTURE.md` (v2), committed on 2026-06-18"

## Current Status

**Folder:** Exists but empty — no decisions reversed or docs superseded yet

## Archive Queries

Planned scripts:
- `node scripts/archive-list.mjs` — list all archived items
- `node scripts/archive-search.mjs pattern` — search archived content
- `node scripts/archive-restore.mjs pattern` — restore specific item

## Freezing History

Every quarterly freeze:
1. Move abandoned/superseded items from active folders to Archive/
2. Update Archive/INDEX.md with summary
3. Create Archive/FREEZE-YYYY-QN.md receipt with what was archived + why
4. Commit freeze as single commit with message "Archive freeze: Q{N} {year}"

## Anti-Pattern to Avoid

❌ Deleting old files — move to Archive/ instead
❌ Editing archived docs — create new version, link from archive
❌ Forgetting cross-references — always link from new location to archive
