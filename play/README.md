# 🎮 Play Folder

Tất cả các file để chơi game được đặt trong folder này.

## 📁 Files

- **play.py** - CLI version (command line)
- **play_game.bat** - Chạy CLI version (Windows)

> **Note**: Web UI đã chuyển sang React. Xem `react-ui/` folder hoặc chạy `START_REACT_UI.bat` từ root folder.

## 🚀 Cách Chơi

### CLI Version (Command Line)
```bash
# Windows
play_game.bat

# Hoặc trực tiếp
python play.py
```

### React UI (Web Interface - Recommended)
```bash
# Từ root folder (GameBuild/)
START_REACT_UI.bat

# Hoặc manual:
# Terminal 1: python server.py
# Terminal 2: cd react-ui && npm run dev
```

Sau đó mở browser: http://localhost:5173

## ⚙️ Yêu Cầu

1. **Python 3.11+**
2. **Dependencies**: 
   ```bash
   # Từ root folder (GameBuild/)
   pip install -r requirements.txt
   
   # Hoặc chạy script
   play\install_requirements.bat
   ```
3. **Gemini API Key** trong `.env` file (root folder):
   ```
   GEMINI_API_KEY=your_key_here
   ```

## 📝 Lưu Ý

- Tất cả scripts tự động chuyển về root folder để tìm `requirements.txt`
- Database và `.env` file nằm ở root folder
- Scripts có thể chạy từ bất kỳ đâu, nhưng tốt nhất là từ folder `play/`

## 📝 Notes

- Tất cả files trong folder này tự động tìm engine ở parent folder
- Database: `../data/world.db`
- Memory system: Simple Memory (SQLite FTS5)

---

**Status**: ✅ Ready to Play

