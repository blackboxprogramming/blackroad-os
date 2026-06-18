# Archive — RULES

Local rules for archiving and managing historical documentation.

## Archiving Decision Criteria

Archive when:
1. **Document superseded** — new version replaces old one (keep old for reference)
2. **Feature cancelled** — planned product/feature not pursued
3. **Decision reversed** — past decision overturned with new reasoning
4. **Research not pursued** — investigation concluded no action needed
5. **Code/config outdated** — no longer relevant to current version

Do NOT archive when:
- Document updated in place — use versioning in document instead
- Still active but in different location — move don't archive
- Temporary/ephemeral content (drafts, scratch notes) — delete instead

## Archiving Procedure

1. **Identify superceded item** (old doc, abandoned feature, etc.)
2. **Create archive filename**: `ORIGINAL-FILENAME-archived-YYYY-MM-DD.md`
3. **Add archive header** (2-3 lines at top):
   ```markdown
   # [Original title] — ARCHIVED

   > ⚠️ **Archived:** [YYYY-MM-DD] — Superseded by [link to new version] | Reason: [brief reason]
   ```
4. **Move file**: `git mv Original Archive/Original-archived-YYYY-MM-DD.md`
5. **Add cross-reference** in new location (if applicable):
   - Link from Index/NEXT pointing to archived version for reference
   - Only 1-2 sentences, not detailed discussion
6. **Commit**: Single commit with message `Archive: [item name] → Archive/ — reason`

## Archive Naming

Standard pattern: `CATEGORY-DESCRIPTION-archived-YYYY-MM-DD.md`

Examples:
- `doc-mesh-topology-v1-archived-2026-07-15.md` (superseded doc)
- `feature-wireless-sync-archived-2026-07-15.md` (cancelled feature)
- `decision-use-sqlite-archived-2026-07-15.md` (decision reversed)
- `research-meshtastic-range-archived-2026-07-15.md` (research not pursued)

## Cross-Referencing

When archiving a doc with a new version:

**In archive file (at top):**
```markdown
> Archived [date]: Replaced by [path to new file]
```

**In new file (in comment or NOTE):**
```markdown
> For previous version, see [path to archived file]
```

**In NEXT.md (brief mention only):**
```markdown
- `ARCHITECTURE.md` (see Archive/ARCHITECTURE-archived-2026-06-18.md for v1)
```

## Invariants

- Archive files are immutable — never edit after archiving
- Archive headers must include date and reason
- Cross-references must link both directions
- Archived receipts stay in Archive/, not linked from Receipts/
- Archive searches must work (`archive-search.mjs pattern`)
- Quarterly freeze must document bulk archives with receipts

## Maintenance

- Theodosia (Agent 23) archives and maintains cross-references
- Archive consistency checked quarterly (no orphaned/unlinked items)
- Archive contents reviewed annually for complete purges (if allowed)
