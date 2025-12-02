# System Contracts & Interfaces

> **Purpose**: Định nghĩa API rõ ràng giữa các systems để tránh tight coupling và dễ test

---

## 🎯 Core Principles

1. **Explicit Contracts**: Mọi interaction qua interfaces rõ ràng
2. **Loose Coupling**: Systems giao tiếp qua events/messages, không direct calls
3. **Testability**: Mọi interface có thể mock dễ dàng
4. **Kill Switches**: Có thể disable bất kỳ system nào

---

## 📋 System Boundaries & Contracts

### 1. GameManager ↔ Systems

**GameManager Interface** (Orchestrator)
```typescript
interface IGameManager {
  // Core lifecycle
  init(): Promise<void>
  start(): void
  pause(): void
  resume(): void
  shutdown(): void
  
  // System registration
  registerSystem(name: string, system: IGameSystem): void
  getSystem(name: string): IGameSystem | null
  
  // Event bus access
  emit(event: GameEvent): void
  on(eventType: string, handler: Function): void
}

interface IGameSystem {
  name: string
  enabled: boolean
  
  // Lifecycle hooks
  onInit(): Promise<void>
  onStart?(): void
  onUpdate?(deltaTime: number): void
  onPause?(): void
  onShutdown?(): void
  
  // Kill switch
  disable(): void
  enable(): void
}
```

**Example Usage**:
```javascript
// GameManager không biết chi tiết implementation
gameManager.registerSystem('world', worldSimulator);
gameManager.registerSystem('story', storyEngine);

// Systems tự quản lý internal logic
// GameManager chỉ điều phối lifecycle
```

---

### 2. EventBus Contract

**Event Schema**:
```typescript
interface GameEvent {
  id: string              // Unique event ID (UUID)
  type: string            // Event type (e.g., 'time.tick', 'npc.action')
  timestamp: number       // When event was created
  actor?: string          // Who/what triggered (optional)
  payload: any            // Event-specific data
  metadata: {
    retryCount: number    // For retry logic
    priority: number      // 0-10, default 5
    idempotent: boolean   // Can be safely retry?
  }
}

interface IEventBus {
  // Publishing
  emit(event: GameEvent): void
  emitAsync(event: GameEvent): Promise<void>
  
  // Subscribing
  on(eventType: string, handler: EventHandler): UnsubscribeFn
  once(eventType: string, handler: EventHandler): UnsubscribeFn
  
  // Pattern matching
  onPattern(pattern: RegExp, handler: EventHandler): UnsubscribeFn
  
  // Debugging
  getEventLog(limit?: number): GameEvent[]
  clearEventLog(): void
}

type EventHandler = (event: GameEvent) => void | Promise<void>
type UnsubscribeFn = () => void
```

**Idempotent Event Handlers**:
```javascript
// ✅ GOOD: Idempotent - can run multiple times safely
function handleResourceDepletion(event) {
  const currentFood = getResource('food');
  const newFood = Math.max(0, currentFood - event.payload.amount);
  setResource('food', newFood); // Uses final value, not delta
}

// ❌ BAD: Not idempotent - running twice would double-consume
function handleResourceDepletion(event) {
  consumeResource('food', event.payload.amount); // Relative change
}
```

---

### 3. StoryEngine Contract

```typescript
interface IStoryEngine {
  // Scene management
  loadScene(sceneId: string): Promise<Scene>
  getCurrentScene(): Scene | null
  
  // Choice handling
  getAvailableChoices(): Choice[]
  processChoice(choiceId: string): Promise<ChoiceResult>
  
  // Conditions
  evaluateCondition(condition: Condition): boolean
  
  // State queries
  hasFlag(flag: string): boolean
  setFlag(flag: string, value: boolean): void
  getStoryState(): StoryState
}

// Data Models
interface Scene {
  id: string
  title: string
  content: string
  choices: Choice[]
  conditions?: Condition
  autoEvents?: EventTrigger[]
}

interface Choice {
  id: string
  text: string
  conditions?: Condition
  consequences: Consequences
}

interface Condition {
  flags?: string[]           // Required flags
  resources?: ResourceCheck  // Resource requirements
  custom?: string            // Custom condition function name
}

interface Consequences {
  flags?: Record<string, boolean>
  resources?: Record<string, number>
  events?: string[]          // Events to trigger
  nextScene?: string
}

interface ChoiceResult {
  success: boolean
  nextSceneId?: string
  eventsTriggered: string[]
  stateChanges: StateChange[]
}
```

**Example**:
```javascript
// StoryEngine doesn't know about WorldSimulator
// It just emits events
await storyEngine.processChoice('choice_brave_storm');
// → Emits: { type: 'story.choice', payload: { consequences } }
// → WorldSimulator hears event and updates world
```

---

### 4. WorldSimulator Contract

```typescript
interface IWorldSimulator {
  // Simulation
  simulate(elapsedTimeMs: number): SimulationResult
  tick(deltaTime: number): void
  
  // State
  getWorldState(): WorldState
  setWorldState(state: WorldState): void
  
  // Configuration
  setSimulationMode(mode: 'realtime' | 'fast' | 'summary'): void
  
  // Kill switch
  enableSimulation(enabled: boolean): void
}

interface SimulationResult {
  summaryText: string          // Human-readable summary
  majorEvents: SimulationEvent[]
  stateChanges: StateChange[]
  deterministic: boolean       // Was simulation deterministic?
  seed?: number               // Random seed used
}

interface SimulationEvent {
  type: string
  timestamp: number
  description: string
  actors: string[]
  impact: 'minor' | 'major' | 'critical'
}

interface WorldState {
  gameTime: number
  location: string
  weather: WeatherState
  resources: Record<string, number>
  npcs: NPCState[]
  factions: FactionState[]
}
```

**Deterministic Simulation**:
```javascript
// CRITICAL: Use seeded random for reproducibility
class WorldSimulator {
  simulate(elapsedTimeMs, seed = Date.now()) {
    const rng = new SeededRandom(seed); // Deterministic
    
    // Calculate deterministically
    const events = this.calculateEvents(elapsedTimeMs, rng);
    const changes = this.applyEvents(events);
    
    return {
      summaryText: this.generateSummary(events),
      majorEvents: events.filter(e => e.impact !== 'minor'),
      stateChanges: changes,
      deterministic: true,
      seed: seed
    };
  }
  
  calculateEvents(time, rng) {
    // Example: 1 event per 4 hours
    const eventCount = Math.floor(time / (4 * 60 * 60 * 1000));
    const events = [];
    
    for (let i = 0; i < eventCount; i++) {
      // Use rng, not Math.random()!
      if (rng.next() < 0.3) {
        events.push(generateRandomEvent(rng));
      }
    }
    
    return events;
  }
}
```

---

### 5. NPC AI Contract

```typescript
interface INPC {
  id: string
  name: string
  
  // Behavior
  tick(deltaTime: number, context: NPCContext): NPCIntent | null
  
  // State
  getState(): NPCState
  setState(state: NPCState): void
  
  // Relationship
  getRelationship(targetId: string): number
  modifyRelationship(targetId: string, delta: number): void
  
  // Memory
  remember(event: MemoryEvent): void
  recall(query: MemoryQuery): MemoryEvent[]
}

interface NPCContext {
  worldState: WorldState      // What NPC can see
  playerActions: Action[]     // Recent player actions
  nearbyEntities: Entity[]    // Who's nearby
  currentTime: number
}

interface NPCIntent {
  type: 'move' | 'action' | 'dialog' | 'wait'
  target?: string
  data?: any
  priority: number
}

interface NPCState {
  location: string
  health: number
  morale: number
  currentGoal?: string
  schedule: ScheduleEntry[]
  memory: MemoryEvent[]
}

interface MemoryEvent {
  timestamp: number
  type: string
  description: string
  actors: string[]
  emotionalImpact: number  // -10 to +10
}
```

**AI Modes**:
```typescript
enum NPCAIMode {
  RULE_BASED = 'rule',    // Fast, deterministic
  LLM_ASSISTED = 'llm',   // Slow, creative
  HYBRID = 'hybrid'       // Rule-based with LLM fallback
}

interface INPCAIProvider {
  mode: NPCAIMode
  
  // Main decision function
  makeDecision(npc: INPC, context: NPCContext): Promise<NPCIntent>
  
  // Fallback
  getDefaultDecision(npc: INPC): NPCIntent
}

// Example: Rule-based AI (MVP)
class RuleBasedAI implements INPCAIProvider {
  mode = NPCAIMode.RULE_BASED;
  
  async makeDecision(npc, context) {
    // Simple rules
    if (context.worldState.weather.dangerous) {
      return { type: 'action', target: 'seek_shelter', priority: 8 };
    }
    
    // Follow schedule
    const currentActivity = this.getScheduledActivity(npc, context.currentTime);
    return { type: 'action', target: currentActivity, priority: 5 };
  }
  
  getDefaultDecision(npc) {
    return { type: 'wait', priority: 1 };
  }
}

// Example: LLM AI (future enhancement)
class LLMAIProvider implements INPCAIProvider {
  mode = NPCAIMode.LLM_ASSISTED;
  
  async makeDecision(npc, context) {
    try {
      // Call LLM with timeout
      const decision = await this.callLLM(npc, context, { timeout: 2000 });
      return this.parseDecision(decision);
    } catch (error) {
      // Fallback to rule-based
      console.warn('LLM failed, using fallback');
      return this.getDefaultDecision(npc);
    }
  }
  
  getDefaultDecision(npc) {
    // Always have a safe fallback
    return { type: 'wait', priority: 1 };
  }
}
```

---

### 6. SaveManager Contract

```typescript
interface ISaveManager {
  // Save/Load
  save(slotId?: string): Promise<SaveResult>
  load(slotId: string): Promise<LoadResult>
  
  // Auto-save
  enableAutoSave(intervalMs: number): void
  disableAutoSave(): void
  
  // Export/Import
  exportSave(slotId: string): Promise<Blob>
  importSave(data: Blob): Promise<string>
  
  // Metadata
  listSaves(): SaveMetadata[]
  deleteSave(slotId: string): void
}

interface SaveData {
  version: string           // CRITICAL: for migration
  schemaVersion: number     // Data structure version
  timestamp: number
  playTime: number
  
  // Core state (minimal!)
  player: PlayerState
  story: StoryState
  world: WorldState
  
  // Checksums for validation
  checksum?: string
}

interface SaveResult {
  success: boolean
  slotId: string
  size: number
  error?: string
}
```

**Save Versioning & Migration**:
```typescript
// Save Schema Versions
const SAVE_SCHEMAS = {
  1: {
    // v1: MVP - minimal state
    player: ['name', 'ship'],
    story: ['currentScene', 'flags'],
    world: ['location', 'resources']
  },
  2: {
    // v2: Added NPC system
    player: ['name', 'ship', 'reputation'],
    story: ['currentScene', 'flags', 'history'],
    world: ['location', 'resources', 'npcs']
  }
  // ... future versions
};

class SaveMigration {
  migrate(saveData: SaveData, targetVersion: number): SaveData {
    let data = saveData;
    const currentVersion = data.schemaVersion || 1;
    
    // Apply migrations sequentially
    for (let v = currentVersion; v < targetVersion; v++) {
      data = this[`migrate_${v}_to_${v + 1}`](data);
    }
    
    return data;
  }
  
  migrate_1_to_2(data: SaveData): SaveData {
    return {
      ...data,
      schemaVersion: 2,
      player: {
        ...data.player,
        reputation: {}  // Add new field with default
      },
      story: {
        ...data.story,
        history: []     // Add new field
      },
      world: {
        ...data.world,
        npcs: []        // Add new field
      }
    };
  }
  
  // ... more migrations
}
```

---

## 🔧 Critical Implementation Rules

### 1. Event Ordering & Idempotency

```javascript
class EventQueue {
  processEvents(events) {
    // Sort by timestamp + priority
    const sorted = events.sort((a, b) => {
      if (a.timestamp !== b.timestamp) {
        return a.timestamp - b.timestamp;
      }
      return b.metadata.priority - a.metadata.priority;
    });
    
    // Process with retry logic
    for (const event of sorted) {
      this.processEventWithRetry(event);
    }
  }
  
  processEventWithRetry(event) {
    const maxRetries = 3;
    let attempt = event.metadata.retryCount || 0;
    
    try {
      this.emit(event);
    } catch (error) {
      if (attempt < maxRetries && event.metadata.idempotent) {
        // Retry idempotent events
        event.metadata.retryCount = attempt + 1;
        setTimeout(() => this.processEventWithRetry(event), 1000);
      } else {
        // Log and skip
        console.error('Event failed:', event, error);
        this.deadLetterQueue.push(event);
      }
    }
  }
}
```

### 2. System Kill Switches

```javascript
class GameManager {
  systemConfig = {
    world: { enabled: true, fallbackMode: false },
    ai: { enabled: true, fallbackMode: false },
    story: { enabled: true, fallbackMode: false }
  };
  
  update(deltaTime) {
    // WorldSimulator
    if (this.systemConfig.world.enabled) {
      if (this.systemConfig.world.fallbackMode) {
        // Dumb mode: no simulation, just basic updates
        this.worldSimulator.updateBasic(deltaTime);
      } else {
        // Full simulation
        this.worldSimulator.tick(deltaTime);
      }
    }
    
    // NPC AI
    if (this.systemConfig.ai.enabled) {
      if (this.systemConfig.ai.fallbackMode) {
        // NPCs follow simple schedules only
        this.npcManager.updateSchedules();
      } else {
        // Full AI decision making
        this.npcManager.tick(deltaTime);
      }
    }
  }
  
  // Emergency disable
  disableSystem(name) {
    this.systemConfig[name].enabled = false;
    console.warn(`System '${name}' disabled`);
  }
  
  // Fallback mode for debugging
  setFallbackMode(name, enabled) {
    this.systemConfig[name].fallbackMode = enabled;
  }
}
```

### 3. Performance Budget

```javascript
class PerformanceMonitor {
  budgets = {
    'world.simulation': 16,    // 16ms max (60fps)
    'ai.decisions': 33,        // 33ms (30fps acceptable)
    'story.render': 8,         // 8ms
    'render.total': 16         // Total frame budget
  };
  
  measure(category, fn) {
    const start = performance.now();
    const result = fn();
    const duration = performance.now() - start;
    
    if (duration > this.budgets[category]) {
      console.warn(`⚠️ Performance: ${category} took ${duration.toFixed(2)}ms (budget: ${this.budgets[category]}ms)`);
    }
    
    return result;
  }
}

// Usage
performanceMonitor.measure('world.simulation', () => {
  worldSimulator.tick(deltaTime);
});
```

---

## 📊 Testing Contracts

### Mock Implementations

```javascript
// Mock WorldSimulator for testing StoryEngine
class MockWorldSimulator implements IWorldSimulator {
  simulateCalled = false;
  lastElapsedTime = 0;
  
  simulate(elapsedTime) {
    this.simulateCalled = true;
    this.lastElapsedTime = elapsedTime;
    
    return {
      summaryText: 'Mock simulation',
      majorEvents: [],
      stateChanges: [],
      deterministic: true
    };
  }
  
  // ... other required methods
}

// Test
test('StoryEngine triggers world simulation after choice', async () => {
  const mockWorld = new MockWorldSimulator();
  const storyEngine = new StoryEngine(mockWorld);
  
  await storyEngine.processChoice('choice_sail');
  
  assert(mockWorld.simulateCalled);
});
```

---

## ✅ Contract Checklist

Before implementing any system, ensure:

- [ ] Interface defined with TypeScript-style types
- [ ] Event schemas documented
- [ ] Idempotency considered
- [ ] Fallback/default behavior specified
- [ ] Kill switch mechanism in place
- [ ] Performance budget set
- [ ] Mock implementation for testing
- [ ] Migration strategy (for stateful systems)

---

**Version**: 1.0  
**Last Updated**: 2025-12-02  
**Status**: Contract Definitions Complete
