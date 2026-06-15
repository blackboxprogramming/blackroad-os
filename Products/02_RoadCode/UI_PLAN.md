# UI Plan — RoadCode

## First-run experience
User connects or points RoadCode at a repo/folder. RoadCode inspects it and shows a clear summary of what exists, what is missing, and suggested next steps.

## Main screens
1. Project Dashboard – Overview of the current project, status, and quick actions.
2. Inspection View – Detailed breakdown of repo structure, dependencies, and issues.
3. Patch Planner – Where proposed changes are reviewed and approved.
4. Test & Deploy Readiness – Checklist and execution surface.
5. History & Receipts – Past actions with proof links.

## Empty states
- No project connected: Clear prompt to select or connect a repo/folder.
- Fresh project: Helpful onboarding with common first steps.

## Primary flows
1. Inspect repo → Get summary + missing pieces
2. Generate patch plan → Review risk → Approve
3. Run tests → View results
4. Prepare deploy plan → Get approval → Execute (with receipt)

## Navigation
- Top-level command/search bar (integrated with RoadOS)
- Sidebar: Projects | Recent | Capabilities
- Agent rail for assistance

## Agent presence
RoadCode should prominently show which agents are helping (e.g., Elias for coding, Silas for infrastructure).

## Receipts/proof display
Every meaningful action (inspection, patch, test, deploy plan) should show a clear RoadChain receipt link.

## Mobile considerations
Core flows should work well on tablet; full patch review may be desktop-optimized.

## Black-and-white baseline
All screens must be fully functional and clear in simple black-and-white before any color or visual polish is added.