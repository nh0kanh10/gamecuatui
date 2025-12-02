import ollama from 'ollama/browser'

export interface GameState {
    playerName: string;
    location: string;
    hp: number;
    maxHp: number;
    inventory: string[];
    history: ChatMessage[];
}

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
}

export class GameEngine {
    state: GameState;
    model: string;

    constructor() {
        this.model = 'qwen2.5:3b'; // Default model
        this.state = {
            playerName: 'Adventurer',
            location: 'Dungeon Entrance',
            hp: 100,
            maxHp: 100,
            inventory: ['Rusty Sword', 'Torch'],
            history: []
        };
    }

    async generateResponse(userInput: string): Promise<string> {
        // Add user message to history
        this.state.history = [...this.state.history, {
            role: 'user',
            content: userInput,
            timestamp: new Date()
        }];

        const systemPrompt = `You are a game master for a text adventure game.
CURRENT STATE:
- Player: ${this.state.playerName}
- Location: ${this.state.location}
- HP: ${this.state.hp}/${this.state.maxHp}
- Inventory: ${this.state.inventory.join(', ')}

RULES:
- Be descriptive and atmospheric
- Keep responses 2-3 paragraphs
- Respond to player actions naturally
`;

        try {
            const response = await ollama.generate({
                model: this.model,
                prompt: `${systemPrompt}\n\nPlayer: ${userInput}\nGame Master:`,
                options: {
                    num_predict: 200,
                    temperature: 0.7
                }
            });

            const aiText = response.response;

            // Add AI message to history
            this.state.history = [...this.state.history, {
                role: 'assistant',
                content: aiText,
                timestamp: new Date()
            }];

            return aiText;
        } catch (error) {
            console.error('Ollama error:', error);
            return "⚠️ Error connecting to AI. Make sure Ollama is running (`ollama serve`).";
        }
    }

    reset() {
        this.state.history = [];
        this.state.hp = 100;
        this.state.inventory = ['Rusty Sword', 'Torch'];
        this.state.location = 'Dungeon Entrance';
    }
}

export const game = new GameEngine();
