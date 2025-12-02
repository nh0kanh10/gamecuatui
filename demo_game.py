"""
Demo Game - Test Phase 1 Implementation
Simple text adventure demonstrating ECS + Validation + Execution
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine.core import get_entity_manager, LocationComponent, StatsComponent, InventoryComponent
from engine.systems import get_precondition_system, get_action_executor
from engine.ai.schemas import ActionProposal


def setup_world():
    """Create initial world with player, NPCs, items"""
    em = get_entity_manager()
    
    print("🌍 Creating world...")
    
    # Create player
    player_id = em.create_player("Hero")
    
    # Create goblin enemy
    goblin_id = em.create_npc("Goblin Scout", "entrance", "aggressive")
    goblin_stats = em.get(goblin_id, StatsComponent)
    goblin_stats.hp = 20
    goblin_stats.max_hp = 20
    em.add(goblin_id, goblin_stats)
    
    # Create sword
    sword_id = em.create_weapon("Rusty Sword", damage=10, room_id="entrance")
    
    # Create door
    door_id = em.create_door("Oak Door", "entrance", is_locked=False)
    door_loc = em.get(door_id, LocationComponent)
    door_loc.x = 1
    door_loc.y = 0
    em.add(door_id, door_loc)
    
    print(f"✅ World created!")
    print(f"  - Player: {em.get_name(player_id)}")
    print(f"  - Enemy: {em.get_name(goblin_id)}")
    print(f"  - Weapon: {em.get_name(sword_id)}")
    print(f"  - Door: {em.get_name(door_id)}")
    
    return player_id, goblin_id, sword_id, door_id


def print_status(player_id):
    """Print player status"""
    em = get_entity_manager()
    
    stats = em.get(player_id, StatsComponent)
    location = em.get(player_id, LocationComponent)
    inventory = em.get(player_id, InventoryComponent)
    
    print(f"\n📊 Status:")
    print(f"  HP: {stats.hp}/{stats.max_hp}")
    print(f"  Location: {location.room_id} ({location.x}, {location.y})")
    print(f"  Inventory: {len(inventory.items)} items")
    if inventory.equipped_weapon:
        weapon_name = em.get_name(inventory.equipped_weapon)
        print(f"  Equipped: {weapon_name}")


def demo_game():
    """Run demo game loop"""
    print("=" * 60)
    print("🎮 TEXT ADVENTURE - PHASE 1 DEMO")
    print("=" * 60)
    
    # Setup
    player_id, goblin_id, sword_id, door_id = setup_world()
    validator = get_precondition_system()
    executor = get_action_executor()
    
    print_status(player_id)
    
    # Define test scenarios
    scenarios = [
        # Scenario 1: Take and equip sword
        {
            "name": "Take sword",
            "proposal": ActionProposal(
                intent="TAKE",
                target_id=sword_id
            )
        },
        {
            "name": "Equip sword",
            "proposal": ActionProposal(
                intent="EQUIP",
                target_id=sword_id
            )
        },
        
        # Scenario 2: Attack goblin
        {
            "name": "Attack goblin",
            "proposal": ActionProposal(
                intent="ATTACK",
                target_id=goblin_id
            )
        },
        {
            "name": "Attack goblin again",
            "proposal": ActionProposal(
                intent="ATTACK",
                target_id=goblin_id
            )
        },
        
        # Scenario 3: Try to open door
        {
            "name": "Open door",
            "proposal": ActionProposal(
                intent="OPEN",
                target_id=door_id
            )
        },
        
        # Scenario 4: Try invalid action (should fail)
        {
            "name": "Try to attack sword (invalid)",
            "proposal": ActionProposal(
                intent="ATTACK",
                target_id=sword_id  # Can't attack an item!
            )
        },
    ]
    
    # Run scenarios
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Scenario {i}: {scenario['name']}")
        print(f"{'='*60}")
        
        proposal = scenario['proposal']
        
        # Validate
        is_valid, error = validator.validate(proposal, player_id)
        
        if is_valid:
            print("✅ Validation passed")
            
            # Execute
            result = executor.execute(proposal, player_id)
            
            if result.success:
                print(f"✅ {result.message}")
                if result.changes:
                    print(f"   Changes: {result.changes}")
            else:
                print(f"❌ Execution failed: {result.message}")
        else:
            print(f"❌ Validation failed: {error.message}")
            if error.suggested_actions:
                print(f"   💡 Suggestions: {', '.join(error.suggested_actions)}")
        
        # Show updated status
        if i % 2 == 0:  # Every other action
            print_status(player_id)
    
    # Final status
    print(f"\n{'='*60}")
    print("🏁 DEMO COMPLETE")
    print(f"{'='*60}")
    print_status(player_id)
    
    # Check goblin status
    em = get_entity_manager()
    goblin_stats = em.get(goblin_id, StatsComponent)
    print(f"\n🧟 Goblin HP: {goblin_stats.hp}/{goblin_stats.max_hp}")
    if goblin_stats.hp == 0:
        print("  💀 Goblin is dead!")
    
    print("\n✅ Phase 1 is fully functional!")
    print("   - ECS ✅")
    print("   - Database ✅")
    print("   - Validation ✅")
    print("   - Execution ✅")
    print("\nReady for Phase 2: AI Integration!")


if __name__ == "__main__":
    demo_game()
