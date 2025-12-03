# 🎮 Quick Start Guide - One Click!

## ⚡ Cách Chạy Game

### **Cách 1: PLAY_GAME.bat** (Khuyến nghị)
1. Double-click `PLAY_GAME.bat` ở thư mục gốc
2. Đợi script tự động:
   - ✅ Check Python & Node.js
   - ✅ Clean ports cũ
   - ✅ Install dependencies (nếu cần)
   - ✅ Start backend server
   - ✅ Start frontend
   - ✅ Mở browser tự động

**→ Chỉ cần double-click và chờ!**

---

### **Cách 2: START.bat** (Nhanh nhất)
1. Double-click `START.bat` ở thư mục gốc
2. Game sẽ start ngay (minimal checks)

**→ Nhanh nhất, nhưng cần dependencies đã cài**

---

### **Cách 3: QUICK_START.bat** (Tùy chọn)
- Tương tự START.bat nhưng có thêm output

---

## 📋 Yêu Cầu

### Bắt buộc:
- ✅ Python 3.10+ (tự động check)
- ✅ Internet (để install dependencies)

### Tùy chọn:
- ⚠️ Node.js (cho frontend, nếu không có thì chỉ backend)

---

## 🎯 Sau Khi Start

### Backend Server:
- **URL:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs
- **Window:** "Cultivation Simulator - Backend"

### Frontend:
- **URL:** http://localhost:5173
- **Window:** "Cultivation Simulator - Frontend"

### Browser:
- Tự động mở http://localhost:5173

---

## ⚡ RAM Optimizations

Nếu có `optimizations.py`:
- ✅ Database cache → RAM (10,000x faster)
- ✅ AI response cache (instant cho cached prompts)
- ✅ In-memory SQLite (10x faster)

**→ Game sẽ nhanh hơn đáng kể!**

---

## 🛑 Cách Dừng

1. **Đóng các cửa sổ server** (Ctrl+C trong mỗi window)
2. **Hoặc dùng Task Manager** để kill processes

---

## ❌ Troubleshooting

### "Python not found"
```
→ Cài Python 3.10+ từ python.org
→ Nhớ check "Add to PATH" khi cài
```

### "Node.js not found"
```
→ Cài Node.js từ nodejs.org (optional)
→ Nếu không có, backend vẫn chạy được
```

### "Port already in use"
```
→ Script tự động kill processes cũ
→ Nếu vẫn lỗi, kill thủ công:
   netstat -ano | findstr :8001
   taskkill /PID <PID> /F
```

### "Dependencies failed"
```
→ Check internet connection
→ Chạy thủ công:
   cd cultivation-sim
   pip install -r requirements.txt
   cd cultivation-ui
   npm install
```

---

## 🎉 Tóm Tắt

**Chỉ cần:**
1. Double-click `PLAY_GAME.bat`
2. Đợi vài giây
3. Game tự động mở!

**→ Đơn giản như vậy!** 🚀

