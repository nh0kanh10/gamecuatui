# Game Architecture - The Last Voyage

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   UI     │  │  Render  │  │  Input   │              │
│  │ Manager  │  │  Engine  │  │ Handler  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                     GAME LOGIC LAYER                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Game    │  │  Story   │  │  Choice  │              │
│  │ Manager  │  │  Engine  │  │  System  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  World   │  │   NPC    │  │ Faction  │              │
│  │Simulator │  │    AI    │  │  System  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                      DATA LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Game    │  │  World   │  │ Content  │              │
│  │  State   │  │  State   │  │   Data   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  ┌──────────┐  ┌──────────┐                             │
│  │  Save    │  │  Event   │                             │
│  │  System  │  │  Queue   │                             │
│  └──────────┘  └──────────┘                             │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
GameBuild/
├── src/                          # Source code
│   ├── core/                     # Core game systems
│   │   ├── GameManager.js        # Main game loop & orchestration
│   │   ├── TimeSystem.js         # Time tracking & simulation
│   │   ├── EventBus.js           # Event communication system
│   │   └── Config.js             # Global configuration
│   │
│   ├── world/                    # World simulation
│   │   ├── WorldSimulator.js     # Main world simulation engine
│   │   ├── ResourceManager.js    # Resource tracking (food, fuel, etc.)
│   │   ├── WeatherSystem.js      # Weather generation & effects
│   │   └── LocationManager.js    # Map & location handling
│   │
│   ├── entities/                 # Game entities
│   │   ├── NPC.js                # NPC base class
│   │   ├── Crew.js               # Crew member implementation
│   │   ├── Ship.js               # Player's ship
│   │   └── Faction.js            # Faction system
│   │
│   ├── story/                    # Narrative systems
│   │   ├── StoryEngine.js        # Story flow controller
│   │   ├── SceneRenderer.js      # Scene display logic
│   │   ├── ChoiceSystem.js       # Choice handling & consequences
│   │   └── DialogSystem.js       # Dialog trees
│   │
│   ├── ai/                       # AI systems
│   │   ├── NPCBehavior.js        # NPC decision making
│   │   ├── FactionAI.js          # Faction strategy & conflicts
│   │   └── EventGenerator.js     # Procedural event generation
│   │
│   ├── persistence/              # Save/load
│   │   ├── SaveManager.js        # Save/load orchestration
│   │   ├── StateSerializer.js    # State serialization
│   │   └── StorageAdapter.js     # LocalStorage wrapper
│   │
│   ├── ui/                       # User interface
│   │   ├── UIManager.js          # UI coordination
│   │   ├── components/           # UI components
│   │   │   ├── SceneDisplay.js
│   │   │   ├── ChoiceButtons.js
│   │   │   ├── StatusPanel.js
│   │   │   └── MessageLog.js
│   │   └── animations/           # UI animations
│   │       └── TextAnimator.js
│   │
│   └── utils/                    # Utilities
│       ├── Random.js             # Random number generation
│       ├── Logger.js             # Logging system
│       └── Helpers.js            # Helper functions
│
├── data/                         # Game content (JSON)
│   ├── scenes/                   # Story scenes
│   │   ├── prologue.json
│   │   ├── chapter1/
│   │   └── ...
│   │
│   ├── npcs/                     # NPC definitions
│   │   ├── crew.json
│   │   ├── traders.json
│   │   └── pirates.json
│   │
│   ├── events/                   # Event definitions
│   │   ├── random_events.json
│   │   ├── story_events.json
│   │   └── world_events.json
│   │
│   ├── items/                    # Items & resources
│   │   └── items.json
│   │
│   └── config/                   # Configuration data
│       ├── game_settings.json
│       └── balance.json
│
├── assets/                       # Static assets
│   ├── css/
│   │   ├── main.css
│   │   ├── components.css
│   │   └── animations.css
│   ├── images/
│   └── sounds/
│
├── test/                         # Test files (DELETE WHEN DONE)
│   ├── unit/
│   ├── integration/
│   └── playground.js             # Experimental code
│
├── docs/                         # Documentation
│   ├── architecture/             # Architecture docs
│   │   ├── ARCHITECTURE.md       # This file
│   │   ├── DATA_MODELS.md
│   │   └── SYSTEMS.md
│   │
│   └── design/                   # Design documents
│       ├── GAME_DESIGN.md
│       └── NARRATIVE.md
│
├── ideas/                        # Ideas & brainstorming
│   └── game-concepts.md
│
├── index.html                    # Entry point
├── main.js                       # Application bootstrap
├── .gitignore
└── README.md
```

---

## 🔧 Core Systems

### 1. Game Manager
**Responsibility**: Orchestrate all game systems, manage game loop

```javascript
class GameManager {
  constructor()
  init()                    // Initialize all systems
  start()                   // Start game loop
  pause()                   // Pause game
  resume()                  // Resume game
  update(deltaTime)         // Main update loop
  shutdown()                // Clean shutdown
}
```

**Dependencies**: All core systems

---

### 2. Time System
**Responsibility**: Track time, calculate offline simulation

```javascript
class TimeSystem {
  getCurrentTime()          // Get current game time
  getElapsedTime()          // Time since last save
  convertRealToGame(ms)     // Convert real time to game time
  tick(deltaTime)           // Advance time
}
```

**Key Feature**: Offline time calculation for world simulation

---

### 3. World Simulator
**Responsibility**: Simulate world changes over time

```javascript
class WorldSimulator {
  simulate(elapsedTime)     // Main simulation entry point
  
  // Sub-simulations
  simulateNPCs(time)        // NPC actions & movement
  simulateFactions(time)    // Faction conflicts & changes
  simulateResources(time)   // Resource depletion/regeneration
  simulateWeather(time)     // Weather changes
  simulateEvents(time)      // Random & scheduled events
  
  getSimulationSummary()    // Generate summary for player
}
```

**Optimization**: Smart simulation - không simulate từng tick, chỉ calculate major changes

---

### 4. NPC AI
**Responsibility**: NPC behavior & decision making

```javascript
class NPC {
  // Properties
  id
  name
  personality
  skills
  relationships
  schedule
  goals
  memory
  
  // Behavior
  tick(deltaTime)           // Update NPC state
  makeDecision(context)     // AI decision making
  interact(entity)          // Interaction logic
  updateRelationship(target, delta)
  remember(event)           // Store in memory
}
```

**Key Feature**: NPCs act independently based on goals & context

---

### 5. Story Engine
**Responsibility**: Control narrative flow

```javascript
class StoryEngine {
  currentScene
  sceneHistory
  
  loadScene(sceneId)        // Load a scene
  processChoice(choice)     // Handle player choice
  evaluateConditions(scene) // Check if scene conditions met
  triggerEvent(eventId)     // Trigger story event
  
  // Branching logic
  getAvailableChoices()
  applyConsequences(choice)
}
```

**Data-Driven**: All scenes & choices defined in JSON

---

### 6. Save System
**Responsibility**: Persist & restore game state

```javascript
class SaveManager {
  save()                    // Save complete game state
  load()                    // Load game state
  autoSave()                // Automatic save
  
  // Serialization
  serializeState()          // Convert state to saveable format
  deserializeState(data)    // Restore state from data
  
  // Storage
  saveToLocalStorage()
  loadFromLocalStorage()
  exportSave()              // Export save file
  importSave(file)          // Import save file
}
```

**State Includes**:
- Player progress
- World state
- NPC states
- Faction states
- Event queue
- Timestamp (for offline simulation)

---

## 📊 Data Models

### Game State
```javascript
{
  version: "1.0.0",
  saveTime: timestamp,
  playTime: hours,
  
  player: {
    name: string,
    ship: {...},
    inventory: [...],
    reputation: {...}
  },
  
  world: {
    currentLocation: id,
    weather: {...},
    time: {...}
  },
  
  story: {
    currentScene: id,
    flags: {...},
    completedEvents: [...]
  },
  
  npcs: [],
  factions: [],
  resources: {...}
}
```

### Scene Definition
```javascript
{
  id: "scene_001",
  title: "Storm on the Horizon",
  content: "Long narrative text...",
  
  conditions: {
    flags: ["prologue_complete"],
    resources: {food: {min: 10}}
  },
  
  choices: [
    {
      id: "choice_001",
      text: "Sail into the storm",
      consequences: {
        flags: ["brave_choice"],
        resources: {fuel: -20},
        nextScene: "scene_002"
      }
    }
  ],
  
  autoEvents: [...]  // Events that trigger automatically
}
```

### NPC Definition
```javascript
{
  id: "npc_engineer",
  name: "Marcus Chen",
  role: "Engineer",
  
  personality: {
    cautious: 7,
    loyal: 8,
    optimism: 4
  },
  
  skills: {
    engineering: 9,
    combat: 3
  },
  
  schedule: {
    default: ["work", "eat", "sleep"],
    emergency: ["repair", "assist"]
  },
  
  goals: ["keep_ship_running", "survive"],
  
  relationships: {
    player: 50,
    npc_cook: 30
  },
  
  dialogs: {...}
}
```

---

## 🔄 Game Flow

### Startup Flow
```
1. Load HTML/CSS/JS
2. Initialize GameManager
3. Check for existing save
   ├─ Yes → Load save
   │        → Calculate offline time
   │        → Run WorldSimulator
   │        → Show summary
   └─ No  → New game
            → Show prologue
4. Start main game loop
```

### Main Game Loop
```
Every frame:
1. Update TimeSystem (deltaTime)
2. Process EventQueue
3. Update World (weather, resources)
4. Update NPCs (if active)
5. Update UI
6. Auto-save (periodic)
```

### Choice Flow
```
1. Player makes choice
2. StoryEngine.processChoice()
   ├─ Apply immediate consequences
   ├─ Update game state
   ├─ Trigger events
   └─ Queue future events
3. WorldSimulator reacts
4. Load next scene
5. Render new state
```

---

## 🎯 Design Principles

### 1. Separation of Concerns
- Mỗi system chỉ làm 1 việc
- Clear interfaces giữa các layers
- Minimize dependencies

### 2. Data-Driven
- Content trong JSON, không hard-code
- Dễ expand, mod, debug
- Designer-friendly

### 3. Performance
- Smart simulation (không brute-force)
- Lazy loading cho scenes
- Efficient state serialization

### 4. Maintainability
- Clear naming conventions
- JSDoc comments
- Modular architecture

### 5. Extensibility
- Plugin-based event system
- Easy to add new NPCs, factions, events
- Modding support foundation

---

## 🚀 Development Phases

### Phase 1: Core Foundation (Week 1-2)
```
[ ] Setup project structure
[ ] Implement GameManager
[ ] Implement TimeSystem
[ ] Basic StoryEngine
[ ] Simple ChoiceSystem
[ ] Save/Load functionality
[ ] Basic UI rendering
```

**Deliverable**: Can play through 5 hardcoded scenes with choices

---

### Phase 2: World Simulation (Week 3-4)
```
[ ] Implement WorldSimulator
[ ] Resource management
[ ] Weather system
[ ] Basic NPC behavior
[ ] Offline simulation
[ ] Event queue system
```

**Deliverable**: World continues when offline, NPCs act independently

---

### Phase 3: Content & Polish (Week 5-6)
```
[ ] Write 30+ story scenes
[ ] Create 15+ NPCs
[ ] Design 50+ events
[ ] Faction system
[ ] Advanced AI
```

**Deliverable**: Full gameplay loop with rich content

---

### Phase 4: Enhancement (Week 7-8)
```
[ ] UI/UX polish
[ ] Animations & transitions
[ ] Sound effects
[ ] Achievement system
[ ] Balance & testing
```

**Deliverable**: Polished, release-ready game

---

## 🔐 Critical Rules

### File Organization
✅ **DO**:
- Production code → `src/`
- Test code → `test/`
- Content → `data/`
- Documentation → `docs/`

❌ **DON'T**:
- Mix test code with production
- Hard-code content in JS
- Leave experimental code in src

### Code Quality
✅ **DO**:
- Write JSDoc comments
- Follow naming conventions
- Keep functions small & focused
- Use meaningful variable names

❌ **DON'T**:
- Write God classes
- Create circular dependencies
- Use magic numbers

### Testing
✅ **DO**:
- Test core systems thoroughly
- All test files in `test/` folder
- Mark experimental code clearly

❌ **DON'T**:
- Leave test code in production
- Skip edge case testing

---

## 📝 Notes

- Architecture designed for **scalability** và **maintainability**
- **Living world** là core feature - architecture support điều này
- **Data-driven** approach để dễ expand content
- Clear separation giúp tránh tái cấu trúc sau này

---

**Version**: 1.0  
**Last Updated**: 2025-12-02  
**Status**: Foundation Design Complete → Ready for Implementation
