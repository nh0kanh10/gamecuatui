"""
Combat System với Hybrid Damage Formula và Action Value
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
import math


class ActionValueSystem:
    """
    Action Value System - Turn order based on speed
    AV = 10000 / Speed
    """
    
    def __init__(self):
        self.combatants: List[Dict[str, Any]] = []
        self.current_av: Dict[str, float] = {}
    
    def add_combatant(self, combatant_id: str, speed: float):
        """Add combatant to battle"""
        self.combatants.append({
            "id": combatant_id,
            "speed": speed,
            "av": 10000.0 / speed if speed > 0 else 9999.0
        })
        self.current_av[combatant_id] = 10000.0 / speed if speed > 0 else 9999.0
    
    def get_next_actor(self) -> Optional[str]:
        """
        Get next actor (lowest AV)
        
        Returns:
            Combatant ID hoặc None
        """
        if not self.current_av:
            return None
        
        # Find lowest AV
        next_id = min(self.current_av.items(), key=lambda x: x[1])[0]
        return next_id
    
    def advance_turn(self, combatant_id: str, action_cost: float = 0.0):
        """
        Advance turn for a combatant
        
        Args:
            combatant_id: Combatant ID
            action_cost: AV cost for action (default 0 = full turn)
        """
        if combatant_id not in self.current_av:
            return
        
        combatant = next((c for c in self.combatants if c["id"] == combatant_id), None)
        if not combatant:
            return
        
        # Reset AV to full if action_cost is 0, otherwise subtract
        if action_cost == 0.0:
            self.current_av[combatant_id] = combatant["av"]
        else:
            self.current_av[combatant_id] -= action_cost
    
    def apply_action_advance(self, combatant_id: str, advance_amount: float):
        """
        Apply Action Advance (đẩy lượt)
        
        Args:
            combatant_id: Combatant ID
            advance_amount: Amount to advance (negative = delay)
        """
        if combatant_id in self.current_av:
            self.current_av[combatant_id] = max(0, self.current_av[combatant_id] - advance_amount)
    
    def get_turn_order(self) -> List[Dict[str, Any]]:
        """Get current turn order (sorted by AV)"""
        sorted_combatants = sorted(
            self.current_av.items(),
            key=lambda x: x[1]
        )
        
        return [
            {
                "id": combatant_id,
                "av": av,
                "speed": next((c["speed"] for c in self.combatants if c["id"] == combatant_id), 0)
            }
            for combatant_id, av in sorted_combatants
        ]


class CombatFormulas:
    """
    Hybrid Damage Formula
    - Linear khi ATK >= DEF: Damage = ATK × 2 - DEF
    - Quadratic khi ATK < DEF: Damage = ATK² / DEF
    """
    
    @staticmethod
    def calculate_damage(attack: int, defense: int) -> int:
        """
        Calculate damage using hybrid formula
        
        Args:
            attack: Attack stat
            defense: Defense stat
        
        Returns:
            Damage dealt
        """
        if attack >= defense:
            # Linear formula
            damage = attack * 2 - defense
        else:
            # Quadratic formula
            damage = (attack ** 2) // defense if defense > 0 else attack * 2
        
        return max(1, damage)  # Minimum 1 damage
    
    @staticmethod
    def calculate_critical_damage(
        base_damage: int,
        crit_chance: float,
        crit_multiplier: float = 2.0
    ) -> Dict[str, Any]:
        """
        Calculate critical hit damage
        
        Args:
            base_damage: Base damage
            crit_chance: Critical chance (0.0 - 1.0)
            crit_multiplier: Critical damage multiplier
        
        Returns:
            {"is_critical": bool, "damage": int}
        """
        import random
        
        is_critical = random.random() < crit_chance
        
        if is_critical:
            damage = int(base_damage * crit_multiplier)
        else:
            damage = base_damage
        
        return {
            "is_critical": is_critical,
            "damage": damage
        }
    
    @staticmethod
    def calculate_elemental_damage(
        base_damage: int,
        attacker_element: str,
        defender_element: str
    ) -> int:
        """
        Calculate elemental damage với Ngũ Hành tương khắc
        
        Tương khắc:
        - Hỏa > Kim > Mộc > Thổ > Thủy > Hỏa
        
        Args:
            base_damage: Base damage
            attacker_element: Attacker element
            defender_element: Defender element
        
        Returns:
            Final damage
        """
        # Ngũ Hành cycle
        element_order = ["Fire", "Metal", "Wood", "Earth", "Water"]
        
        try:
            attacker_idx = element_order.index(attacker_element)
            defender_idx = element_order.index(defender_element)
            
            # Check if attacker counters defender
            if (attacker_idx + 1) % len(element_order) == defender_idx:
                # Tương khắc: +50% damage
                return int(base_damage * 1.5)
            elif (defender_idx + 1) % len(element_order) == attacker_idx:
                # Bị khắc: -25% damage
                return int(base_damage * 0.75)
            else:
                # Neutral
                return base_damage
        except ValueError:
            # Unknown element, no modifier
            return base_damage
    
    @staticmethod
    def calculate_defense_reduction(
        damage: int,
        defense: int,
        penetration: float = 0.0
    ) -> int:
        """
        Calculate damage after defense reduction
        
        Args:
            damage: Raw damage
            defense: Defense stat
            penetration: Armor penetration (0.0 - 1.0)
        
        Returns:
            Final damage
        """
        effective_defense = int(defense * (1.0 - penetration))
        final_damage = max(1, damage - effective_defense)
        return final_damage


class CombatSystem:
    """
    Main Combat System
    """
    
    def __init__(self):
        self.av_system = ActionValueSystem()
        self.formulas = CombatFormulas()
    
    def start_battle(self, combatants: List[Dict[str, Any]]):
        """Start a battle"""
        self.av_system = ActionValueSystem()
        
        for combatant in combatants:
            self.av_system.add_combatant(
                combatant_id=combatant["id"],
                speed=combatant.get("speed", 100)
            )
    
    def perform_attack(
        self,
        attacker: Dict[str, Any],
        defender: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform attack
        
        Returns:
            Attack result
        """
        # Calculate base damage
        attack_stat = attacker.get("attack", 0)
        defense_stat = defender.get("defense", 0)
        base_damage = self.formulas.calculate_damage(attack_stat, defense_stat)
        
        # Apply elemental damage
        attacker_element = attacker.get("element", "None")
        defender_element = defender.get("element", "None")
        elemental_damage = self.formulas.calculate_elemental_damage(
            base_damage,
            attacker_element,
            defender_element
        )
        
        # Apply critical hit
        crit_chance = attacker.get("crit_chance", 0.05)
        crit_result = self.formulas.calculate_critical_damage(
            elemental_damage,
            crit_chance,
            attacker.get("crit_multiplier", 2.0)
        )
        
        # Apply defense reduction
        penetration = attacker.get("penetration", 0.0)
        final_damage = self.formulas.calculate_defense_reduction(
            crit_result["damage"],
            defense_stat,
            penetration
        )
        
        # Apply damage to defender
        defender["current_hp"] = max(0, defender.get("current_hp", 0) - final_damage)
        
        return {
            "attacker_id": attacker["id"],
            "defender_id": defender["id"],
            "base_damage": base_damage,
            "elemental_damage": elemental_damage,
            "is_critical": crit_result["is_critical"],
            "final_damage": final_damage,
            "defender_hp_remaining": defender["current_hp"]
        }
    
    def get_next_turn(self) -> Optional[Dict[str, Any]]:
        """Get next turn info"""
        next_actor_id = self.av_system.get_next_actor()
        if not next_actor_id:
            return None
        
        turn_order = self.av_system.get_turn_order()
        
        return {
            "current_actor": next_actor_id,
            "turn_order": turn_order
        }
    
    def end_turn(self, combatant_id: str):
        """End turn for combatant"""
        self.av_system.advance_turn(combatant_id, action_cost=0.0)

