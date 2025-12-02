"""
Text Adventure Game - Main Application
Clean, modern UI with NiceGUI
"""

from nicegui import ui, app
import ollama
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GameState:
    """Current game state"""
    player_name: str = "Adventurer"
    location: str = "Starting Point"
    hp: int = 100
    max_hp: int = 100
    inventory: List[str] = None
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = ["Rusty Sword", "Torch"]


class TextAdventureGame:
    """Main game engine"""
    
    def __init__(self):
        self.state = GameState()
        self.conversation_history: List[Dict[str, str]] = []
        self.ai_model = "qwen2.5:3b"  # Best from benchmark
        
    def generate_response(self, player_input: str) -> str:
        """Generate AI response for player input"""
        try:
            # Build context
            context = self._build_context(player_input)
            
            # Call Ollama
            response = ollama.generate(
                model=self.ai_model,
                prompt=context,
                options={
                    'num_predict': 200,
                    'temperature': 0.7
                }
            )
            
            ai_response = response['response'].strip()
            
            # Save to history
            self.conversation_history.append({
                'player': player_input,
                'ai': ai_response,
                'timestamp': datetime.now().isoformat()
            })
            
            return ai_response
            
        except Exception as e:
            return f"⚠️ Error: {str(e)}\nMake sure Ollama is running: `ollama serve`"
    
    def _build_context(self, player_input: str) -> str:
        """Build prompt context for AI"""
        system_prompt = f"""You are a game master for a text adventure game.

CURRENT STATE:
- Player: {self.state.player_name}
- Location: {self.state.location}
- HP: {self.state.hp}/{self.state.max_hp}
- Inventory: {', '.join(self.state.inventory)}

RULES:
- Be descriptive and atmospheric
- Keep responses 2-3 paragraphs
- Respond to player actions naturally
- Maintain consistency with game state

Player says: "{player_input}"

Describe what happens next:"""
        
        return system_prompt
    
    def reset_game(self):
        """Reset to initial state"""
        self.state = GameState()
        self.conversation_history = []


# Global game instance
game = TextAdventureGame()


def create_ui():
    """Create the main UI"""
    
    # Custom CSS for dark fantasy theme
    ui.add_head_html("""
    <style>
        :root {
            --bg-dark: #1a1a2e;
            --bg-card: #16213e;
            --accent: #0f3460;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --health-bar: #e74c3c;
            --border: #2a2a4e;
        }
        
        body {
            background: var(--bg-dark);
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        .game-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            color: var(--text-primary);
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            margin-top: 4px;
        }
        
        .chat-container {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            min-height: 500px;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .message {
            margin-bottom: 16px;
            padding: 12px;
            border-radius: 8px;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.player {
            background: var(--accent);
            color: var(--text-primary);
            margin-left: 20%;
        }
        
        .message.ai {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-primary);
            margin-right: 20%;
        }
        
        .message-label {
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 6px;
            font-weight: 600;
        }
        
        .health-bar {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
        }
        
        .health-fill {
            background: linear-gradient(90deg, #e74c3c, #c0392b);
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .inventory-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 8px 12px;
            border-radius: 6px;
            margin: 4px;
            display: inline-block;
            font-size: 14px;
            color: var(--text-primary);
        }
    </style>
    """)
    
    with ui.row().classes('game-container w-full p-4 gap-4'):
        
        # Left sidebar - Player Stats
        with ui.column().classes('w-80'):
            with ui.card().classes('stat-card'):
                ui.label('⚔️ PLAYER STATUS').classes('text-xl font-bold mb-4')
                
                # Player name
                ui.label('CHARACTER').classes('stat-label')
                player_name_label = ui.label(game.state.player_name).classes('stat-value')
                
                ui.separator().classes('my-4')
                
                # Health
                ui.label('HEALTH').classes('stat-label')
                with ui.row().classes('w-full items-center gap-2'):
                    hp_label = ui.label(f'{game.state.hp}/{game.state.max_hp}').classes('stat-value')
                
                hp_percent = (game.state.hp / game.state.max_hp) * 100
                with ui.element('div').classes('health-bar w-full mt-2'):
                    hp_bar = ui.element('div').classes('health-fill').style(f'width: {hp_percent}%')
                
                ui.separator().classes('my-4')
                
                # Location
                ui.label('LOCATION').classes('stat-label')
                location_label = ui.label(game.state.location).classes('stat-value text-base')
                
                ui.separator().classes('my-4')
                
                # Inventory
                ui.label('INVENTORY').classes('stat-label')
                inventory_container = ui.column().classes('mt-2')
                
                def refresh_inventory():
                    inventory_container.clear()
                    with inventory_container:
                        for item in game.state.inventory:
                            ui.label(f'• {item}').classes('inventory-item')
                
                refresh_inventory()
        
        # Main area - Chat & Input
        with ui.column().classes('flex-1'):
            # Title
            with ui.card().classes('stat-card mb-4'):
                ui.label('🗡️ TEXT ADVENTURE').classes('text-2xl font-bold')
                ui.label('Powered by Local AI').classes('text-sm text-gray-400')
            
            # Chat area
            chat_container = ui.column().classes('chat-container')
            
            # Welcome message
            with chat_container:
                with ui.element('div').classes('message ai'):
                    ui.label('GAME MASTER').classes('message-label')
                    ui.label('''Welcome, brave adventurer! You stand at the entrance of an ancient dungeon, 
                    shrouded in mist and mystery. The air is thick with danger and opportunity. 
                    
                    What would you like to do?''').classes('text-sm leading-relaxed')
            
            # Input area
            with ui.card().classes('stat-card mt-4'):
                with ui.row().classes('w-full gap-2'):
                    input_field = ui.input(
                        placeholder='Type your action (e.g., "examine the door", "go north")...'
                    ).classes('flex-1').props('outlined dense')
                    
                    send_button = ui.button('Send', icon='send').props('unelevated')
                    
                with ui.row().classes('w-full gap-2 mt-2'):
                    ui.button('📜 Look Around', on_click=lambda: handle_quick_action('look around')).props('outline dense')
                    ui.button('🎒 Check Inventory', on_click=lambda: handle_quick_action('check inventory')).props('outline dense')
                    ui.button('❓ Help', on_click=lambda: handle_quick_action('help')).props('outline dense')
                    ui.button('🔄 New Game', on_click=lambda: reset_game()).props('outline dense color=orange')
            
            # Handle input
            async def handle_input():
                user_input = input_field.value.strip()
                if not user_input:
                    return
                
                # Clear input
                input_field.value = ''
                
                # Disable input while processing
                input_field.disable()
                send_button.disable()
                
                # Show player message
                with chat_container:
                    with ui.element('div').classes('message player'):
                        ui.label('YOU').classes('message-label')
                        ui.label(user_input).classes('text-sm')
                
                # Show typing indicator
                with chat_container:
                    typing_indicator = ui.element('div').classes('message ai')
                    with typing_indicator:
                        ui.label('GAME MASTER').classes('message-label')
                        ui.spinner('dots', size='sm')
                
                # Scroll to bottom
                ui.run_javascript('document.querySelector(".chat-container").scrollTop = document.querySelector(".chat-container").scrollHeight')
                
                # Generate response
                await ui.run_in_executor(game.generate_response, user_input)
                ai_response = game.conversation_history[-1]['ai']
                
                # Remove typing indicator
                typing_indicator.delete()
                
                # Show AI response
                with chat_container:
                    with ui.element('div').classes('message ai'):
                        ui.label('GAME MASTER').classes('message-label')
                        ui.label(ai_response).classes('text-sm leading-relaxed')
                
                # Re-enable input
                input_field.enable()
                send_button.enable()
                input_field.focus()
                
                # Scroll to bottom
                ui.run_javascript('document.querySelector(".chat-container").scrollTop = document.querySelector(".chat-container").scrollHeight')
            
            async def handle_quick_action(action: str):
                input_field.value = action
                await handle_input()
            
            def reset_game():
                game.reset_game()
                chat_container.clear()
                inventory_container.clear()
                
                # Reset UI
                player_name_label.set_text(game.state.player_name)
                hp_label.set_text(f'{game.state.hp}/{game.state.max_hp}')
                location_label.set_text(game.state.location)
                refresh_inventory()
                
                # Show welcome message
                with chat_container:
                    with ui.element('div').classes('message ai'):
                        ui.label('GAME MASTER').classes('message-label')
                        ui.label('Game reset! You stand once again at the dungeon entrance. What will you do?').classes('text-sm')
            
            # Connect events
            send_button.on_click(handle_input)
            input_field.on('keydown.enter', handle_input)


# Run the app
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title='Text Adventure Game',
        dark=True,
        reload=False,
        port=8080,
        host='0.0.0.0'
    )
