# MVP Architecture - Simplified & Practical

> **Goal**: Build something PLAYABLE in 1-2 weeks, not a perfect enterprise system

---

## 🎯 MVP Philosophy

### The Truth About First Projects

```
❌ Enterprise Architecture → 3 months setup → Burn out → Abandoned
✅ Simple MVP → 1 week → PLAYABLE → Iterate → Success
```

**MVP Rules**:
1. **Playable in 24-48 hours** - must see gameplay fast
2. **One feature at a time** - không làm hết một lúc
3. **Hardcode first, abstract later** - khi thấy pattern mới abstract
4. **Kill switches everywhere** - có thể disable features bị bug

---

## 🏗️ Simplified Architecture

### Phase 0: Absolute Minimum (24 hours)

**Goal**: Chơi được 1 scene với 2-3 choices

```
index.html
  ↓
main.js (100 lines)
  ├─ renderScene(scene)
  ├─ handleChoice(choice)
  └─ scenes = {...}  // HARDCODED trong file
```

**That's it.** Không cần:
- ❌ Không cần GameManager
- ❌ Không cần EventBus
- ❌ Không cần class hierarchy
- ❌ Không cần separate files

**Code Example**:
```javascript
// main.js - EVERYTHING in 1 file
const scenes = {
  start: {
    title: "Departure",
    text: "Your ship leaves port as the sun sets...",
    choices: [
      { text: "Sail north", next: "north_route" },
      { text: "Sail south", next: "south_route" }
    ]
  },
  north_route: {
    title: "Northern Waters",
    text: "Cold winds bite your face...",
    choices: [
      { text: "Continue", next: "end" }
    ]
  }
  // ... 3-5 scenes total
};

let currentScene = 'start';

function render() {
  const scene = scenes[currentScene];
  document.getElementById('title').textContent = scene.title;
  document.getElementById('content').textContent = scene.text;
  
  const choicesDiv = document.getElementById('choices');
  choicesDiv.innerHTML = scene.choices.map((c, i) =>
    `<button onclick="choose(${i})">${c.text}</button>`
  ).join('');
}

function choose(index) {
  const choice = scenes[currentScene].choices[index];
  currentScene = choice.next;
  render();
}

render(); // Start game
```

**Test**: Mở browser, CHƠI ĐƯỢC → Success! 🎉

---

### Phase 1: Add Basics (Week 1)

**Goal**: Save/load, simple stats, 10+ scenes

```
index.html
main.js (150 lines)
  ├─ gameState = { scene, stats, flags }
  ├─ renderScene()
  ├─ handleChoice()
  ├─ save() / load()
  └─ checkConditions()

scenes.json  // Move hardcoded data ra file
```

**New Features**:
- Save to localStorage
- Stats (food, fuel, morale)
- Conditional choices (if food > 10)
- 10-15 interconnected scenes

**Still NO**:
- ❌ WorldSimulator
- ❌ NPC AI
- ❌ Complex event system

**Code Example**:
```javascript
// main.js
let gameState = {
  currentScene: 'start',
  stats: { food: 100, fuel: 100, morale: 50 },
  flags: new Set()
};

function handleChoice(choice) {
  // Apply consequences
  if (choice.consume) {
    gameState.stats.food -= choice.consume.food || 0;
    gameState.stats.fuel -= choice.consume.fuel || 0;
  }
  
  if (choice.setFlag) {
    gameState.flags.add(choice.setFlag);
  }
  
  // Move to next scene
  gameState.currentScene = choice.next;
  
  // Auto-save
  save();
  
  render();
}

function save() {
  // Simple JSON save
  localStorage.setItem('save', JSON.stringify({
    ...gameState,
    flags: Array.from(gameState.flags) // Set → Array
  }));
}

function load() {
  const data = JSON.parse(localStorage.getItem('save'));
  if (data) {
    gameState = {
      ...data,
      flags: new Set(data.flags) // Array → Set
    };
    render();
  }
}
```

---

### Phase 2: Add Structure (Week 2)

**Goal**: Refactor khi code quá dài, thêm 1-2 advanced features

```
src/
  ├─ core/
  │   ├─ GameState.js      // Manage state
  │   └─ SceneManager.js   // Handle scenes
  ├─ ui/
  │   └─ Renderer.js       // Render logic
  └─ utils/
      └─ Storage.js        // Save/load

data/
  └─ scenes.json

index.html
main.js (50 lines - just init)
```

**New Features (pick 1-2)**:
- Simple time system (time passes between choices)
- Basic NPC encounters (pre-scripted, not simulated)
- Resource depletion (food decreases over time)

**Still NO**:
- ❌ Living world simulation
- ❌ Complex AI
- ❌ Offline simulation

**When to refactor?**
- File > 200 lines → split
- Copy-paste 3+ times → abstract to function
- NOT before then!

---

### Phase 3: Add ONE Advanced Feature (Week 3-4)

Pick **ONE** to implement well:

#### Option A: Simple Living World
```javascript
class SimpleWorldTick {
  tick(deltaTime) {
    // SIMPLE rules only
    gameState.stats.food -= deltaTime * 0.01; // Consume food
    
    // Random event (10% chance per tick)
    if (Math.random() < 0.1) {
      triggerRandomEvent();
    }
  }
}

// When load game:
const timePassed = Date.now() - gameState.lastSaveTime;
const ticksPassed = Math.floor(timePassed / 1000); // 1 tick per second

// Simulate ticks (MAX 100 to avoid lag)
for (let i = 0; i < Math.min(ticksPassed, 100); i++) {
  worldTick.tick(1);
}
```

#### Option B: Simple NPC System
```javascript
const NPCs = {
  marcus: {
    name: "Marcus",
    morale: 50,
    
    // Simple state machine
    getDialog() {
      if (this.morale < 30) return "I'm worried about our supplies...";
      if (this.morale > 70) return "We'll make it through this!";
      return "Just another day at sea.";
    },
    
    // React to story events
    onEvent(event) {
      if (event === 'storm_survived') this.morale += 10;
      if (event === 'crew_died') this.morale -= 20;
    }
  }
};
```

#### Option C: Better UI/UX
- Animations (text fade-in, choice hover effects)
- Sound effects
- Better visual design
- Mobile responsive

**Pick ONE. Implement well. Test thoroughly.**

---

## 🚨 Critical Simplifications

### 1. Offline Simulation: SUMMARY MODE

```javascript
// ❌ DON'T: Simulate every second
for (let i = 0; i < 86400; i++) {  // 24 hours
  worldSimulator.tick(1);  // LAG CITY
}

// ✅ DO: Calculate summary
function calculateOfflineChanges(hoursPassed) {
  return {
    food: Math.max(0, gameState.stats.food - hoursPassed * 2),
    fuel: Math.max(0, gameState.stats.fuel - hoursPassed * 1),
    events: generateSummaryEvents(hoursPassed), // Max 5 events
    message: generateSummaryMessage(hoursPassed)
  };
}

function generateSummaryEvents(hours) {
  // Simple probability
  const events = [];
  
  if (hours > 12 && Math.random() < 0.5) {
    events.push({ type: 'storm', text: 'A storm passed through' });
  }
  
  if (hours > 24 && Math.random() < 0.3) {
    events.push({ type: 'encounter', text: 'Ship spotted on horizon' });
  }
  
  return events.slice(0, 5); // Max 5
}
```

### 2. NPC AI: RULE-BASED ONLY (MVP)

```javascript
// ❌ DON'T: Complex AI decision tree
class NPCAIEngine {
  async makeDecision(context) {
    const state = await this.analyzeContext(context);
    const goals = this.prioritizeGoals(state);
    const plan = this.planActions(goals);
    return this.executeOptimalAction(plan);
  }
}

// ✅ DO: Simple if-else
class SimpleNPCBehavior {
  tick(npc, worldState) {
    // Simple priorities
    if (worldState.danger) return 'seek_safety';
    if (npc.health < 30) return 'rest';
    if (worldState.time === 'morning') return 'work';
    if (worldState.time === 'evening') return 'socialize';
    return 'idle';
  }
}
```

### 3. Save System: JSON ONLY

```javascript
// ❌ DON'T: Complex serialization
class SaveManager {
  serialize(state) {
    return this.compressor.compress(
      this.encoder.encode(
        this.validator.validate(state)
      )
    );
  }
}

// ✅ DO: Plain JSON
function save() {
  const saveData = {
    version: '1.0',
    timestamp: Date.now(),
    state: gameState
  };
  
  localStorage.setItem('save', JSON.stringify(saveData));
}

function load() {
  const data = JSON.parse(localStorage.getItem('save'));
  
  // Version check
  if (data.version !== '1.0') {
    alert('Save file from old version, starting new game');
    return null;
  }
  
  return data.state;
}
```

### 4. Event System: CALLBACKS ONLY

```javascript
// ❌ DON'T: Complex event bus
class EventBus {
  constructor() {
    this.queue = new PriorityQueue();
    this.handlers = new Map();
    this.middleware = [];
  }
  // ... 200 lines
}

// ✅ DO: Simple callbacks
const eventHandlers = {};

function on(event, callback) {
  if (!eventHandlers[event]) eventHandlers[event] = [];
  eventHandlers[event].push(callback);
}

function emit(event, data) {
  if (eventHandlers[event]) {
    eventHandlers[event].forEach(cb => cb(data));
  }
}

// Usage
on('choice_made', (data) => {
  console.log('Player chose:', data.choice);
});

emit('choice_made', { choice: 'sail_north' });
```

---

## 🔧 Kill Switches & Fallbacks

### Feature Flags

```javascript
const FEATURES = {
  auto_save: true,
  animations: true,
  sound: false,           // Not implemented yet
  world_sim: false,       // Phase 3 feature
  npc_ai: false          // Phase 3 feature
};

function tick(deltaTime) {
  // Only run if enabled
  if (FEATURES.world_sim) {
    worldSimulator.tick(deltaTime);
  }
  
  // Graceful degradation
  if (FEATURES.auto_save) {
    autoSave();
  }
}

// Easy to disable broken features
if (somethingBroke) {
  FEATURES.animations = false;
  console.warn('Animations disabled due to error');
}
```

### Safe Defaults

```javascript
function loadScene(id) {
  const scene = scenes[id];
  
  if (!scene) {
    console.error(`Scene ${id} not found`);
    // Fallback to safe default
    return scenes.error_scene || scenes.start;
  }
  
  return scene;
}

function applyChoice(choice) {
  try {
    // Apply consequences
    applyConsequences(choice.consequences);
  } catch (error) {
    console.error('Error applying choice:', error);
    // Don't crash the game
    alert('Something went wrong, but the game continues');
    // Just move to next scene
    gameState.currentScene = choice.next || 'start';
  }
}
```

---

## 📊 Performance Budgets (Realistic)

```javascript
// Target: 60fps on mid-range mobile (2019+)

const PERFORMANCE_BUDGETS = {
  frame_total: 16,        // 16ms per frame (60fps)
  scene_render: 5,        // 5ms to render scene
  choice_process: 10,     // 10ms to process choice
  save: 20,               // 20ms to save (don't block)
  
  // Phase 3 features
  world_tick: 8,          // 8ms for world simulation
  npc_update: 5           // 5ms for all NPCs combined
};

// Monitor in dev mode
let frameStart;
function tick() {
  frameStart = performance.now();
  
  // ... game logic
  
  const frameTime = performance.now() - frameStart;
  if (frameTime > PERFORMANCE_BUDGETS.frame_total) {
    console.warn(`⚠️ Slow frame: ${frameTime.toFixed(2)}ms`);
  }
}
```

**Optimization Rules**:
- < 60fps on your machine → **MUST FIX**
- < 30fps on mobile → **CRITICAL**
- Lag after load → Reduce offline simulation complexity

---

## 🎯 MVP Feature Matrix

| Feature | Phase 0 (24h) | Phase 1 (Week 1) | Phase 2 (Week 2) | Phase 3 (Week 3-4) |
|---------|---------------|------------------|------------------|--------------------|
| **Scenes** | 3-5 hardcoded | 10+ in JSON | 20-30 structured | 50+ with branches |
| **Choices** | Simple next | Conditional | Multi-consequence | Complex conditions |
| **Stats** | None | Food/Fuel/Morale | + Custom stats | + Derived stats |
| **Save/Load** | None | LocalStorage | + Export/Import | + Versioning |
| **Time** | None | None | Simple counter | Offline simulation |
| **NPCs** | None | Mentioned in text | Simple dialogs | Basic behavior |
| **UI** | Plain HTML | Basic CSS | Styled components | Animated + Sound |
| **Events** | None | None | Random events | Scheduled events |

**Rule**: Move to next phase ONLY when current phase is PLAYABLE and TESTED

---

## ✅ MVP Checklist

### Phase 0 Complete When:
- [ ] Can play through 3-5 scenes
- [ ] Choices lead to different scenes
- [ ] No bugs/crashes
- [ ] Loads in browser under 1 second

### Phase 1 Complete When:
- [ ] 10+ scenes playable
- [ ] Save/load works
- [ ] Stats affect story (at least 3 conditional branches)
- [ ] Content in JSON, not hardcoded
- [ ] Tested on mobile

### Phase 2 Complete When:
- [ ] Code is organized (no 300-line files)
- [ ] 20+ scenes with multiple paths
- [ ] At least 3 different endings
- [ ] Basic time mechanic works
- [ ] UI looks decent (not beautiful, just not ugly)

### Phase 3 Complete When:
- [ ] ONE advanced feature fully working
- [ ] No performance issues
- [ ] Polish pass on UI/UX
- [ ] Ready to show to others

---

## 🚫 Things to AVOID in MVP

### ❌ Premature Abstraction
```javascript
// ❌ DON'T do this in Phase 0-1
class AbstractStoryNodeFactory {
  createNode(type: NodeType): IStoryNode {
    return this.registry.get(type).instantiate();
  }
}

// ✅ DO this instead
const scenes = { start: {...}, next: {...} };
```

### ❌ Over-Engineering
```javascript
// ❌ DON'T: Enterprise patterns
class GameFacade {
  constructor(
    private storyService: IStoryService,
    private worldService: IWorldService,
    private eventAggregator: IEventAggregator
  ) {}
}

// ✅ DO: Simple & direct
function playGame() {
  renderScene(scenes[gameState.currentScene]);
}
```

### ❌ Too Many Files Too Soon
```javascript
// ❌ DON'T: Split into 50 files immediately
src/
  core/
    managers/
      GameManager.ts
      StateManager.ts
      ...
  systems/
    story/
      SceneLoader.ts
      ChoiceProcessor.ts
      ...
    // ... 40 more files

// ✅ DO: Start with 1-3 files
main.js        // Everything initially
scenes.json    // Data only
styles.css     // Styles
```

---

## 🎓 Learning Path

### Week 1: Basics
- Vanilla JavaScript (no frameworks!)
- DOM manipulation
- JSON data structures
- localStorage API

### Week 2: Game Dev Concepts
- State management
- Scene graphs
- Conditional logic树
- Save systems

### Week 3-4: ONE Advanced Topic
- Animation (GSAP or CSS)
- OR procedural generation
- OR simple AI
- OR audio system

**Don't try to learn everything at once!**

---

## 💡 Success Metrics

### Phase 0 Success = 
- **1 person (you) plays through and smiles** ✅

### Phase 1 Success =
- **Friend plays through without bugs** ✅
- **They want to play again** ✅

### Phase 2 Success =
- **3+ friends play without instructions** ✅
- **At least 1 replays to see other endings** ✅

### Phase 3 Success =
- **Stranger on internet plays and leaves positive comment** ✅
- **You're proud to share it** ✅

---

## 🔑 Key Takeaways

1. **Start tiny** - 1 file, 100 lines, playable in 24h
2. **Iterate fast** - add 1 feature at a time
3. **Test constantly** - play your game every hour
4. **Refactor when painful** - not before
5. **One advanced feature** - do it well, not many poorly
6. **Kill switches** - easy to disable broken stuff
7. **Performance matters** - test on phone
8. **Content is king** - good story > fancy tech

---

**The MVP Way**:
```
Prototype (1 day) 
  → MVP (1 week) 
    → Structured (2 weeks) 
      → Enhanced (1 month)
        → Polished (2 months)
```

Not:
```
Perfect Architecture (3 months) → Burnout → Abandoned ❌
```

---

**Version**: 1.0  
**Last Updated**: 2025-12-02  
**Status**: MVP Strategy Defined - Ready to Build! 🚀
