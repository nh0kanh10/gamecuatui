# Development Rules & Guidelines

## 🎯 Core Principles

### 1. **Clean Architecture First**
- Thiết kế trước, code sau
- Không code lung tung rồi refactor
- Mọi feature phải fit vào architecture

### 2. **Separation of Production & Test**
- Code production: `src/`, `data/`, `assets/`
- Code test/experimental: `test/` folder
- **KHÔNG BAO GIỜ** mix test code vào production

### 3. **Data-Driven Development**
- Content = Data (JSON), không hard-code
- Code = Logic, không chứa content
- Dễ modify, dễ expand, dễ debug

---

## 📁 File Organization Rules

### ✅ DO - Đúng Cách

```
✓ Production code → src/
✓ Game content → data/
✓ Documentation → docs/
✓ Test files → test/
✓ Ideas/brainstorm → ideas/
✓ Static assets → assets/
```

### ❌ DON'T - Tránh

```
✗ Test code trong src/
✗ Experimental code không được đánh dấu
✗ Hard-coded content trong .js files
✗ Files tạm thời không được clean up
✗ Code không có structure rõ ràng
```

---

## 🗂️ Test Folder Rules

### Mục đích của `test/`
Folder này chứa **TẤT CẢ** code không thuộc production:
- Unit tests
- Integration tests
- Playground code (thử nghiệm)
- Prototype code
- Debug utilities
- Mock data

### Quy tắc sử dụng

1. **Tất cả test code phải vào `test/`**
   ```
   test/
   ├── unit/           # Unit tests
   ├── integration/    # Integration tests
   ├── playground/     # Experimental code
   └── mocks/          # Mock data
   ```

2. **Đặt tên rõ ràng**
   - Test files: `*.test.js` hoặc `*.spec.js`
   - Playground: `playground-<feature>.js`
   - Mocks: `mock-<entity>.js`

3. **Comment mục đích**
   ```javascript
   // TEST ONLY - Thử nghiệm WorldSimulator
   // TODO: Delete sau khi verify logic
   ```

4. **Regular cleanup**
   - Review `test/` folder hàng tuần
   - Xóa code không còn cần thiết
   - Backup nếu muốn giữ lại

5. **Sử dụng workflow cleanup**
   ```
   /cleanup-test-files
   ```

---

## 💻 Coding Standards

### JavaScript Style

#### 1. Naming Conventions
```javascript
// Classes: PascalCase
class GameManager {}
class NPCBehavior {}

// Functions & variables: camelCase
function calculateDamage() {}
let playerHealth = 100;

// Constants: UPPER_SNAKE_CASE
const MAX_CREW_SIZE = 10;
const DEFAULT_FUEL = 100;

// Private properties: _prefixed
class Ship {
  _internalState = {};
}

// File names: PascalCase for classes, camelCase for utilities
GameManager.js
helpers.js
```

#### 2. Function Rules
```javascript
// ✅ GOOD: Small, focused functions
function validateChoice(choice, availableChoices) {
  return availableChoices.includes(choice);
}

// ❌ BAD: God function doing everything
function processEverything() {
  // 500 lines of code...
}
```

#### 3. Comments
```javascript
/**
 * Calculate damage based on weather conditions
 * @param {number} baseDamage - Base damage value
 * @param {Object} weather - Current weather state
 * @returns {number} Modified damage
 */
function calculateWeatherDamage(baseDamage, weather) {
  // Storm increases damage by 50%
  if (weather.type === 'storm') {
    return baseDamage * 1.5;
  }
  return baseDamage;
}
```

#### 4. Error Handling
```javascript
// ✅ GOOD: Proper error handling
function loadScene(sceneId) {
  if (!sceneId) {
    throw new Error('Scene ID is required');
  }
  
  const scene = sceneData[sceneId];
  if (!scene) {
    console.error(`Scene not found: ${sceneId}`);
    return getDefaultScene();
  }
  
  return scene;
}

// ❌ BAD: Silent failures
function loadScene(sceneId) {
  return sceneData[sceneId]; // Returns undefined if not found
}
```

---

## 🏗️ Architecture Rules

### 1. Single Responsibility Principle
Mỗi class/module chỉ làm 1 việc:

```javascript
// ✅ GOOD
class TimeSystem {
  // Chỉ quản lý thời gian
  getCurrentTime() {}
  tick(delta) {}
}

class SaveManager {
  // Chỉ quản lý save/load
  save() {}
  load() {}
}

// ❌ BAD
class GameController {
  // Làm tất cả mọi thứ
  updateTime() {}
  saveGame() {}
  renderUI() {}
  processAI() {}
}
```

### 2. Dependency Injection
```javascript
// ✅ GOOD: Dependencies passed in
class WorldSimulator {
  constructor(timeSystem, eventQueue) {
    this.timeSystem = timeSystem;
    this.eventQueue = eventQueue;
  }
}

// ❌ BAD: Hard-coded dependencies
class WorldSimulator {
  constructor() {
    this.timeSystem = new TimeSystem(); // Tight coupling
  }
}
```

### 3. Don't Repeat Yourself (DRY)
```javascript
// ✅ GOOD: Reusable utility
function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

const health = clamp(playerHealth, 0, 100);
const fuel = clamp(shipFuel, 0, maxFuel);

// ❌ BAD: Repeated logic
const health = Math.min(Math.max(playerHealth, 0), 100);
const fuel = Math.min(Math.max(shipFuel, 0), maxFuel);
```

---

## 📊 Data Structure Rules

### JSON Format Standards

#### Scene Data
```json
{
  "id": "scene_storm_01",
  "title": "The Storm Approaches",
  "content": "Dark clouds gather on the horizon...",
  "conditions": {
    "flags": ["chapter1_started"],
    "resources": {
      "fuel": {"min": 10}
    }
  },
  "choices": [
    {
      "id": "choice_001",
      "text": "Brave the storm",
      "consequences": {
        "flags": ["brave_decision"],
        "resources": {"fuel": -20, "morale": -10},
        "nextScene": "scene_storm_02"
      }
    }
  ]
}
```

#### NPC Data
```json
{
  "id": "npc_engineer",
  "name": "Marcus Chen",
  "role": "Engineer",
  "personality": {
    "cautious": 7,
    "loyal": 8,
    "optimism": 4
  },
  "skills": {
    "engineering": 9,
    "combat": 3,
    "navigation": 5
  },
  "schedule": {
    "default": ["work_engine", "eat", "sleep"],
    "emergency": ["repair", "assist_crew"]
  }
}
```

### Validation Rules
- All IDs must be unique
- All references must be valid (no broken links)
- Numbers in reasonable ranges
- Required fields must exist

---

## 🔍 Code Review Checklist

Trước khi commit, check:

- [ ] Code theo đúng architecture?
- [ ] Không có test code trong `src/`?
- [ ] Functions nhỏ và focused?
- [ ] Có comments cho logic phức tạp?
- [ ] Error handling proper?
- [ ] Naming conventions đúng?
- [ ] Không có magic numbers?
- [ ] Không có code duplication?
- [ ] Data-driven (không hard-code content)?

---

## 🚫 Common Anti-Patterns to Avoid

### 1. God Objects
```javascript
// ❌ BAD
class Game {
  updatePhysics() {}
  renderGraphics() {}
  handleInput() {}
  manageAI() {}
  saveData() {}
  // ... 50 more methods
}
```

### 2. Magic Numbers
```javascript
// ❌ BAD
if (playerHealth < 20) {
  // What does 20 mean?
}

// ✅ GOOD
const CRITICAL_HEALTH_THRESHOLD = 20;
if (playerHealth < CRITICAL_HEALTH_THRESHOLD) {
  // Clear meaning
}
```

### 3. Callback Hell
```javascript
// ❌ BAD
loadScene(id, (scene) => {
  processScene(scene, (result) => {
    updateUI(result, (response) => {
      // ...
    });
  });
});

// ✅ GOOD: Use async/await
async function loadAndProcess(id) {
  const scene = await loadScene(id);
  const result = await processScene(scene);
  const response = await updateUI(result);
  return response;
}
```

### 4. Tight Coupling
```javascript
// ❌ BAD
class NPCBehavior {
  act() {
    window.gameManager.updateWorld(); // Global dependency
  }
}

// ✅ GOOD
class NPCBehavior {
  constructor(worldUpdater) {
    this.worldUpdater = worldUpdater;
  }
  
  act() {
    this.worldUpdater.update();
  }
}
```

---

## 📝 Documentation Requirements

### Code Documentation
- Mọi public class cần JSDoc header
- Complex functions cần explain logic
- Magic numbers cần comment giải thích

### Architecture Documentation
- Update `ARCHITECTURE.md` khi thay đổi cấu trúc
- Document major design decisions
- Keep diagrams up to date

### Content Documentation
- Maintain content changelog
- Document scene flow diagrams
- List all available flags/conditions

---

## 🔄 Git Workflow

### Commit Message Format
```
<type>: <short description>

<detailed explanation if needed>

Examples:
feat: Add weather system simulation
fix: Correct offline time calculation
docs: Update architecture diagram
test: Add WorldSimulator unit tests
refactor: Simplify NPC decision logic
```

### Branch Strategy
```
main          → Production-ready code
develop       → Active development
feature/*     → New features
fix/*         → Bug fixes
test/*        → Experimental (delete after merge)
```

---

## 🧹 Cleanup Procedures

### Daily
- [ ] Remove console.log statements
- [ ] Delete commented-out code
- [ ] Clean up imports

### Weekly
- [ ] Review `test/` folder
- [ ] Delete unused files
- [ ] Update documentation

### Before Release
- [ ] Run full cleanup workflow
- [ ] Remove all test code
- [ ] Verify no debug code in production
- [ ] Optimize asset sizes

---

## ⚡ Performance Guidelines

### 1. Avoid Unnecessary Calculations
```javascript
// ✅ GOOD: Calculate once
const distance = calculateDistance(a, b);
if (distance < threshold) {
  doSomething(distance);
}

// ❌ BAD: Calculate multiple times
if (calculateDistance(a, b) < threshold) {
  doSomething(calculateDistance(a, b));
}
```

### 2. Lazy Loading
```javascript
// ✅ GOOD: Load scenes on demand
function loadScene(id) {
  return import(`./data/scenes/${id}.json`);
}

// ❌ BAD: Load everything upfront
const allScenes = importAllScenes(); // Heavy!
```

### 3. Efficient Loops
```javascript
// ✅ GOOD: Cache length
const len = npcs.length;
for (let i = 0; i < len; i++) {
  npcs[i].update();
}

// ❌ BAD: Recalculate every iteration
for (let i = 0; i < npcs.length; i++) {
  npcs[i].update();
}
```

---

## 🎯 Final Reminders

1. **Architecture First**: Thiết kế trước, code sau
2. **Test Isolation**: Test code PHẢI ở `test/` folder
3. **Data-Driven**: Content trong JSON, logic trong JS
4. **Clean Code**: Readable, maintainable, focused
5. **Regular Cleanup**: Không để rác tích tụ

**Mục tiêu**: Code base clean, maintainable, scalable - tránh tái cấu trúc sau này!

---

**Version**: 1.0  
**Last Updated**: 2025-12-02  
**Status**: Active Guidelines
