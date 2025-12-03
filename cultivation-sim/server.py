"""
FastAPI Server for Cultivation Simulator
Exposes the Game as a REST API for the React Frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import sys
import traceback
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import logging

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Import game
from game import CultivationSimulator

app = FastAPI(title="Cultivation Simulator API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game instance
_game_instance: Optional[CultivationSimulator] = None

# Request models
class CharacterData(BaseModel):
    gender: str
    talent: str
    race: str
    background: str
    physique_id: Optional[str] = None

class NewGameRequest(BaseModel):
    player_name: str
    character_data: CharacterData

class ActionRequest(BaseModel):
    user_input: str  # Choice index (1-6) or text

class ActionResponse(BaseModel):
    narrative: str
    choices: List[str]
    game_state: Dict[str, Any]
    debug_info: Optional[Dict[str, Any]] = None

def safe_to_dict(obj):
    """Safely convert Pydantic model to dict (v1/v2 compatible)"""
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    elif hasattr(obj, 'dict'):
        return obj.dict()
    else:
        return obj

def _normalize_game_state(game_state: Dict[str, Any], save_id: str, character_name: str) -> Dict[str, Any]:
    """
    Normalize game state for React frontend compatibility
    Ensures all fields match React GameState interface
    """
    # Ensure character_name exists (React expects this)
    if 'character_name' not in game_state:
        game_state['character_name'] = game_state.get('name', character_name)
    
    # Ensure save_id exists
    if 'save_id' not in game_state:
        game_state['save_id'] = save_id
    
    # Ensure character_story exists (for narrative display)
    if 'character_story' not in game_state:
        game_state['character_story'] = game_state.get('story', '')
    
    # Ensure current_choices exists (React expects this)
    if 'current_choices' not in game_state:
        game_state['current_choices'] = game_state.get('choices', [])
    
    # Ensure all required fields have defaults
    defaults = {
        'age': game_state.get('age', 0),
        'gender': game_state.get('gender', 'Nam'),
        'talent': game_state.get('talent', 'Bình thường'),
        'race': game_state.get('race', 'Nhân Tộc'),
        'background': game_state.get('background', 'Thường Dân'),
        'turn_count': game_state.get('turn_count', 0),
        'cultivation': game_state.get('cultivation', {}),
        'resources': game_state.get('resources', {}),
        'attributes': game_state.get('attributes', {}),
        'needs': game_state.get('needs', {}),
        'relationships': game_state.get('relationships', {}),
        'location': game_state.get('location', {}),
        'sect_id': game_state.get('sect_id'),
        'sect_context': game_state.get('sect_context', ''),
        'skills': game_state.get('skills', []),
        'economy': game_state.get('economy', {}),
        'social_graph': game_state.get('social_graph', {}),
        'formations': game_state.get('formations', []),
        'quests': game_state.get('quests', {'pending': [], 'active': [], 'completed': 0}),
        'rewrite_destiny_perks': game_state.get('rewrite_destiny_perks', []),
        'tao_souls': game_state.get('tao_souls', [])
    }
    
    # Apply defaults for missing or None fields
    for key, default_value in defaults.items():
        if key not in game_state or game_state[key] is None:
            game_state[key] = default_value
    
    return game_state

@app.get("/health")
async def health():
    """Health check"""
    logger.info("Request: GET /health")
    try:
        result = {"status": "healthy", "service": "cultivation-simulator", "log_file": str(LOG_FILE)}
        logger.info(f"Response: GET /health - Status: 200 - Time: 0.001s")
        return result
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.post("/game/new", response_model=Dict[str, Any])
async def new_game(request: NewGameRequest):
    """Start new game"""
    global _game_instance
    
    logger.info(f"New game request: player_name={request.player_name}, character_data={request.character_data}")
    
    try:
        save_id = f"cultivation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert Pydantic model to dict
        character_data = safe_to_dict(request.character_data) if request.character_data else {}
        
        # Create game instance and initialize with character data
        try:
            logger.info(f"Creating game instance with save_id: {save_id}")
            _game_instance = CultivationSimulator(save_id)
            logger.info("Game instance created successfully")
        except Exception as e:
            error_msg = f"Failed to create game instance: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create game instance: {str(e)}. See log: {LOG_FILE}"
            )
        
        # Initialize game
        try:
            logger.info(f"Initializing game with: gender={character_data.get('gender')}, talent={character_data.get('talent')}, race={character_data.get('race')}, background={character_data.get('background')}, physique_id={character_data.get('physique_id')}")
            _game_instance._new_game(
                player_name=request.player_name,
                gender=character_data.get('gender', 'Nam'),
                talent=character_data.get('talent', 'Bình thường'),
                race=character_data.get('race', 'Người'),
                background=character_data.get('background', 'Nông dân'),
                physique_id=character_data.get('physique_id')
            )
            logger.info("Game initialized successfully")
        except ValueError as e:
            error_msg = f"ValueError during game initialization: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            if "GEMINI_API_KEY" in str(e) or "CultivationAgent" in str(e):
                raise HTTPException(
                    status_code=500,
                    detail="GEMINI_API_KEY not found or invalid. Please check your .env file. See log: {LOG_FILE}"
                )
            raise
        except Exception as e:
            error_msg = f"Unexpected error during game initialization: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise
        
        # Get initial state
        try:
            game_state = _game_instance.get_game_state()
            logger.info("Game state retrieved successfully")
        except Exception as e:
            error_msg = f"Failed to get game state: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise
        
        logger.info(f"New game started successfully: save_id={save_id}")
        
        # Normalize game_state for React compatibility
        normalized_state = _normalize_game_state(game_state, save_id, request.player_name)
        
        return {
            "message": "Game started",
            "save_id": save_id,
            "narrative": game_state.get('story', game_state.get('character_story', '')),
            "choices": game_state.get('choices', []),
            "character_name": game_state.get('name', game_state.get('character_name', request.player_name)),
            "game_state": normalized_state
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Failed to start game: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start game: {str(e)}. See log: {LOG_FILE}"
        )


@app.post("/game/action", response_model=ActionResponse)
async def process_action(request: ActionRequest):
    """Process player action (select choice)"""
    global _game_instance
    
    logger.info(f"Action request: user_input={request.user_input}")
    
    if not _game_instance:
        logger.warning("Action requested but no active game instance")
        raise HTTPException(status_code=400, detail="No active game. Please start a new game first.")
    
    try:
        # Parse user input (could be "1", "2", etc. or text)
        choice_index = None
        try:
            choice_index = int(request.user_input) - 1  # Convert to 0-based index
        except ValueError:
            # If not a number, treat as text and find matching choice
            current_choices = _game_instance.current_choices
            for i, choice in enumerate(current_choices):
                if request.user_input.lower() in choice.lower():
                    choice_index = i
                    break
        
        if choice_index is None:
            raise HTTPException(status_code=400, detail=f"Invalid choice: {request.user_input}")
        
        logger.info(f"Processing choice index: {choice_index}")
        logger.info(f"Processing choice {choice_index + 1}: '{current_choices[choice_index] if choice_index < len(current_choices) else 'Invalid'}'")
        
        # Process turn
        result = _game_instance.process_year_turn(choice_index)
        
        # Get updated state
        game_state = _game_instance.get_game_state()
        
        # Get debug info if available
        debug_info = None
        if hasattr(_game_instance, 'agent') and _game_instance.agent:
            debug_info = {
                'prompt': getattr(_game_instance.agent, '_last_prompt', None),
                'ai_raw_response': getattr(_game_instance.agent, '_last_ai_response', None),
                'parsed_result': getattr(_game_instance.agent, '_last_parsed_result', None),
                'error': getattr(_game_instance.agent, '_last_error', None)
            }
        
        # Normalize for React
        normalized_state = _normalize_game_state(
            game_state,
            _game_instance.save_id,
            game_state.get('name', game_state.get('character_name', 'Unknown'))
        )
        
        logger.info(f"Action processed successfully. Narrative length: {len(result.get('narrative', ''))}")
        logger.info(f"Narrative preview: {result.get('narrative', '')[:100]}...")
        logger.info(f"Choices count: {len(result.get('choices', []))}")
        
        response = ActionResponse(
            narrative=result.get('narrative', ''),
            choices=result.get('choices', []),
            game_state=normalized_state,
            debug_info=debug_info
        )
        
        # Convert to dict for response (Pydantic v2 compatible)
        result_dict = safe_to_dict(response)
        
        logger.info(f"Response: POST /game/action - Status: 200 - Time: 0.001s")
        return result_dict
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Failed to process action: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process action: {str(e)}. See log: {LOG_FILE}"
        )


@app.get("/game/state")
async def get_state():
    """Get current game state"""
    global _game_instance
    
    if not _game_instance:
        raise HTTPException(status_code=400, detail="No active game. Please start a new game first.")
    
    try:
        game_state = _game_instance.get_game_state()
        
        # Normalize for React
        normalized_state = _normalize_game_state(
            game_state,
            _game_instance.save_id,
            game_state.get('name', game_state.get('character_name', 'Unknown'))
        )
        
        return normalized_state
    except Exception as e:
        error_msg = f"Failed to get game state: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get game state: {str(e)}. See log: {LOG_FILE}"
        )


@app.get("/memory/count")
async def get_memory_count():
    """Get memory count"""
    global _game_instance
    
    try:
        if not _game_instance or not hasattr(_game_instance, 'memory'):
            return {"count": 0}
        
        count = _game_instance.memory.get_total_memory_count()
        return {"count": count}
    except Exception as e:
        logger.warning(f"Error getting memory count: {e}")
        return {"count": 0}


# Save Management Endpoints
@app.get("/saves/list")
async def list_saves():
    """List all available save games"""
    from pathlib import Path
    import sqlite3
    
    saves_dir = Path("data/saves")
    saves = []
    
    if saves_dir.exists():
        for db_file in saves_dir.glob("*.db"):
            save_id = db_file.stem
            try:
                # Try to load basic info from database
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT age, gender, talent, name, updated_at
                    FROM game_state
                    WHERE save_id = ?
                """, (save_id,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    saves.append({
                        "save_id": save_id,
                        "age": row[0] or 0,
                        "gender": row[1] or "Unknown",
                        "talent": row[2] or "Unknown",
                        "character_name": row[3] or "Unknown",
                        "updated_at": row[4] or "",
                        "file_path": str(db_file)
                    })
            except Exception as e:
                logger.warning(f"Error reading save {save_id}: {e}")
                # Still add it but with minimal info
                saves.append({
                    "save_id": save_id,
                    "age": 0,
                    "gender": "Unknown",
                    "talent": "Unknown",
                    "character_name": "Unknown",
                    "updated_at": "",
                    "file_path": str(db_file)
                })
    
    # Sort by updated_at descending (most recent first)
    saves.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    return {"saves": saves}


@app.post("/saves/load")
async def load_save(request: dict):
    """Load a saved game"""
    global _game_instance
    
    save_id = request.get("save_id")
    if not save_id:
        raise HTTPException(status_code=400, detail="save_id is required")
    
    try:
        # Create game instance with existing save_id
        logger.info(f"Loading save: {save_id}")
        _game_instance = CultivationSimulator(save_id)
        
        # Load state
        _game_instance._load_state()
        
        # Get game state
        game_state = _game_instance.get_game_state()
        
        # Normalize for React
        normalized_state = _normalize_game_state(
            game_state, 
            save_id, 
            game_state.get('name', game_state.get('character_name', 'Unknown'))
        )
        
        return {
            "message": "Game loaded",
            "save_id": save_id,
            "narrative": game_state.get('story', game_state.get('character_story', '')),
            "choices": game_state.get('choices', []),
            "character_name": game_state.get('name', game_state.get('character_name', 'Unknown')),
            "game_state": normalized_state
        }
    except Exception as e:
        error_msg = f"Failed to load save: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load save: {str(e)}. See log: {LOG_FILE}"
        )


@app.delete("/saves/{save_id}")
async def delete_save(save_id: str):
    """Delete a save game"""
    from pathlib import Path
    import os
    
    save_file = Path(f"data/saves/{save_id}.db")
    
    if not save_file.exists():
        raise HTTPException(status_code=404, detail=f"Save {save_id} not found")
    
    try:
        # Close connection if this save is currently loaded
        global _game_instance
        if _game_instance and _game_instance.save_id == save_id:
            _game_instance = None
        
        # Delete file
        os.remove(save_file)
        logger.info(f"Deleted save: {save_id}")
        
        return {"message": f"Save {save_id} deleted successfully"}
    except Exception as e:
        error_msg = f"Failed to delete save: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete save: {str(e)}"
        )


# Advanced Systems Endpoints (Shop, Skills, Quests, Combat)
@app.get("/shop/items")
async def get_shop_items(location_id: Optional[str] = None):
    """Get shop items (Database-First approach)"""
    global _game_instance
    
    if not _game_instance:
        raise HTTPException(status_code=400, detail="No active game")
    
    try:
        # Get items from world database
        items = []
        if location_id:
            location = _game_instance.world_db.get_location(location_id)
            if location:
                shop_items = location.get('shop_items', [])
                for item_id in shop_items:
                    item = _game_instance.world_db.get_item(item_id)
                    if item:
                        items.append(item)
        else:
            # Get all items
            all_items = _game_instance.world_db.get_all_items()
            items = list(all_items.values())[:20]  # Limit to 20 for performance
        
        # Get player money
        player_money = _game_instance.resources.spirit_stones if _game_instance.resources else 0
        
        # Format items
        formatted_items = []
        for item in items:
            formatted_items.append({
                "id": item.get('id', ''),
                "name": item.get('name', ''),
                "type": item.get('type', ''),
                "price": item.get('price', 0),
                "description": item.get('description', ''),
                "rarity": item.get('rarity', 'Common'),
                "can_afford": player_money >= item.get('price', 0),
                "stats": item.get('stats', {})
            })
        
        return {
            "location_id": location_id or "global",
            "items": formatted_items,
            "player_money": player_money
        }
    except Exception as e:
        logger.error(f"Error getting shop items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/shop/buy")
async def buy_item(request: dict):
    """Buy item from shop (Database-First approach)"""
    global _game_instance
    
    if not _game_instance:
        raise HTTPException(status_code=400, detail="No active game")
    
    item_id = request.get("item_id")
    if not item_id:
        raise HTTPException(status_code=400, detail="item_id is required")
    
    try:
        # Get item from database
        item = _game_instance.world_db.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
        
        # Check if player can afford
        price = item.get('price', 0)
        player_money = _game_instance.resources.spirit_stones if _game_instance.resources else 0
        
        if player_money < price:
            raise HTTPException(status_code=400, detail="Not enough money")
        
        # Deduct money
        _game_instance.resources.spirit_stones -= price
        
        # Add item to inventory (simplified - just add to resources)
        if 'materials' not in _game_instance.resources.dict():
            _game_instance.resources.materials = {}
        
        materials = _game_instance.resources.materials
        if item_id in materials:
            materials[item_id] += 1
        else:
            materials[item_id] = 1
        
        # Save state
        _game_instance._save_state()
        
        return {
            "success": True,
            "message": f"Đã mua {item.get('name', item_id)}",
            "item": {
                "id": item_id,
                "name": item.get('name', ''),
                "type": item.get('type', '')
            },
            "remaining_money": _game_instance.resources.spirit_stones
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error buying item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/skills/available")
async def get_available_skills():
    """Get available skills"""
    global _game_instance
    
    if not _game_instance:
        raise HTTPException(status_code=400, detail="No active game")
    
    try:
        skills = _game_instance._get_available_skills()
        return {"skills": skills}
    except Exception as e:
        logger.error(f"Error getting skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/skills/learn")
async def learn_skill(request: dict):
    """Learn a skill"""
    global _game_instance
    
    if not _game_instance:
        raise HTTPException(status_code=400, detail="No active game")
    
    skill_id = request.get("skill_id")
    if not skill_id:
        raise HTTPException(status_code=400, detail="skill_id is required")
    
    try:
        # Simplified - just return success
        # Real implementation would check requirements and add skill
        return {
            "success": True,
            "message": f"Đã học kỹ năng {skill_id}",
            "skill_id": skill_id
        }
    except Exception as e:
        logger.error(f"Error learning skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quests/available")
async def get_available_quests():
    """Get available quests"""
    global _game_instance
    
    if not _game_instance:
        raise HTTPException(status_code=400, detail="No active game")
    
    try:
        quests_info = _game_instance._get_quests_info()
        return quests_info
    except Exception as e:
        logger.error(f"Error getting quests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/combat/start")
async def start_combat(request: dict):
    """Start combat"""
    global _game_instance
    
    if not _game_instance:
        raise HTTPException(status_code=400, detail="No active game")
    
    enemy_id = request.get("enemy_id")
    if not enemy_id:
        raise HTTPException(status_code=400, detail="enemy_id is required")
    
    try:
        # Simplified combat - just return combat state
        return {
            "success": True,
            "combat_state": {
                "enemy_id": enemy_id,
                "enemy_hp": 100,
                "player_hp": 100
            },
            "message": "Combat started"
        }
    except Exception as e:
        logger.error(f"Error starting combat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/combat/action")
async def combat_action(request: dict):
    """Perform combat action"""
    global _game_instance
    
    if not _game_instance:
        raise HTTPException(status_code=400, detail="No active game")
    
    try:
        # Simplified combat action
        return {
            "success": True,
            "message": "Combat action performed",
            "combat_state": {}
        }
    except Exception as e:
        logger.error(f"Error performing combat action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Fix console buffering for Windows
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    
    print("\n" + "="*60)
    print("🚀 Starting Cultivation Simulator Server...")
    print("="*60)
    print(f"📝 Log file: {LOG_FILE}")
    print(f"📍 Server will be available at http://localhost:8001")
    print(f"📍 API docs at http://localhost:8001/docs")
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
