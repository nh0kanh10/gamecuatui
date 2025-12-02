import { useState, useEffect } from 'react';
import { api, type GameState } from './api';

// Simple emoji icons (no external dependency)
const Brain = () => <span>🧠</span>;
const Sword = () => <span>⚔️</span>;
const MapPin = () => <span>📍</span>;
const Package = () => <span>📦</span>;
const Users = () => <span>👥</span>;
const Send = () => <span>➤</span>;
const Loader2 = ({ className }: { className?: string }) => <span className={className}>⏳</span>;

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [currentView, setCurrentView] = useState<'menu' | 'game'>('menu');
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [saves, setSaves] = useState<string[]>([]);
  const [memoryCount, setMemoryCount] = useState(0);
  const [serverStatus, setServerStatus] = useState('checking...');

  useEffect(() => {
    checkServer();
    loadSaves();
  }, []);

  async function checkServer() {
    try {
      const result = await api.checkHealth();
      setServerStatus(result.status || 'connected');
    } catch {
      setServerStatus('disconnected');
    }
  }

  async function loadSaves() {
    try {
      const result = await api.listSaves();
      setSaves(result.saves || []);
    } catch (error) {
      console.error('Failed to load saves:', error);
    }
  }

  async function loadMemoryCount() {
    try {
      const data = await api.getMemoryCount();
      setMemoryCount(data.count || 0);
    } catch {
      setMemoryCount(0);
    }
  }

  async function startNewGame() {
    setIsLoading(true);
    try {
      const result = await api.newGame('Hero');
      setGameState(result.game_state);
      setCurrentView('game');
      await loadMemoryCount();
    } catch (error: any) {
      alert('Failed to start game. Make sure the server is running!');
      console.error('Failed to start game:', error);
    } finally {
      setIsLoading(false);
    }
  }

  async function loadGame(saveId: string) {
    setIsLoading(true);
    try {
      const result = await api.loadGame(saveId);
      setGameState(result.game_state);
      setCurrentView('game');
      await loadMemoryCount();
    } catch (error) {
      alert('Failed to load game!');
      console.error('Failed to load game:', error);
    } finally {
      setIsLoading(false);
    }
  }

  async function sendAction() {
    if (!userInput.trim() || isLoading) return;

    setIsLoading(true);
    const input = userInput;
    setUserInput('');

    try {
      const result = await api.sendAction(input);
      setGameState(result.game_state);
      await loadMemoryCount();
    } catch (error) {
      console.error('Failed to send action:', error);
    } finally {
      setIsLoading(false);
    }
  }

  if (currentView === 'menu') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black flex items-center justify-center p-8">
        <div className="max-w-2xl w-full">
          <div className="text-center mb-12">
            <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 mb-4">
              🏰 The Last Voyage
            </h1>
            <p className="text-gray-400 text-lg">A Dark Fantasy Text Adventure</p>
          </div>

          <div className="space-y-4">
            <button
              onClick={startNewGame}
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-8 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" />
                  Starting...
                </>
              ) : (
                '🆕 New Game'
              )}
            </button>

            {saves.length > 0 && (
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
                <h3 className="text-white font-bold mb-3 flex items-center gap-2">
                  <Package />
                  Load Game
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {saves.map((save) => (
                    <button
                      key={save}
                      onClick={() => loadGame(save)}
                      className="w-full text-left bg-gray-700/50 hover:bg-gray-600/50 text-white py-3 px-4 rounded transition-colors"
                    >
                      {save}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="text-center mt-8 space-y-2">
            <div className="text-gray-500 text-sm">
              Powered by Gemini 2.0 Flash • Built with React + Vite
            </div>
            <div
              className={`text-xs ${
                serverStatus === 'disconnected' ? 'text-red-400' : 'text-green-400'
              }`}
            >
              Server: {serverStatus}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentView === 'game' && gameState) {
    return (
      <div className="min-h-screen bg-background text-foreground flex">
        {/* Sidebar */}
        <div className="w-80 bg-card border-r border-border p-6 space-y-6 overflow-y-auto">
          {/* Player Stats */}
          <div className="bg-gradient-to-br from-red-900/30 to-purple-900/30 border border-red-700/50 rounded-lg p-4">
            <h3 className="text-sm font-bold text-muted-foreground mb-3 flex items-center gap-2">
              <Sword />
              PLAYER
            </h3>
            <div className="space-y-2">
              <div>
                <div className="text-xs text-muted-foreground">Name</div>
                <div className="font-bold">{gameState.player_name}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">Health</div>
                <div className="w-full bg-muted rounded-full h-4 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-red-500 to-pink-500 h-full transition-all"
                    style={{ width: `${(gameState.player_hp / gameState.player_max_hp) * 100}%` }}
                  ></div>
                </div>
                <div className="text-xs text-right mt-1">
                  {gameState.player_hp}/{gameState.player_max_hp} HP
                </div>
              </div>
            </div>
          </div>

          {/* Location */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-bold text-muted-foreground mb-2 flex items-center gap-2">
              <MapPin />
              LOCATION
            </h3>
            <div className="font-bold text-primary">{gameState.current_room}</div>
            <p className="text-sm text-muted-foreground mt-2">{gameState.room_description}</p>
          </div>

          {/* Inventory */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-bold text-muted-foreground mb-2 flex items-center gap-2">
              <Package />
              INVENTORY
            </h3>
            {gameState.inventory.length > 0 ? (
              <div className="space-y-1">
                {gameState.inventory.map((item, i) => (
                  <div key={i} className="text-sm bg-muted px-2 py-1 rounded">
                    {item.name}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground italic">Empty</div>
            )}
          </div>

          {/* Entities */}
          {gameState.visible_entities.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-4">
              <h3 className="text-sm font-bold text-muted-foreground mb-2 flex items-center gap-2">
                <Users />
                VISIBLE
              </h3>
              <div className="space-y-1">
                {gameState.visible_entities.map((entity, i) => (
                  <div key={i} className="text-sm bg-muted px-2 py-1 rounded">
                    {entity.name}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Memory System */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-bold text-muted-foreground mb-2 flex items-center gap-2">
              <Brain />
              MEMORY SYSTEM
            </h3>
            <div className="text-sm">
              <div className="text-muted-foreground">Memories stored:</div>
              <div className="font-bold text-primary">{memoryCount}</div>
            </div>
          </div>

          {/* Menu Button */}
          <button
            onClick={() => setCurrentView('menu')}
            className="w-full bg-secondary hover:bg-secondary/80 text-secondary-foreground py-2 rounded transition-colors border border-border"
          >
            ← Back to Menu
          </button>
        </div>

        {/* Main Game Area */}
        <div className="flex-1 flex flex-col">
          {/* Narrative Log */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {gameState.narrative_log.map((entry, i) => (
              <div key={i} className="animate-fade-in">
                {entry.startsWith('🎮') ? (
                  <div className="text-cyan-400 font-mono">{entry}</div>
                ) : entry.startsWith('📖') ? (
                  <div className="text-foreground leading-relaxed ml-4">{entry.substring(2).trim()}</div>
                ) : (
                  <div className="text-muted-foreground">{entry}</div>
                )}
              </div>
            ))}
          </div>

          {/* Input Area */}
          <div className="border-t border-border bg-card p-6">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendAction();
              }}
              className="flex gap-4"
            >
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                disabled={isLoading}
                placeholder={isLoading ? 'AI thinking...' : 'Enter your command...'}
                className="flex-1 bg-background border border-input px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={isLoading || !userInput.trim()}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold px-8 py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isLoading ? (
                  <Loader2 className="animate-spin" />
                ) : (
                  <Send />
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default App;

