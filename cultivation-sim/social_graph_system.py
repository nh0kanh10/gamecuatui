"""
Graph Social System với NetworkX
- Centrality caching
- Memory decay
- Personality facets
- Dynamic opinion calculation
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import math

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("⚠️ NetworkX not installed, using simple dict-based graph")


class RelationshipEdge(BaseModel):
    """Relationship edge data"""
    relationship_type: str = Field(default="acquaintance", description="Type: friend, enemy, master, disciple, etc.")
    affinity: int = Field(default=0, ge=-100, le=100, description="Affinity score (-100 to 100)")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Interaction history")
    created_at: datetime = Field(default_factory=datetime.now)
    last_interaction: datetime = Field(default_factory=datetime.now)
    
    def add_interaction(self, event_type: str, value: int, description: str = ""):
        """Add interaction to history"""
        self.history.append({
            "type": event_type,
            "value": value,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        self.last_interaction = datetime.now()
        
        # Update affinity
        self.affinity = max(-100, min(100, self.affinity + value))


class PersonalityFacets(BaseModel):
    """Personality facets (0-100 spectrum)"""
    altruism: float = Field(default=50.0, ge=0.0, le=100.0)
    assertiveness: float = Field(default=50.0, ge=0.0, le=100.0)
    impulse_control: float = Field(default=50.0, ge=0.0, le=100.0)
    beauty: float = Field(default=50.0, ge=0.0, le=100.0)
    romance_chance: float = Field(default=50.0, ge=0.0, le=100.0)
    
    def get_beauty_bias(self) -> float:
        """Get beauty bias for opinion calculation"""
        # Beauty 0-100 -> Bias -20 to +20
        return (self.beauty - 50.0) / 50.0 * 20.0


class SocialGraphSystem:
    """
    Social Graph System với NetworkX và caching
    """
    
    def __init__(self):
        if HAS_NETWORKX:
            self.graph = nx.Graph()
        else:
            self.graph = {}  # Fallback: dict-based
        
        self.relationships: Dict[str, Dict[str, RelationshipEdge]] = {}  # entity_id -> {target_id: edge}
        self.personalities: Dict[str, PersonalityFacets] = {}
        
        # Centrality cache
        self._centrality_cache: Dict[str, float] = {}
        self._centrality_cache_time: float = 0
        self._cache_ttl: float = 60.0  # 60 seconds
        
        # Memory decay settings
        self.memory_decay_rate = 0.1  # 10% per day
        self.deep_memory_threshold = 30  # Events with value > 30 are deep memories
    
    def add_entity(self, entity_id: str, personality: Optional[PersonalityFacets] = None):
        """Add entity to graph"""
        if HAS_NETWORKX:
            self.graph.add_node(entity_id)
        else:
            if entity_id not in self.graph:
                self.graph[entity_id] = {}
        
        if personality:
            self.personalities[entity_id] = personality
        else:
            self.personalities[entity_id] = PersonalityFacets()
        
        if entity_id not in self.relationships:
            self.relationships[entity_id] = {}
    
    def add_relationship(
        self,
        entity_a: str,
        entity_b: str,
        relationship_type: str = "acquaintance",
        initial_affinity: int = 0
    ):
        """Add or update relationship"""
        # Add to graph
        if HAS_NETWORKX:
            self.graph.add_edge(entity_a, entity_b)
        else:
            if entity_a not in self.graph:
                self.graph[entity_a] = {}
            if entity_b not in self.graph:
                self.graph[entity_b] = {}
            self.graph[entity_a][entity_b] = True
            self.graph[entity_b][entity_a] = True
        
        # Add relationship data
        if entity_a not in self.relationships:
            self.relationships[entity_a] = {}
        if entity_b not in self.relationships:
            self.relationships[entity_b] = {}
        
        edge = RelationshipEdge(
            relationship_type=relationship_type,
            affinity=initial_affinity
        )
        
        self.relationships[entity_a][entity_b] = edge
        self.relationships[entity_b][entity_a] = edge
        
        # Invalidate centrality cache
        self._centrality_cache_time = 0
    
    def calculate_opinion(
        self,
        entity_a: str,
        entity_b: str,
        current_time: Optional[datetime] = None
    ) -> float:
        """
        Calculate dynamic opinion using formula:
        Opinion = BaseCompatibility + Σ(Memory × Decay) + BeautyBias + TraitInteraction
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Get relationship
        edge = self.relationships.get(entity_a, {}).get(entity_b)
        if not edge:
            return 0.0
        
        # Base compatibility (from seed ID)
        base_compatibility = self._get_base_compatibility(entity_a, entity_b)
        
        # Memory decay calculation
        memory_sum = 0.0
        for event in edge.history:
            event_time = datetime.fromisoformat(event["timestamp"])
            days_ago = (current_time - event_time).days
            
            # Decay rate
            if abs(event["value"]) > self.deep_memory_threshold:
                # Deep memory: slower decay
                decay = math.exp(-self.memory_decay_rate * days_ago * 0.1)
            else:
                # Normal memory: faster decay
                decay = math.exp(-self.memory_decay_rate * days_ago)
            
            memory_sum += event["value"] * decay
        
        # Beauty bias
        personality_b = self.personalities.get(entity_b, PersonalityFacets())
        beauty_bias = personality_b.get_beauty_bias()
        
        # Trait interaction (simplified)
        trait_interaction = self._calculate_trait_interaction(entity_a, entity_b)
        
        # Final opinion
        opinion = base_compatibility + memory_sum + beauty_bias + trait_interaction
        
        return max(-100.0, min(100.0, opinion))
    
    def _get_base_compatibility(self, entity_a: str, entity_b: str) -> float:
        """Get base compatibility from seed (deterministic)"""
        # Simple hash-based compatibility
        combined = hash(f"{entity_a}_{entity_b}") % 100
        return (combined - 50) * 0.5  # -25 to +25
    
    def _calculate_trait_interaction(self, entity_a: str, entity_b: str) -> float:
        """Calculate trait interaction bonus/penalty"""
        personality_a = self.personalities.get(entity_a, PersonalityFacets())
        personality_b = self.personalities.get(entity_b, PersonalityFacets())
        
        # Example: Similar altruism = bonus
        altruism_diff = abs(personality_a.altruism - personality_b.altruism)
        if altruism_diff < 20:
            return 5.0  # Similar values = bonus
        elif altruism_diff > 60:
            return -5.0  # Very different = penalty
        
        return 0.0
    
    def get_centrality(self, entity_id: str) -> float:
        """
        Get betweenness centrality (cached)
        
        Returns:
            Centrality score (0-1)
        """
        # Check cache
        current_time = time.time()
        if current_time - self._centrality_cache_time < self._cache_ttl:
            return self._centrality_cache.get(entity_id, 0.0)
        
        # Recalculate
        self._recalculate_centrality()
        return self._centrality_cache.get(entity_id, 0.0)
    
    def _recalculate_centrality(self):
        """Recalculate centrality for all nodes (expensive operation)"""
        if not HAS_NETWORKX:
            # Fallback: simple degree centrality
            for node_id in self.graph:
                degree = len(self.graph.get(node_id, {}))
                self._centrality_cache[node_id] = degree / 100.0  # Normalize
            self._centrality_cache_time = time.time()
            return
        
        if len(self.graph.nodes) == 0:
            return
        
        # Calculate betweenness centrality
        try:
            centrality = nx.betweenness_centrality(self.graph)
            self._centrality_cache = centrality
            self._centrality_cache_time = time.time()
        except Exception as e:
            print(f"❌ Error calculating centrality: {e}")
            # Fallback to degree centrality
            degree_centrality = nx.degree_centrality(self.graph)
            self._centrality_cache = degree_centrality
            self._centrality_cache_time = time.time()
    
    def add_interaction(
        self,
        entity_a: str,
        entity_b: str,
        event_type: str,
        value: int,
        description: str = ""
    ):
        """Add interaction between entities"""
        if entity_a not in self.relationships or entity_b not in self.relationships[entity_a]:
            # Create relationship if doesn't exist
            self.add_relationship(entity_a, entity_b)
        
        edge = self.relationships[entity_a][entity_b]
        edge.add_interaction(event_type, value, description)
        
        # Invalidate cache if high-value event
        if abs(value) > 20:
            self._centrality_cache_time = 0
    
    def get_all_relationships(self, entity_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all relationships for an entity"""
        relationships = self.relationships.get(entity_id, {})
        
        result = {}
        for target_id, edge in relationships.items():
            opinion = self.calculate_opinion(entity_id, target_id)
            centrality = self.get_centrality(target_id)
            
            result[target_id] = {
                "relationship_type": edge.relationship_type,
                "affinity": edge.affinity,
                "opinion": opinion,
                "centrality": centrality,
                "last_interaction": edge.last_interaction.isoformat(),
                "history_count": len(edge.history)
            }
        
        return result
    
    def propagate_consequence(
        self,
        entity_id: str,
        event_type: str,
        value: int,
        radius: int = 2
    ):
        """
        Propagate consequence through social network
        
        Args:
            entity_id: Entity that caused event
            event_type: Type of event
            value: Impact value
            radius: How many degrees of separation
        """
        if not HAS_NETWORKX:
            # Fallback: only direct relationships
            for target_id in self.relationships.get(entity_id, {}):
                self.add_interaction(entity_id, target_id, event_type, value // 2, "Propagated")
            return
        
        # Get neighbors within radius
        try:
            neighbors = nx.single_source_shortest_path_length(self.graph, entity_id, cutoff=radius)
            
            for neighbor_id, distance in neighbors.items():
                if neighbor_id == entity_id:
                    continue
                
                # Value decreases with distance
                propagated_value = int(value / (distance + 1))
                self.add_interaction(
                    entity_id,
                    neighbor_id,
                    f"{event_type}_propagated",
                    propagated_value,
                    f"Propagated from {distance} degrees away"
                )
        except Exception as e:
            print(f"❌ Error propagating consequence: {e}")

