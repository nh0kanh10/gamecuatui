# Critical Issues & Resolutions

> **Document Purpose**: Track critical architectural issues raised and how they were resolved

---

## 🚨 Issues Identified (2025-12-02)

### 1. ❌ Over-Engineered Architecture

**Problem**: Initial ARCHITECTURE.md designed enterprise-level system:
- Too many abstractions for MVP
- Complex class hierarchies
- 3-month timeline for "foundation"
- Would lead to burnout before seeing gameplay

**Impact**: 
- Developer frustration
- Never reach playable state
- Technical debt from premature optimization

**Resolution**: ✅
- Created [MVP_ARCHITECTURE.md](architecture/MVP_ARCHITECTURE.md)
- Phase 0: Playable in 24h (single file)
- Progressive enhancement strategy
- Full architecture is "Phase 3+" goal, not requirement

**Status**: RESOLVED - MVP approach documented

---

### 2. ❌ Missing System Contracts

**Problem**: No clear API definitions between systems:
- GameManager ↔ WorldSimulator unclear
- Event payloads not specified
- No idempotency guarantees
- Race conditions possible

**Impact**:
- Systems tightly coupled
- Hard to test (no mocks)
- Integration bugs likely
- Can't disable broken features

**Resolution**: ✅
- Created [CONTRACTS.md](architecture/CONTRACTS.md)
- TypeScript-style interfaces for all systems
- Event schemas with idempotency rules
- Kill switch mechanisms documented

**Status**: RESOLVED - Contracts defined for Phase 2+

---

### 3. ❌ Save System Versioning

**Problem**: No versioning or migration strategy:
- Breaking changes would lose player saves
- No rollback plan
- Data structure changes risky

**Impact**:
- Player frustration (lost saves)
- Fear of changing data models
- Technical debt accumulation

**Resolution**: ✅
- Schema versioning in [CONTRACTS.md](architecture/CONTRACTS.md)
- Migration strategy defined
- Sequential migration pipeline
- MVP: Simple version check, no complex migration

**Status**: RESOLVED - Strategy documented

---

### 4. ❌ Offline Simulation Not Deterministic

**Problem**: "Smart simulation" lacked:
- Deterministic random seed usage
- Clear calculation rules
- Performance bounds (could lag on long offline periods)

**Impact**:
- Unpredictable results
- Browser lag when loading after days offline
- Save scumming possible
- Hard to debug

**Resolution**: ✅
- Seeded RNG requirement in [CONTRACTS.md](architecture/CONTRACTS.md)
- Summary-mode simulation for MVP
- Max 100 ticks limit for safety
- Full deterministic simulation in Phase 3

**Status**: RESOLVED - Simple approach for MVP, advanced for later

---

### 5. ❌ NPC AI Scope Undefined

**Problem**: `makeDecision(context)` too vague:
- No input/output spec
- Compute cost unknown (rule-based vs LLM)
- No fallback for failures

**Impact**:
- Feature creep risk
- Performance unpredictable
- No degradation path if AI fails

**Resolution**: ✅
- Rule-based AI ONLY for MVP ([MVP_ARCHITECTURE.md](architecture/MVP_ARCHITECTURE.md))
- Simple if-else behavior
- LLM option defined in [CONTRACTS.md](architecture/CONTRACTS.md) for future
- Fallback mechanisms required

**Status**: RESOLVED - MVP uses simple rules, advanced AI is Phase 4+

---

### 6. ❌ Event Queue Race Conditions

**Problem**: Event ordering, retries, idempotency not defined:
- Concurrent events could conflict
- No retry logic
- No dead letter queue

**Impact**:
- State corruption possible
- Events lost on errors
- Hard to debug issues

**Resolution**: ✅
- Event schema with retry count in [CONTRACTS.md](architecture/CONTRACTS.md)
- Idempotency requirements
- Priority + timestamp ordering
- MVP: Simple callback system, no queue

**Status**: RESOLVED - Callbacks for MVP, full queue Phase 3+

---

### 7. ❌ Performance Budget Not Set

**Problem**: No performance targets:
- Could build laggy game
- Mobile users ignored
- No monitoring

**Impact**:
- Unplayable on lower-end devices
- Bad user experience
- Hard to optimize later

**Resolution**: ✅
- Performance budgets in [MVP_ARCHITECTURE.md](architecture/MVP_ARCHITECTURE.md)
- 60fps target on mid-range mobile
- Frame time monitoring code
- Optimization rules defined

**Status**: RESOLVED - Budgets set, monitoring planned

---

### 8. ❌ No Kill Switches

**Problem**: Can't disable broken features:
- All systems required to run
- One bug = entire game broken
- No fallback modes

**Impact**:
- Development blocked by bugs
- Can't ship with known issues
- Hard to A/B test features

**Resolution**: ✅
- Feature flags in [MVP_ARCHITECTURE.md](architecture/MVP_ARCHITECTURE.md)
- System kill switches in [CONTRACTS.md](architecture/CONTRACTS.md)
- Fallback modes defined
- Graceful degradation

**Status**: RESOLVED - Flags & switches required

---

### 9. ❌ Testing Strategy Missing

**Problem**: No plan for testing complex systems:
- Deterministic tests hard
- No mocks defined
- Integration testing unclear

**Impact**:
- Bugs in production
- Fear of refactoring
- Slow development

**Resolution**: ✅
- Mock interfaces in [CONTRACTS.md](architecture/CONTRACTS.md)
- Deterministic seeds for repeatability
- Phase 0-1: Manual testing OK
- Phase 2+: Unit tests for core systems

**Status**: RESOLVED - Testing strategy defined

---

### 10. ❌ Content Validation Missing

**Problem**: JSON content could have errors:
- Invalid scene references
- Missing required fields
- Broken condition syntax

**Impact**:
- Runtime errors
- Bad player experience
- Hard to debug content bugs

**Resolution**: ✅
- Phase 1: Manual validation
- Phase 2: JSON Schema validation
- Phase 3: CI/CD lint pipeline
- Validation tools planned

**Status**: RESOLVED - Progressive validation approach

---

## 📊 Risk Assessment

### Before Fixes
| Risk | Severity | Likelihood | Impact |
|------|----------|------------|---------|
| Burnout before playable | CRITICAL | 90% | Project abandoned |
| Performance issues | HIGH | 70% | Unplayable on mobile |
| Lost saves on updates | HIGH | 80% | User frustration |
| Race conditions | MEDIUM | 50% | State corruption |
| Tight coupling | HIGH | 90% | Hard to maintain |

### After Fixes
| Risk | Severity | Likelihood | Impact |
|------|----------|------------|---------|
| Burnout before playable | LOW | 10% | MVP in 24h! |
| Performance issues | LOW | 20% | Budgets set |
| Lost saves on updates | LOW | 10% | Migration strategy |
| Race conditions | LOW | 10% | Events well-defined |
| Tight coupling | LOW | 10% | Contracts defined |

---

## ✅ New Development Strategy

### Old Approach (Rejected)
```
Perfect Architecture → Enterprise Patterns → Complex Systems → 3 Months → Burnout ❌
```

### New Approach (Adopted)
```
Phase 0 (24h): Playable prototype → See gameplay
Phase 1 (1w): Basic features → Friend plays
Phase 2 (2w): Structure → Replayable
Phase 3 (1m): Advanced features → Polished
```

**Key Changes**:
1. **Playable First**: See results in 24 hours
2. **Iterate**: Add ONE feature at a time
3. **Test**: Play the game constantly
4. **Refactor**: Only when code gets messy (>200 lines)
5. **Document**: As you go, not upfront

---

## 📝 Lessons Learned

### What We Almost Did Wrong
1. **Enterprise patterns for simple game** - Would take months
2. **Perfect architecture first** - Never see gameplay
3. **All features at once** - Overwhelming
4. **Complex systems before basic** - Cart before horse

### What We're Doing Right
1. **MVP mindset** - Playable ASAP
2. **Progressive enhancement** - Build up gradually
3. **Kill switches** - Can disable broken stuff
4. **Clear contracts** - When needed (Phase 2+)
5. **Performance budgets** - Keep it playable

---

## 🎯 Next Steps

1. **Build Phase 0** (TODAY): Single file, 3-5 scenes, playable
2. **Test**: Play it. Show a friend.
3. **Iterate**: Add ONE feature from Phase 1
4. **Repeat**: Keep it playable at ALL times

**Rule**: Never go more than 1 hour without testing the game!

---

## 🔗 Related Documents

- [MVP Architecture](architecture/MVP_ARCHITECTURE.md) - **Start here!**
- [System Contracts](architecture/CONTRACTS.md) - API definitions (Phase 2+)
- [Full Architecture](architecture/ARCHITECTURE.md) - Long-term vision (Phase 3+)
- [Development Rules](DEVELOPMENT_RULES.md) - Coding standards

---

**Status**: All critical issues RESOLVED ✅  
**Ready to**: Start building Phase 0!  
**Timeline**: Playable in 24 hours 🚀

---

**Last Updated**: 2025-12-02  
**Reviewed By**: User feedback incorporated  
**Action**: Begin Phase 0 implementation
