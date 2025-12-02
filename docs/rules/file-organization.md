# Hướng Dẫn Tổ Chức File & Folder

> **Mục đích**: Quy định rõ ràng file nào nằm folder nào, tránh lộn xộn

---

## 📁 Cấu Trúc Thư Mục

```
GameBuild/
├── 📄 index.html                 # Entry point của game
├── 📄 PROJECT_STATUS.md          # Trạng thái dự án (ROOT level)
├── 📄 README.md                  # Tổng quan dự án
├── 📄 .gitignore                 # Git ignore rules
│
├── 📁 src/                       # MÃ NGUỒN PRODUCTION
│   ├── 📁 core/                  # Game engine core
│   │   ├── game.js              # Game loop, orchestration
│   │   ├── state.js             # State management
│   │   └── events.js            # Event system
│   │
│   ├── 📁 ai/                    # TÍCH HỢP AI
│   │   ├── gemini.js            # Gemini API integration
│   │   ├── context.js           # Context builder
│   │   ├── parser.js            # Response parser
│   │   └── local-ai.js          # Local AI (Phase 3+)
│   │
│   └── 📁 ui/                    # USER INTERFACE
│       ├── chat.js              # Chat interface logic
│       ├── stats.js             # Stats panel
│       └── renderer.js          # Display rendering
│
├── 📁 data/                      # DỮ LIỆU GAME
│   ├── 📁 prompts/              # System prompts cho AI
│   │   ├── game-master.md       # Main GM prompt
│   │   ├── npc-personalities.md # NPCs prompts
│   │   └── world-lore.md        # World context
│   │
│   └── 📁 static/               # Static content (nếu có)
│       └── initial-scene.json   # Opening scene
│
├── 📁 assets/                    # TÀI NGUYÊN TĨNH
│   ├── 📁 css/                  # Styles
│   │   ├── main.css             # Main stylesheet
│   │   ├── chat.css             # Chat UI
│   │   └── theme.css            # Color theme
│   │
│   ├── 📁 images/               # Hình ảnh (nếu có)
│   └── 📁 sounds/               # Âm thanh (Phase 2+)
│
├── 📁 docs/                      # TÀI LIỆU
│   ├── 📁 architecture/         # Kiến trúc kỹ thuật
│   │   ├── ARCHITECTURE.md      # Full architecture (Phase 3+)
│   │   ├── MVP_ARCHITECTURE.md  # MVP approach ⭐
│   │   ├── CONTRACTS.md         # System contracts
│   │   └── AI_INTEGRATION.md    # AI integration guide
│   │
│   ├── 📁 guides/               # Hướng dẫn
│   │   ├── PROMPTING.md         # Prompt engineering
│   │   └── DEPLOYMENT.md        # Deploy guide
│   │
│   ├── 📁 rules/                # Quy tắc dự án
│   │   ├── update-status.md     # Update status rule
│   │   └── file-organization.md # File này!
│   │
│   ├── DEVELOPMENT_RULES.md     # Coding standards
│   └── CRITICAL_ISSUES.md       # Issues tracker
│
├── 📁 ideas/                     # Ý TƯỞNG & BRAINSTORM
│   └── game-concepts.md         # Game concepts
│
├── 📁 test/                      # TEST CODE ⚠️
│   ├── 📁 unit/                 # Unit tests
│   ├── 📁 integration/          # Integration tests
│   └── 📁 playground/           # Thử nghiệm
│   └── ⚠️ XÓA FOLDER NÀY TRƯỚC KHI RELEASE!
│
└── 📁 .agent/                    # Agent workflows (gitignored)
    └── workflows/
        └── cleanup-test-files.md
```

---

## 🗂️ Quy Tắc Đặt File

### 1. **Code Production** → `src/`

**Nguyên tắc**:
- ✅ Code chạy thực tế
- ✅ Được import trong game
- ❌ KHÔNG có test code
- ❌ KHÔNG có experimental code

**Ví dụ**:
```javascript
// ✅ ĐÚNG: src/ai/gemini.js
export async function callGemini(prompt) { ... }

// ❌ SAI: src/ai/test-gemini.js
function testGeminiAPI() { ... }
```

---

### 2. **AI-Related Code** → `src/ai/`

**Khi nào dùng**:
- ✅ API integration (Gemini, OpenAI)
- ✅ Context building
- ✅ Response parsing
- ✅ Local AI models

**Files**:
```
src/ai/
├── gemini.js          # Gemini API wrapper
├── context.js         # Build context for AI
├── parser.js          # Parse AI responses
└── local-ai.js        # Local models (Phase 3+)
```

---

### 3. **System Prompts** → `data/prompts/`

**Định dạng**: Markdown (`.md`)

**Quy tắc**:
- ✅ Mỗi prompt 1 file riêng
- ✅ Dễ edit, không cần rebuild
- ✅ Version control friendly

**Ví dụ**:
```markdown
<!-- data/prompts/game-master.md -->
You are the Game Master for "The Last Voyage"...

Rules:
- ...
```

---

### 4. **UI/Styling** → `assets/css/`

**Quy tắc**:
- ✅ Tách file theo component
- ✅ Main theme trong `theme.css`
- ❌ Không inline CSS trong HTML

**Files**:
```
assets/css/
├── main.css           # Global styles, imports
├── chat.css           # Chat interface
├── stats.css          # Stats panel
└── theme.css          # Colors, fonts, variables
```

---

### 5. **Documentation** → `docs/`

**Phân loại**:

| Loại | Folder | Ví dụ |
|------|--------|-------|
| **Architecture** | `docs/architecture/` | ARCHITECTURE.md |
| **Guides** | `docs/guides/` | PROMPTING.md |
| **Rules** | `docs/rules/` | update-status.md |
| **Root docs** | `docs/` | DEVELOPMENT_RULES.md |

**Nguyên tắc đặt tên**:
- UPPER_CASE.md cho docs quan trọng
- lower-case.md cho guides

---

### 6. **Test Code** → `test/` ⚠️

**QUAN TRỌNG**:
- ✅ TẤT CẢ test code vào đây
- ✅ Experimental code vào `test/playground/`
- ⚠️ **XÓA toàn bộ folder này trước release!**

**Workflow**:
```bash
# Khi cần xóa test code
/cleanup-test-files
```

---

### 7. **Ideas & Brainstorm** → `ideas/`

**Mục đích**:
- 📝 Brainstorming
- 💡 Game concepts
- 🎨 Design ideas
- ❌ KHÔNG phải docs chính thức

---

## 📋 Checklist Trước Khi Tạo File Mới

### Tự hỏi:

1. **File này là loại gì?**
   - Code production → `src/`
   - AI integration → `src/ai/`
   - System prompt → `data/prompts/`
   - CSS → `assets/css/`
   - Documentation → `docs/`
   - Test → `test/`

2. **Có cần folder con mới không?**
   - Nếu có > 5 files cùng loại → Tạo subfolder

3. **Naming convention đúng chưa?**
   - Code: `camelCase.js`
   - Docs: `UPPER_CASE.md` hoặc `lower-case.md`
   - Prompts: `descriptive-name.md`

---

## 🔍 Ví Dụ Thực Tế

### ❓ "Tôi muốn tạo file để lưu prompt cho NPC Marcus"

**✅ Đúng**: `data/prompts/npc-marcus.md`

**❌ Sai**:
- `src/prompts/marcus.md` - prompts không phải code
- `marcus-prompt.txt` - không follow structure
- `data/marcus.md` - thiếu subfolder

---

### ❓ "Tôi muốn tạo file test cho Gemini API"

**✅ Đúng**: `test/integration/test-gemini-api.js`

**❌ Sai**:
- `src/ai/test-gemini.js` - test không vào src/
- `gemini-test.js` - không có folder structure

---

### ❓ "Tôi muốn lưu CSS cho chat interface"

**✅ Đúng**: `assets/css/chat.css`

**❌ Sai**:
- `src/ui/chat.css` - CSS không vào src/
- `chat-styles.css` - thiếu folder structure
- Inline trong HTML - vi phạm separation

---

## 🚨 Red Flags - Dấu Hiệu Sai

### ❌ Nếu thấy những điều này → SAI!

```
❌ src/test-something.js          # Test code trong src/
❌ data/game.js                    # Code trong data/
❌ marcus.md (root level)          # File lẻ ở root
❌ src/styles.css                  # CSS trong src/
❌ ai-prompt.txt                   # Prompt không có structure
```

---

## ✅ Best Practices

### 1. **Tách Biệt Rõ Ràng**
```
Code (src/) ≠ Data (data/) ≠ Docs (docs/) ≠ Test (test/)
```

### 2. **Một File Một Mục Đích**
```javascript
// ✅ GOOD: ai/gemini.js chỉ làm Gemini API
// ❌ BAD: ai/everything.js làm tất cả
```

### 3. **Naming Consistency**
```
✅ chat.js, chat.css, chat.md      # Consistent naming
❌ chat.js, chatUI.css, Chat.md    # Inconsistent
```

### 4. **Cleanup Regularly**
```bash
# Mỗi tuần
1. Review test/ folder
2. Xóa experimental code
3. Move stable code to src/
```

---

## 📊 Quick Reference

| Tôi cần... | Tạo ở đây | Tên file |
|-----------|-----------|----------|
| **AI API integration** | `src/ai/` | `gemini.js` |
| **System prompt** | `data/prompts/` | `game-master.md` |
| **Game logic** | `src/core/` | `game.js` |
| **UI rendering** | `src/ui/` | `renderer.js` |
| **Styling** | `assets/css/` | `main.css` |
| **Architecture doc** | `docs/architecture/` | `DESIGN.md` |
| **Guide** | `docs/guides/` | `setup.md` |
| **Test code** | `test/` | `test-*.js` |
| **Brainstorm** | `ideas/` | `concept.md` |

---

## 🔄 Khi Cần Refactor

**Dấu hiệu cần refactor structure**:
- ❌ Có > 10 files trong 1 folder (không có subfolder)
- ❌ Không biết file nào nằm đâu
- ❌ Test code lẫn với production code
- ❌ CSS scattered everywhere

**Giải pháp**:
1. Tạo subfolder theo tính năng
2. Move files về đúng chỗ
3. Update imports
4. Test lại

---

**Nhớ**: Structure tốt = Dễ maintain = Ít bug = Happy coding! 🎉
