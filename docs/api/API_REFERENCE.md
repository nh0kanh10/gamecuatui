# 📚 API Reference

> **Base URL**: `http://localhost:8000`  
> **API Version**: 1.0

---

## 🔐 Authentication

All endpoints (except `/health`) require API key authentication.

**Header**: `X-API-Key: your_api_key_here`

---

## 📋 Endpoints

### Game Management

#### `POST /game/new`
Create a new game.

**Request**:
```json
{
  "player_name": "Hero",
  "game_mode": "last_voyage"
}
```

**Response**:
```json
{
  "message": "Game started",
  "save_id": "save_20251203_123456",
  "game_mode": "last_voyage",
  "game_state": {...}
}
```

**Rate Limit**: 5/minute

---

#### `POST /game/load`
Load an existing game.

**Request**:
```json
{
  "save_id": "save_20251203_123456"
}
```

**Response**:
```json
{
  "message": "Game loaded",
  "save_id": "save_20251203_123456",
  "game_mode": "last_voyage",
  "game_state": {...}
}
```

---

#### `POST /game/action`
Process a player action.

**Request**:
```json
{
  "user_input": "go north"
}
```

**Response**:
```json
{
  "narrative": "You walk north...",
  "action_intent": "MOVE",
  "game_state": {...}
}
```

**Rate Limit**: 
- Per IP: 20/minute
- Per API Key: 60/minute

**Features**:
- ✅ Token budget check
- ✅ Content moderation
- ✅ State locking

---

#### `POST /game/save`
Explicitly save game state.

**Response**:
```json
{
  "message": "Game saved successfully",
  "save_id": "save_20251203_123456"
}
```

**Rate Limit**: 10/minute

---

#### `GET /game/state`
Get current game state.

**Response**:
```json
{
  "player_hp": 100,
  "player_max_hp": 100,
  "player_name": "Hero",
  "current_room": "room_001",
  "room_description": "...",
  "inventory": [...],
  "narrative_log": [...]
}
```

---

#### `GET /game/saves`
List all save files.

**Response**:
```json
{
  "saves": ["save_20251203_123456", "save_20251202_234567"]
}
```

---

#### `GET /game/modes`
List available game modes.

**Response**:
```json
{
  "modes": [
    {
      "id": "last_voyage",
      "name": "The Last Voyage",
      "description": "Post-apocalyptic survival RPG"
    }
  ]
}
```

---

### Memory System

#### `GET /memory/count`
Get memory count for current game.

**Response**:
```json
{
  "count": 42
}
```

---

### Billing

#### `GET /billing/usage`
Get token usage for API key.

**Response**:
```json
{
  "used": 12500,
  "limit": 100000,
  "remaining": 87500,
  "month": "2025-12"
}
```

---

### Health

#### `GET /health`
Health check (no auth required).

**Response**:
```json
{
  "status": "healthy"
}
```

---

## 🔒 Security

### Rate Limiting
- **Per IP**: 20 requests/minute
- **Per API Key**: 60 requests/minute
- **New Game**: 5 requests/minute
- **Save**: 10 requests/minute

### Token Budget
- **Default Limit**: 100,000 tokens/month per API key
- **Per Request Limit**: 10,000 tokens
- **Tracking**: Automatic via Redis

### Content Moderation
- **Input**: Sanitized before processing
- **Output**: Filtered for unsafe content
- **Violations**: Logged for review

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing API key"
}
```

### 409 Conflict
```json
{
  "detail": "Game is being updated by another request"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Remaining: 5 requests"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 📝 Examples

### Python Example
```python
import requests

API_KEY = "your_api_key"
BASE_URL = "http://localhost:8000"

headers = {"X-API-Key": API_KEY}

# Create new game
response = requests.post(
    f"{BASE_URL}/game/new",
    json={"player_name": "Hero", "game_mode": "last_voyage"},
    headers=headers
)
save_id = response.json()["save_id"]

# Process action
response = requests.post(
    f"{BASE_URL}/game/action",
    json={"user_input": "go north"},
    headers=headers
)
print(response.json()["narrative"])
```

### JavaScript Example
```javascript
const API_KEY = "your_api_key";
const BASE_URL = "http://localhost:8000";

// Create new game
const response = await fetch(`${BASE_URL}/game/new`, {
  method: "POST",
  headers: {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    player_name: "Hero",
    game_mode: "last_voyage"
  })
});

const data = await response.json();
console.log(data.save_id);
```

---

**Version**: 1.0  
**Last Updated**: 2025-12-03

