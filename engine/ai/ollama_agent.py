"""
AI Agent - Ollama Integration
Parses natural language input and generates narrative
"""

import ollama
import json
from typing import Optional, Tuple
from pydantic import ValidationError as PydanticValidationError

from engine.ai.schemas import ActionProposal, ActionResult, GameContext


class OllamaAgent:
    """Local AI agent using Ollama"""
    
    def __init__(self, model: str = "qwen2.5:3b"):
        self.model = model
        self._test_connection()
    
    def _test_connection(self):
        """Test if Ollama is available"""
        try:
            ollama.list()
        except Exception as e:
            print(f"⚠️  Warning: Ollama not available: {e}")
            print("   Make sure Ollama is running: ollama serve")
    
    def parse_input(self, user_input: str, context: GameContext) -> Optional[ActionProposal]:
        """
        Parse natural language into ActionProposal
        
        Examples:
            "take the sword" → ActionProposal(intent="TAKE", target_name="sword")
            "attack goblin" → ActionProposal(intent="ATTACK", target_name="goblin")
        """
        
        # Build prompt
        prompt = self._build_parse_prompt(user_input, context)
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                format='json',  # Force JSON output
                options={
                    'temperature': 0.3,  # Low temp for consistent parsing
                    'num_predict': 150
                }
            )
            
            # Parse JSON
            json_text = response['response'].strip()
            data = json.loads(json_text)
            
            # Convert to ActionProposal
            proposal = ActionProposal(**data)
            return proposal
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error: {e}")
            print(f"   Raw response: {response['response'][:100]}")
            return None
        except PydanticValidationError as e:
            print(f"⚠️  Validation error: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Error: {e}")
            return None
    
    def generate_narrative(self, result: ActionResult, context: GameContext) -> str:
        """Generate descriptive narrative from action result"""
        
        prompt = self._build_narrative_prompt(result, context)
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'num_predict': 200
                }
            )
            
            return response['response'].strip()
            
        except Exception as e:
            # Fallback to basic message
            return result.message
    
    def _build_parse_prompt(self, user_input: str, context: GameContext) -> str:
        """Build prompt for parsing user input"""
        
        # List visible entities for disambiguation
        entity_names = [e['name'] for e in context.visible_entities]
        inventory_names = [i['name'] for i in context.inventory]
        
        prompt = f"""You are a game input parser. Convert natural language to JSON.

CURRENT CONTEXT:
- Player: {context.player_name}
- Location: {context.current_room_id}
- Visible: {', '.join(entity_names) if entity_names else 'nothing'}
- Inventory: {', '.join(inventory_names) if inventory_names else 'empty'}

VALID ACTIONS:
- MOVE (parameters: direction = north/south/east/west)
- TAKE (target_name)
- DROP (target_name)
- OPEN (target_name)
- CLOSE (target_name)
- UNLOCK (target_name)
- ATTACK (target_name)
- TALK (target_name, parameters: topic optional)
- EXAMINE (target_name)
- EQUIP (target_name)

USER INPUT: "{user_input}"

Convert to JSON with format:
{{
  "intent": "ACTION_NAME",
  "target_name": "entity name or null",
  "parameters": {{"key": "value"}} or {{}}
}}

Examples:
- "go north" → {{"intent": "MOVE", "target_name": null, "parameters": {{"direction": "north"}}}}
- "take sword" → {{"intent": "TAKE", "target_name": "sword", "parameters": {{}}}}
- "attack the goblin" → {{"intent": "ATTACK", "target_name": "goblin", "parameters": {{}}}}

Output ONLY valid JSON, no explanation:"""
        
        return prompt
    
    def _build_narrative_prompt(self, result: ActionResult, context: GameContext) -> str:
        """Build prompt for narrative generation"""
        
        if result.success:
            prompt = f"""You are a game narrator. Describe what happened in 2-3 vivid sentences.

ACTION: {result.action}
RESULT: {result.message}
CHANGES: {json.dumps(result.changes)}

Write ONLY the narrative description, no meta-commentary:"""
        else:
            prompt = f"""You are a game narrator. Explain why the action failed in 1-2 sentences.

ATTEMPTED: {result.action}
ERROR: {result.message}

Write ONLY the failure explanation:"""
        
        return prompt


# Global instance
_agent = None

def get_ollama_agent(model: str = "qwen2.5:3b") -> OllamaAgent:
    """Get or create global Ollama agent"""
    global _agent
    if _agent is None:
        _agent = OllamaAgent(model)
    return _agent
