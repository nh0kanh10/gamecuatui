"""
Playable Text Adventure Game - Gemini Edition
Cloud-native AI powered by Gemini 1.5 Flash
"""

import sys
import os
import glob
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load env vars
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.core import (
    get_entity_manager, get_db,
    LocationComponent, StatsComponent, InventoryComponent,
    IdentityComponent, DialogueComponent, StateComponent
)
from engine.ai import get_gemini_agent, GameContext, ContextBuilder

class Game:
    """Main game controller using Gemini"""
    
    def __init__(self):
        self.save_id = "default"
        self.db_path = str(Path(__file__).parent.parent / "data" / "world.db")
        self.em = None
        self.context_builder = None
        self.ai = get_gemini_agent()
        self.player_id = None
        self.turn_count = 0
        
    def init_engine(self, db_path: str):
        """Initialize engine with specific DB"""
        self.db_path = db_path
        # Reset global instances to ensure we use the new DB path
        import engine.core.database
        import engine.core.entity
        engine.core.database._db = None
        engine.core.entity._em = None
        
        self.em = get_entity_manager(get_db(db_path))
        self.context_builder = ContextBuilder(self.em)
        
    def setup_world(self):
        """Create initial game world"""
        print("🌍 Creating world...")
        
        # Player
        self.player_id = self.em.create_player("Hero")
        
        # NPCs
        guard_id = self.em.create_npc("Old Guard", "entrance", "passive")
        guard_dialogue = self.em.get(guard_id, DialogueComponent)
        guard_dialogue.greeting = "Welcome, traveler. Beware the dungeon ahead."
        self.em.add(guard_id, guard_dialogue)
        
        goblin_id = self.em.create_npc("Goblin", "entrance", "aggressive")
        goblin_stats = self.em.get(goblin_id, StatsComponent)
        goblin_stats.hp = 15
        goblin_stats.max_hp = 15
        self.em.add(goblin_id, goblin_stats)
        
        # Items
        self.em.create_weapon("Iron Sword", damage=12, room_id="entrance")
        self.em.create_item("Torch", "A flickering torch", room_id="entrance")
        
        # Door
        self.em.create_door("Heavy Door", "entrance", is_locked=False)
        
        print("✅ World created!")
        
    def apply_updates(self, updates: dict):
        """Apply state updates from AI"""
        if not updates:
            return

        # Handle HP changes
        if 'target_hp_change' in updates:
            # For simplicity in this demo, we assume target is the goblin if attacking
            # In real engine, AI should provide target_id
            # Here we hackily find the goblin
            entities = self.em.find_at_location("entrance")
            for eid in entities:
                name = self.em.get_name(eid)
                # Only apply to Goblin for now (Demo hack)
                if "Goblin" in name:
                    stats = self.em.get(eid, StatsComponent)
                    if stats:
                        old_hp = stats.hp
                        stats.hp += updates['target_hp_change']
                        stats.hp = max(0, stats.hp)
                        self.em.add(eid, stats)
                        
                        if old_hp != stats.hp:
                             print(f"   [DEBUG] {name} HP: {old_hp} -> {stats.hp}")
                        
                        if stats.hp == 0:
                            state = self.em.get(eid, StateComponent) or StateComponent()
                            state.is_dead = True
                            self.em.add(eid, state)
                            print(f"   [DEBUG] {name} died.")
                    break # Stop after finding first goblin to avoid spam
        
        # Handle Movement
        if 'new_location_id' in updates:
            loc = self.em.get(self.player_id, LocationComponent)
            loc.room_id = updates['new_location_id']
            self.em.add(self.player_id, loc)
            print(f"   [DEBUG] Moved to: {loc.room_id}")

    def play_turn(self, user_input: str):
        """Process one game turn"""
        self.turn_count += 1
        
        # 1. Build Context
        context = self.context_builder.build(self.player_id)
        
        # 2. AI Processing (Parse + Validate + Narrate)
        print("🤖 Gemini thinking...")
        # Pass save_id to AI for memory context
        response = self.ai.process_turn(user_input, context, save_id=self.save_id)
        
        # 3. Display Narrative
        print(f"\n📖 {response.get('narrative', '...')}\n")
        
        # 4. Apply State Updates (Hard Rules applied by Engine)
        updates = response.get('state_updates', {})
        self.apply_updates(updates)
        
        # 5. Debug Info
        intent = response.get('action_intent', 'UNKNOWN')
        if intent != 'NONE':
            print(f"   (Action: {intent})")
    
    def show_main_menu(self):
        """Show CLI Main Menu"""
        print("\n=== 🏰 THE LAST VOYAGE ===")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        
        choice = input("\nSelect option: ").strip()
        return choice

    def start_new_game(self):
        """Start a fresh game session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_id = f"save_{timestamp}"
        db_path = f"data/saves/{self.save_id}.db"
        
        print(f"\n🆕 Starting New Game (Slot: {self.save_id})...")
        self.init_engine(db_path)
        self.setup_world()
        self.run_game_loop()

    def load_game(self):
        """Load an existing game session"""
        saves = glob.glob("data/saves/*.db")
        if not saves:
            print("\n❌ No save files found!")
            return

        print("\n📂 Select Save File:")
        for i, save in enumerate(saves):
            print(f"{i+1}. {os.path.basename(save)}")
        
        try:
            choice = int(input("\nSelect save number: ")) - 1
            if 0 <= choice < len(saves):
                db_path = saves[choice]
                self.save_id = Path(db_path).stem
                print(f"\n🔄 Loading {self.save_id}...")
                
                self.init_engine(db_path)
                
                # Find player
                self.player_id = self.em.find_player()
                if self.player_id:
                    print(f"✅ Loaded successfully! Welcome back.")
                    self.run_game_loop()
                else:
                    print("⚠️ Error: Player not found in save file.")
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Invalid input.")

    def run_game_loop(self):
        """Main gameplay loop"""
        print("\n(Type 'quit' to exit and save)")
        while True:
            try:
                user_input = input("🎮 > ").strip()
                if not user_input: continue
                if user_input.lower() in ['quit', 'exit']: 
                    print("💾 Game saved.")
                    break
                
                self.play_turn(user_input)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

    def run(self):
        """Entry point"""
        # Ensure saves directory exists
        os.makedirs("data/saves", exist_ok=True)
        
        # Check API Key
        if not os.environ.get("GEMINI_API_KEY"):
            print("\n❌ ERROR: GEMINI_API_KEY not found!")
            return

        model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash-latest")
        print(f"🤖 AI Model: {model_name}")
        
        while True:
            choice = self.show_main_menu()
            if choice == '1':
                self.start_new_game()
            elif choice == '2':
                self.load_game()
            elif choice == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    game = Game()
    game.run()
