"""
FastAPI Server for Game Engine
Exposes the Game as a REST API for the React Frontend
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import glob
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import asyncio

# Auth and rate limiting
from engine.auth import require_api_key, setup_rate_limiter, create_rate_limit_decorator
from engine.auth.rate_limiter import rate_limit_key_func

# State management
from engine.state import (
    acquire_lock, release_lock,
    save_state, load_state, snapshot_save,
    periodic_snapshot_worker
)

# Cost control
from engine.llm.cost_control import check_and_charge_tokens, estimate_tokens, get_token_usage

# Moderation
from engine.moderator import moderate_content, is_safe_content

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

# Setup rate limiting
limiter = setup_rate_limiter(app)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task: Start periodic snapshot worker
@app.on_event("startup")
async def startup_event():
    """Start background workers on startup"""
    # Start snapshot worker in background
    asyncio.create_task(periodic_snapshot_worker(interval_seconds=60))

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
@create_rate_limit_decorator("5/minute")  # Limit new game creation
async def new_game(
    request: Request,
    game_request: NewGameRequest,
    api_key: str = Depends(require_api_key)
):
    """Start a new game"""
    request.state.api_key = api_key
    os.makedirs("data/saves", exist_ok=True)
    
    # Create game instance based on mode
    if game_request.game_mode == "cultivation_sim":
        game_instance = CultivationSimGame()
        character_data = game_request.character_data or {}
        character_data['player_name'] = game_request.player_name
        save_id = game_instance.start_new_game(character=character_data, player_name=game_request.player_name)
    else:
        game_instance = LastVoyageGame()
        save_id = game_instance.start_new_game(player_name=game_request.player_name)
    
    game.game_mode = game_request.game_mode
    game.game_instance = game_instance
    game.save_id = save_id
    
    # Acquire lock for initial state
    await acquire_lock(save_id, ttl=30)
    try:
        # Get initial narrative
        if game_request.game_mode == "cultivation_sim":
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
        
        # Save initial state to Redis
        game_state = get_game_state()
        await save_state(save_id, {
            "game_mode": game.game_mode,
            "turn_count": game.turn_count,
            "narrative_log": game.narrative_log,
            "game_state": game_state
        })
        
        # Snapshot to SQLite immediately
        await snapshot_save(save_id)
        
        return {
            "message": "Game started",
            "save_id": save_id,
            "game_mode": game_request.game_mode,
            "game_state": game_state
        }
    finally:
        await release_lock(save_id)

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
@create_rate_limit_decorator("20/minute")  # Per-IP limit
@create_rate_limit_decorator("60/minute", key_func=rate_limit_key_func)  # Per-API-key limit
async def process_action(
    request: Request,
    action_request: ActionRequest,
    api_key: str = Depends(require_api_key)
):
    """Process a player action with rate limiting and cost control"""
    if not game.game_instance or not game.game_instance.player_id:
        raise HTTPException(status_code=400, detail="No active game")
    
    # Store API key in request state for rate limiting
    request.state.api_key = api_key
    
    # Estimate tokens for cost control
    user_input = action_request.user_input
    tokens_estimate = estimate_tokens(user_input)
    
    # Check token budget
    allowed, remaining = await check_and_charge_tokens(api_key, tokens_estimate)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Token limit exceeded. Remaining: {remaining} tokens this month."
        )
    
    # Acquire lock for state update
    save_id = game.save_id
    if not await acquire_lock(save_id, ttl=30):
        raise HTTPException(status_code=409, detail="Game is being updated by another request")
    
    try:
        game.turn_count += 1
        
        # Process turn using game instance
        if game.game_mode == "cultivation_sim":
            # For cultivation sim, check if it's a choice selection
            if user_input.isdigit():
                choice_idx = int(user_input) - 1
                response = game.game_instance.process_year_turn(choice_idx)
            else:
                # Regular input
                response = game.game_instance.process_turn(user_input)
        else:
            # Last Voyage or other modes
            response = game.game_instance.process_turn(user_input)
        
        # Moderate narrative content
        narrative = response.get('narrative', '...')
        is_safe, reason = moderate_content(narrative)
        if not is_safe:
            narrative = "Nội dung đã được lọc để đảm bảo an toàn."
            print(f"⚠️  Content moderated: {reason}")
        
        # Add to narrative log
        game.narrative_log.append(f"🎮 {user_input}")
        game.narrative_log.append(f"📖 {narrative}")
        
        # Save state to Redis
        game_state = get_game_state()
        await save_state(save_id, {
            "game_mode": game.game_mode,
            "turn_count": game.turn_count,
            "narrative_log": game.narrative_log[-50:],  # Last 50 entries
            "game_state": game_state
        })
        
        # For cultivation sim, include choices in response
        result = {
            "narrative": narrative,
            "action_intent": response.get('action_intent', 'NONE'),
            "game_state": game_state
        }
        
        if game.game_mode == "cultivation_sim" and 'choices' in response:
            result['choices'] = response['choices']
            game.game_instance.current_choices = response['choices']
        
        return ActionResponse(**result)
    
    finally:
        # Release lock
        await release_lock(save_id)

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
async def list_game_modes(api_key: str = Depends(require_api_key)):
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

@app.get("/billing/usage")
async def get_billing_usage(api_key: str = Depends(require_api_key)):
    """Get token usage for API key"""
    usage = await get_token_usage(api_key)
    return usage

@app.post("/game/save")
@create_rate_limit_decorator("10/minute")
async def save_game(
    request: Request,
    api_key: str = Depends(require_api_key)
):
    """Explicitly save game state to SQLite"""
    if not game.save_id:
        raise HTTPException(status_code=400, detail="No active game to save")
    
    request.state.api_key = api_key
    
    # Acquire lock
    if not await acquire_lock(game.save_id, ttl=10):
        raise HTTPException(status_code=409, detail="Game is being updated")
    
    try:
        # Snapshot to SQLite
        await snapshot_save(game.save_id)
        return {"message": "Game saved successfully", "save_id": game.save_id}
    finally:
        await release_lock(game.save_id)

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
