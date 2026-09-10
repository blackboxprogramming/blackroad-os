# UI Plan — RoadOS

## First-run experience
New user sees a clean one-tab workspace with:
- Prominent command/search dock at top
- Product launcher grid (27 products with one-line definitions)
- Empty workspace panels that explain themselves
- Quick "Route my first intent" prompt
- Agent rail (collapsed by default)

Black-and-white baseline first. Color accents (green for safe routes, pink for memory/operator attention) added only after core flows work.

## Main screens
1. Workspace home (command dock + product launcher + active context strip)
2. File surface / memory map viewer
3. Terminal / command output panel
4. Agent presence rail (who is helping right now)
5. Receipt / provenance drawer
6. Settings / layout customizer

## Empty states
- No files yet: "Drop files here or route a command to create context"
- No active route: "Type what you want to do — I’ll route it safely"
- No agents: "Invite Roadie, Lucidia, or others when you need help"

## Primary flows
1. User types intent → infer → show safe route options → execute or hand off
2. Open file from memory/git → view + edit in context + write receipt if changed
3. Launch product from launcher → hand off context cleanly
4. Ask agent for help inside workspace → scoped CarKeys grant → visible session

## Navigation
- Command palette (Cmd/Ctrl+K) is primary navigation
- Product launcher always visible or one click away
- Breadcrumbs show current route + previous context
- Receipt drawer accessible from any screen

## Agent presence
Agents appear in the right rail with role, permission scope, and last action. User can approve/revoke per session.

## Receipts/proof display
Important state changes (file saved, route executed, agent action) show a small receipt badge that expands to full RoadChain proof.

## Mobile considerations
Command dock becomes bottom sheet. Product launcher is a clean grid. File surface uses responsive cards. Agent rail collapses to floating action button.

## Black-and-white baseline
All core flows must be fully usable with no color, no icons, and minimal CSS. Visual polish comes after functionality and safety.