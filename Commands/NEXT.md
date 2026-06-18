# Commands — NEXT

**Immediate next action:** Document the 17 core commands with examples and agent assignments.

**Current state:**
- Commands registered in Registry/lanes.json (command lane subset)
- Command folder exists but holds only scaffold
- No per-command documentation yet

**Next steps:**
1. Extract command definitions from Registry/lanes.json
2. Create per-command doc: `cmd-slug.md` with:
   - Command name + number
   - Syntax (flags, args, sub-commands)
   - Primary agents (who executes)
   - Supported products
   - Capabilities used
   - Example usage
   - Permissions required (CarKeys)
3. Create ROUTING.md, CONTROL.md, DATA.md, HANDOFF.md, META.md per category
4. Create SCHEMA.md for command syntax specification
5. Create EXAMPLES.md with real workflow chains

**Owner:** Roadie (Agent 02) / Command documentation lead

**Status:** Scaffold phase — awaiting documentation extraction
