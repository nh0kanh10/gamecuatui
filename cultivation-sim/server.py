"""
FastAPI Server for Cultivation Simulator
Standalone server (port 8001)
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from game import CultivationSimulator
from schemas import CharacterData, GameState

app = FastAPI(title="Cultivation Simulator API")

# Include advanced systems router
app.include_router(advanced_router)

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


# Request/Response Models
class NewGameRequest(BaseModel):
    player_name: str = "Người Tu Tiên"
    character_data: CharacterData


class ActionRequest(BaseModel):
    user_input: str  # Choice index (1-6) or text


class ActionResponse(BaseModel):
    narrative: str
    choices: List[str]
    game_state: Dict[str, Any]


# API Routes
@app.post("/game/new")
async def new_game(request: NewGameRequest):
    """Start new game"""
    global _game_instance
    
    try:
        save_id = f"cultivation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        _game_instance = CultivationSimulator(save_id)
        
        # Create character
        response = _game_instance.create_character(request.character_data)
        
        return {
            "message": "Game started",
            "save_id": save_id,
            "narrative": response.get('narrative', ''),
            "choices": response.get('choices', []),
            "character_name": response.get('character_name', request.player_name),
            "game_state": _game_instance.get_game_state().dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start game: {str(e)}"
        )


@app.post("/game/action", response_model=ActionResponse)
async def process_action(request: ActionRequest):
    """Process player action (select choice)"""
    global _game_instance
    
    if not _game_instance:
        raise HTTPException(status_code=400, detail="No active game. Please start a new game first.")
    
    try:
        # Check if it's a choice index
        if request.user_input.isdigit():
            choice_idx = int(request.user_input) - 1
            if choice_idx < 0 or choice_idx >= len(_game_instance.current_choices):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid choice index. Please select 1-{len(_game_instance.current_choices)}"
                )
            response = _game_instance.process_year_turn(choice_idx)
        else:
            # Text input (future: custom actions)
            raise HTTPException(
                status_code=400,
                detail="Please select a choice by number (1-6)"
            )
        
        return ActionResponse(
            narrative=response.get('narrative', ''),
            choices=response.get('choices', []),
            game_state=_game_instance.get_game_state().dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process action: {str(e)}"
        )


@app.get("/game/state")
async def get_state():
    """Get current game state"""
    if not _game_instance:
        raise HTTPException(
            status_code=400,
            detail="No active game. Please start a new game first."
        )
    
    try:
        return _game_instance.get_game_state().dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get game state: {str(e)}"
        )


@app.get("/memory/count")
async def get_memory_count():
    """Get memory count"""
    if not _game_instance:
        return {"count": 0}
    
    return {"count": _game_instance.memory.get_count()}


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "cultivation-simulator"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

