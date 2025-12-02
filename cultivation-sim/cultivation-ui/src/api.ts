import axios from 'axios';

const API_BASE = 'http://localhost:8001';

export interface CharacterData {
  gender: string;
  talent: string;
  race: string;
  background: string;
}

export interface CultivationData {
  realm: string;
  realm_level: number;
  spiritual_power: number;
  max_spiritual_power: number;
  breakthrough_progress: number;
  techniques: string[];
  pills_consumed: number;
  spirit_stones: number;
  cultivation_age: number;
}

export interface ResourceData {
  spirit_stones: number;
  pills: Record<string, number>;
  materials: Record<string, number>;
}

export interface GameState {
  save_id: string;
  character_name: string;
  age: number;
  gender: string;
  talent: string;
  race: string;
  background: string;
  character_story: string | null;
  current_choices: string[];
  turn_count: number;
  cultivation?: CultivationData | null;
  resources?: ResourceData | null;
}

export interface ActionResponse {
  narrative: string;
  choices: string[];
  game_state: GameState;
}

class CultivationAPI {
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
        throw new Error('Cannot connect to server. Make sure the server is running on port 8001!');
      }
      throw error;
    }
  }

  async checkHealth() {
    return this.request<{ status: string; service: string }>('GET', '/health');
  }

  async newGame(playerName: string, characterData: CharacterData) {
    return this.request<{
      message: string;
      save_id: string;
      narrative: string;
      choices: string[];
      character_name: string;
      game_state: GameState;
    }>('POST', '/game/new', {
      player_name: playerName,
      character_data: characterData,
    });
  }

  async sendAction(choice: string): Promise<ActionResponse> {
    return this.request<ActionResponse>('POST', '/game/action', {
      user_input: choice,
    });
  }

  async getState() {
    return this.request<GameState>('GET', '/game/state');
  }

  async getMemoryCount() {
    try {
      return await this.request<{ count: number }>('GET', '/memory/count');
    } catch {
      return { count: 0 };
    }
  }
}

export const api = new CultivationAPI();
