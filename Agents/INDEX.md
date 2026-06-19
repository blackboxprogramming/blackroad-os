# Agents — INDEX

Map of the 27 BlackRoad agents, their roles, responsibilities, and activity.

**Canonical registry:** `Registry/agents.json` (validated by `scripts/validate-agents.mjs`)

## Agent Roster

| # | Name | Role | Slug | Folder | Status |
|---|------|------|------|--------|--------|
| 01 | Lucidia | Orchestration and continuity keeper | `lucidia` | `01_Lucidia/` | registered |
| 02 | Roadie | Operator support and RoadOS guide | `roadie` | `02_Roadie/` | registered |
| 03 | Sophia | Judgment, ethics, and tutoring | `sophia` | `03_Sophia/` | registered |
| 04 | Cecilia | Language / communication | `cecilia` | `04_Cecilia/` | registered |
| 05 | Sebastian | Code builder | `sebastian` | `05_Sebastian/` | registered |
| 06 | Elias | Code architect | `elias` | `06_Elias/` | registered |
| 07 | Silas | Tester / verifier | `silas` | `07_Silas/` | registered |
| 08 | Gaia | Environment / systems | `gaia` | `08_Gaia/` | registered |
| 09 | Atticus | Law / policy / review | `atticus` | `09_Atticus/` | registered |
| 10 | Valeria | Risk / finance / judgment | `valeria` | `10_Valeria/` | registered |
| 11 | Alice | File / index assistant | `alice` | `11_Alice/` | registered |
| 12 | Octavia | Supervisor | `octavia` | `12_Octavia/` | registered |
| 13 | Anastasia | Memory / continuity | `anastasia` | `13_Anastasia/` | registered |
| 14 | Lyra | Music / rhythm / media | `lyra` | `14_Lyra/` | registered |
| 15 | Sapphira | Visual / polish | `sapphira` | `15_Sapphira/` | registered |
| 16 | Ophelia | Research | `ophelia` | `16_Ophelia/` | registered |
| 17 | Thalia | Teaching / explanation | `thalia` | `17_Thalia/` | registered |
| 18 | Aria | Voice / interface | `aria` | `18_Aria/` | registered |
| 19 | Seraphina | Security / protection | `seraphina` | `19_Seraphina/` | registered |
| 20 | Gematria | Numbers / math / pattern | `gematria` | `20_Gematria/` | registered |
| 21 | Cicero | Writing / rhetoric | `cicero` | `21_Cicero/` | registered |
| 22 | Portia | Legal argument / opposition | `portia` | `22_Portia/` | registered |
| 23 | Theodosia | Records / governance | `theodosia` | `23_Theodosia/` | registered |
| 24 | Celeste | Planning | `celeste` | `24_Celeste/` | registered |
| 25 | Calliope | Story / publishing | `calliope` | `25_Calliope/` | registered |
| 26 | Cordelia | Care / human sensecheck | `cordelia` | `26_Cordelia/` | registered |
| 27 | Olympia | Final review / launch | `olympia` | `27_Olympia/` | registered |

## Key Principles

- **Roadie (Agent 02) is an agent only** — never a product. Support function, not owned product.
- **Agents request; Operator approves** — Alexa (Operator) gates all major decisions
- **CarKeys gates access** — Permissions controlled via CarKeys lane, not per-agent
- **RoadChain records activity** — All significant actions produce receipts
- **Context handoff across one road** — Each agent passes context to next, no silos

## Agent Folder Structure

Each agent has:
- `README.md` — Overview + role
- `INDEX.md` — Agent's domain map
- `STATUS.md` — Current state + progress
- `NEXT.md` — Immediate next action
- `RESPONSIBILITIES.md` — Product assignments (planned)
- `ACTIVITY.md` — Recent work + receipts (planned)
- `HANDOFF_PROTOCOL.md` — Context passing patterns (planned)
- `_permissions/` — CarKeys matrix + access control
- `_handoffs/` — Handoff templates
- `_receipts/` — Proof trails + activity records

## Current Workflow

1. **Agents propose** → work request to Operator
2. **Operator approves** → decision + scope
3. **CarKeys gates** → permissions verified
4. **Agent executes** → work on assigned products/domains
5. **RoadChain records** → receipt filed in Receipts/
6. **Hand off** → context passed to next agent or back to Operator

## Immediate Next Steps

See NEXT.md for Phase 2 roadmap.
