# 🐛 Troubleshooting Guide

## 404 Not Found Error

### Problem
```
HTTPException: 404: Not Found
```

### Solutions

#### 1. Server Not Running
**Check:**
```bash
# Check if server is running
curl http://localhost:8000/

# Or open in browser
http://localhost:8000
```

**Fix:**
```bash
# Start server
python server.py

# Or use script
start_server.bat
```

#### 2. Wrong Port
**Check:** Frontend expects `http://localhost:8000`

**Fix:** Make sure server runs on port 8000:
```python
# In server.py
uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 3. CORS Issues
**Check:** Browser console for CORS errors

**Fix:** Server already has CORS enabled, but check:
```python
# In server.py - should be:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ...
)
```

#### 4. Route Not Found
**Check:** Available routes:
- `GET /` - Health check
- `GET /health` - Health check (alias)
- `POST /game/new` - New game
- `POST /game/load` - Load game
- `GET /game/saves` - List saves
- `POST /game/action` - Send action
- `GET /game/state` - Get state
- `GET /memory/count` - Memory count

**Fix:** Check `server.py` for all routes

---

## Connection Errors

### Problem
```
Cannot connect to server at http://localhost:8000
```

### Solutions

1. **Start Server First**
   ```bash
   python server.py
   ```

2. **Check Firewall**
   - Windows Firewall might block port 8000
   - Allow Python through firewall

3. **Check Port Availability**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # If port is in use, change port in server.py
   ```

---

## API Errors

### Problem
```
Failed to start game. Make sure the server is running!
```

### Solutions

1. **Check Server Status**
   - UI shows server status in menu
   - Green = connected
   - Red = disconnected

2. **Check API Key**
   - Make sure `.env` has `GEMINI_API_KEY`
   - Restart server after adding API key

3. **Check Logs**
   - Server console shows errors
   - Check for import errors, missing dependencies

---

## Quick Fixes

### Restart Everything
```bash
# 1. Stop server (Ctrl+C)
# 2. Start server
python server.py

# 3. Refresh browser/UI
```

### Check Dependencies
```bash
python -c "import fastapi, uvicorn, google.generativeai; print('OK')"
```

### Check API Key
```bash
# Windows PowerShell
$env:GEMINI_API_KEY
```

---

**Status**: ✅ Common Issues Covered

