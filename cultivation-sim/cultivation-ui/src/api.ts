import axios from 'axios';

const API_BASE = 'http://localhost:8001';

export interface CharacterData {
  gender: string;
  talent: string;
  race: string;
  background: string;
  physique_id?: string;
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

export interface LocationData {
  location_id: string;
  name: string;
  type: string;
  region: string;
  qi_density: number;
}

export interface NeedsData {
  hunger: number;
  energy: number;
  social: number;
}

export interface RelationshipInfo {
  relationship_type: string;
  affinity: number;
  trust_level: number;
  metadata: any;
}

export interface SkillData {
  id: string;
  name: string;
  description: string;
  mana_cost: number;
  cooldown: number;
  damage?: number;
  effects?: any;
}

export interface EconomyData {
  prices: Record<string, any>;
  economic_cycle: string;
  active_auctions: number;
}

export interface SocialGraphData {
  relationships: Record<string, any>;
  centrality: number;
  total_relationships: number;
}

export interface FormationData {
  id: string;
  bonus: any;
  node_count: number;
}

export interface QuestData {
  quest_id: string;
  title: string;
  description: string;
  status?: string;
}

export interface QuestsInfo {
  pending: QuestData[];
  active: QuestData[];
  completed: number;
}

export interface AttributesData {
  con?: number; // Căn cốt
  int?: number; // Ngộ tính
  per?: number; // Thần thức
  luk?: number; // Phúc duyên
  cha?: number; // Mị lực
  kar?: number; // Cơ duyên
  physique?: string; // Thể chất (Trời sinh thần lực, Thiên Linh Thể, ...)
  physique_level?: number; // Cấp độ thể chất
  appearance?: number; // Nhan sắc (0-100)
  luck?: number; // Vận may (0-100)
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
  attributes?: AttributesData | null;
  location?: LocationData | null;
  sect_id?: string | null;
  sect_context?: string | null;
  needs?: NeedsData | null;
  relationships?: Record<string, RelationshipInfo> | null;
  // Advanced Systems
  skills?: SkillData[];
  economy?: EconomyData;
  social_graph?: SocialGraphData;
  formations?: FormationData[];
  quests?: QuestsInfo;
  rewrite_destiny_perks?: any[];
  tao_souls?: any[];
}

export interface ActionResponse {
  narrative: string;
  choices: string[];
  game_state: GameState;
  debug_info?: {
    prompt?: string;
    raw_response?: string;
    parsed_result?: any;
    error?: string;
  };
}

export interface HistoryEntry {
  timestamp: string;
  prompt?: string;
  response?: string;
  narrative?: string;
  choices?: string[];
  error?: string;
}

export interface SaveInfo {
  save_id: string;
  age: number;
  gender: string;
  talent: string;
  character_name: string;
  updated_at: string;
  file_path: string;
}

class CultivationAPI {
  // Debug callback
  private debugCallback?: (info: any) => void;
  
  setDebugCallback(callback: (info: any) => void) {
    this.debugCallback = callback;
  }
  
  private async request<T>(method: string, endpoint: string, data?: any, retries: number = 3): Promise<T> {
    let lastError: any = null;
    
    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        if (this.debugCallback && method === 'POST' && endpoint === '/game/action') {
          this.debugCallback({ type: 'request', data });
        }
        
        const response = await axios({
          method,
          url: `${API_BASE}${endpoint}`,
          data,
          headers: { 'Content-Type': 'application/json' },
          timeout: 30000, // 30 seconds timeout
        });
        
        if (this.debugCallback && method === 'POST' && endpoint === '/game/action') {
          this.debugCallback({ type: 'response', data: response.data });
        }
        
        return response.data;
      } catch (error: any) {
        lastError = error;
        
        // If it's a connection error, wait and retry
        if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
          if (attempt < retries - 1) {
            // Wait before retrying (exponential backoff)
            await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
            continue;
          }
          throw new Error(`Cannot connect to server at ${API_BASE}. Please make sure the server is running on port 8001. Error: ${error.message}`);
        }
        
        // If it's a timeout, retry
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
          if (attempt < retries - 1) {
            await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
            continue;
          }
          throw new Error(`Server request timed out. The server may be overloaded or not responding.`);
        }
        
        // For other errors, check if it's a server error
        if (error.response) {
          // Server responded with error status
          const status = error.response.status;
          const detail = error.response.data?.detail || error.response.data?.message || 'Unknown error';
          throw new Error(`Server error (${status}): ${detail}`);
        }
        
        // Unknown error
        throw error;
      }
    }
    
    throw lastError;
  }

  async checkHealth() {
    try {
      return await this.request<{ status: string; service: string; log_file?: string }>('GET', '/health');
    } catch (error: any) {
      // Return a failed health status instead of throwing
      return {
        status: 'unhealthy',
        service: 'cultivation-simulator',
        error: error.message || 'Server not responding'
      };
    }
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

  // Save Management
  async listSaves() {
    return this.request<{ saves: SaveInfo[] }>('GET', '/saves/list');
  }

  async loadSave(saveId: string) {
    return this.request<{
      message: string;
      save_id: string;
      narrative: string;
      choices: string[];
      character_name: string;
      game_state: GameState;
    }>('POST', '/saves/load', { save_id: saveId });
  }

  async deleteSave(saveId: string) {
    return this.request<{ message: string }>('DELETE', `/saves/${saveId}`);
  }

  // Shop API
  async getShopItems(locationId?: string) {
    const params = locationId ? `?location_id=${locationId}` : '';
    return this.request<{
      location_id: string;
      items: Array<{
        id: string;
        name: string;
        type: string;
        price: number;
        description: string;
        rarity: string;
        can_afford: boolean;
        stats: Record<string, any>;
      }>;
      player_money: number;
    }>('GET', `/shop/items${params}`);
  }

  async buyItem(itemId: string) {
    return this.request<{
      success: boolean;
      message: string;
      narrative?: string;
      item?: { id: string; name: string; type: string };
      remaining_money: number;
    }>('POST', '/shop/buy', { item_id: itemId });
  }

  // Skills API
  async getAvailableSkills() {
    return this.request<{
      skills: Array<{
        id: string;
        name: string;
        type: string;
        tier: string;
        description: string;
        requirements: Record<string, any>;
        learning_cost: Record<string, any>;
        effects: Record<string, any>;
        can_learn: boolean;
      }>;
      player_realm: string;
      player_level: number;
      player_money: number;
    }>('GET', '/skills/available');
  }

  async learnSkill(skillId: string) {
    return this.request<{
      success: boolean;
      message: string;
      narrative?: string;
      technique?: { id: string; name: string; type: string; tier: string };
      remaining_money: number;
    }>('POST', '/skills/learn', { skill_id: skillId });
  }

  // Quests API
  async getAvailableQuests() {
    return this.request<{
      pending: QuestData[];
      active: QuestData[];
      completed: number;
    }>('GET', '/quests/available');
  }

  // Combat API
  async startCombat(enemyId?: string, enemyType?: string) {
    return this.request<{
      success: boolean;
      combat_state: any;
      message: string;
    }>('POST', '/combat/start', {
      enemy_id: enemyId,
      enemy_type: enemyType || 'spirit_beast',
    });
  }

  async combatAction(action: string, combatState: any) {
    return this.request<{
      success: boolean;
      combat_state: any;
      narrative?: string;
      result?: string;
      rewards?: Record<string, any>;
    }>('POST', '/combat/action', {
      action,
      combat_state: combatState,
    });
  }
}

export const api = new CultivationAPI();
