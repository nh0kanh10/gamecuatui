# ✅ Physique System V2 - Cơ Chế Thực Tế

## 🎯 Thay Đổi Quan Trọng

**Vấn đề cũ:**
- ❌ Chỉ có số liệu (effects) → AI có thể viết sai
- ❌ Không có cơ chế khóa/mở tính năng
- ❌ Không có prompt để AI viết đúng

**Giải pháp mới:**
- ✅ **Cơ chế hệ thống** - Khóa/mở tính năng cụ thể
- ✅ **AI Prompt** - Đảm bảo AI viết đúng theo thể chất
- ✅ **Forbidden Words** - Ngăn AI dùng từ không phù hợp
- ✅ **Modifiers** - Số liệu được tính toán, không phải AI viết

---

## 📋 8 Thể Chất Gameplay

### **1. Phế Linh Mạch**
- **Khóa:** Tu luyện, đột phá, công pháp nội khí
- **Mở:** Võ thể, Ma hóa, Huyết thuật, Đan phụ
- **Prompt:** Không được dùng "linh lực", "chân khí", "tu vi"
- **Style:** Phàm nhân dùng thể lực

### **2. Đạo Thai Thiên Mệnh**
- **Mở:** Ngộ đạo path, Heavenly insight
- **Modifier:** +300% enlightenment rate
- **Prompt:** Miêu tả ngộ đạo tự nhiên, đạo lý tự chảy vào tâm

### **3. Ma Tâm Dị Thai**
- **Modifier:** +200% cultivation speed
- **Cơ chế:** Tăng Heart Demon Points mỗi lần tu
- **Threshold:** 50 points → mất kiểm soát
- **Prompt:** Thì thầm, ảo giác, giằng xé nội tâm

### **4. Linh Căn Vô Tướng**
- **Mở:** Học mọi công pháp
- **Modifier:** Technique growth 75%
- **Fusion:** 3 công pháp khác hệ → Ngũ Hành Hợp Nhất
- **Prompt:** Hòa hợp, trống rỗng, dung nạp mọi lực

### **5. Bất Tử Mộc Thai**
- **Cơ chế:** Hồi máu 5% mỗi 3s
- **Revive:** 1 lần/tuần với 30% HP
- **Weakness:** Yếu trước hỏa hệ
- **Prompt:** Tái sinh, mọc lại, nhưng dễ bị đốt

### **6. Hàn Tủy Băng Tâm**
- **Modifier:** +80% heart demon resistance
- **Stability:** +30% cultivation stability
- **Penalty:** -20% emotional buffs
- **Prompt:** Tâm trí lạnh, suy nghĩ rõ như tuyết tan

### **7. Hỗn Độn Tiên Thai**
- **Mở:** Tất cả hệ, Rule breaking
- **Modifier:** -10% damage taken
- **Breakthrough:** Giảm 50% yêu cầu
- **Prompt:** Hỗn loạn, quy tắc méo mó

### **8. Tịch Diệt Chi Cốt**
- **Khóa:** Normal qi absorption
- **Mở:** Killing path, Destruction cultivation
- **Modifier:** Tu chậm 70%, damage theo % HP địch
- **Prompt:** Trống rỗng, lạnh lẽo, sát ý tự nhiên

---

## ⚙️ System Mechanics

### **Locks/Unlocks:**
```python
# Check if feature is locked
if physique_system.check_locks(physique_id, 'cultivation_qi_absorption'):
    # Cannot cultivate normally
    
# Check if feature is unlocked
if physique_system.check_unlocks(physique_id, 'martial_body_path'):
    # Can use martial body path
```

### **Modifiers:**
```python
# Get modifiers (calculated, not AI-written)
modifiers = physique_system.get_modifiers(physique_id)
# {
#   "cultivation_speed_multiplier": 3.0,
#   "enlightenment_rate_multiplier": 4.0,
#   "heart_demon_points_per_cultivation": 1,
#   ...
# }
```

### **AI Prompt Integration:**
```python
# Get prompt for AI
prompt = physique_system.get_ai_prompt(physique_id)
# Automatically added to agent prompt

# Get forbidden words
forbidden = physique_system.get_forbidden_words(physique_id)
# ["linh lực", "chân khí", "tu vi", ...]
```

---

## 🔧 Game Integration

### **1. Character Creation:**
- Assign physique based on talent tier
- Store physique_id in game state

### **2. Cultivation:**
- Check if cultivation is locked
- Apply speed modifiers (calculated)
- Track heart demon points

### **3. AI Prompt:**
- Automatically inject physique prompt
- Add forbidden words check
- Ensure AI writes correctly

### **4. Combat/Other:**
- Apply damage reduction
- Check unlocks for techniques
- Apply HP regen, revive, etc.

---

## ✅ Benefits

**1. Đảm bảo đúng:**
- ✅ Số liệu được tính toán, không phải AI viết
- ✅ Cơ chế khóa/mở rõ ràng
- ✅ AI viết đúng nhờ prompt

**2. Gameplay thực tế:**
- ✅ Thay đổi cách chơi thực sự
- ✅ Mở nhánh riêng
- ✅ Có trade-offs

**3. Dễ mở rộng:**
- ✅ Thêm thể chất mới dễ dàng
- ✅ Chỉ cần thêm vào JSON
- ✅ Tự động tích hợp

---

## 📊 Example Usage

```python
# In game.py
if self.character_physique:
    # Check locks
    if self.physique_system.apply_cultivation_lock(self.character_physique):
        # Cannot cultivate - remove cultivation updates
        updates.pop('cultivation', None)
    
    # Apply modifiers
    speed = self.physique_system.apply_cultivation_speed(
        self.character_physique, base_speed
    )
    
    # Track heart demon
    self.heart_demon_points += self.physique_system.apply_heart_demon_points(
        self.character_physique, 0
    )
```

```python
# In agent.py (automatic)
physique_prompt = physique_system.get_ai_prompt(physique_id)
# Added to prompt automatically
```

---

## 🎮 Status

**Backend:** ✅ Complete
- PhysiqueSystemV2 class
- 8 gameplay physiques
- System mechanics
- AI prompt integration

**Frontend:** ✅ Ready
- AttributesPanel supports physique
- Will display physique info

**Next:**
- Test với từng thể chất
- Verify AI writes correctly
- Add more physiques if needed

---

**Hệ thống thể chất với cơ chế thực tế đã sẵn sàng!** 🎉

