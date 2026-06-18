# Commands — RULES

Local rules for command documentation and specification in this folder.

## Naming Conventions

- Command docs: `cmd-slug.md` (e.g., `cmd-hand-off.md`)
- Category docs: `ROUTING.md`, `CONTROL.md`, `DATA.md`, `HANDOFF.md`, `META.md`
- Syntax spec: `SCHEMA.md`
- Examples: `EXAMPLES.md`

## Command Document Structure

Each command doc must include:

1. **Command name** and assigned number (if any)
2. **Syntax** — full command line format with flags and arguments
3. **Description** — what the command does in one sentence
4. **Primary agents** — who can execute (from Registry/agents.json)
5. **Supported products** — which products this command targets
6. **Capabilities** — which capabilities it requires
7. **Permissions** — CarKeys lane requirements
8. **Examples** — 2-3 realistic usage examples
9. **Exit codes** — success/error return codes
10. **Related commands** — links to related commands (chaining)

## Syntax Specification

All commands follow the format:

```
roadie <command> [sub-command] [options] [arguments]
```

- Options: `--flag value` or `-f value`
- Aliases: Short form in parens `(a)`
- Optional args: `[arg]`
- Required args: `<arg>`

## Invariants

- Every command must be backed by agent assignment
- Every command must map to at least one capability
- No command can bypass CarKeys permissions
- Commands must document fallback/error behavior
- Deprecated commands must reference their replacement

## Maintenance

- Commands sync with Registry/lanes.json via CI validators
- Changes to command registry require doc updates
- Docs reviewed by Roadie (Agent 02) or Octavia (Agent 12)
