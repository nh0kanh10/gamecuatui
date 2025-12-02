import { useState, useEffect } from 'react';
import { api, type GameState, type CharacterData } from './api';

// Simple emoji icons
const Sparkles = () => <span>✨</span>;
const User = () => <span>👤</span>;
const Calendar = () => <span>📅</span>;
const Brain = () => <span>🧠</span>;
const Send = () => <span>➤</span>;
const Loader2 = ({ className }: { className?: string }) => <span className={className}>⏳</span>;
const Flame = () => <span>🔥</span>;
const Gem = () => <span>💎</span>;
const Pill = () => <span>💊</span>;
const Star = () => <span>⭐</span>;

type View = 'menu' | 'character-creation' | 'game';

function App() {
  const [currentView, setCurrentView] = useState<View>('menu');
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [narrative, setNarrative] = useState<string>('');
  const [choices, setChoices] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [memoryCount, setMemoryCount] = useState(0);
  const [serverStatus, setServerStatus] = useState('checking...');

  // Character creation state
  const [characterData, setCharacterData] = useState<CharacterData>({
    gender: 'Nam',
    talent: 'Thiên Linh Căn',
    race: 'Nhân Tộc',
    background: 'Gia Đình Tu Tiên',
  });

  useEffect(() => {
    checkServer();
  }, []);

  async function checkServer() {
    try {
      const result = await api.checkHealth();
      setServerStatus(result.status || 'connected');
    } catch {
      setServerStatus('disconnected');
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
      const result = await api.newGame('Người Tu Tiên', characterData);
      setGameState(result.game_state);
      setNarrative(result.narrative);
      setChoices(result.choices);
      setCurrentView('game');
      await loadMemoryCount();
    } catch (error) {
      alert('Failed to start game. Make sure the server is running on port 8001!');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }

  async function selectChoice(choiceIndex: number) {
    if (isLoading) return;

    setIsLoading(true);
    try {
      const result = await api.sendAction((choiceIndex + 1).toString());
      setNarrative(result.narrative);
      setChoices(result.choices);
      setGameState(result.game_state);
      await loadMemoryCount();
    } catch (error) {
      console.error('Failed to process choice:', error);
      alert('Failed to process choice!');
    } finally {
      setIsLoading(false);
    }
  }

  // Menu View
  if (currentView === 'menu') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-900 via-red-900 to-black flex items-center justify-center p-8">
        <div className="max-w-2xl w-full">
          <div className="text-center mb-12">
            <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-red-600 mb-4">
              🌟 Tu Tiên Simulator
            </h1>
            <p className="text-gray-300 text-lg">Cultivation Life Simulation</p>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => setCurrentView('character-creation')}
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-amber-600 to-red-600 hover:from-amber-700 hover:to-red-700 text-white font-bold py-4 px-8 rounded-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Sparkles /> New Game
            </button>
          </div>

          <div className="text-center mt-8 space-y-2">
            <div className="text-gray-500 text-sm">
              Powered by Gemini 2.0 Flash • Built with React + Vite
            </div>
            <div className={`text-xs ${serverStatus === 'disconnected' ? 'text-red-400' : 'text-green-400'}`}>
              Server: {serverStatus}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Character Creation View
  if (currentView === 'character-creation') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-900 via-red-900 to-black flex items-center justify-center p-8">
        <div className="max-w-2xl w-full">
          <div className="text-center mb-8">
            <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-red-600 mb-2">
              Tạo Nhân Vật
            </h2>
            <p className="text-gray-400">Choose your cultivation path</p>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 space-y-6">
            {/* Gender */}
            <div>
              <label className="text-white font-bold mb-2 block">Giới Tính</label>
              <div className="grid grid-cols-2 gap-2">
                {['Nam', 'Nữ'].map((g) => (
                  <button
                    key={g}
                    onClick={() => setCharacterData({ ...characterData, gender: g })}
                    className={`py-2 px-4 rounded transition-colors ${characterData.gender === g
                        ? 'bg-amber-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                  >
                    {g}
                  </button>
                ))}
              </div>
            </div>

            {/* Talent */}
            <div>
              <label className="text-white font-bold mb-2 block">Thiên Phú</label>
              <div className="grid grid-cols-2 gap-2">
                {['Thiên Linh Căn', 'Địa Linh Căn', 'Hỗn Độn Thể', 'Phàm Thể'].map((t) => (
                  <button
                    key={t}
                    onClick={() => setCharacterData({ ...characterData, talent: t })}
                    className={`py-2 px-4 rounded transition-colors text-sm ${characterData.talent === t
                        ? 'bg-amber-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {/* Race */}
            <div>
              <label className="text-white font-bold mb-2 block">Chủng Tộc</label>
              <div className="grid grid-cols-2 gap-2">
                {['Nhân Tộc', 'Yêu Tộc', 'Ma Tộc', 'Tiên Tộc'].map((r) => (
                  <button
                    key={r}
                    onClick={() => setCharacterData({ ...characterData, race: r })}
                    className={`py-2 px-4 rounded transition-colors text-sm ${characterData.race === r
                        ? 'bg-amber-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            {/* Background */}
            <div>
              <label className="text-white font-bold mb-2 block">Bối Cảnh</label>
              <div className="grid grid-cols-2 gap-2">
                {['Gia Đình Tu Tiên', 'Gia Đình Phàm Nhân', 'Mồ Côi', 'Tông Môn Đệ Tử'].map((b) => (
                  <button
                    key={b}
                    onClick={() => setCharacterData({ ...characterData, background: b })}
                    className={`py-2 px-4 rounded transition-colors text-sm ${characterData.background === b
                        ? 'bg-amber-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                  >
                    {b}
                  </button>
                ))}
              </div>
            </div>

            {/* Buttons */}
            <div className="flex gap-4 pt-4">
              <button
                onClick={() => setCurrentView('menu')}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-3 rounded-lg transition-colors"
              >
                ← Back
              </button>
              <button
                onClick={startNewGame}
                disabled={isLoading}
                className="flex-1 bg-gradient-to-r from-amber-600 to-red-600 hover:from-amber-700 hover:to-red-700 text-white font-bold py-3 rounded-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Sparkles /> Begin Journey
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Game View
  if (currentView === 'game' && gameState) {
    return (
      <div className="min-h-screen bg-background text-foreground flex">
        {/* Sidebar */}
        <div className="w-80 bg-card border-r border-border p-6 space-y-6 overflow-y-auto">
          {/* Character Info */}
          <div className="bg-gradient-to-br from-amber-900/30 to-red-900/30 border border-amber-700/50 rounded-lg p-4">
            <h3 className="text-sm font-bold text-muted-foreground mb-3 flex items-center gap-2">
              <User />
              CHARACTER
            </h3>
            <div className="space-y-2">
              <div>
                <div className="text-xs text-muted-foreground">Name</div>
                <div className="font-bold text-amber-400">{gameState.character_name}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Age</div>
                <div className="font-bold">{gameState.age} tuổi</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Gender</div>
                <div className="text-sm">{gameState.gender}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Talent</div>
                <div className="text-sm text-amber-400">{gameState.talent}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Race</div>
                <div className="text-sm">{gameState.race}</div>
              </div>
            </div>
          </div>

          {/* Cultivation Stats */}
          {gameState.cultivation && (
            <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 border border-purple-700/50 rounded-lg p-4 space-y-4">
              <h3 className="text-sm font-bold text-muted-foreground mb-3 flex items-center gap-2">
                <Flame />
                CULTIVATION
              </h3>
              
              {/* Realm */}
              <div>
                <div className="text-xs text-muted-foreground mb-1">Realm</div>
                <div className="font-bold text-purple-400 text-lg">{gameState.cultivation.realm}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Level {gameState.cultivation.realm_level}/10
                </div>
              </div>

              {/* Spiritual Power */}
              <div>
                <div className="text-xs text-muted-foreground mb-1 flex justify-between">
                  <span>Spiritual Power</span>
                  <span className="text-purple-400">
                    {gameState.cultivation.spiritual_power}/{gameState.cultivation.max_spiritual_power}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-blue-500 h-full transition-all duration-300"
                    style={{
                      width: `${(gameState.cultivation.spiritual_power / gameState.cultivation.max_spiritual_power) * 100}%`,
                    }}
                  />
                </div>
              </div>

              {/* Breakthrough Progress */}
              <div>
                <div className="text-xs text-muted-foreground mb-1 flex justify-between">
                  <span>Breakthrough</span>
                  <span className="text-amber-400">
                    {gameState.cultivation.breakthrough_progress.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-amber-500 to-orange-500 h-full transition-all duration-300"
                    style={{
                      width: `${gameState.cultivation.breakthrough_progress}%`,
                    }}
                  />
                </div>
              </div>

              {/* Techniques */}
              {gameState.cultivation.techniques && gameState.cultivation.techniques.length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Techniques</div>
                  <div className="flex flex-wrap gap-1">
                    {gameState.cultivation.techniques.map((tech, idx) => (
                      <span
                        key={idx}
                        className="text-xs bg-purple-900/50 text-purple-300 px-2 py-1 rounded"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Cultivation Age */}
              <div className="text-xs text-muted-foreground">
                Cultivating for {gameState.cultivation.cultivation_age} years
              </div>
            </div>
          )}

          {/* Resources */}
          {gameState.resources && (
            <div className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border border-emerald-700/50 rounded-lg p-4 space-y-3">
              <h3 className="text-sm font-bold text-muted-foreground mb-3 flex items-center gap-2">
                <Gem />
                RESOURCES
              </h3>

              {/* Spirit Stones */}
              <div className="flex items-center justify-between">
                <div className="text-xs text-muted-foreground flex items-center gap-1">
                  <Gem />
                  Spirit Stones
                </div>
                <div className="font-bold text-emerald-400">{gameState.resources.spirit_stones}</div>
              </div>

              {/* Pills */}
              {gameState.resources.pills && Object.keys(gameState.resources.pills).length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                    <Pill />
                    Pills
                  </div>
                  <div className="space-y-1">
                    {Object.entries(gameState.resources.pills).map(([name, qty]) => (
                      <div key={name} className="flex justify-between text-xs">
                        <span className="text-foreground truncate">{name}</span>
                        <span className="text-emerald-400 font-bold ml-2">x{qty}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Materials */}
              {gameState.resources.materials && Object.keys(gameState.resources.materials).length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-2">Materials</div>
                  <div className="space-y-1">
                    {Object.entries(gameState.resources.materials).map(([name, qty]) => (
                      <div key={name} className="flex justify-between text-xs">
                        <span className="text-foreground truncate">{name}</span>
                        <span className="text-teal-400 font-bold ml-2">x{qty}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Memory */}
          <div className="bg-card border border-border rounded-lg p-4">
            <h3 className="text-sm font-bold text-muted-foreground mb-2 flex items-center gap-2">
              <Brain />
              MEMORIES
            </h3>
            <div className="text-sm">
              <div className="text-muted-foreground">Stored:</div>
              <div className="font-bold text-primary">{memoryCount}</div>
            </div>
          </div>

          {/* Back Button */}
          <button
            onClick={() => setCurrentView('menu')}
            className="w-full bg-secondary hover:bg-secondary/80 text-secondary-foreground py-2 rounded transition-colors border border-border"
          >
            ← Back to Menu
          </button>
        </div>

        {/* Main Game Area */}
        <div className="flex-1 flex flex-col">
          {/* Narrative Area */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Current Narrative */}
              <div className="bg-card border border-border rounded-lg p-6">
                <h2 className="text-sm font-bold text-muted-foreground mb-4 flex items-center gap-2">
                  <Calendar />
                  YEAR {gameState.age}
                </h2>
                <p className="text-foreground leading-relaxed whitespace-pre-wrap">{narrative}</p>
              </div>

              {/* Choices */}
              {choices.length > 0 && (
                <div className="bg-card border border-amber-700/30 rounded-lg p-6">
                  <h3 className="text-sm font-bold text-amber-400 mb-4">What will you do?</h3>
                  <div className="space-y-2">
                    {choices.map((choice, idx) => (
                      <button
                        key={idx}
                        onClick={() => selectChoice(idx)}
                        disabled={isLoading}
                        className="w-full text-left bg-gray-800/50 hover:bg-amber-900/30 border border-gray-700 hover:border-amber-600 text-white py-3 px-4 rounded transition-all disabled:opacity-50 group"
                      >
                        <span className="text-amber-400 font-bold mr-2">{idx + 1}.</span>
                        <span className="group-hover:text-amber-300">{choice}</span>
                      </button>
                    ))}
                  </div>
                  {isLoading && (
                    <div className="text-center mt-4 text-amber-400 flex items-center justify-center gap-2">
                      <Loader2 className="animate-spin" />
                      AI đang suy nghĩ...
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default App;
