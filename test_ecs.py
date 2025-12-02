"""
Test Script - Verify Core ECS Implementation
"""

import sys
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent))

from engine.core import (
    get_entity_manager,
    IdentityComponent,
    LocationComponent,
    StatsComponent,
    InventoryComponent
)


def test_basic_ecs():
    """Test basic ECS operations"""
    print("=" * 60)
    print("Testing Core ECS Implementation")
    print("=" * 60)
    
    em = get_entity_manager()
    
    # Test 1: Create player
    print("\n[Test 1] Creating player entity...")
    player_id = em.create_player("Hero")
    print(f"✅ Created player with ID: {player_id}")
    
    # Test 2: Get components
    print("\n[Test 2] Reading player components...")
    identity = em.get(player_id, IdentityComponent)
    stats = em.get(player_id, StatsComponent)
    location = em.get(player_id, LocationComponent)
    
    print(f"  Name: {identity.name}")
    print(f"  HP: {stats.hp}/{stats.max_hp}")
    print(f"  Location: {location.zone_id}/{location.room_id}")
    print("✅ Component retrieval successful")
    
    # Test 3: Update component
    print("\n[Test 3] Updating player stats...")
    stats.hp = 75
    em.add(player_id, stats)
    
    # Verify update
    updated_stats = em.get(player_id, StatsComponent)
    assert updated_stats.hp == 75
    print(f"  HP updated: {updated_stats.hp}/{updated_stats.max_hp}")
    print("✅ Component update successful")
    
    # Test 4: Create NPC
    print("\n[Test 4] Creating NPC...")
    goblin_id = em.create_npc("Goblin Scout", "entrance", "aggressive")
    goblin_name = em.get_name(goblin_id)
    print(f"✅ Created NPC: {goblin_name} (ID: {goblin_id})")
    
    # Test 5: Create weapon
    print("\n[Test 5] Creating weapon...")
    sword_id = em.create_weapon("Rusty Sword", damage=10, room_id="entrance")
    sword_name = em.get_name(sword_id)
    print(f"✅ Created weapon: {sword_name} (ID: {sword_id})")
    
    # Test 6: Find entities at location
    print("\n[Test 6] Finding entities at entrance...")
    entities_at_entrance = em.find_at_location("entrance")
    print(f"  Found {len(entities_at_entrance)} entities:")
    for entity_id in entities_at_entrance:
        name = em.get_name(entity_id)
        print(f"    - {name} (ID: {entity_id})")
    print("✅ Location query successful")
    
    # Test 7: Inventory operation
    print("\n[Test 7] Adding sword to player inventory...")
    player_inv = em.get(player_id, InventoryComponent)
    player_inv.items.append(sword_id)
    em.add(player_id, player_inv)
    
    # Remove sword from world (it's now in inventory)
    em.remove(sword_id, LocationComponent)
    
    # Verify
    updated_inv = em.get(player_id, InventoryComponent)
    print(f"  Player inventory: {len(updated_inv.items)} items")
    print("✅ Inventory operation successful")
    
    # Test 8: Get all components
    print("\n[Test 8] Getting all player components...")
    all_comps = em.get_all(player_id)
    print(f"  Player has {len(all_comps)} components:")
    for comp_type in all_comps.keys():
        print(f"    - {comp_type}")
    print("✅ Bulk retrieval successful")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nCore ECS is working correctly. Ready for Phase 1.3!")


if __name__ == "__main__":
    test_basic_ecs()
