"""
Formation System với Ngũ Hành
- Cached calculations (không real-time)
- Qi flow simulation
- Elemental compatibility
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import math
import time


class ElementType(str, Enum):
    """Ngũ Hành"""
    FIRE = "Fire"
    WATER = "Water"
    EARTH = "Earth"
    METAL = "Metal"
    WOOD = "Wood"


class FormationNode(BaseModel):
    """Formation node (Trận Nhãn/Trận Cước)"""
    node_id: str
    node_type: str = Field(default="auxiliary", description="Type: main (Trận Nhãn) or auxiliary (Trận Cước)")
    position: Tuple[float, float] = Field(default=(0.0, 0.0), description="Position (x, y)")
    element: ElementType = Field(default=ElementType.FIRE, description="Elemental affinity")
    qi_capacity: int = Field(default=100, ge=0, description="Qi capacity")
    current_qi: int = Field(default=0, ge=0, description="Current qi")
    connected_to: List[str] = Field(default_factory=list, description="Connected node IDs")


class FormationSystem:
    """
    Formation System với cached calculations
    """
    
    def __init__(self):
        self.formations: Dict[str, Dict[str, Any]] = {}
        self._qi_flow_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Dict[str, float] = {}
        self._cache_ttl: float = 60.0  # 60 seconds cache
    
    def create_formation(
        self,
        formation_id: str,
        nodes: List[FormationNode],
        main_node_id: str
    ) -> Dict[str, Any]:
        """
        Create formation
        
        Args:
            formation_id: Formation ID
            nodes: List of nodes
            main_node_id: Main node (Trận Nhãn) ID
        
        Returns:
            Formation data
        """
        formation = {
            "id": formation_id,
            "nodes": {node.node_id: node.dict() for node in nodes},
            "main_node_id": main_node_id,
            "created_at": time.time()
        }
        
        self.formations[formation_id] = formation
        
        # Calculate and cache qi flow
        self._calculate_qi_flow(formation_id)
        
        return formation
    
    def _calculate_qi_flow(self, formation_id: str):
        """
        Calculate qi flow (cached, không real-time)
        
        Formula:
        - Qi flows from auxiliary nodes to main node
        - Elemental compatibility affects flow efficiency
        - Tương sinh: +20% efficiency
        - Tương khắc: -30% efficiency
        """
        formation = self.formations.get(formation_id)
        if not formation:
            return
        
        nodes = formation["nodes"]
        main_node_id = formation["main_node_id"]
        
        # Get main node
        main_node_data = nodes.get(main_node_id)
        if not main_node_data:
            return
        
        main_node = FormationNode(**main_node_data)
        
        # Calculate flow from each auxiliary node
        total_qi_flow = 0
        flow_details = []
        
        for node_id, node_data in nodes.items():
            if node_id == main_node_id:
                continue
            
            node = FormationNode(**node_data)
            
            # Check if connected
            if main_node_id not in node.connected_to:
                continue
            
            # Calculate base flow
            base_flow = min(node.current_qi, node.qi_capacity)
            
            # Apply elemental compatibility
            compatibility = self._calculate_elemental_compatibility(
                node.element,
                main_node.element
            )
            
            effective_flow = base_flow * compatibility
            total_qi_flow += effective_flow
            
            flow_details.append({
                "from_node": node_id,
                "to_node": main_node_id,
                "base_flow": base_flow,
                "compatibility": compatibility,
                "effective_flow": effective_flow
            })
        
        # Cache result
        self._qi_flow_cache[formation_id] = {
            "total_qi_flow": total_qi_flow,
            "main_node_qi": main_node.current_qi + total_qi_flow,
            "flow_details": flow_details,
            "formation_bonus": self._calculate_formation_bonus(formation_id),
            "is_stable": self._check_formation_stability(formation_id)
        }
        
        self._cache_timestamp[formation_id] = time.time()
    
    def _calculate_elemental_compatibility(
        self,
        source_element: ElementType,
        target_element: ElementType
    ) -> float:
        """
        Calculate elemental compatibility
        
        Tương sinh (Generation):
        - Hỏa sinh Thổ
        - Thổ sinh Kim
        - Kim sinh Thủy
        - Thủy sinh Mộc
        - Mộc sinh Hỏa
        
        Tương khắc (Destruction):
        - Hỏa khắc Kim
        - Kim khắc Mộc
        - Mộc khắc Thổ
        - Thổ khắc Thủy
        - Thủy khắc Hỏa
        """
        # Generation cycle
        generation_cycle = [
            ElementType.FIRE,
            ElementType.EARTH,
            ElementType.METAL,
            ElementType.WATER,
            ElementType.WOOD
        ]
        
        # Check generation
        try:
            source_idx = generation_cycle.index(source_element)
            target_idx = generation_cycle.index(target_element)
            
            if (source_idx + 1) % len(generation_cycle) == target_idx:
                # Tương sinh: +20% efficiency
                return 1.2
        except ValueError:
            pass
        
        # Check destruction
        destruction_map = {
            ElementType.FIRE: ElementType.METAL,
            ElementType.METAL: ElementType.WOOD,
            ElementType.WOOD: ElementType.EARTH,
            ElementType.EARTH: ElementType.WATER,
            ElementType.WATER: ElementType.FIRE
        }
        
        if destruction_map.get(source_element) == target_element:
            # Tương khắc: -30% efficiency
            return 0.7
        
        # Neutral: 100% efficiency
        return 1.0
    
    def _calculate_formation_bonus(self, formation_id: str) -> Dict[str, float]:
        """
        Calculate formation bonus based on qi flow
        
        Returns:
            Bonus dict (attack, defense, cultivation_speed, etc.)
        """
        cache = self._qi_flow_cache.get(formation_id, {})
        total_qi = cache.get("total_qi_flow", 0)
        
        # Bonus scales with total qi
        bonus_multiplier = 1.0 + (total_qi / 1000.0) * 0.1  # Max 10% per 1000 qi
        
        return {
            "attack_bonus": bonus_multiplier,
            "defense_bonus": bonus_multiplier,
            "cultivation_speed_bonus": bonus_multiplier * 1.5,  # Cultivation gets more bonus
            "qi_regen_bonus": bonus_multiplier
        }
    
    def _check_formation_stability(self, formation_id: str) -> bool:
        """
        Check if formation is stable
        
        Formation is unstable if:
        - Tương khắc elements are adjacent
        - Main node has no connections
        - Qi flow is negative
        """
        formation = self.formations.get(formation_id)
        if not formation:
            return False
        
        nodes = formation["nodes"]
        main_node_id = formation["main_node_id"]
        
        # Check main node connections
        main_node_data = nodes.get(main_node_id)
        if not main_node_data:
            return False
        
        main_node = FormationNode(**main_node_data)
        if not main_node.connected_to:
            return False
        
        # Check for destructive element pairs
        for node_id, node_data in nodes.items():
            node = FormationNode(**node_data)
            for connected_id in node.connected_to:
                connected_data = nodes.get(connected_id)
                if not connected_data:
                    continue
                
                connected_node = FormationNode(**connected_data)
                
                # Check if elements are destructive
                compatibility = self._calculate_elemental_compatibility(
                    node.element,
                    connected_node.element
                )
                
                if compatibility < 0.8:  # Tương khắc
                    return False  # Unstable
        
        return True
    
    def get_formation_bonus(self, formation_id: str) -> Dict[str, Any]:
        """
        Get formation bonus (cached)
        
        Returns:
            Bonus dict
        """
        # Check cache
        current_time = time.time()
        cache_time = self._cache_timestamp.get(formation_id, 0)
        
        if current_time - cache_time > self._cache_ttl:
            # Recalculate
            self._calculate_qi_flow(formation_id)
        
        cache = self._qi_flow_cache.get(formation_id, {})
        return {
            "formation_bonus": cache.get("formation_bonus", {}),
            "total_qi_flow": cache.get("total_qi_flow", 0),
            "is_stable": cache.get("is_stable", False),
            "flow_details": cache.get("flow_details", [])
        }
    
    def update_formation(
        self,
        formation_id: str,
        node_updates: Dict[str, Dict[str, Any]]
    ):
        """
        Update formation nodes (triggers recalculation)
        
        Args:
            formation_id: Formation ID
            node_updates: Dict of {node_id: {field: value}}
        """
        formation = self.formations.get(formation_id)
        if not formation:
            return
        
        # Update nodes
        for node_id, updates in node_updates.items():
            if node_id in formation["nodes"]:
                formation["nodes"][node_id].update(updates)
        
        # Recalculate qi flow
        self._calculate_qi_flow(formation_id)

