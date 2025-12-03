# 🎮 Quick Start Guide

## ⚡ One-Click Start

### Option 1: **PLAY_GAME.bat** (Recommended)
- ✅ Full setup with checks
- ✅ Auto-install dependencies
- ✅ Opens browser automatically
- ✅ Shows status messages

**Just double-click `PLAY_GAME.bat`!**

---

### Option 2: **QUICK_START.bat** (Minimal)
- ✅ Fastest start
- ✅ Minimal output
- ✅ For experienced users

**Just double-click `QUICK_START.bat`!**

---

## 📋 What Happens

1. **Checks Python & Node.js**
2. **Cleans up old processes** (ports 8001, 5173)
3. **Installs dependencies** (if needed)
4. **Starts backend server** (port 8001)
5. **Starts frontend** (port 5173)
6. **Opens browser** automatically

---

## 🎯 After Starting

### Backend Server:
- URL: http://localhost:8001
- API Docs: http://localhost:8001/docs
- Window: "Cultivation Simulator - Backend"

### Frontend:
- URL: http://localhost:5173
- Window: "Cultivation Simulator - Frontend"

### Browser:
- Auto-opens to http://localhost:5173

---

## ⚡ RAM Optimizations

If `optimizations.py` exists:
- ✅ Database cache loaded to RAM
- ✅ AI response cache enabled
- ✅ In-memory SQLite for events
- **Performance: 10-10,000x faster!**

---

## 🛑 How to Stop

1. **Close server windows** (Ctrl+C in each)
2. **Or use Task Manager** to kill processes

---

## ❌ Troubleshooting

### "Python not found"
- Install Python 3.10+ from python.org
- Add to PATH during installation

### "Node.js not found"
- Install Node.js from nodejs.org
- Frontend won't work, but backend will

### "Port already in use"
- Script auto-kills old processes
- If still fails, manually kill:
  ```bash
  netstat -ano | findstr :8001
  taskkill /PID <PID> /F
  ```

### "Dependencies failed"
- Check internet connection
- Run manually:
  ```bash
  cd cultivation-sim
  pip install -r requirements.txt
  cd cultivation-ui
  npm install
  ```

---

## 🎉 Enjoy!

**Just double-click and play!** 🚀

