"""
FastAPI Server for Game Engine
Exposes the Game as a REST API for the React Frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import glob
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from engine.core import (
    get_entity_manager, get_db,
    LocationComponent, StatsComponent, InventoryComponent,
    IdentityComponent, DialogueComponent, StateComponent
)
from engine.ai import get_gemini_agent, ContextBuilder
from engine.games import LastVoyageGame, CultivationSimGame

app = FastAPI(title="Game Engine API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game state
class GameSession:
    def __init__(self):
        self.game_mode: Optional[str] = None  # "last_voyage" or "cultivation_sim"
        self.game_instance = None  # BaseGame instance
        self.save_id: Optional[str] = None
        self.turn_count = 0
        self.narrative_log: List[str] = []

game = GameSession()

# Request/Response Models
class NewGameRequest(BaseModel):
    player_name: str = "Hero"
    game_mode: str = "last_voyage"  # "last_voyage" or "cultivation_sim"
    character_data: Optional[Dict[str, Any]] = None  # For cultivation_sim

class LoadGameRequest(BaseModel):
    save_id: str

class ActionRequest(BaseModel):
    user_input: str

class GameStateResponse(BaseModel):
    player_hp: int
    player_max_hp: int
    player_name: str
    current_room: str
    room_description: str
    inventory: List[Dict[str, Any]]
    visible_entities: List[Dict[str, Any]]
    narrative_log: List[str]

class ActionResponse(BaseModel):
    narrative: str
    action_intent: str
    game_state: GameStateResponse
    choices: Optional[List[str]] = None  # For cultivation sim

# Helper Functions - Now using game instances

def get_game_state() -> GameStateResponse:
    """Build current game state"""
    if not game.game_instance or not game.game_instance.player_id:
        raise HTTPException(status_code=400, detail="No active game")
    
    state = game.game_instance.get_game_state()
    context = game.game_instance.context_builder.build(game.game_instance.player_id)
    
    return GameStateResponse(
        player_hp=state.get('player_hp', context.player_hp),
        player_max_hp=state.get('player_max_hp', context.player_max_hp),
        player_name=state.get('player_name', context.player_name),
        current_room=state.get('current_room', context.current_room_id),
        room_description=state.get('room_description', context.room_description),
        inventory=state.get('inventory', context.inventory),
        visible_entities=state.get('visible_entities', context.visible_entities),
        narrative_log=game.narrative_log[-20:]  # Last 20 entries
    )

# apply_updates is now handled by game instances

# API Routes
@app.post("/game/new")
async def new_game(request: NewGameRequest):
    """Start a new game"""
    os.makedirs("data/saves", exist_ok=True)
    
    # Create game instance based on mode
    if request.game_mode == "cultivation_sim":
        game_instance = CultivationSimGame()
        character_data = request.character_data or {}
        character_data['player_name'] = request.player_name
        save_id = game_instance.start_new_game(character=character_data, player_name=request.player_name)
    else:
        game_instance = LastVoyageGame()
        save_id = game_instance.start_new_game(player_name=request.player_name)
    
    game.game_mode = request.game_mode
    game.game_instance = game_instance
    game.save_id = save_id
    
    # Get initial narrative
    if request.game_mode == "cultivation_sim":
        # For cultivation sim, AI generates character background
        from engine.ai import get_cultivation_agent
        agent = get_cultivation_agent()
        context = game_instance.context_builder.build(game_instance.player_id)
        char_data = {
            'age': 0,
            'gender': character_data.get('gender', 'Nam'),
            'talent': character_data.get('talent', 'Thiên Linh Căn'),
            'race': character_data.get('race', 'Nhân Tộc'),
            'background': character_data.get('background', 'Gia Đình Tu Tiên')
        }
        response = agent.process_turn("Tạo nhân vật", context, save_id, char_data)
        game.narrative_log = [response.get('narrative', 'Character created')]
        game_instance.character_story = response.get('narrative', '')
        game_instance.current_choices = response.get('choices', [])
    else:
        game.narrative_log = [
            "🌍 A new adventure begins...",
            "You find yourself standing at the entrance of a mysterious dungeon."
        ]
    
    return {
        "message": "Game started",
        "save_id": save_id,
        "game_mode": request.game_mode,
        "game_state": get_game_state()
    }

@app.post("/game/load")
async def load_game(request: LoadGameRequest):
    """Load an existing game"""
    # Determine game mode from save_id
    if request.save_id.startswith("cultivation_sim_"):
        game_instance = CultivationSimGame()
        game_mode = "cultivation_sim"
    else:
        game_instance = LastVoyageGame()
        game_mode = "last_voyage"
    
    try:
        game_instance.load_game(request.save_id)
        game.game_mode = game_mode
        game.game_instance = game_instance
        game.save_id = request.save_id
        game.narrative_log = ["📂 Game loaded successfully."]
        
        return {
            "message": "Game loaded",
            "save_id": request.save_id,
            "game_mode": game_mode,
            "game_state": get_game_state()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load game: {str(e)}")

@app.get("/game/saves")
async def list_saves():
    """List all save files"""
    saves = glob.glob("data/saves/*.db")
    return {
        "saves": [Path(s).stem for s in saves]
    }

@app.post("/game/action", response_model=ActionResponse)
async def process_action(request: ActionRequest):
    """Process a player action"""
    if not game.game_instance or not game.game_instance.player_id:
        raise HTTPException(status_code=400, detail="No active game")
    
    game.turn_count += 1
    
    # Process turn using game instance
    if game.game_mode == "cultivation_sim":
        # For cultivation sim, check if it's a choice selection
        if request.user_input.isdigit():
            choice_idx = int(request.user_input) - 1
            response = game.game_instance.process_year_turn(choice_idx)
        else:
            # Regular input
            response = game.game_instance.process_turn(request.user_input)
    else:
        # Last Voyage or other modes
        response = game.game_instance.process_turn(request.user_input)
    
    # Add to narrative log
    narrative = response.get('narrative', '...')
    game.narrative_log.append(f"🎮 {request.user_input}")
    game.narrative_log.append(f"📖 {narrative}")
    
    # For cultivation sim, include choices in response
    result = {
        "narrative": narrative,
        "action_intent": response.get('action_intent', 'NONE'),
        "game_state": get_game_state()
    }
    
    if game.game_mode == "cultivation_sim" and 'choices' in response:
        result['choices'] = response['choices']
        game.game_instance.current_choices = response['choices']
    
    return ActionResponse(**result)

@app.get("/game/state", response_model=GameStateResponse)
async def get_state():
    """Get current game state"""
    return get_game_state()

@app.get("/memory/count")
async def get_memory_count():
    """Get memory count for current save"""
    if not game.save_id:
        return {"count": 0}
    
    from engine.memory import get_memory_manager
    mm = get_memory_manager()
    count = mm.memory.get_count(game.save_id)
    return {"count": count}

@app.get("/game/modes")
async def list_game_modes():
    """List available game modes"""
    return {
        "modes": [
            {
                "id": "last_voyage",
                "name": "The Last Voyage",
                "description": "Post-apocalyptic survival RPG"
            },
            {
                "id": "cultivation_sim",
                "name": "Cultivation Simulator",
                "description": "Tu Tiên life simulation from birth to cultivation master"
            }
        ]
    }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Game Engine API",
        "status": "running",
        "version": "1.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint (alias)"""
    return {"status": "healthy", "service": "game-engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
