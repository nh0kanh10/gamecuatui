# Kiến Trúc Multi-AI Tối Ưu - The Last Voyage

> **Mục tiêu**: Tăng tốc độ, tăng đa dạng, tối ưu chi phí, TRÁNH vỡ logic

---

## 🚨 CRITICAL WARNING

> **⚠️ VẤN ĐỀ NGHIÊM TRỌNG ĐƯỢC PHÁT HIỆN!**
> 
> Document này có nhiều lỗ hổng bảo mật và consistency:
> - State inconsistency / race conditions
> - Prompt injection risks  
> - Unbounded cost
> - Hallucinationcontrols missing
> - No observability/replay
>
> **📖 ĐỌC NGAY**: [CRITICAL_FIXES.md](CRITICAL_FIXES.md) trước khi implement!
>
> **📋 IMPLEMENTATION PLAN**: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

---

## 🎯 Ý Tưởng Cốt Lõi

### **Nguyên Tắc Vàng: "Phân Quyền Rõ Ràng"**

```
┌─────────────────────────────────────────────┐
│         MỖI AI MỘT NHIỆM VỤ RIÊNG           │
│              KHÔNG CHỒNG CHÉO               │
└─────────────────────────────────────────────┘

Gemini (Master):
├─ Narrative chính
├─ Quản lý state (food, fuel, morale)
└─ Kết hợp tất cả responses

Grok (Characters):
├─ Dialog cho Marcus
├─ Dialog cho Elena  
└─ Dialog cho Cook
   (KHÔNG được đụng state!)

Claude (Optional - Phase 3+):
└─ Logic phức tạp (combat, events)
```

---

## 🏗️ Kiến Trúc Chi Tiết

### **Cấu Trúc File**

```
src/ai/
├── orchestrator.js              # Điều phối AI
├── providers/
│   ├── gemini-provider.js      # Gemini API wrapper
│   ├── grok-provider.js        # Grok API wrapper
│   └── claude-provider.js      # Claude (optional)
├── state-manager.js            # Quản lý state tập trung
└── response-merger.js          # Gộp responses an toàn

data/prompts/
├── gemini/
│   ├── game-master.md          # GM chính (narrative + state)
│   └── dialog-wrapper.md       # Wrap NPC dialogs
└── grok/
    ├── marcus-personality.md   # Marcus character
    ├── elena-personality.md    # Elena character
    └── cook-personality.md     # Cook character
```

---

## 💻 Triển Khai Từng Bước

### **PHASE 0: Foundation (Tuần 1)**

**Mục tiêu**: Game chạy được với Gemini only

```javascript
// Simple single-AI
async function handleInput(input) {
  const response = await gemini.generate({
    systemPrompt: GAME_MASTER_PROMPT,
    userInput: input,
    gameState: gameState
  });
  
  return response;
}
```

**Deliverable**:
- ✅ Chat với Gemini
- ✅ State tracking (food, fuel, morale)
- ✅ Save/load
- ✅ Chơi được 30-60 phút

**Test**: Chơi 1 session hoàn chỉnh không bug

---

### **PHASE 1: Add Grok NPCs (Tuần 2)**

**Mục tiêu**: NPCs có personality riêng biệt

#### **1.1: Tạo Character Prompts**

```markdown
<!-- data/prompts/grok/marcus-personality.md -->

BẠN LÀ Marcus Chen - Kỹ sư tàu "Horizon's Edge"

TÍNH CÁCH:
- Thận trọng, bi quan, trung thành
- Nói ít, giọng trầm
- Chuyên môn cao
- Bảo vệ con tàu như mạng sống

QUY TẮC QUAN TRỌNG:
1. CHỈ tạo dialog - KHÔNG đề cập số liệu cụ thể
2. Phản ứng theo TÂM TRẠNG, không theo state chính xác
3. Sử dụng thuật ngữ kỹ thuật
4. Ngắn gọn (2-3 câu)

❌ KHÔNG NÓI: "Chúng ta còn 65 food"
✅ NÓI: "Đồ ăn đang cạn, Captain"

❌ KHÔNG NÓI: "Bão sẽ đến sau đúng 6 giờ"
✅ NÓI: "Bão đang tới gần"

VÍ DỤ:
Player: "How's the engine?"
Marcus: "Port side's running hot. I can nurse her 
along, but don't push it."
```

#### **1.2: Orchestrator Logic**

```javascript
// src/ai/orchestrator.js

class GameOrchestrator {
  constructor() {
    this.gemini = new GeminiProvider();
    this.grok = new GrokProvider();
    this.stateManager = new StateManager();
  }
  
  async handlePlayerInput(input) {
    // Phân tích input
    const analysis = this.analyzeInput(input);
    
    if (analysis.isNPCConversation) {
      return await this.handleNPCDialog(input, analysis);
    } else {
      return await this.handleGeneralAction(input);
    }
  }
  
  async handleNPCDialog(input, analysis) {
    // PARALLEL: Gọi đồng thời
    const [geminiNarrative, npcDialog] = await Promise.all([
      
      // Gemini: Narrative + state tracking
      this.gemini.generateNarrative({
        input: input,
        state: this.stateManager.getState(),
        context: 'player talking to NPC'
      }),
      
      // Grok: Pure dialog
      this.grok.generateDialog({
        character: analysis.npcName,
        playerSays: input,
        mood: this.stateManager.getNPCMood(analysis.npcName)
        // CHÚ Ý: KHÔNG truyền full state!
      })
    ]);
    
    // Gemini wrap dialog vào narrative
    const final = await this.gemini.wrapDialog({
      narrative: geminiNarrative,
      npcName: analysis.npcName,
      dialog: npcDialog
    });
    
    // CHỈ Gemini được update state
    this.stateManager.applyChanges(
      this.parseStateChanges(final)
    );
    
    return final;
  }
  
  async handleGeneralAction(input) {
    // Chỉ Gemini
    const response = await this.gemini.generate({
      input: input,
      state: this.stateManager.getState()
    });
    
    this.stateManager.applyChanges(
      this.parseStateChanges(response)
    );
    
    return response;
  }
  
  analyzeInput(input) {
    // Detect NPC conversation
    const npcs = ['Marcus', 'Elena', 'Cook'];
    
    for (const npc of npcs) {
      if (input.toLowerCase().includes(npc.toLowerCase())) {
        return {
          isNPCConversation: true,
          npcName: npc
        };
      }
    }
    
    return { isNPCConversation: false };
  }
  
  parseStateChanges(response) {
    // Extract [FOOD: -10], [MORALE: +5], etc.
    const changes = {};
    const regex = /\[([A-Z]+):\s*([+-]?\d+)\]/g;
    let match;
    
    while ((match = regex.exec(response)) !== null) {
      changes[match[1].toLowerCase()] = parseInt(match[2]);
    }
    
    return changes;
  }
}
```

#### **1.3: State Manager**

```javascript
// src/ai/state-manager.js

class StateManager {
  constructor() {
    this.state = {
      food: 100,
      fuel: 100,
      morale: 50,
      day: 1,
      location: 'Open Sea',
      weather: 'Clear',
      npcs: {
        Marcus: { mood: 'neutral', loyalty: 75 },
        Elena: { mood: 'optimistic', loyalty: 60 },
        Cook: { mood: 'mysterious', loyalty: 50 }
      }
    };
  }
  
  getState() {
    return { ...this.state }; // Clone
  }
  
  getNPCMood(npcName) {
    // Trả về mood chung chung, không chi tiết
    const npc = this.state.npcs[npcName];
    const morale = this.state.morale;
    
    if (morale < 30) return 'worried';
    if (morale > 70) return 'hopeful';
    return 'neutral';
  }
  
  applyChanges(changes) {
    for (const [key, value] of Object.entries(changes)) {
      if (this.state.hasOwnProperty(key)) {
        this.state[key] = Math.max(0, this.state[key] + value);
      }
    }
    
    // Auto-save
    this.save();
  }
  
  save() {
    localStorage.setItem('gameState', JSON.stringify(this.state));
  }
  
  load() {
    const saved = localStorage.getItem('gameState');
    if (saved) {
      this.state = JSON.parse(saved);
    }
  }
}
```

**Deliverable Phase 1**:
- ✅ NPCs có personality riêng biệt
- ✅ Responses nhanh hơn (parallel)
- ✅ Gemini + Grok work together
- ✅ KHÔNG có conflict về state

---

### **PHASE 2: Optimization (Tuần 3)**

**Mục tiêu**: Tăng tốc, maximize free tier

#### **2.1: Smart Caching**

```javascript
class ResponseCache {
  constructor() {
    this.cache = new Map();
  }
  
  async getOrGenerate(key, generator) {
    if (this.cache.has(key)) {
      return this.cache.get(key);
    }
    
    const response = await generator();
    this.cache.set(key, response);
    
    return response;
  }
}

// Usage
const dialogCache = new ResponseCache();

const marcusGreeting = await dialogCache.getOrGenerate(
  'marcus_greeting',
  () => grok.generate('Marcus greets player')
);
```

#### **2.2: Request Queue**

```javascript
class APIRateLimiter {
  constructor(maxPerMinute) {
    this.max = maxPerMinute;
    this.queue = [];
    this.count = 0;
  }
  
  async execute(apiCall) {
    // Wait if over limit
    while (this.count >= this.max) {
      await this.sleep(1000);
      this.count = 0; // Reset every second
    }
    
    this.count++;
    return await apiCall();
  }
}

const geminiLimiter = new APIRateLimiter(60);
const grokLimiter = new APIRateLimiter(100);
```

#### **2.3: Fallback Strategy**

```javascript
async function generateWithFallback(input) {
  try {
    // Try Gemini first
    return await geminiLimiter.execute(() =>
      gemini.generate(input)
    );
  } catch (geminiError) {
    console.warn('Gemini failed, using Grok');
    
    try {
      // Fallback to Grok
      return await grokLimiter.execute(() =>
        grok.generate(input)
      );
    } catch (grokError) {
      // Last resort: static response
      return "Hệ thống AI tạm thời gặp sự cố. Vui lòng thử lại.";
    }
  }
}
```

---

### **PHASE 3: Advanced (Tuần 4+)**

**Optional enhancements**:

#### **3.1: Local AI cho Offline**

```javascript
// Sử dụng transformers.js cho local AI
import { pipeline } from '@xenova/transformers';

class LocalAIProvider {
  async init() {
    this.model = await pipeline(
      'text-generation',
      'Xenova/gpt2'
    );
  }
  
  async generate(input) {
    const output = await this.model(input, {
      max_length: 100
    });
    return output[0].generated_text;
  }
}

// Fallback chain
async function smartGenerate(input) {
  if (navigator.onLine) {
    // Online: Use Gemini/Grok
    return await gemini.generate(input);
  } else {
    // Offline: Use local AI
    return await localAI.generate(input);
  }
}
```

#### **3.2: Claude cho Complex Logic**

```javascript
// Chỉ dùng cho tính toán phức tạp
async function resolveComplexEvent(event) {
  const calculation = await claude.calculate({
    prompt: `
Calculate outcomes for storm encounter:
- Ship condition: ${gameState.shipHealth}
- Fuel: ${gameState.fuel}
- Crew morale: ${gameState.morale}

Determine: damage, fuel cost, morale impact
`,
    format: 'json'
  });
  
  // Gemini narrates the result
  const narrative = await gemini.narrate({
    event: 'storm',
    outcome: calculation
  });
  
  return narrative;
}
```

---

## 📊 So Sánh Các Phương Án

| Approach | Speed | Quality | Cost | Complexity | Consistency |
|----------|-------|---------|------|------------|-------------|
| **Single AI (Gemini)** | ⭐⭐ | ⭐⭐⭐ | Free | ⭐⭐⭐ Simple | ⭐⭐⭐ Perfect |
| **Gemini + Grok** ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Free | ⭐⭐ Medium | ⭐⭐⭐ Excellent |
| **Multi-AI + Local** | ⭐⭐⭐ | ⭐⭐ | Free | ⭐ Complex | ⭐⭐ Good |

**⭐ = Lựa chọn tối ưu**

---

## 🎯 Roadmap Triển Khai

### **Tuần 1: Foundation**
```
✅ Gemini only
✅ Basic chat interface
✅ State tracking
✅ Save/load
→ Playable MVP!
```

### **Tuần 2: Add Grok**
```
✅ 3 character prompts (Marcus, Elena, Cook)
✅ Orchestrator logic
✅ Parallel calls
✅ Safe state management
→ Rich NPCs!
```

### **Tuần 3: Polish**
```
✅ Caching
✅ Rate limiting
✅ Error handling
✅ UI improvements
→ Production ready!
```

### **Tuần 4+: Optional**
```
□ Local AI offline support
□ Claude for complex logic
□ Advanced features
→ Enhanced experience!
```

---

## 💰 Chi Phí Ước Tính

### **Free Tier Limits**
```
Gemini Free: 60 requests/minute
Grok Free: 100 requests/minute
Claude Free: 50 requests/minute
```

### **Typical Session**
```
50 player actions
├─ 50 Gemini calls (narrative)
├─ 20 Grok calls (NPC dialogs)
└─ 5 Claude calls (optional, complex events)
= 75 total calls

Time: ~1 hour gameplay
Cost: $0 (within free tier!)
```

### **Heavy Usage**
```
500 actions/day (very heavy!)
= 750 API calls
→ Still within free tier!

If exceed:
- Gemini: ~$0.001/request
- 100 extra calls = $0.10
→ Vẫn rất rẻ!
```

---

## ✅ Checklist Triển Khai

### **Phase 0 (Tuần 1)**
- [ ] Setup Gemini API
- [ ] Create game-master.md prompt
- [ ] Build chat interface (HTML/CSS/JS)
- [ ] Implement state manager
- [ ] Test basic gameplay (30 mins session)

### **Phase 1 (Tuần 2)**
- [ ] Setup Grok API
- [ ] Create 3 character prompts
- [ ] Implement orchestrator
- [ ] Test parallel calls
- [ ] Verify no state conflicts

### **Phase 2 (Tuần 3)**
- [ ] Add caching
- [ ] Implement rate limiting
- [ ] Error handling
- [ ] UI polish
- [ ] Performance testing

### **Phase 3 (Optional)**
- [ ] Local AI integration
- [ ] Claude setup
- [ ] Advanced features

---

## 🔐 Bảo Mật API Keys

```javascript
// ❌ KHÔNG BAO GIỜ hardcode!
const API_KEY = 'AIzaSy...'; // DANGER!

// ✅ Dùng environment variables
const API_KEY = import.meta.env.VITE_GEMINI_KEY;

// ✅ Hoặc config file (gitignored)
import { API_KEYS } from './config.private.js';
```

**.gitignore**:
```
config.private.js
.env
.env.local
```

---

## 🚨 Xử Lý Lỗi

```javascript
async function robustGenerate(input) {
  const maxRetries = 3;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await gemini.generate(input);
    } catch (error) {
      if (i === maxRetries - 1) {
        // Final fallback
        return `[Hệ thống tạm thời quá tải. 
        Vui lòng thử lại sau.]`;
      }
      
      // Wait và retry
      await sleep(1000 * (i + 1));
    }
  }
}
```

---

## 🎨 UI/UX Considerations

```javascript
// Show loading states
function displayThinking() {
  showMessage('🤔 AI đang suy nghĩ...');
}

// Streaming responses (future)
async function streamResponse(input) {
  displayThinking();
  
  const stream = await gemini.generateStream(input);
  
  let fullText = '';
  for await (const chunk of stream) {
    fullText += chunk;
    updateMessage(fullText); // Real-time display!
  }
}
```

---

## 📈 Metrics & Monitoring

```javascript
class PerformanceMonitor {
  track(aiName, duration, success) {
    console.log(`
[${aiName}] 
Duration: ${duration}ms
Success: ${success}
Timestamp: ${Date.now()}
    `);
    
    // Optional: Send to analytics
  }
}

const monitor = new PerformanceMonitor();

async function trackedGenerate(input) {
  const start = Date.now();
  
  try {
    const result = await gemini.generate(input);
    monitor.track('gemini', Date.now() - start, true);
    return result;
  } catch (error) {
    monitor.track('gemini', Date.now() - start, false);
    throw error;
  }
}
```

---

## 🎉 Kết Luận

### **Ý Tưởng Tối Ưu Nhất**

**Gemini (Master) + Grok (NPCs) với Orchestration thông minh**

**Tại sao?**
1. ✅ **Nhanh**: Parallel calls
2. ✅ **Đa dạng**: Mỗi AI có personality khác nhau
3. ✅ **Miễn phí**: Trong free tier
4. ✅ **An toàn**: Không vỡ logic (Gemini control state)
5. ✅ **Scalable**: Dễ thêm AI sau
6. ✅ **Simple enough**: Không quá phức tạp

**Triển khai**:
- Tuần 1: Gemini MVP
- Tuần 2: Add Grok NPCs
- Tuần 3: Polish
- Tuần 4+: Advanced features (optional)

**Chi phí**: $0 (free tier đủ!)  
**Thời gian**: 2-4 tuần đến production-ready  
**Rủi ro**: Thấp (có fallbacks)

---

**READY TO BUILD!** 🚀

---

**Version**: 1.0  
**Last Updated**: 2025-12-02  
**Status**: Detailed Design Complete → Ready for Implementation
