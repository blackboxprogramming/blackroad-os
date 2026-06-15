# Open Source Alternatives — RoadOS

## Purpose
Tools and patterns that can help build the browser-native workspace, command routing, file/memory surface, and safe agent integration.

## Candidate families
- Browser-based desktop / workspace frameworks (Tauri, Electron alternatives, web-based OS shells)
- Command palette / intent routing libraries
- In-browser file systems and virtual filesystems
- Memory / context management (local-first databases, CRDTs, vector stores for memory map)
- Agent orchestration / tool-calling frameworks that run in browser or edge
- Receipt / provenance logging (simple hash-chain or local ledger libraries)

## Candidate tools

### Tauri + webview
Use: Build native-feeling desktop shell that is still browser-native at core.
License: MIT / Apache
Commercial review: Likely safe
BlackRoad fit: Strong for local-first workspace with system integration
Risks: Some native permissions need CarKeys gating
Status: candidate

### Monaco Editor + custom command layer
Use: Rich code/file editing surface inside workspace
License: MIT
Commercial review: Safe
BlackRoad fit: Excellent for terminal + file + agent surfaces
Risks: Low
Status: candidate

### LocalForage / IndexedDB + CRDT libs (e.g. yjs)
Use: Persistent local memory and conflict-free context sync
License: Various open
Commercial review: Safe for most
BlackRoad fit: Core for memory map and workspace state
Risks: Data model must align with RoadChain receipts
Status: candidate

### WebLLM / Transformers.js + tool calling
Use: Run small models locally for intent inference and safe routing suggestions
License: MIT / Apache
Commercial review: Safe
BlackRoad fit: Enables on-device intent classification without external calls
Risks: Model size and performance on low-end devices
Status: candidate_review_required

## License rule
All candidates require license review before marking commercial-safe. AGPL/SSPL/BSL tools need Portia review. Prefer permissive licenses for core workspace components.