"""
Playable Text Adventure Game
Natural language input with AI-powered responses
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from engine.core import (
    get_entity_manager, 
    LocationComponent, StatsComponent, InventoryComponent,
    IdentityComponent, DialogueComponent
)
from engine.systems import get_precondition_system, get_action_executor
from engine.ai import get_ollama_agent, GameContext, ActionProposal


class Game:
    """Main game controller"""
    
    def __init__(self):
        self.em = get_entity_manager()
        self.validator = get_precondition_system()
        self.executor = get_action_executor()
        self.ai = get_ollama_agent()
        self.player_id = None
        self.turn_count = 0
        
    def setup_world(self):
        """Create initial game world"""
        print("🌍 Creating world...")
        
        # Player
        self.player_id = self.em.create_player("Hero")
        
        # NPCs
        guard_id = self.em.create_npc("Old Guard", "entrance", "passive")
        guard_dialogue = self.em.get(guard_id, DialogueComponent)
        guard_dialogue.greeting = "Welcome, traveler. Beware the dungeon ahead."
        guard_dialogue.topics = {
            "dungeon": "The dungeon is filled with dangerous creatures.",
            "quest": "Find the ancient artifact in the depths."
        }
        self.em.add(guard_id, guard_dialogue)
        
        goblin_id = self.em.create_npc("Goblin", "entrance", "aggressive")
        goblin_stats = self.em.get(goblin_id, StatsComponent)
        goblin_stats.hp = 15
        goblin_stats.max_hp = 15
        self.em.add(goblin_id, goblin_stats)
        
        # Items
        sword_id = self.em.create_weapon("Iron Sword", damage=12, room_id="entrance")
        torch_id = self.em.create_item("Torch", "A flickering torch", room_id="entrance")
        
        # Door
        door_id = self.em.create_door("Heavy Door", "entrance", is_locked=False)
        door_loc = self.em.get(door_id, LocationComponent)
        door_loc.x = 1
        door_loc.y = 0
        self.em.add(door_id, door_loc)
        
        print("✅ World created!")
        
    def get_context(self) -> GameContext:
        """Build current game context for AI"""
        player_stats = self.em.get(self.player_id, StatsComponent)
        player_loc = self.em.get(self.player_id, LocationComponent)
        player_inv = self.em.get(self.player_id, InventoryComponent)
        
        # Get visible entities
        entities_here = self.em.find_at_location(player_loc.room_id)
        visible = []
        for entity_id in entities_here:
            if entity_id == self.player_id:
                continue
            identity = self.em.get(entity_id, IdentityComponent)
            if identity:
                visible.append({
                    'id': entity_id,
                    'name': identity.name,
                    'description': identity.description
                })
        
        # Get inventory
        inventory = []
        for item_id in player_inv.items:
            identity = self.em.get(item_id, IdentityComponent)
            if identity:
                inventory.append({
                    'id': item_id,
                    'name': identity.name
                })
        
        return GameContext(
            player_id=self.player_id,
            player_name="Hero",
            player_hp=player_stats.hp,
            player_max_hp=player_stats.max_hp,
            current_room_id=player_loc.room_id,
            room_description=f"You are in the {player_loc.room_id}.",
            visible_entities=visible,
            inventory=inventory
        )
    
    def print_status(self):
        """Display current status"""
        stats = self.em.get(self.player_id, StatsComponent)
        location = self.em.get(self.player_id, LocationComponent)
        inventory = self.em.get(self.player_id, InventoryComponent)
        
        print(f"\n{'='*60}")
        print(f"❤️  HP: {stats.hp}/{stats.max_hp}")
        print(f"📍 Location: {location.room_id}")
        
        # List visible entities
        entities_here = self.em.find_at_location(location.room_id)
        visible_names = []
        for eid in entities_here:
            if eid != self.player_id:
                visible_names.append(self.em.get_name(eid))
        
        if visible_names:
            print(f"👁️  You see: {', '.join(visible_names)}")
        
        if inventory.items:
            inv_names = [self.em.get_name(iid) for iid in inventory.items]
            print(f"🎒 Inventory: {', '.join(inv_names)}")
        
        print(f"{'='*60}\n")
    
    def resolve_target_name(self, target_name: Optional[str], context: GameContext) -> Optional[int]:
        """Resolve entity name to ID"""
        if not target_name:
            return None
        
        target_lower = target_name.lower()
        
        # Check visible entities
        for entity in context.visible_entities:
            if target_lower in entity['name'].lower():
                return entity['id']
        
        # Check inventory
        for item in context.inventory:
            if target_lower in item['name'].lower():
                return item['id']
        
        return None
    
    def play_turn(self, user_input: str):
        """Process one game turn"""
        self.turn_count += 1
        
        # Get context
        context = self.get_context()
        
        # Parse input with AI
        print("🤖 AI parsing input...")
        proposal = self.ai.parse_input(user_input, context)
        
        if not proposal:
            print("❌ Sorry, I didn't understand that. Try: 'take sword', 'attack goblin', etc.")
            return
        
        print(f"   → Interpreted as: {proposal.intent}")
        
        # Resolve target name to ID
        if proposal.target_name:
            target_id = self.resolve_target_name(proposal.target_name, context)
            if not target_id:
                print(f"❌ Can't find '{proposal.target_name}' here.")
                return
            proposal.target_id = target_id
        
        # Validate
        is_valid, error = self.validator.validate(proposal, self.player_id)
        
        if not is_valid:
            print(f"\n❌ {error.message}")
            if error.suggested_actions:
                print(f"   💡 Try: {', '.join(error.suggested_actions)}")
            return
        
        # Execute
        result = self.executor.execute(proposal, self.player_id)
        
        if not result.success:
            print(f"\n❌ {result.message}")
            return
        
        # Generate narrative
        print("\n📖 Generating narrative...")
        narrative = self.ai.generate_narrative(result, context)
        
        print(f"\n{narrative}\n")
        
        # Show changes if significant
        if result.changes:
            if 'damage_dealt' in result.changes:
                dmg = result.changes['damage_dealt']
                target_hp = result.changes.get('target_hp', 0)
                print(f"   💥 Dealt {dmg} damage! (Target HP: {target_hp})")
            
            if result.changes.get('target_died'):
                print(f"   💀 Enemy defeated!")
    
    def run(self):
        """Main game loop"""
        print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        🗡️  AI TEXT ADVENTURE - PLAYABLE DEMO 🗡️          ║
║                                                          ║
║  Commands: Natural language                              ║
║  Examples: "take the sword", "attack goblin",           ║
║            "talk to guard", "go north"                   ║
║                                                          ║
║  Type 'quit' to exit                                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        self.setup_world()
        self.print_status()
        
        while True:
            try:
                user_input = input("🎮 > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for playing!")
                    break
                
                if user_input.lower() in ['help', '?']:
                    print("""
Commands:
  - take <item>
  - drop <item>
  - equip <weapon>
  - attack <enemy>
  - talk to <npc>
  - examine <thing>
  - open/close <door>
  - go <direction>
                    """)
                    continue
                
                if user_input.lower() == 'status':
                    self.print_status()
                    continue
                
                # Play turn
                self.play_turn(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Game interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    game = Game()
    game.run()
