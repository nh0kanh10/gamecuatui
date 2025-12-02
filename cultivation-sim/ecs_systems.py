"""
ECS Systems Pattern
Dựa trên báo cáo kỹ thuật: Systems xử lý Components
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import asyncio
import json


class CultivationSystem:
    """
    Cultivation System - Xử lý tu luyện
    
    Chạy mỗi tick (ví dụ: 1 giây)
    Cập nhật Qi, kiểm tra đột phá
    """
    
    def __init__(self, game_state):
        self.game_state = game_state
    
    def tick(self, delta_time: float = 1.0):
        """
        Tick cultivation system
        
        Args:
            delta_time: Thời gian đã trôi qua (giây)
        """
        cultivation = self.game_state.get("cultivation")
        attributes = self.game_state.get("attributes")
        
        if not cultivation or not attributes:
            return
        
        # Tính tốc độ tu luyện
        from attributes import AttributesComponent
        from breakthrough import RealmTier
        
        attrs = AttributesComponent(**attributes)
        cultivation_speed = attrs.calculate_cultivation_speed()
        
        # Get realm tier
        current_realm = cultivation.get("realm", "Qi_Refining")
        realm_tier = RealmTier[current_realm.upper()] if hasattr(RealmTier, current_realm.upper()) else RealmTier.QI_REFINING
        
        # Qi density từ location
        location = self.game_state.get("location", {})
        qi_density = location.get("qi_density", 1.0)
        
        # Calculate Qi gain
        base_qi_gain = 1.0 * delta_time
        qi_gain = base_qi_gain * cultivation_speed * qi_density
        
        # Update spiritual power
        current_qi = cultivation.get("spiritual_power", 0)
        max_qi = cultivation.get("max_spiritual_power", 100)
        
        new_qi = min(max_qi, current_qi + qi_gain)
        cultivation["spiritual_power"] = new_qi
        
        # Check breakthrough progress
        if new_qi >= max_qi:
            breakthrough_progress = cultivation.get("breakthrough_progress", 0.0)
            breakthrough_progress += qi_gain * 0.1  # 10% progress per max_qi
            breakthrough_progress = min(100.0, breakthrough_progress)
            cultivation["breakthrough_progress"] = breakthrough_progress
        
        # Update cultivation age
        cultivation["cultivation_age"] = cultivation.get("cultivation_age", 0) + delta_time / 365.0  # Years
    
    def can_breakthrough(self) -> bool:
        """Check if can breakthrough"""
        cultivation = self.game_state.get("cultivation", {})
        return (
            cultivation.get("spiritual_power", 0) >= cultivation.get("max_spiritual_power", 100) and
            cultivation.get("breakthrough_progress", 0.0) >= 100.0
        )


class RelationshipSystem:
    """
    Relationship System - Xử lý quan hệ xã hội
    
    Dùng NetworkX (in-memory graph) thay Neo4j cho MVP
    """
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.relationships: Dict[str, Dict[str, Any]] = {}  # entity_id -> {target_id: relationship_data}
    
    def add_relationship(
        self,
        entity_id: str,
        target_id: str,
        relationship_type: str,
        affinity: int = 0,
        metadata: Optional[Dict] = None
    ):
        """
        Thêm/quan hệ
        
        Args:
            entity_id: ID của entity (player hoặc NPC)
            target_id: ID của target
            relationship_type: "friend", "enemy", "master", "disciple", "lover", "family"
            affinity: -100 to 100
            metadata: Additional data
        """
        if entity_id not in self.relationships:
            self.relationships[entity_id] = {}
        
        self.relationships[entity_id][target_id] = {
            "relationship_type": relationship_type,
            "affinity": max(-100, min(100, affinity)),
            "trust_level": 0,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "last_interaction": datetime.now().isoformat()
        }
    
    def update_relationship(
        self,
        entity_id: str,
        target_id: str,
        affinity_delta: int,
        trust_delta: int = 0
    ):
        """Update relationship affinity và trust"""
        if entity_id not in self.relationships:
            self.relationships[entity_id] = {}
        
        if target_id not in self.relationships[entity_id]:
            self.relationships[entity_id][target_id] = {
                "relationship_type": "neutral",
                "affinity": 0,
                "trust_level": 0,
                "metadata": {},
                "created_at": datetime.now().isoformat(),
                "last_interaction": datetime.now().isoformat()
            }
        
        rel = self.relationships[entity_id][target_id]
        rel["affinity"] = max(-100, min(100, rel["affinity"] + affinity_delta))
        rel["trust_level"] = max(0, min(10, rel["trust_level"] + trust_delta))
        rel["last_interaction"] = datetime.now().isoformat()
    
    def get_relationship(self, entity_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        """Get relationship data"""
        return self.relationships.get(entity_id, {}).get(target_id)
    
    def get_all_relationships(self, entity_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all relationships for an entity"""
        return self.relationships.get(entity_id, {})
    
    def find_avengers(
        self,
        victim_id: str,
        min_affinity: int = 50,
        min_realm: Optional[str] = None
    ) -> List[str]:
        """
        Tìm ai sẽ trả thù khi victim bị tấn công
        
        Logic "Đánh nhỏ già ra"
        """
        avengers = []
        
        # Tìm trong relationships của victim
        victim_rels = self.relationships.get(victim_id, {})
        
        for target_id, rel_data in victim_rels.items():
            affinity = rel_data.get("affinity", 0)
            rel_type = rel_data.get("relationship_type", "")
            
            # Master, Family, Lover có khả năng trả thù cao
            if rel_type in ["master", "family", "lover"] and affinity >= min_affinity:
                avengers.append(target_id)
            
            # Friend thân thiết
            elif rel_type == "friend" and affinity >= 80:
                avengers.append(target_id)
        
        return avengers
    
    def get_relationship_context(self, entity_id: str) -> str:
        """Get relationship context for AI"""
        rels = self.get_all_relationships(entity_id)
        
        if not rels:
            return "Chưa có quan hệ với ai."
        
        context_parts = ["Quan hệ hiện tại:"]
        for target_id, rel_data in rels.items():
            rel_type = rel_data["relationship_type"]
            affinity = rel_data["affinity"]
            trust = rel_data["trust_level"]
            context_parts.append(f"- {target_id}: {rel_type}, Thiện cảm: {affinity}, Tin cậy: {trust}")
        
        return "\n".join(context_parts)


class AIPlannerSystem:
    """
    AI Planner System - Hybrid AI planning
    
    Chạy bất đồng bộ (Async)
    Thu thập dữ liệu môi trường -> Gọi LLM -> Nhận JSON Plan
    """
    
    def __init__(self, game_state, ai_agent, memory_system):
        self.game_state = game_state
        self.ai_agent = ai_agent
        self.memory_system = memory_system
    
    async def plan_action(
        self,
        entity_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Lập kế hoạch hành động cho entity (NPC hoặc Player)
        
        Returns:
            {
                "thought_process": str,
                "emotional_state": str,
                "decision": {
                    "action_type": str,
                    "target_id": Optional[str],
                    "dialogue_content": Optional[str]
                }
            }
        """
        
        # 1. Thu thập dữ liệu
        entity_data = self._gather_entity_data(entity_id)
        environment_data = self._gather_environment_data()
        memory_context = self.memory_system.get_full_context(query=entity_id)
        
        # 2. Tạo prompt
        prompt = self._create_planning_prompt(
            entity_data=entity_data,
            environment_data=environment_data,
            memory_context=memory_context,
            context=context
        )
        
        # 3. Gọi LLM (async)
        try:
            plan = await self.ai_agent.plan_action(prompt)
            return plan
        except Exception as e:
            print(f"❌ AI Planning error: {e}")
            return self._create_fallback_plan(entity_id)
    
    def _gather_entity_data(self, entity_id: str) -> Dict[str, Any]:
        """Thu thập dữ liệu entity"""
        # Get from game state
        attributes = self.game_state.get("attributes", {})
        cultivation = self.game_state.get("cultivation", {})
        location = self.game_state.get("location", {})
        
        return {
            "attributes": attributes,
            "cultivation": cultivation,
            "location": location,
            "entity_id": entity_id
        }
    
    def _gather_environment_data(self) -> Dict[str, Any]:
        """Thu thập dữ liệu môi trường"""
        location = self.game_state.get("location", {})
        nearby_entities = self.game_state.get("nearby_entities", [])
        
        return {
            "location": location,
            "nearby_entities": nearby_entities,
            "time": datetime.now().isoformat()
        }
    
    def _create_planning_prompt(
        self,
        entity_data: Dict[str, Any],
        environment_data: Dict[str, Any],
        memory_context: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Tạo prompt cho AI planning"""
        
        prompt = f"""
Bạn là AI Planner cho game tu tiên.

Entity Data:
{json.dumps(entity_data, ensure_ascii=False, indent=2)}

Environment:
{json.dumps(environment_data, ensure_ascii=False, indent=2)}

Memory Context:
{memory_context}

Context:
{json.dumps(context or {}, ensure_ascii=False, indent=2)}

Hãy lập kế hoạch hành động. Trả về JSON:
{{
    "thought_process": "Suy nghĩ nội tâm",
    "emotional_state": "Calm|Angry|Fearful|Greedy",
    "decision": {{
        "action_type": "move|attack|talk|cultivate|rest",
        "target_id": "entity_id hoặc null",
        "dialogue_content": "Lời nói (nếu action_type = talk)"
    }}
}}
"""
        return prompt
    
    def _create_fallback_plan(self, entity_id: str) -> Dict[str, Any]:
        """Tạo plan mặc định khi AI fail"""
        return {
            "thought_process": "Không có suy nghĩ đặc biệt",
            "emotional_state": "Calm",
            "decision": {
                "action_type": "rest",
                "target_id": None,
                "dialogue_content": None
            }
        }


class NeedsSystem:
    """
    Needs System - Mô phỏng nhu cầu sinh học/tâm lý
    
    Hunger, Energy, Social Need
    """
    
    def __init__(self, game_state):
        self.game_state = game_state
    
    def tick(self, delta_time: float = 1.0):
        """Update needs over time"""
        needs = self.game_state.setdefault("needs", {
            "hunger": 100.0,
            "energy": 100.0,
            "social": 50.0
        })
        
        # Hunger decreases
        needs["hunger"] = max(0.0, needs["hunger"] - 0.1 * delta_time)
        
        # Energy decreases (faster when cultivating)
        cultivation = self.game_state.get("cultivation", {})
        if cultivation.get("spiritual_power", 0) > 0:
            energy_drain = 0.2  # Cultivating uses more energy
        else:
            energy_drain = 0.05
        
        needs["energy"] = max(0.0, needs["energy"] - energy_drain * delta_time)
        
        # Social need decreases (loneliness)
        needs["social"] = max(0.0, needs["social"] - 0.05 * delta_time)
    
    def get_needs_status(self) -> Dict[str, str]:
        """Get needs status for AI context"""
        needs = self.game_state.get("needs", {})
        
        status = {}
        for need_name, value in needs.items():
            if value >= 80:
                status[need_name] = "Satisfied"
            elif value >= 50:
                status[need_name] = "Moderate"
            elif value >= 20:
                status[need_name] = "Low"
            else:
                status[need_name] = "Critical"
        
        return status

