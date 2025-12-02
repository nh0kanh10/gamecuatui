# Tích Hợp AI - Gemini API

> **Mục đích**: Hướng dẫn tích hợp Gemini API để làm Game Master cho game

---

## 🎯 Tổng Quan

### Game Master AI
**Gemini** đóng vai Game Master:
- Nhận input tự do từ player
- Generate narrative responses
- Maintain world consistency
- Track game state

### Workflow
```
Player: "Tôi nhìn vào đám mây bão"
    ↓
Context: System prompt + History + State
    ↓
Gemini API: Generate response
    ↓
Parser: Extract narrative + state changes
    ↓
Display: Show to player + Update stats
```

---

## 🔑 Setup Gemini API

### 1. Lấy API Key

**Link**: https://makersuite.google.com/app/apikey

**Steps**:
1. Đăng nhập Google Account
2. Create API Key
3. Copy key (dạng: `AIzaSy...`)

### 2. Test API Key

```javascript
// Test đơn giản
const API_KEY = 'AIzaSy...'; // Thay bằng key của bạn
const url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

async function testGemini() {
  const response = await fetch(`${url}?key=${API_KEY}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{
        parts: [{ text: 'Say hello!' }]
      }]
    })
  });
  
  const data = await response.json();
  console.log(data.candidates[0].content.parts[0].text);
  // Should print: "Hello! How can I help you today?"
}

testGemini();
```

**Nếu thành công**: Bạn sẽ thấy response từ Gemini!

---

## 💻 Implementation

### File Structure
```
src/ai/
├── gemini.js          # API wrapper
├── context.js         # Build context
└── parser.js          # Parse responses
```

---

### `src/ai/gemini.js` - API Wrapper

```javascript
// Gemini API configuration
const GEMINI_CONFIG = {
  apiKey: '', // Điền API key vào đây
  model: 'gemini-pro',
  baseUrl: 'https://generativelanguage.googleapis.com/v1beta/models'
};

/**
 * Call Gemini API with conversation history
 * @param {Array} messages - Conversation history
 * @returns {Promise<string>} AI response
 */
export async function callGemini(messages) {
  const url = `${GEMINI_CONFIG.baseUrl}/${GEMINI_CONFIG.model}:generateContent?key=${GEMINI_CONFIG.apiKey}`;
  
  // Convert messages to Gemini format
  const contents = messages.map(msg => ({
    role: msg.role === 'user' ? 'user' : 'model',
    parts: [{ text: msg.content }]
  }));
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contents })
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.candidates[0].content.parts[0].text;
    
  } catch (error) {
    console.error('Gemini API Error:', error);
    throw error;
  }
}

/**
 * Call Gemini with streaming (future feature)
 */
export async function callGeminiStream(messages, onChunk) {
  // TODO: Implement streaming for real-time response
}
```

---

### `src/ai/context.js` - Context Builder

```javascript
/**
 * Build context for Gemini including:
 * - System prompt (world rules, lore)
 * - Conversation history
 * - Current game state
 */

export class ContextBuilder {
  constructor(systemPrompt) {
    this.systemPrompt = systemPrompt;
    this.history = [];
  }
  
  /**
   * Add system instruction
   */
  addSystemMessage(content) {
    this.history.push({
      role: 'system',
      content: content
    });
  }
  
  /**
   * Add player message
   */
  addUserMessage(content) {
    this.history.push({
      role: 'user',
      content: content
    });
  }
  
  /**
   * Add AI response
   */
  addAssistantMessage(content) {
    this.history.push({
      role: 'assistant',
      content: content
    });
  }
  
  /**
   * Build full context with current state
   */
  buildContext(gameState) {
    // Inject current state into context
    const stateContext = `
Current Game State:
- Food: ${gameState.food}
- Fuel: ${gameState.fuel}
- Morale: ${gameState.morale}
- Location: ${gameState.location}
- Weather: ${gameState.weather}
    `.trim();
    
    // Return complete context
    return [
      { role: 'system', content: this.systemPrompt },
      { role: 'system', content: stateContext },
      ...this.history
    ];
  }
  
  /**
   * Get conversation history
   */
  getHistory() {
    return this.history;
  }
  
  /**
   * Clear history (new game)
   */
  clear() {
    this.history = [];
  }
}
```

---

### `src/ai/parser.js` - Response Parser

```javascript
/**
 * Parse AI responses to extract:
 * - Narrative text
 * - State changes (food, fuel, morale)
 * - Special commands
 */

export class ResponseParser {
  /**
   * Parse Gemini response
   * @param {string} response - Raw AI response
   * @returns {Object} Parsed data
   */
  parse(response) {
    return {
      narrative: this.extractNarrative(response),
      stateChanges: this.extractStateChanges(response),
      commands: this.extractCommands(response)
    };
  }
  
  /**
   * Extract main narrative text
   */
  extractNarrative(response) {
    // Remove any metadata/commands
    let text = response;
    
    // Remove state changes (if formatted as [FOOD: -10])
    text = text.replace(/\[([A-Z]+):\s*[+-]?\d+\]/g, '');
    
    // Remove commands (if formatted as {COMMAND: ...})
    text = text.replace(/\{[^}]+\}/g, '');
    
    return text.trim();
  }
  
  /**
   * Extract state changes from response
   * Example: [FOOD: -10] [MORALE: +5]
   */
  extractStateChanges(response) {
    const changes = {};
    const regex = /\[([A-Z]+):\s*([+-]?\d+)\]/g;
    let match;
    
    while ((match = regex.exec(response)) !== null) {
      const [, stat, value] = match;
      changes[stat.toLowerCase()] = parseInt(value);
    }
    
    return changes;
  }
  
  /**
   * Extract special commands
   * Example: {END_GAME: victory}
   */
  extractCommands(response) {
    const commands = [];
    const regex = /\{([A-Z_]+):\s*([^}]+)\}/g;
    let match;
    
    while ((match = regex.exec(response)) !== null) {
      commands.push({
        type: match[1],
        value: match[2]
      });
    }
    
    return commands;
  }
}
```

---

## 🎮 Usage Example

```javascript
import { callGemini } from './ai/gemini.js';
import { ContextBuilder } from './ai/context.js';
import { ResponseParser } from './ai/parser.js';

// Load system prompt
const systemPrompt = await fetch('data/prompts/game-master.md').then(r => r.text());

// Initialize
const context = new ContextBuilder(systemPrompt);
const parser = new ResponseParser();

// Game state
const gameState = {
  food: 100,
  fuel: 100,
  morale: 50,
  location: 'Open Sea',
  weather: 'Clear'
};

// Player sends message
async function handlePlayerInput(input) {
  // Add to context
  context.addUserMessage(input);
  
  // Build full context with state
  const messages = context.buildContext(gameState);
  
  // Call Gemini
  const response = await callGemini(messages);
  
  // Parse response
  const parsed = parser.parse(response);
  
  // Update state
  for (const [stat, change] of Object.entries(parsed.stateChanges)) {
    gameState[stat] += change;
  }
  
  // Add AI response to history
  context.addAssistantMessage(response);
  
  // Display to player
  displayMessage(parsed.narrative);
  updateStats(gameState);
  
  return parsed;
}

// Example
await handlePlayerInput("Tôi nhìn vào bầu trời");
// Gemini responds: "Khi bạn ngẩng đầu lên, bầu trời phía đông..."
```

---

## 📝 System Prompt Guidelines

### Structure

```markdown
# Role Definition
You are the Game Master for "The Last Voyage"...

# World Context
The world has been consumed by rising seas...

# NPCs
- Marcus (Engineer): Cautious, loyal, pessimistic
- Elena (Navigator): Brave, optimistic, reckless

# Rules
1. Maintain consistency
2. Track resources
3. Make choices matter
4. Be descriptive

# Response Format
Narrative text...
[FOOD: -5] (if food consumed)
[MORALE: +10] (if morale changed)
{END_GAME: victory} (if game ends)
```

### Best Practices

1. **Rõ ràng về role**: "You are the Game Master..."
2. **Provide context**: World lore, NPCs, rules
3. **Define format**: Làm sao AI trả về state changes
4. **Examples**: Cho ví dụ conversation tốt
5. **Constraints**: Giới hạn AI (không vượt quá role)

---

## ⚙️ Configuration

### `config.js`

```javascript
export const AI_CONFIG = {
  // Gemini settings
  gemini: {
    apiKey: '', // ĐIỀN VÀO ĐÂY
    model: 'gemini-pro',
    temperature: 0.7, // Creativity (0-1)
    maxTokens: 500,   // Max response length
  },
  
  // Fallback
  fallback: {
    enabled: true,
    staticResponse: "Xin lỗi, AI đang gặp sự cố. Hãy thử lại."
  },
  
  // Rate limiting
  rateLimit: {
    maxRequestsPerMinute: 10,
    cooldown: 1000 // ms between requests
  }
};
```

---

## 🐛 Error Handling

```javascript
export async function callGeminiSafe(messages) {
  try {
    return await callGemini(messages);
  } catch (error) {
    console.error('Gemini Error:', error);
    
    // Handle different error types
    if (error.message.includes('API key')) {
      return "❌ API key không hợp lệ. Vui lòng kiểm tra config.";
    }
    
    if (error.message.includes('429')) {
      return "⏱️ Quá nhiều requests. Vui lòng đợi chút.";
    }
    
    if (error.message.includes('500')) {
      return "🔧 Gemini đang bảo trì. Vui lòng thử lại sau.";
    }
    
    // Generic fallback
    return AI_CONFIG.fallback.staticResponse;
  }
}
```

---

## 📊 Cost Estimation

### Gemini API Pricing (2024)

**Free Tier**:
- 60 requests/minute
- Đủ cho testing & MVP

**Paid** (nếu vượt free tier):
- ~$0.001 per request
- Game session (~50 messages) = ~$0.05

**Conclusion**: Free tier đủ cho personal project! 🎉

---

## 🚀 Next Steps

1. ✅ Lấy Gemini API key
2. ✅ Test với code example
3. ✅ Viết system prompt (`data/prompts/game-master.md`)
4. ✅ Implement trong game
5. ✅ Test & iterate

---

## 🔗 Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **Get API Key**: https://makersuite.google.com/
- **Prompt Guide**: https://www.promptingguide.ai/

---

**Ready to build!** 🤖✨
