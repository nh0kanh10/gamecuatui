# 🚀 Engine 2.0 Upgrade Roadmap

Based on architectural review, the following upgrades are planned to transition from "Prototype" to "Production-Ready Engine".

## 1. Performance & Scalability (Phase 6)
**Goal**: Handle large entity counts and complex simulations.

- [ ] **Pydantic Optimization**
  - Switch to `mode="python"` for validation speed.
  - Evaluate `msgspec` or `attrs` for component-heavy paths if Pydantic becomes a bottleneck.
- [ ] **Database I/O**
  - Implement **Write-behind buffering** (commit every X ticks/actions).
  - Enable SQLite WAL (Write-Ahead Logging) mode.
  - Batch writes for bulk updates.
- [ ] **ECS Optimization**
  - Implement **Archetype-based storage** (dict-of-lists) for cache locality.
  - Add **EntityIndex** for fast component lookups (`entities_with[ComponentType]`).

## 2. Neurosymbolic Layer (Phase 3-4)
**Goal**: Enhance AI coherence and memory.

- [ ] **Model Separation**
  - **Parser**: Keep small/fast (e.g., Qwen 2.5 3B, Llama 3 8B).
  - **Narrator**: Use larger/creative models (e.g., Mistral Large, Gemini Pro).
- [ ] **Context Rehydration Layer** (The "Brain")
  - **StateContextBuilder**: Convert ECS state → Prompt context.
  - **MemoryContextBuilder**: Retrieve lore/history via ChromaDB.
  - **FinalPromptBuilder**: Assemble strict inputs for AI.

## 3. System Orchestration (Phase 3)
**Goal**: Decouple systems and enable async events.

- [ ] **EventBus / Signal System**
  - Publish/Subscribe events: `OnMove`, `OnAttack`, `OnDeath`.
  - Allow systems to react to events without direct coupling.
- [ ] **SystemScheduler**
  - Manage system execution order.
  - Handle async AI queries parallel to game logic.

## 4. Maintainability (Immediate)
**Goal**: Clean code structure for expansion.

- [ ] **ActionRegistry**
  - Central registry for actions (ID, Validator, Executor).
  - Auto-discovery of action handlers.
- [ ] **ComponentRegistry Auto-loader**
  - Scan directories to register components automatically.
- [ ] **Prompt Versioning**
  - Store prompts in versioned files (not hardcoded strings).

---

## 📊 Architecture Evolution

### Current (v1.0)
User → AI Parser → Validator → Executor → AI Narrator → UI

### Target (v2.0)
User → **EventBus** → AI Parser
      ↓
**ContextBuilder** (State + Vector Memory)
      ↓
Validator (Hard Rules)
      ↓
Executor (State Update + **Batch DB Write**)
      ↓
**EventBus** (OnActionSuccess)
      ↓
AI Narrator (Creative Model) → UI
