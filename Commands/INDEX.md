# Commands — INDEX

Map of BlackRoad OS operator command surface. 17 core commands + command variants.

## Core Command Categories

| Category | Count | Examples | Docs |
|----------|-------|----------|------|
| Navigation | 3 | go, jump, look | See ROUTING.md |
| Control | 4 | start, stop, pause, reset | See CONTROL.md |
| Data | 5 | read, write, sync, query, export | See DATA.md |
| Context | 3 | hand-off, load, save | See HANDOFF.md |
| Meta | 2 | help, status | See META.md |

## Command Registry

All commands registered in `Registry/lanes.json` under command lane.
Each command maps to:
- Primary agent(s) responsible for execution
- Supported products
- Permissions (via CarKeys gate)
- Capabilities involved

## Command Variants

Commands support:
- Flags (--flag or -f)
- Aliases (short + long forms)
- Sub-commands (cmd subcommand)
- Chaining (cmd1 | cmd2)

See SCHEMA.md for command syntax specification.

## Current Status

**Complete:** Command definitions in Registry/lanes.json
**In progress:** Per-command documentation + examples
**Planned:** Interactive help system integration + CLI harness
