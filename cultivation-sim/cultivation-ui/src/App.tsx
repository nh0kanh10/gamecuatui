import { useState, useEffect } from 'react';
import { api, type GameState, type CharacterData } from './api';
import { ProfileModal, InventoryModal, CodexModal } from './Modals';

// Emoji icons
const Sparkles = () => <span className="text-2xl">✨</span>;
const User = () => <span className="text-lg">👤</span>;
const Calendar = () => <span className="text-lg">📅</span>;
const Loader2 = ({ className }: { className?: string }) => <span className={className}>⏳</span>;
const Flame = () => <span className="text-lg">🔥</span>;
const Book = () => <span className="text-lg">📖</span>;
const Backpack = () => <span className="text-lg">🎒</span>;
const MapPin = () => <span className="text-lg">📍</span>;

type View = 'menu' | 'character-creation' | 'game';
type ModalView = 'profile' | 'inventory' | 'codex' | null;

const Typewriter = ({ text, speed = 10 }: { text: string; speed?: number }) => {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    setDisplayedText('');
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayedText((prev) => prev + text.charAt(i));
        i++;
      } else {
        clearInterval(timer);
      }
    }, speed);
    return () => clearInterval(timer);
  }, [text, speed]);

  return <span className="whitespace-pre-wrap">{displayedText}</span>;
};

function App() {
  const [currentView, setCurrentView] = useState<View>('menu');
  const [modalView, setModalView] = useState<ModalView>(null);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [narrative, setNarrative] = useState<string>('');
  const [choices, setChoices] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [memoryCount, setMemoryCount] = useState(0);
  const [serverStatus, setServerStatus] = useState('checking...');

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
      alert('Không thể kết nối server! Hãy chắc server đang chạy ở port 8001.');
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
      alert('Lỗi xử lý lựa chọn!');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAdvancedAction(action: string, data?: any) {
    try {
      // Handle different advanced system actions
      switch (action) {
        case 'cast_skill':
          // Call skill cast API
          console.log('Cast skill:', data);
          break;
        case 'start_combat':
          // Call combat start API
          console.log('Start combat:', data);
          break;
        case 'attempt_breakthrough':
          // Call breakthrough API
          console.log('Attempt breakthrough:', data);
          break;
        case 'accept_quest':
          // Call accept quest API
          console.log('Accept quest:', data);
          break;
        case 'complete_quest':
          // Call complete quest API
          console.log('Complete quest:', data);
          break;
        default:
          console.log('Unknown action:', action, data);
      }
      
      // Refresh game state after action
      if (gameState) {
        const newState = await api.getState();
        setGameState(newState);
      }
    } catch (error) {
      console.error('Error handling advanced action:', error);
    }
  }

  // Menu View
  if (currentView === 'menu') {
    return (
      <div className="min-h-screen flex items-center justify-center p-8 spiritual-particles">
        <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] opacity-5 pointer-events-none z-0 animate-spin-slow">
          <img src="/spiritual_energy_vortex_1764712168595.png" alt="" className="w-full h-full object-contain blur-md" />
        </div>

        <div className="max-w-2xl w-full animate-fade-in relative z-10">
          <div className="text-center mb-12">
            <h1 className="text-7xl font-black mb-4 glow-text animate-float"
              style={{ fontFamily: "'Cinzel', serif" }}>
              <span className="bg-gradient-to-r from-yellow-400 via-amber-500 to-orange-600 bg-clip-text text-transparent">
                修仙模拟器
              </span>
            </h1>
            <h2 className="text-3xl font-bold text-amber-400 mb-2" style={{ fontFamily: "'Noto Serif SC', serif" }}>
              Tu Tiên Simulator
            </h2>
            <p className="text-gray-400 text-lg italic">Con đường bất tử</p>

            <div className="flex justify-center gap-4 mt-6">
              <span className="text-4xl opacity-50">✦</span>
              <span className="text-4xl opacity-70 animate-float">⬡</span>
              <span className="text-4xl opacity-50">✦</span>
            </div>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => setCurrentView('character-creation')}
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-amber-600/20 to-orange-600/20 border-2 border-amber-500 hover:border-amber-400 text-amber-400 hover:text-amber-300 font-bold py-6 px-8 rounded-lg transition-all disabled:opacity-50 glow-gold flex items-center justify-center gap-3 group"
            >
              <Sparkles />
              <span className="text-2xl" style={{ fontFamily: "'Noto Serif SC', serif" }}>開始修煉</span>
              {' '}
              <span className="text-xl">Bắt Đầu Tu Luyện</span>
            </button>
          </div>

          <div className="text-center mt-12 space-y-3">
            <div className="text-gray-500 text-sm">
              Hỗ trợ bởi Gemini 2.0 Flash • Phát triển với React + Vite
            </div>
            <div className={`text-xs ${serverStatus === 'disconnected' ? 'text-red-400' : 'text-emerald-400'}`}>
              Máy chủ: {serverStatus === 'disconnected' ? 'Mất kết nối' : 'Đã kết nối'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Character Creation View
  if (currentView === 'character-creation') {
    return (
      <div className="min-h-screen flex items-center justify-center p-8 spiritual-particles">
        <div className="max-w-3xl w-full animate-fade-in">
          <div className="text-center mb-8">
            <h2 className="text-5xl font-black glow-text mb-3" style={{ fontFamily: "'Cinzel', serif" }}>
              <span className="bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
                Tạo Nhân Vật
              </span>
            </h2>
            <p className="text-gray-400 text-lg" style={{ fontFamily: "'Noto Serif SC', serif" }}>
              选择你的修仙之路
            </p>
          </div>

          <div className="bg-slate-900/50 backdrop-blur-xl border-2 border-amber-500/30 rounded-2xl p-8 space-y-6 glow-gold">
            {/* Gender */}
            <div>
              <label className="text-amber-400 font-bold mb-3 block text-lg" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                性別 / Giới Tính
              </label>
              <div className="grid grid-cols-2 gap-3">
                {['Nam', 'Nữ'].map((g) => (
                  <button
                    key={g}
                    onClick={() => setCharacterData({ ...characterData, gender: g })}
                    className={`py-3 px-4 rounded-lg font-bold transition-all border-2 ${characterData.gender === g
                      ? 'bg-amber-600/30 border-amber-500 text-amber-300 glow-gold'
                      : 'bg-slate-800/50 border-slate-700 text-gray-400 hover:border-amber-700'
                      }`}
                  >
                    {g}
                  </button>
                ))}
              </div>
            </div>

            {/* Talent */}
            <div>
              <label className="text-amber-400 font-bold mb-3 block text-lg" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                天賦 / Thiên Phú
              </label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { name: 'Thiên Linh Căn', emoji: '⭐' },
                  { name: 'Địa Linh Căn', emoji: '🌟' },
                  { name: 'Hỗn Độn Thể', emoji: '💫' },
                  { name: 'Phàm Thể', emoji: '✨' }
                ].map((t) => (
                  <button
                    key={t.name}
                    onClick={() => setCharacterData({ ...characterData, talent: t.name })}
                    className={`py-3 px-4 rounded-lg font-semibold transition-all text-sm border-2 ${characterData.talent === t.name
                      ? 'bg-purple-600/30 border-purple-500 text-purple-300 glow-spiritual'
                      : 'bg-slate-800/50 border-slate-700 text-gray-400 hover:border-purple-700'
                      }`}
                  >
                    <span className="mr-2">{t.emoji}</span>
                    {t.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Race */}
            <div>
              <label className="text-amber-400 font-bold mb-3 block text-lg" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                種族 / Chủng Tộc
              </label>
              <div className="grid grid-cols-2 gap-3">
                {['Nhân Tộc', 'Yêu Tộc', 'Ma Tộc', 'Tiên Tộc'].map((r) => (
                  <button
                    key={r}
                    onClick={() => setCharacterData({ ...characterData, race: r })}
                    className={`py-3 px-4 rounded-lg font-semibold transition-all text-sm border-2 ${characterData.race === r
                      ? 'bg-emerald-600/30 border-emerald-500 text-emerald-300 glow-jade'
                      : 'bg-slate-800/50 border-slate-700 text-gray-400 hover:border-emerald-700'
                      }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>

            {/* Background */}
            <div>
              <label className="text-amber-400 font-bold mb-3 block text-lg" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                出身 / Bối Cảnh
              </label>
              <div className="grid grid-cols-2 gap-3">
                {['Gia Đình Tu Tiên', 'Gia Đình Phàm Nhân', 'Mồ Côi', 'Tông Môn Đệ Tử'].map((b) => (
                  <button
                    key={b}
                    onClick={() => setCharacterData({ ...characterData, background: b })}
                    className={`py-3 px-4 rounded-lg font-semibold transition-all text-sm border-2 ${characterData.background === b
                      ? 'bg-amber-600/30 border-amber-500 text-amber-300 glow-gold'
                      : 'bg-slate-800/50 border-slate-700 text-gray-400 hover:border-amber-700'
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
                className="flex-1 bg-slate-800/70 border-2 border-slate-600 hover:border-slate-500 text-gray-300 py-4 rounded-lg transition-all font-bold"
              >
                ← Quay Lại
              </button>
              <button
                onClick={startNewGame}
                disabled={isLoading}
                className="flex-2 bg-gradient-to-r from-amber-600/30 to-orange-600/30 border-2 border-amber-500 hover:border-amber-400 text-amber-300 font-bold py-4 px-6 rounded-lg transition-all disabled:opacity-50 flex items-center justify-center gap-3 glow-gold"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin" />
                    Đang khởi tạo...
                  </>
                ) : (
                  <>
                    <Sparkles />
                    <span style={{ fontFamily: "'Noto Serif SC', serif" }}>開始</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Game View with Modal System
  if (currentView === 'game' && gameState) {
    return (
      <div className="min-h-screen flex flex-col spiritual-particles">
        {/* Top Bar - Quick Stats */}
        <div className="bg-slate-900/90 backdrop-blur-xl border-b-2 border-amber-500/30 p-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            {/* Character Quick Info */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <User />
                <div>
                  <div className="text-xs text-gray-500">Nhân Vật</div>
                  <div className="font-bold text-amber-400">{gameState.character_name}</div>
                </div>
              </div>
              <div className="h-8 w-px bg-gray-700"></div>
              <div className="flex items-center gap-2">
                <Calendar />
                <div>
                  <div className="text-xs text-gray-500">Tuổi</div>
                  <div className="font-bold text-white">{gameState.age} tuổi</div>
                </div>
              </div>
              {gameState.location && (
                <>
                  <div className="h-8 w-px bg-gray-700"></div>
                  <div className="flex items-center gap-2">
                    <MapPin />
                    <div>
                      <div className="text-xs text-gray-500">Vị Trí</div>
                      <div className="font-bold text-emerald-400">{gameState.location.name}</div>
                    </div>
                  </div>
                </>
              )}
              {gameState.cultivation && (
                <>
                  <div className="h-8 w-px bg-gray-700"></div>
                  <div className="flex items-center gap-2">
                    <Flame />
                    <div>
                      <div className="text-xs text-gray-500">Cảnh Giới</div>
                      <div className="font-bold text-purple-400">{gameState.cultivation.realm}</div>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => setModalView('profile')}
                className="px-4 py-2 bg-amber-600/20 border border-amber-600/50 hover:bg-amber-600/30 text-amber-400 rounded-lg transition-all flex items-center gap-2"
              >
                <User />
                <span className="text-sm font-semibold">Cá Nhân</span>
              </button>
              <button
                onClick={() => setModalView('inventory')}
                className="px-4 py-2 bg-emerald-600/20 border border-emerald-600/50 hover:bg-emerald-600/30 text-emerald-400 rounded-lg transition-all flex items-center gap-2"
              >
                <Backpack />
                <span className="text-sm font-semibold">Balo</span>
              </button>
              <button
                onClick={() => setModalView('codex')}
                className="px-4 py-2 bg-indigo-600/20 border border-indigo-600/50 hover:bg-indigo-600/30 text-indigo-400 rounded-lg transition-all flex items-center gap-2"
              >
                <Book />
                <span className="text-sm font-semibold">Codex</span>
              </button>
              <div className="h-8 w-px bg-gray-700 mx-2"></div>
              <button
                onClick={() => setCurrentView('menu')}
                className="px-4 py-2 bg-slate-800/70 border border-slate-600 hover:border-slate-500 text-gray-300 rounded-lg transition-all"
              >
                Menu
              </button>
            </div>
          </div>
        </div>

        {/* Main Game Area */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-5xl mx-auto space-y-8">
            {/* Advanced Systems Panel */}
            {gameState && (
              <AdvancedSystemsPanel 
                gameState={gameState} 
                onAction={handleAdvancedAction}
              />
            )}
            
            {/* Current Narrative */}
            <div className="bg-slate-900/70 backdrop-blur-xl border-2 border-amber-500/30 rounded-2xl p-8 glow-gold">
              <h2 className="text-sm font-bold text-amber-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                <Calendar />
                NĂM THỨ {gameState.age}
              </h2>
              <p className="text-gray-200 leading-relaxed text-lg min-h-[60px]" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                <Typewriter text={narrative} />
              </p>
            </div>

            {/* Choices */}
            {choices.length > 0 && (
              <div className="bg-slate-900/50 backdrop-blur-xl border-2 border-amber-500/40 rounded-2xl p-8">
                <h3 className="text-xl font-bold text-amber-400 mb-6 text-center glow-text" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                  選擇你的道路 / Chọn Đường Của Bạn
                </h3>
                <div className="space-y-3">
                  {choices.map((choice, idx) => (
                    <button
                      key={idx}
                      onClick={() => selectChoice(idx)}
                      disabled={isLoading}
                      className="choice-box w-full text-left disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span className="text-amber-400 font-bold text-lg mr-3">{idx + 1}.</span>
                      <span className="text-gray-200 text-base">{choice}</span>
                    </button>
                  ))}
                </div>
                {isLoading && (
                  <div className="text-center mt-6 text-amber-400 flex items-center justify-center gap-3 text-lg">
                    <Loader2 className="animate-spin text-2xl" />
                    <span style={{ fontFamily: "'Noto Serif SC', serif" }}>AI đang suy nghĩ...</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Modal Overlays */}
        {modalView === 'profile' && (
          <ProfileModal
            gameState={gameState}
            memoryCount={memoryCount}
            onClose={() => setModalView(null)}
          />
        )}
        {modalView === 'inventory' && (
          <InventoryModal
            gameState={gameState}
            onClose={() => setModalView(null)}
          />
        )}
        {modalView === 'codex' && (
          <CodexModal
            gameState={gameState}
            memoryCount={memoryCount}
            onClose={() => setModalView(null)}
          />
        )}
      </div>
    );
  }

  return null;
}

export default App;
