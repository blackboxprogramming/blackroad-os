# BlackRoad OS Implementation Roadmap

## Current State (2026-06-19)

**Completed:**
- ✅ Registry system architecture (products, agents, carkeys, orgs, domains, lanes)
- ✅ GloveBox tool registry with 15 seed tools
- ✅ RoadChain receipt ledger foundation
- ✅ CarKeys expanded to 20 permission lanes
- ✅ Agent ecosystem structure (folders, permissions, handoffs)
- ✅ Product manifests (tools, handoffs, capabilities)
- ✅ Comprehensive validators for all registries
- ✅ Architecture documentation

**Not Yet Started:**
- Product implementations (UI, business logic)
- Agent implementations (reasoning, tool execution)
- Tool implementations (most tools are MOCK or PLANNED)
- Frontend (index.html enhancements)
- CI/CD integration
- Desktop deployment

---

## Implementation Phases

### **Phase 1: Foundation & Batch 1 MVP (Weeks 1–4)**

**Goal:** Browser-native operating environment that can route commands to products

**Deliverables:**
1. RoadOS shell UI with command palette
2. File navigation (os.file-nav tool)
3. Intent routing to RoadCode and other products
4. Persistence (IndexedDB)
5. RoadChain receipt logging

**Files to Create:**
- `index.html` — Enhanced with app router, window manager
- `frontend/roados/shell.js` — Terminal emulation
- `frontend/roados/intent-router.js` — Command routing logic
- `frontend/shared/receipt-logger.js` — RoadChain integration
- Tests + CI integration

**Success Criteria:**
- User can type command in shell
- Command routes to correct product
- Window opens without page reload
- Session persists across refreshes
- All actions logged to RoadChain

**Risk:** Medium (new architecture, browser limitations)

---

### **Phase 2: Build System & Batch 1 Complete (Weeks 5–8)**

**Goal:** End-to-end build, test, deploy pipeline for code repositories

**Deliverables:**
1. RoadCode repo inspection
2. Qwen-powered patch planning
3. Test execution in sandbox (exec.sandbox)
4. GitHub PR/commit workflow
5. Deploy readiness verification

**Files to Create:**
- `frontend/roadcode/repo-inspector.js`
- `frontend/roadcode/patch-planner.js`
- `backend/sandbox/executor.js` or Docker config
- `backend/github/integration.js`
- `frontend/roadcode/deploy-checklist.js`

**Success Criteria:**
- RoadCode can analyze repo structure
- Qwen generates patch planning output
- Tests execute in sandbox and report results
- Can commit and PR to GitHub
- Deploy checklist prevents incomplete deployments

**Risk:** High (sandbox exec, external API integration)

---

### **Phase 3: Agent Ecosystem & Orchestration (Weeks 9–12)**

**Goal:** Multi-agent coordination system where agents can hand off work

**Deliverables:**
1. RoadTrip UI for long-running tasks
2. Agent dispatch system (Lucidia orchestrator)
3. Agent handoff mechanism (Roadie → Sebastian → Silas, etc.)
4. Task progress tracking
5. Agent memory/reasoning caching

**Files to Create:**
- `frontend/roadtrip/task-orchestrator.js`
- `backend/agents/dispatcher.js`
- `backend/agents/lucidia.js` (sample implementation)
- `frontend/shared/agent-memory.js`
- Tests for handoff graph

**Success Criteria:**
- User can define multi-step task
- Lucidia assigns agents correctly
- Agents hand off work with context
- Task completion is logged
- Agent memory persists across sessions

**Risk:** Medium-High (coordination complexity)

---

### **Phase 4: Remaining Products (Weeks 13–20)**

**Goal:** Implement remaining products from Batch 2-5

**Priority Order (by risk/value):**

**Tier A (Critical, next after Phase 3):**
- **CarKeys (07)** — Permissions system (gates everything else)
- **RoadChain (11)** — Receipt verification (audit trail)
- **GloveBox (24)** — Tool discovery UI
- **OneWay (16)** — Data pipeline for privacy

**Tier B (Important, depends on Tier A):**
- **BackRoad (06)** — Social feed aggregator
- **RoadView (10)** — Master search
- **CarPool (14)** — Multi-operator workspaces
- **HighWay (18)** — Infrastructure registry

**Tier C (Nice-to-have, can ship MVP without):**
- **RoadBook (08)** — Publishing
- **RoadWorld (09)** — Worldbuilding
- **PitStop (04)** — Tutoring
- **RoadWork (05)** — Compliance
- **RoadSide (12)** — Help widget
- **RoadBand (17)** — Audio profiling
- **RoadSport (19)** — Physics sim
- **OfficeRoad (20)** — Spatial workspace
- **RoadStream (21)** — Media subscriptions
- **RoadShow (22)** — Programming blocks
- **RoundAbout (23)** — Trip preparation
- **RoadMap (25)** — Status dashboard
- **RoadWire (26)** — Async comms
- **Detour (27)** — Transit routing

---

## Critical Path Dependencies

```
RoadOS (01)
  ↓ depends on
RoadChain (11) [receipts]
  ↓ depends on
CarKeys (07) [permissions]
  ↓ depends on
GloveBox (24) [tool discovery]

RoadCode (02)
  ↓ depends on
RoadChain (11) [deploy audit]
  ↓ depends on
HighWay (18) [networking]

RoadTrip (03)
  ↓ depends on
RoadChain (11) [task logging]
  ↓ depends on
GloveBox (24) [tool dispatch]
```

**Critical Non-Negotiable:**
1. RoadChain (receipts)
2. CarKeys (permissions)
3. GloveBox (tool registry)

Everything else builds on top of these three.

---

## Tool Implementation Priorities

**Must Implement (Phase 1-2):**
- `os.file-nav` — REAL (Tier 1)
- `storage.indexeddb` — REAL (Tier 0)
- `crypto.signing` — REAL (Tier 3) [for RoadChain]
- `auth.carkeys` — REAL (Tier 3) [for permissions]
- `model.gemma` — REAL (Tier 2) [already exists]
- `model.qwen` — REAL (Tier 2) [already exists]

**Should Implement (Phase 2-3):**
- `os.shell` — MOCK → REAL (Tier 4)
- `exec.sandbox` — MOCK → REAL (Tier 4)
- `api.http` — REAL (Tier 2)
- `api.github` — REAL (Tier 3)
- `storage.workspace` — REAL (Tier 1)

**Can Implement Later (Phase 4+):**
- `network.proxy` — PLANNED (Tier 4)
- `data.vector-search` — PLANNED (Tier 2)
- All media/audio tools (lower priority)

---

## Quality Gates (Before Each Merge)

### Before Phase 1 PR Merge:
- [ ] RoadOS shell renders in browser
- [ ] Command palette accepts input
- [ ] At least 1 product routes work (e.g., → RoadCode)
- [ ] IndexedDB persistence works
- [ ] All validators pass
- [ ] RoadChain logging works for basic actions
- [ ] 80%+ test coverage for critical paths

### Before Phase 2 PR Merge:
- [ ] RoadCode can inspect repo (git info available)
- [ ] Qwen patch planning produces usable output
- [ ] exec.sandbox isolates code execution
- [ ] GitHub API calls work (read + write)
- [ ] Tests run and report in UI
- [ ] Deploy checklist blocks unsafe deployments
- [ ] All RoadChain receipts for deploy actions are valid

### Before Phase 3 PR Merge:
- [ ] RoadTrip task definition UI works
- [ ] Lucidia can dispatch agents to tasks
- [ ] Agent handoffs preserve context
- [ ] Multi-step workflows complete successfully
- [ ] Agent memory caching works across restarts
- [ ] Handoff graph validated (no cycles)

---

## Estimated Timeline

- **Weeks 1-4:** Phase 1 (RoadOS MVP) — 30%
- **Weeks 5-8:** Phase 2 (RoadCode) — 25%
- **Weeks 9-12:** Phase 3 (Agents) — 25%
- **Weeks 13-20:** Phase 4 (Remaining) — 20%

**Total: 20 weeks (~5 months)**

If parallelized with multiple developers:
- **Agent 1:** RoadOS + RoadCode (Weeks 1-8)
- **Agent 2:** CarKeys + RoadChain + GloveBox (Weeks 1-6, parallel)
- **Agent 3:** Remaining products (Weeks 7-20, after Tier A)

→ **Parallelized estimate: 12-14 weeks (~3 months)**

---

## Success Metrics

### MVP (End of Phase 2):
- [ ] User can type command in RoadOS
- [ ] Command routes to RoadCode
- [ ] Can inspect repo, plan patch, run tests
- [ ] All actions logged immutably to RoadChain
- [ ] Permissions enforced via CarKeys
- [ ] 70%+ test coverage

### Launch (End of Phase 3):
- [ ] RoadTrip multi-agent orchestration works
- [ ] Agents can hand off work across team
- [ ] CarPool workspaces for multi-user
- [ ] 85%+ test coverage
- [ ] CI/CD pipeline automated

### Full Platform (End of Phase 4):
- [ ] All 27 products discoverable + usable
- [ ] 1,729 tools catalogued in GloveBox
- [ ] Complete audit trail in RoadChain
- [ ] 95%+ test coverage
- [ ] Deployed to production

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Browser limitations (file access, execution) | High | Use ServiceWorker + WebAssembly sandbox |
| External API integration (GitHub, state APIs) | High | Mock APIs in dev, test with real in staging |
| Agent coordination complexity | Medium | Start with simple 2-agent handoff, expand |
| Qwen/Gemma model latency | Medium | Implement caching, async UI updates |
| Registry drift (generated files out of sync) | High | Automated sync + CI checks prevent merges |
| Circular dependencies in agent handoffs | Medium | Lucidia validates graph on startup |
| Performance (27 products in one tab) | Medium | Lazy load products, IndexedDB indexing |

---

## Success Factors

1. **Registry as truth.** Never hand-edit generated files. Sync scripts must run automatically.
2. **Receipts first.** Log to RoadChain before returning from any action. Trust the ledger.
3. **Permissions are code.** CarKeys lanes are not decorative; they gate actual execution.
4. **Agents are real.** Don't mock orchestration; implement actual handoff logic from day 1.
5. **Test at boundaries.** Unit test tools, integration test handoffs, end-to-end test workflows.
6. **Documentation is code.** ARCHITECTURE.md and BATCH_*_STATUS.md are maintained in parallel with code.

---

**Last Updated:** 2026-06-19
**Review Cycle:** Every 2 weeks (align with sprint ends)
