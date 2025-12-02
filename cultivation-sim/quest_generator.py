"""
Procedural Quest Generator với Background Jobs
AI-generated quests based on social graph analysis
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import json
from pathlib import Path

try:
    from agent import CultivationAgent
    HAS_AGENT = True
except ImportError:
    HAS_AGENT = False


class Quest(BaseModel):
    """Quest definition"""
    quest_id: str
    title: str
    description: str
    quest_giver_id: str
    quest_type: str = Field(default="fetch", description="Type: fetch, kill, escort, etc.")
    objectives: List[Dict[str, Any]] = Field(default_factory=list)
    rewards: Dict[str, Any] = Field(default_factory=dict)
    time_limit: Optional[int] = Field(None, description="Time limit in days")
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="active", description="Status: active, completed, failed")


class QuestGenerator:
    """
    Procedural Quest Generator với background jobs
    """
    
    def __init__(self, agent: Optional[Any] = None, social_graph: Optional[Any] = None):
        self.agent = agent
        self.social_graph = social_graph
        self.pending_quests: Dict[str, Quest] = {}
        self.active_quests: Dict[str, Quest] = {}
        self.completed_quests: Dict[str, Quest] = {}
        self._generation_queue: List[Dict[str, Any]] = []
        self._is_generating = False
    
    async def generate_quest_for_npc(
        self,
        npc_id: str,
        player_id: str = "player"
    ) -> Optional[Quest]:
        """
        Generate quest for NPC based on social graph analysis
        
        This is a background job (async)
        """
        if not self.social_graph:
            return None
        
        # Analyze NPC desires and relationships
        npc_relationships = self.social_graph.get_all_relationships(npc_id)
        npc_opinion_of_player = npc_relationships.get(player_id, {}).get("opinion", 0)
        
        # Get NPC needs (simplified)
        npc_needs = self._analyze_npc_needs(npc_id, npc_relationships)
        
        # Generate quest using AI
        quest_data = await self._ai_generate_quest(
            npc_id=npc_id,
            npc_needs=npc_needs,
            npc_opinion=npc_opinion_of_player,
            relationships=npc_relationships
        )
        
        if not quest_data:
            return None
        
        # Create quest object
        import uuid
        quest = Quest(
            quest_id=str(uuid.uuid4()),
            title=quest_data.get("title", "Unknown Quest"),
            description=quest_data.get("description", ""),
            quest_giver_id=npc_id,
            quest_type=quest_data.get("type", "fetch"),
            objectives=quest_data.get("objectives", []),
            rewards=quest_data.get("rewards", {}),
            time_limit=quest_data.get("time_limit")
        )
        
        self.pending_quests[quest.quest_id] = quest
        return quest
    
    def _analyze_npc_needs(
        self,
        npc_id: str,
        relationships: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze NPC needs from social graph
        
        Returns:
            Needs dict (money, items, revenge, etc.)
        """
        needs = {
            "money": False,
            "items": [],
            "revenge": [],
            "protection": False,
            "information": False
        }
        
        # Check for enemies (revenge)
        for target_id, rel_data in relationships.items():
            if rel_data.get("opinion", 0) < -50:
                needs["revenge"].append(target_id)
        
        # Check for low resources (money/items)
        # Simplified: assume NPCs always need money
        needs["money"] = True
        
        return needs
    
    async def _ai_generate_quest(
        self,
        npc_id: str,
        npc_needs: Dict[str, Any],
        npc_opinion: float,
        relationships: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate quest using AI (LLM call)
        
        This is the expensive operation (2-5s)
        """
        if not self.agent or not HAS_AGENT:
            # Fallback: simple quest generation
            return self._simple_quest_generation(npc_id, npc_needs, npc_opinion)
        
        # Build prompt
        prompt = f"""
Phân tích NPC {npc_id} và tạo nhiệm vụ:
- Nhu cầu: {json.dumps(npc_needs, ensure_ascii=False)}
- Quan điểm về người chơi: {npc_opinion}
- Quan hệ: {len(relationships)} người

Tạo nhiệm vụ phù hợp với:
1. Nhu cầu của NPC
2. Quan điểm của NPC về người chơi
3. Bối cảnh xã hội

Trả về JSON:
{{
    "title": "Tên nhiệm vụ",
    "description": "Mô tả chi tiết",
    "type": "fetch/kill/escort",
    "objectives": [{{"type": "collect", "target": "item_id", "quantity": 1}}],
    "rewards": {{"spirit_stones": 100, "reputation": 10}},
    "time_limit": 7
}}
"""
        
        try:
            # Call AI (this is async and slow)
            response = await self.agent.generate_quest(prompt)
            
            # Parse JSON response
            if isinstance(response, str):
                quest_data = json.loads(response)
            else:
                quest_data = response
            
            return quest_data
        except Exception as e:
            print(f"❌ Error generating quest with AI: {e}")
            return self._simple_quest_generation(npc_id, npc_needs, npc_opinion)
    
    def _simple_quest_generation(
        self,
        npc_id: str,
        npc_needs: Dict[str, Any],
        npc_opinion: float
    ) -> Dict[str, Any]:
        """Simple quest generation (fallback)"""
        if npc_needs.get("revenge"):
            # Revenge quest
            target = npc_needs["revenge"][0]
            return {
                "title": f"Trả thù {target}",
                "description": f"NPC muốn bạn giúp trả thù {target}",
                "type": "kill",
                "objectives": [{"type": "kill", "target": target, "quantity": 1}],
                "rewards": {"spirit_stones": 200, "reputation": 20},
                "time_limit": 14
            }
        elif npc_needs.get("money"):
            # Fetch quest
            return {
                "title": "Thu thập Linh Thạch",
                "description": "NPC cần Linh Thạch để tu luyện",
                "type": "fetch",
                "objectives": [{"type": "collect", "target": "spirit_stone", "quantity": 50}],
                "rewards": {"spirit_stones": 100, "reputation": 5},
                "time_limit": 7
            }
        else:
            # Default quest
            return {
                "title": "Nhiệm vụ thường",
                "description": "NPC cần giúp đỡ",
                "type": "fetch",
                "objectives": [],
                "rewards": {"spirit_stones": 50},
                "time_limit": None
            }
    
    async def background_quest_generator(self, interval: int = 60):
        """
        Background job to generate quests
        
        Args:
            interval: Generation interval in seconds
        """
        while True:
            try:
                # Generate quests for NPCs that need them
                # This is a simplified version
                # In real implementation, would check NPCs that need quests
                
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"❌ Error in background quest generator: {e}")
                await asyncio.sleep(interval)
    
    def get_pending_quests(self) -> List[Quest]:
        """Get pending quests"""
        return list(self.pending_quests.values())
    
    def accept_quest(self, quest_id: str) -> bool:
        """Accept quest"""
        if quest_id not in self.pending_quests:
            return False
        
        quest = self.pending_quests.pop(quest_id)
        quest.status = "active"
        self.active_quests[quest_id] = quest
        
        return True
    
    def complete_quest(self, quest_id: str) -> bool:
        """Complete quest"""
        if quest_id not in self.active_quests:
            return False
        
        quest = self.active_quests.pop(quest_id)
        quest.status = "completed"
        self.completed_quests[quest_id] = quest
        
        return True

