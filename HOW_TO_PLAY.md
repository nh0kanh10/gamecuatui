# 🎮 How to Play

## Quick Start

```bash
play_game.bat
```

Hoặc:
```bash
venv\Scripts\activate
python play.py
```

---

## Commands

Nhập lệnh **tự nhiên** bằng tiếng Anh:

### Di chuyển
- `go north / south / east / west`
- `move to the door`

### Tương tác với vật phẩm
- `take the sword`
- `pick up torch`
- `drop sword`
- `equip iron sword`

### Chiến đấu
- `attack the goblin`
- `fight goblin`
- `strike the enemy`

### Nói chuyện
- `talk to the guard`
- `speak with old guard`

### Khám phá
- `examine the door`
- `look at torch`
- `inspect room`

### Quản lý
- `open door`
- `close door`
- `unlock heavy door`

### Hệ thống
- `status` - Hiển thị trạng thái hiện tại
- `help` - Hiển thị help
- `quit` - Thoát game

---

## Example Session

```
🎮 > take the sword
🤖 AI parsing input...
   → Interpreted as: TAKE

📖 Generating narrative...

With practiced fingers, you lifted the heavy iron sword from 
its resting place and felt its weight settle into your grasp.

🎮 > equip iron sword
🤖 AI parsing input...
   → Interpreted as: EQUIP

📖 You ready the iron sword, feeling its balance.

🎮 > attack the goblin
🤖 AI parsing input...
   → Interpreted as: ATTACK

📖 Your blade connects with the goblin's flesh! The creature 
staggers back, wounded but still dangerous.

   💥 Dealt 22 damage! (Target HP: 0)
   💀 Enemy defeated!
```

---

## Features

✅ **Natural Language Input** - Viết tự nhiên, AI hiểu
✅ **AI-Generated Narrative** - Mô tả sống động cho mỗi action
✅ **Physics Validation** - Không thể làm điều vô lý
✅ **Real Combat** - Damage calculation, death detection
✅ **Inventory System** - Take/drop/equip items
✅ **NPC Dialogue** - Talk to characters

---

## Current World

**NPCs:**
- Old Guard (passive) - Can talk, knows about quests
- Goblin (aggressive) - 15 HP, can be attacked

**Items:**
- Iron Sword - 12 damage
- Torch - Light source

**Objects:**
- Heavy Door - Can open/close

---

## Tips

1. **Try natural language** - "pick up the shiny sword" works!
2. **Check status often** - `status` shows HP, inventory, location
3. **Talk to NPCs** - They have useful information
4. **Equip weapons** - More damage in combat

---

## Powered By

- **Engine**: Custom ECS (Entity-Component-System)
- **AI**: Ollama (qwen2.5:3b local model)
- **Database**: SQLite (auto-saves state)
- **Validation**: Precondition system (prevents invalid actions)

---

**Enjoy your adventure!** 🗡️
