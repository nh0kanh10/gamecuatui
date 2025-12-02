# Game Concepts - Text-Based RPG with Living World

## 🎯 Core Vision
Game text-based RPG với thế giới "sống" - NPCs và events tiếp tục diễn ra khi player offline. Tránh kiểu "mì ăn liền" - muốn narrative chắc chắn, có structure, không phải custom tùy tiện.

---

## 💡 Game Ideas

### 1. 🌊 The Last Voyage - Survival Mystery
**Concept**: Thuyền trưởng con tàu cuối cùng trong thế giới hậu tận thế bị nhấn chìm

**Core Features**:
- Resource Management: thực phẩm, nước, nhiên liệu, morale
- Dynamic Events: đảo bí ẩn, tàu ma, cướp biển, bão
- Crew System: mỗi thành viên có kỹ năng, tính cách, loyalty
- Multiple Endings dựa trên choices
- Rich Narrative qua ship logs, diaries, radio transmissions

**Living World Mechanics**:
- Weather changes overtime
- Resources deplete continuously
- Crew members have daily schedules
- Random encounters based on location
- Factions (pirates, traders) move across map

---

### 2. ⚔️ Blade of Dynasty - Wuxia RPG
**Concept**: Kiếm khách trong thời loạn lạc, chọn phe phái, ảnh hưởng vận mệnh thiên hạ

**Core Features**:
- Faction System: 5 phái (Chính, Tà, Độc lập...), mỗi phe có quest line
- Martial Arts Progression: học võ công theo choices
- Reputation System: hành động ảnh hưởng danh vọng
- Branching Story based on faction, relationships
- ASCII Combat: tactical, chọn chiêu thức

**Living World Mechanics**:
- Faction wars occur automatically
- NPCs change allegiances
- Masters travel between locations
- Tournaments happen on schedule
- Power balance shifts based on victories

---

### 3. 🏛️ Echoes of Rome - Historical Strategy
**Concept**: Patrician trong thời suy tàn La Mã, political intrigue

**Core Features**:
- Political Simulation: alliances, betrayals, senate votes
- Multiple Roles: general, senator, merchant, spy
- Historical Events: có thể thay đổi lịch sử
- Complex Choices với trade-offs rõ ràng
- Character Relationships: NPCs có memory

**Living World Mechanics**:
- Senate votes happen periodically
- Wars progress on frontiers
- Economic conditions change
- Plagues and famines occur
- NPCs plot and scheme independently

---

### 4. 🔮 Codex Arcanum - Magic Academy Mystery
**Concept**: Học sinh năm cuối học viện ma thuật, giải án mạng bí ẩn

**Core Features**:
- Investigation Mechanics: clues, interrogation, divination
- Time Management: học tập vs điều tra vs social
- Spell Crafting: tự tạo spells
- Persistent World: NPCs có schedule
- Mystery Web: mysteries interconnected

**Living World Mechanics**:
- Classes happen on schedule
- NPCs follow daily routines
- Relationships evolve based on interactions
- Mystery clues appear over time
- School events (exams, festivals) occur automatically

---

## 🎮 Selected Concept: The Last Voyage

**Lý do chọn**:
- ✅ Scope manageable (1 tàu, limited crew)
- ✅ Living world dễ implement (weather, resources, crew)
- ✅ Clear win/lose conditions
- ✅ Expandable (thêm islands, factions sau)
- ✅ Narrative focus phù hợp với yêu cầu

**Target Features**:
1. **Core Loop**: Navigate → Encounter Event → Make Choice → Consequences
2. **Living World**: Time passes, resources deplete, crew acts independently
3. **Persistence**: World changes even when offline
4. **Depth**: Rich lore, character development, branching paths

---

## 🌍 Living World System Design

### Core Principle
**"The world doesn't wait for the player"**

### Key Systems

#### 1. Time System
- Real-time to game-time conversion (1 real hour = 1 game day)
- Calculate elapsed time between sessions
- Simulate events that would have occurred

#### 2. NPC AI
```
Each NPC has:
- Daily Schedule (routine)
- Goals & Motivations
- Relationships (player + other NPCs)
- Memory (remembers player actions)
- State Machine (working, traveling, plotting, etc.)
```

#### 3. Faction Dynamics
```
Factions have:
- Power Score (changes over time)
- Territory Control
- Relations with other factions
- Auto-conflicts (wars happen automatically)
- Recruitment (NPCs choose sides)
```

#### 4. Event Queue
```
Events can be:
- Scheduled (predetermined)
- Random (probability-based)
- Chained (event A triggers event B)
- Player-triggered (consequences from past choices)
```

### Simulation Example

**Player offline 24 hours:**
```
Game calculates:
1. Weather changes (storm passed through)
2. Resource depletion (food consumed by crew)
3. NPC actions (engineer repaired engine, cook got sick)
4. Faction movements (pirates moved to new area)
5. Random events (discovered island drifted into view)

Player returns to find:
- "24 hours have passed..."
- Summary of major events
- New situations to handle
- Messages from crew members
```

---

## 📋 Development Priorities

### Must Have (MVP)
- [ ] Basic narrative engine
- [ ] Choice system with consequences
- [ ] Save/Load functionality
- [ ] Time system
- [ ] Simple resource management
- [ ] 5-10 core story scenes

### Should Have (V1.0)
- [ ] Full living world simulation
- [ ] 10-15 NPCs with personalities
- [ ] Faction system
- [ ] 30+ story scenes
- [ ] Multiple endings

### Nice to Have (Future)
- [ ] Sound effects
- [ ] Advanced UI animations
- [ ] Achievement system
- [ ] Multiple playable characters
- [ ] Modding support

---

## 🎨 Aesthetic Direction

**Theme**: Dark, atmospheric, melancholic but hopeful
**Visual Style**: Terminal/ASCII aesthetic with modern CSS
**Color Palette**: 
- Dark blues and grays (ocean, fog)
- Warm ambers (lanterns, hope)
- Deep reds (danger, urgency)

**UI Inspiration**:
- Cyberpunk terminal aesthetics
- Vintage nautical maps
- Ship log interfaces
- Weather-worn documents

---

## 📝 Notes

- Focus on quality over quantity
- Every choice should matter
- NPCs are characters, not just quest-givers
- World should feel alive and reactive
- Narrative depth > gameplay complexity

---

---

## 🤖 **CONCEPT CHÍNH THỨC: AI-Driven Chat RPG** ⭐

### **Thay Đổi Quan Trọng**

**Từ**: Traditional text game với pre-written branches  
**Sang**: AI-driven roleplay với free-form input

### **Concept Mới**

**Không phải**:
```
Game: "Bạn thấy bão đến gần. Bạn làm gì?"
[1] Lướt qua bão
[2] Tìm nơi trú ẩn
```

**Mà là**:
```
Bạn: "Tôi đi đến mạn tàu và nhìn vào đám mây"

Gemini (Game Master): "Khi bạn tiến đến lan can, gió lạnh 
cắt da thịt. Những đám mây phía trước xoáy tròn một cách 
kỳ lạ, tạo thành những hoa văn khiến da bạn nổi gai ốc. 
Marcus, kỹ sư của bạn, hét từ phía sau: 'Thuyền trưởng! 
Đó không phải mây bão bình thường!'"

Bạn: "Tôi hỏi Marcus ý anh ta là gì"

Gemini: "Marcus chỉ tay run rẩy về phía đám mây..."
```

### **Core Mechanics**

#### **1. Free-Form Input**
- Player gõ bất cứ gì muốn làm
- Không bị giới hạn bởi pre-written choices
- Natural language interaction

#### **2. AI Game Master (Gemini)**
- Responds to player actions narratively
- Maintains world consistency
- Tracks game state (food, fuel, morale)
- Creates dynamic events

#### **3. Persistent World State**
```javascript
gameState = {
  food: 100,
  fuel: 100,
  morale: 50,
  location: "Open Sea",
  weather: "Clear",
  day: 3
}
```

AI aware of state và adjust narrative accordingly.

#### **4. AI Modes**

**Phase 0-2**: Gemini API (online)
- Main Game Master
- High quality responses
- Handles complex scenarios

**Phase 3+**: Local AI (offline)
- Background NPCs
- Minor characters
- Autonomous actions

---

### **Gameplay Loop**

```
1. Player types action: "I check the engine room"
   ↓
2. System builds context:
   - System prompt (world rules)
   - Conversation history
   - Current state
   ↓
3. Send to Gemini API
   ↓
4. Gemini generates response:
   "You descend into the engine room. Marcus looks up 
   from a tangle of pipes, grease on his face..."
   [MORALE: +2] (Marcus happy you visited)
   ↓
5. Parse response:
   - Extract narrative
   - Update game state
   ↓
6. Display to player + Save history
```

---

### **Advantages**

✅ **Infinite possibilities** - không bị giới hạn bởi pre-written content  
✅ **Natural interaction** - chat tự nhiên, không awkward choices  
✅ **Dynamic storytelling** - mỗi playthrough khác nhau  
✅ **Less content creation** - AI generates, không cần viết 100 scenes  
✅ **Emergent gameplay** - player creativity matters  

### **Challenges**

⚠️ **Quality control** - AI có thể inconsistent  
⚠️ **State tracking** - phải parse AI responses carefully  
⚠️ **Cost** - API calls (nhưng free tier đủ)  
⚠️ **Internet required** - cần mạng (Phase 0-2)  
⚠️ **Prompt engineering** - system prompt phải tốt  

---

### **Implementation Strategy**

**Phase 0** (2-3h): Basic chat với Gemini
```html
<input type="text" placeholder="What do you do?">
<button>Send</button>
<div id="response"></div>
```

**Phase 1** (1 week): State tracking
- Parse [FOOD: -10] from responses
- Display stats panel
- Save/load conversations

**Phase 2** (1-2 weeks): Enhanced context
- Better prompts
- NPC personalities
- Event systems

**Phase 3** (1 month): Local AI cho NPCs
- Gemini for main story
- Local LLM for background characters

---

### **System Prompt Example**

```markdown
You are the Game Master for "The Last Voyage", a post-
apocalyptic survival RPG set on the last ship in a world 
consumed by rising seas.

WORLD:
- Endless ocean, few islands remain
- Resources scarce
- Pirates, traders, mysterious phenomena
- Atmosphere: Melancholic but hopeful

PLAYER:
- Captain of the ship "Horizon's Edge"
- Responsible for crew survival
- Makes all major decisions

CREW:
- Marcus (Engineer): Loyal, pessimistic, skilled
- Elena (Navigator): Brave, reckless, optimistic  
- Cook (unnamed): Quiet, mysterious

RESOURCES:
- Food: 100 (party of 4, -2/day)
- Fuel: 100 (-5/day sailing)
- Morale: 50 (affects performance)

RULES:
1. Respond narratively to player actions
2. Update resources when appropriate: [FOOD: -5]
3. Track morale changes: [MORALE: +10]
4. End game when food=0 or morale=0: {END_GAME: death}
5. Be descriptive, atmospheric
6. Player choices have real consequences
7. Maintain consistency

RESPONSE FORMAT:
[Narrative text describing what happens]
[FOOD: ±X] (if food changes)
[FUEL: ±X] (if fuel changes)  
[MORALE: ±X] (if morale changes)
{COMMAND: value} (special commands)

Example:
Player: "I share my rations with Marcus"
You: "Marcus looks surprised as you hand him extra food. 
'Thanks, Captain. I was running low.' He smiles, a rare 
sight. [FOOD: -5] [MORALE: +3]"
```

---

### **Why This Concept?**

1. **Personal preference** - User thích chơi roleplay, không thích "mì ăn liền"
2. **Unique** - Khác với traditional text games
3. **Scalable** - Bắt đầu đơn giản, expand dần
4. **Modern** - Leverage AI capabilities
5. **Fun to build** - Prompt engineering là creative process

---

### **Technical Requirements**

**Must Have**:
- ✅ Gemini API key (free)
- ✅ Vanilla JS (no frameworks)
- ✅ localStorage for save
- ✅ Good system prompt

**Nice to Have**:
- ✅ Streaming responses (real-time)
- ✅ Image generation (scenes)
- ✅ Voice input/output
- ✅ Local AI fallback

---

**Last Updated**: 2025-12-02  
**Status**: AI-Driven Concept Finalized → Ready to Build Prototype
