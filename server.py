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
        self.save_id: Optional[str] = None
        self.db_path: Optional[str] = None
        self.em = None
        self.context_builder = None
        self.ai = get_gemini_agent()
        self.player_id: Optional[int] = None
        self.turn_count = 0
        self.narrative_log: List[str] = []

game = GameSession()

# Request/Response Models
class NewGameRequest(BaseModel):
    player_name: str = "Hero"

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

# Helper Functions
def init_engine(db_path: str, save_id: str):
    """Initialize engine with specific DB"""
    game.db_path = db_path
    game.save_id = save_id
    
    # Reset global instances
    import engine.core.database
    import engine.core.entity
    engine.core.database._db = None
    engine.core.entity._em = None
    
    game.em = get_entity_manager(get_db(db_path))
    game.context_builder = ContextBuilder(game.em)

def setup_world():
    """Create initial game world"""
    game.player_id = game.em.create_player("Hero")
    
    # NPCs
    guard_id = game.em.create_npc("Old Guard", "entrance", "passive")
    guard_dialogue = game.em.get(guard_id, DialogueComponent)
    guard_dialogue.greeting = "Welcome, traveler. Beware the dungeon ahead."
    game.em.add(guard_id, guard_dialogue)
    
    goblin_id = game.em.create_npc("Goblin", "entrance", "aggressive")
    goblin_stats = game.em.get(goblin_id, StatsComponent)
    goblin_stats.hp = 15
    goblin_stats.max_hp = 15
    game.em.add(goblin_id, goblin_stats)
    
    # Items
    game.em.create_weapon("Iron Sword", damage=12, room_id="entrance")
    game.em.create_item("Torch", "A flickering torch", room_id="entrance")
    
    # Door
    game.em.create_door("Heavy Door", "entrance", is_locked=False)

def get_game_state() -> GameStateResponse:
    """Build current game state"""
    if not game.player_id:
        raise HTTPException(status_code=400, detail="No active game")
    
    context = game.context_builder.build(game.player_id)
    
    return GameStateResponse(
        player_hp=context.player_hp,
        player_max_hp=context.player_max_hp,
        player_name=context.player_name,
        current_room=context.current_room_id,
        room_description=context.room_description,
        inventory=context.inventory,
        visible_entities=context.visible_entities,
        narrative_log=game.narrative_log[-20:]  # Last 20 entries
    )

def apply_updates(updates: dict):
    """Apply state updates from AI"""
    if not updates:
        return

    # Handle HP changes
    if 'target_hp_change' in updates:
        entities = game.em.find_at_location("entrance")
        for eid in entities:
            name = game.em.get_name(eid)
            if "Goblin" in name:
                stats = game.em.get(eid, StatsComponent)
                if stats:
                    stats.hp += updates['target_hp_change']
                    stats.hp = max(0, stats.hp)
                    game.em.add(eid, stats)
                    
                    if stats.hp == 0:
                        state = game.em.get(eid, StateComponent) or StateComponent()
                        state.is_dead = True
                        game.em.add(eid, state)
                break
    
    # Handle Movement
    if 'new_location_id' in updates:
        loc = game.em.get(game.player_id, LocationComponent)
        loc.room_id = updates['new_location_id']
        game.em.add(game.player_id, loc)

# API Routes
@app.post("/game/new")
async def new_game(request: NewGameRequest):
    """Start a new game"""
    os.makedirs("data/saves", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_id = f"save_{timestamp}"
    db_path = f"data/saves/{save_id}.db"
    
    init_engine(db_path, save_id)
    setup_world()
    
    game.narrative_log = [
        "🌍 A new adventure begins...",
        "You find yourself standing at the entrance of a mysterious dungeon."
    ]
    
    return {
        "message": "Game started",
        "save_id": save_id,
        "game_state": get_game_state()
    }

@app.post("/game/load")
async def load_game(request: LoadGameRequest):
    """Load an existing game"""
    db_path = f"data/saves/{request.save_id}.db"
    
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Save file not found")
    
    init_engine(db_path, request.save_id)
    
    game.player_id = game.em.find_player()
    if not game.player_id:
        raise HTTPException(status_code=400, detail="Save file corrupted")
    
    game.narrative_log = ["📂 Game loaded successfully."]
    
    return {
        "message": "Game loaded",
        "save_id": request.save_id,
        "game_state": get_game_state()
    }

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
    if not game.player_id:
        raise HTTPException(status_code=400, detail="No active game")
    
    game.turn_count += 1
    
    # Build context and send to AI
    context = game.context_builder.build(game.player_id)
    response = game.ai.process_turn(request.user_input, context, save_id=game.save_id)
    
    # Apply state updates
    updates = response.get('state_updates', {})
    apply_updates(updates)
    
    # Add to narrative log
    narrative = response.get('narrative', '...')
    game.narrative_log.append(f"🎮 {request.user_input}")
    game.narrative_log.append(f"📖 {narrative}")
    
    return ActionResponse(
        narrative=narrative,
        action_intent=response.get('action_intent', 'NONE'),
        game_state=get_game_state()
    )

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
