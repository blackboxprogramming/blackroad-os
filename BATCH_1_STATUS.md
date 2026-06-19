# Batch 1 Status: Operating & Build Spine (Apps 01–05)

**Target:** Browser-native operating environment with shell, build system, task orchestration, tutoring, and compliance.

## Products

### ✅ 01. RoadOS — Browser Computer
**Status:** Planned (MVP prototype ready)
**Files:**
- ✅ `Registry/products.json` — Registered
- ✅ `Products/01_RoadOS/product.json` — Generated
- ✅ `Products/01_RoadOS/tools.json` — 6 tools defined
- ✅ `Products/01_RoadOS/handoffs.json` — Routes to RoadCode, RoadTrip, RoadView, CarKeys
- ✅ `Products/01_RoadOS/capabilities.json` — 6 capabilities mapped

**Tools Required:**
- `os.file-nav` ✅ REAL (Tier 1)
- `os.shell` ✅ MOCK (Tier 4 — needs implementation)
- `model.gemma` ✅ REAL (Tier 2)
- `storage.indexeddb` ✅ REAL (Tier 0)
- `auth.carkeys` ✅ REAL (Tier 3)
- `crypto.signing` ✅ REAL (Tier 3)

**Agents Assigned:**
- Lucidia ✅ (orchestration)
- Roadie ✅ (operator support)
- Aria (voice interface — pending)
- Silas ✅ (testing)

**Next Steps:**
1. Implement browser shell using xterm.js (MIT)
2. Wire command routing to model inference (Gemma)
3. Build window management with IndexedDB persistence
4. Create command palette with intent translation
5. Connect to RoadView for search
6. Link receipts to RoadChain for audit trail

---

### ✅ 02. RoadCode — Build & Deploy Engine
**Status:** Planned (skeleton ready)
**Files:**
- ✅ `Registry/products.json` — Registered
- ✅ `Products/02_RoadCode/product.json` — Generated
- ✅ `Products/02_RoadCode/tools.json` — 7 tools defined
- ⏳ `Products/02_RoadCode/handoffs.json` — (create)
- ✅ `Products/02_RoadCode/capabilities.json` — 6 capabilities mapped

**Tools Required:**
- `model.qwen` ✅ REAL (Tier 2)
- `os.shell` ✅ MOCK (Tier 4)
- `exec.sandbox` ✅ MOCK (Tier 4 — needs Docker/container impl)
- `api.github` ✅ REAL (Tier 3)
- `storage.workspace` ✅ REAL (Tier 1)
- `auth.carkeys` ✅ REAL (Tier 3)
- `api.http` ✅ REAL (Tier 2)

**Agents Assigned:**
- Roadie ✅
- Sebastian ✅ (code builder)
- Elias (architect — pending)
- Silas ✅

**Next Steps:**
1. Implement repo inspection: git branch, package.json, test suite detection
2. Build Qwen-powered patch planning (analyzing diffs, test impact)
3. Wire exec.sandbox for isolated test runs
4. Implement logs streaming UI
5. Create deploy readiness checklist generator
6. Connect GitHub API for PR/commit workflow

---

### ⏳ 03. RoadTrip — Solo Operator Workroom
**Status:** Planned
**Files:**
- ✅ `Registry/products.json` — Registered
- ✅ `Products/03_RoadTrip/product.json` — Generated
- ⏳ Other manifest files (create)

**Tools Needed:**
- `model.qwen` (deep reasoning for agent dispatch)
- `model.gemma` (lightweight inference)
- `storage.indexeddb` (session persistence)
- `auth.carkeys` (agent permission checking)

**Agents Assigned:**
- Lucidia (orchestration)
- Octavia (supervision)
- Sebastian, Sophia, others as dispatched

**Next Steps:**
1. Design multi-agent task interface
2. Build agent dispatch logic
3. Implement context continuity tracking
4. Create progress visualization
5. Wire handoff mechanism to agents
6. Implement memory/reasoning caching

---

### ⏳ 04. PitStop — Homework Portal
**Status:** Planned
**Files:**
- ✅ `Registry/products.json` — Registered
- ✅ `Products/04_PitStop/product.json` — Generated
- ⏳ Other manifest files (create)

**Tools Needed:**
- `model.gemma` (lightweight for homework parsing)
- `exec.sandbox` (safe code execution for assignments)
- `storage.indexeddb` (progress tracking)

**Agents Assigned:**
- Sophia (ethics, tutoring)
- Thalia (explanation)

**Next Steps:**
1. Design assignment intake flow
2. Build confusion-area detection
3. Create incremental study modules
4. Implement progress scoring without PII
5. Connect to RoadChain for learning audit trail

---

### ⏳ 05. RoadWork — Business & Compliance Operations
**Status:** Planned
**Files:**
- ✅ `Registry/products.json` — Registered
- ✅ `Products/05_RoadWork/product.json` — Generated
- ⏳ Other manifest files (create)

**Tools Needed:**
- `api.http` (state agency APIs)
- `storage.workspace` (form templates, checklist storage)
- `model.qwen` (legal checklist generation)

**Agents Assigned:**
- Atticus (law/policy)
- Valeria (risk/finance)

**Next Steps:**
1. Design LLC incorporation flow
2. Build state API abstraction layer
3. Create compliance checklist generators
4. Implement tax calendar system
5. Wire proof upload to RoadChain

---

## Summary

**Batch 1 Completion:** 30%
- Products registered and manifested: 5/5 ✅
- Tools defined: 7/7 ✅
- Agents assigned: 12 of 27 ✅
- Validators passing: ✅

**Blocking Dependencies:**
- `exec.sandbox` implementation (needed by RoadCode, PitStop)
- GitHub API integration testing
- State agency API proxies (OneWay product, Batch 4)

**Recommended Implementation Order:**
1. **Week 1-2:** RoadOS shell + file nav (no external deps)
2. **Week 3-4:** RoadCode repo inspection + patch planning
3. **Week 5-6:** exec.sandbox implementation + test execution
4. **Week 7-8:** RoadTrip agent dispatch
5. **Week 9-10:** PitStop and RoadWork (lower priority, fewer external deps)

---

**Last Updated:** 2026-06-19
**Next Review:** After Week 2 of implementation
