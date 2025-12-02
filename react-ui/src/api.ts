import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export interface GameState {
  player_hp: number;
  player_max_hp: number;
  player_name: string;
  current_room: string;
  room_description: string;
  inventory: Array<{ name: string; description: string }>;
  visible_entities: Array<{ name: string; description: string; type: string }>;
  narrative_log: string[];
}

export interface ActionResponse {
  narrative: string;
  action_intent: string;
  game_state: GameState;
}

class GameAPI {
  private async request<T>(method: string, endpoint: string, data?: any): Promise<T> {
    try {
      const response = await axios({
        method,
        url: `${API_BASE}${endpoint}`,
        data,
        headers: { 'Content-Type': 'application/json' },
      });
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNREFUSED') {
        throw new Error('Cannot connect to server. Make sure the server is running on port 8000!');
      }
      throw error;
    }
  }

  async checkHealth() {
    return this.request<{ message: string; status: string }>('GET', '/');
  }

  async newGame(playerName: string = 'Hero') {
    return this.request<{ game_state: GameState }>('POST', '/game/new', { player_name: playerName });
  }

  async loadGame(saveId: string) {
    return this.request<{ game_state: GameState }>('POST', '/game/load', { save_id: saveId });
  }

  async listSaves() {
    return this.request<{ saves: string[] }>('GET', '/game/saves');
  }

  async sendAction(userInput: string): Promise<ActionResponse> {
    return this.request<ActionResponse>('POST', '/game/action', { user_input: userInput });
  }

  async getMemoryCount() {
    try {
      return await this.request<{ count: number }>('GET', '/memory/count');
    } catch {
      return { count: 0 };
    }
  }
}

export const api = new GameAPI();

