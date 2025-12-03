"""
Simple FastAPI Server cho Simple Game
Chỉ 60 lines vs server.py (379 lines)!
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from simple_game import SimpleCultivationGame

app = FastAPI(title="Simple Cultivation Game API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game instance
game: Optional[SimpleCultivationGame] = None

# Request models
class NewGameRequest(BaseModel):
    name: str = "Lâm Tiêu"
    gender: str = "Nam"
    talent: str = "Bình thường"

class ChoiceRequest(BaseModel):
    choice_index: int

# API Routes
@app.post("/game/new")
async def new_game(request: NewGameRequest):
    """Start new game"""
    global game
    game = SimpleCultivationGame()
    
    try:
        result = game.create_character(
            name=request.name,
            gender=request.gender,
            talent=request.talent
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/game/choice")
async def process_choice(request: ChoiceRequest):
    """Process player choice"""
    if not game:
        raise HTTPException(status_code=400, detail="No active game")
    
    try:
        result = game.process_choice(request.choice_index)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/game/save")
async def save_game():
    """Save game"""
    if not game:
        raise HTTPException(status_code=400, detail="No active game")
    
    game.save_to_file("simple_save.json")
    return {"message": "Game saved"}

@app.post("/game/load")
async def load_game():
    """Load game"""
    global game
    game = SimpleCultivationGame()
    
    try:
        game.load_from_file("simple_save.json")
        state = game.get_state()
        
        # Get last choices from conversation
        choices = game._extract_choices(state["last_narrative"])
        
        return {
            "character": state["character"],
            "turn_count": state["turn_count"],
            "narrative": state["last_narrative"],
            "choices": choices
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No save file found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Serve test HTML"""
    return FileResponse("simple_test.html")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌟 Simple Cultivation Game Server")
    print("="*60)
    print("\n📍 URLs:")
    print("   - Game UI:  http://localhost:8001")
    print("   - API Docs: http://localhost:8001/docs")
    print("\n💡 So Sánh:")
    print("   - Simple Server: 60 lines")
    print("   - Complex Server: 379 lines")
    print("\n🚀 Starting server...")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
