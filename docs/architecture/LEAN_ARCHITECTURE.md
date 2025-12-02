# Lean Architecture - Solo Player Game

> **Mục tiêu**: An toàn, deterministic, nhưng KHÔNG over-engineer cho 1 người chơi

---

## 🎯 Core Philosophy

```
Game này CHỈ cho mình bạn chơi
→ KHÔNG cần enterprise safety
→ KHÔNG cần production monitoring
→ KHÔNG cần multi-user orchestration

CẦN:
✅ Logic nhất quán (state không vỡ)
✅ Trải nghiệm mượt (narrative liền mạch)
✅ Privacy (không ai biết state)
```

---

## ✅ GIỮ LẠI (Core Essentials)

### **1. State Manager (Versioned)**

```javascript
// src/core/state-manager.js

class StateManager {
  constructor() {
    this.state = {
      version: 0,
      food: 100,
      fuel: 100,
      morale: 50
    };
  }
  
  applyDelta(delta) {
    // Simple, deterministic
    for (const [key, value] of Object.entries(delta)) {
      this.state[key] = Math.max(0, this.state[key] + value);
    }
    this.state.version++;
  }
  
  getState() {
    return { ...this.state }; // Clone
  }
}
```

**Tại sao**: Đảm bảo state không tự phá

---

### **2. Command Queue (Single-threaded)**

```javascript
// src/core/command-queue.js

class CommandQueue {
  constructor(stateManager) {
    this.stateManager = stateManager;
    this.queue = [];
    this.processing = false;
  }
  
  async enqueue(command) {
    return new Promise((resolve) => {
      this.queue.push({ command, resolve });
      this.process();
    });
  }
  
  async process() {
    if (this.processing) return;
    this.processing = true;
    
    while (this.queue.length > 0) {
      const { command, resolve } = this.queue.shift();
      
      // Apply command
      this.stateManager.applyDelta(command.delta);
      
      // Log event (simple!)
      this.logEvent(command);
      
      resolve(this.stateManager.getState());
    }
    
    this.processing = false;
  }
  
  logEvent(command) {
    // Simple JSON append
    const event = {
      timestamp: Date.now(),
      command: command
    };
    
    // Append to log file (không cần checksum!)
    appendToFile('events.jsonl', JSON.stringify(event) + '\n');
  }
}
```

**Tại sao**: Chống race condition khi multi-AI parallel

---

### **3. AI Proposals Only**

```javascript
// src/ai/orchestrator.js

class LeanOrchestrator {
  async handleInput(input) {
    // Step 1: Get proposals (parallel - OK!)
    const [geminiProposal, grokProposal] = await Promise.all([
      gemini.generateProposal(input),
      grok.generateDialog(input)
    ]);
    
    // Step 2: Validate
    if (!this.isValidProposal(geminiProposal)) {
      console.warn('Invalid proposal, skipping');
      geminiProposal.delta = {}; // No state change
    }
    
    // Step 3: Queue command (sequential!)
    if (geminiProposal.delta) {
      await this.cmdQueue.enqueue({
        intent: geminiProposal.intent,
        delta: geminiProposal.delta
      });
    }
    
    // Step 4: Format response
    return this.formatResponse(geminiProposal, grokProposal);
  }
  
  isValidProposal(proposal) {
    // Simple validation
    return proposal 
      && proposal.delta 
      && typeof proposal.delta === 'object';
  }
}
```

**Tại sao**: AIs không được ghi trực tiếp state

---

### **4. Simple Sanitizer**

```javascript
// src/security/sanitizer.js

class SimpleSanitizer {
  sanitizeInput(input) {
    // Remove control chars
    let clean = input.replace(/[\x00-\x1F\x7F]/g, '');
    
    // Truncate
    clean = clean.substring(0, 500);
    
    // Remove dangerous patterns (30 patterns, không phải 200!)
    const dangerous = [
      /SYSTEM:/gi,
      /\[INST\]/gi,
      /<\|im_start\|>/gi,
      // ... ~27 more common patterns
    ];
    
    for (const pattern of dangerous) {
      clean = clean.replace(pattern, '');
    }
    
    return clean;
  }
  
  sanitizeState(state) {
    // Whitelist only
    return {
      food: Math.floor(state.food),
      fuel: Math.floor(state.fuel),
      morale: Math.floor(state.morale)
      // NO PII
    };
  }
}
```

**Tại sao**: Chống prompt injection cơ bản, đủ dùng

---

### **5. Simple Budget Limiter**

```javascript
// src/security/budget-limiter.js

class BudgetLimiter {
  constructor(maxCalls = 200) {
    this.maxCalls = maxCalls;
    this.currentCalls = 0;
    this.sessionStart = Date.now();
  }
  
  async execute(apiCall) {
    // Check limit
    if (this.currentCalls >= this.maxCalls) {
      throw new Error('Budget exceeded - refresh to reset');
    }
    
    // Execute
    try {
      const result = await apiCall();
      this.currentCalls++;
      return result;
    } catch (error) {
      // Simple retry
      console.warn('API error, retrying once...');
      return await apiCall(); // Retry once
    }
  }
  
  getRemaining() {
    return this.maxCalls - this.currentCalls;
  }
}
```

**Tại sao**: Tránh cháy ví, nhưng không cần circuit breaker phức tạp

---

## ❌ BỎ ĐI (Over-engineering)

### **1. ❌ Prompt Version Manager**
```
KHÔNG CẦN:
- Git commit hash tracking
- Versioning system
- Migration logic

CHỈ CẦN:
- Prompts trong files
- Edit trực tiếp khi cần
```

### **2. ❌ Event Store với Checksum**
```
KHÔNG CẦN:
- Tamper-proof checksums
- Database-grade integrity
- Audit compliance

CHỈ CẦN:
- events.jsonl (append-only file)
- Replay bằng cách đọc lại file
```

### **3. ❌ Circuit Breaker Enterprise**
```
KHÔNG CẦN:
- Health checks
- Graceful degradation
- Cluster failover

CHỈ CẦN:
- Retry 1 lần
- Show error message
- Done
```

### **4. ❌ Monitoring Dashboard**
```
KHÔNG CẦN:
- Metrics collection
- Performance monitoring
- Alerting system

CHỈ CẦN:
- console.log khi debug
```

### **5. ❌ 200 Red-team Injection Tests**
```
KHÔNG CẦN:
- Professional penetration testing
- Automated security scanning

CHỈ CẦN:
- 30 common injection patterns
- Đủ để chống basic attacks
```

---

## 📁 Lean File Structure

```
src/
├── core/
│   ├── state-manager.js       # State với versioning
│   ├── command-queue.js       # Single-threaded queue
│   └── event-log.js           # Simple JSON append
│
├── ai/
│   ├── orchestrator.js        # Lean orchestrator
│   ├── gemini.js              # Gemini provider
│   └── grok.js                # Grok provider
│
├── security/
│   ├── sanitizer.js           # Simple input cleaning
│   └── budget-limiter.js      # Basic cost control
│
└── utils/
    └── replay.js              # Replay từ events.jsonl

data/
└── prompts/
    ├── gemini-gm.md           # Fixed prompts
    ├── grok-marcus.md
    ├── grok-elena.md
    └── grok-cook.md

# Runtime files (git-ignored)
events.jsonl                   # Event log
state.json                     # Current state backup
```

**Total**: ~500 lines code (thay vì 2000+)

---

## 💻 Complete Implementation

### **Main Game Loop**

```javascript
// main.js - TOÀN BỘ game trong ~150 lines

import { StateManager } from './src/core/state-manager.js';
import { CommandQueue } from './src/core/command-queue.js';
import { LeanOrchestrator } from './src/ai/orchestrator.js';
import { SimpleSanitizer } from './src/security/sanitizer.js';
import { BudgetLimiter } from './src/security/budget-limiter.js';

// Initialize
const stateManager = new StateManager();
const cmdQueue = new CommandQueue(stateManager);
const sanitizer = new SimpleSanitizer();
const budgetLimiter = new BudgetLimiter(200);
const orchestrator = new LeanOrchestrator(cmdQueue, budgetLimiter);

// Load state
function loadState() {
  const saved = localStorage.getItem('gameState');
  if (saved) {
    const state = JSON.parse(saved);
    stateManager.state = state;
  }
}

// Save state
function saveState() {
  localStorage.setItem('gameState', JSON.stringify(stateManager.getState()));
}

// Handle player input
async function handlePlayerInput(input) {
  // Sanitize
  const clean = sanitizer.sanitizeInput(input);
  
  // Process
  const response = await orchestrator.handleInput(clean);
  
  // Save
  saveState();
  
  // Display
  displayResponse(response);
  
  // Update UI
  updateStats(stateManager.getState());
}

// Start
loadState();
render();
```

---

## 🎯 Testing Strategy (Lean)

### **Manual Tests** (Đủ!)

```javascript
// 1. Basic flow
test('Player action → state changes correctly')

// 2. Race condition
test('100 concurrent actions → state deterministic')

// 3. Security
test('30 injection strings → all sanitized')

// 4. Budget
test('201 actions → budget error shown')

// 5. Replay
test('Replay events.jsonl → same state')
```

**Total**: 5 tests, không phải 50!

---

## 📊 Comparison

| Feature | Enterprise | Lean (Solo) |
|---------|-----------|-------------|
| **Lines of Code** | ~2000 | ~500 |
| **Files** | ~25 | ~10 |
| **Complexity** | HIGH | LOW |
| **Safe?** | ✅ Very | ✅ Enough |
| **Overkill?** | ✅ Yes | ❌ No |
| **Fun to build?** | 😰 Stressful | 😊 Enjoyable |

---

## 🚀 Development Timeline

### **Week 1: Core (3-4 days)**
```
Day 1-2: State + Queue + Event log
Day 3-4: Orchestrator + Sanitizer
→ Single-AI MVP working!
```

### **Week 2: Multi-AI (3-4 days)**
```
Day 1-2: Add Grok NPCs
Day 3-4: Test + Polish
→ Multi-AI working safely!
```

**Total**: 1-2 tuần (không phải 3 tuần!)

---

## ✅ What Makes This Safe

1. **State Consistency**: 
   - Single-threaded queue ✅
   - Proposals-only ✅

2. **Security**:
   - Input sanitization ✅
   - No direct state writes ✅

3. **Debugging**:
   - Event log ✅
   - Replay capability ✅

4. **Cost Control**:
   - Budget limiter ✅

**Nhưng KHÔNG có**:
- Enterprise-grade monitoring
- Production-level audit
- Multi-user orchestration
- Over-engineered safety

---

## 💡 Key Principles

### **1. Trải Nghiệm > Enterprise Safety**

```
Game cho 1 người:
→ Ưu tiên: narrative mượt, gameplay fun
→ KHÔNG ưu tiên: audit compliance, SLA 99.9%
```

### **2. Privacy Built-in**

```
Data chỉ ở máy bạn:
→ localStorage (không cloud)
→ events.jsonl (local file)
→ Không analytics
→ Không tracking
```

### **3. Simple = Maintainable**

```
500 lines code:
→ Dễ debug
→ Dễ modify
→ Dễ understand
→ Vui khi code!
```

---

## 🎉 Kết Luận

**Enterprise Architecture** (original):
- ✅ Rất an toàn
- ❌ Quá phức tạp (2000+ lines)
- ❌ Over-kill cho 1 player
- ❌ 3 tuần development
- 😰 Stress khi build

**Lean Architecture** (này):
- ✅ Đủ an toàn
- ✅ Đơn giản (500 lines)
- ✅ Perfect cho solo player
- ✅ 1-2 tuần development
- 😊 Fun khi build!

---

**Version**: Lean 1.0  
**Target**: Solo Player Only  
**Last Updated**: 2025-12-02  
**Status**: READY TO BUILD! 🚀
