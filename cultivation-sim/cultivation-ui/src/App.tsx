import { useState, useEffect } from 'react';
import { api, type GameState, type CharacterData, type HistoryEntry } from './api';
import { ProfileModal, InventoryModal, CodexModal } from './Modals';
import { AdvancedSystemsPanel } from './components/AdvancedSystemsPanel';
import { ShopPanel } from './components/ShopPanel';
import { SkillsPanel } from './components/SkillsPanel';
import { QuestsPanel } from './components/QuestsPanel';
import { AttributesPanel } from './components/AttributesPanel';
import { HistoryPanel } from './components/HistoryPanel';

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
type PanelView = 'shop' | 'skills' | 'quests' | null;

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
  const [panelView, setPanelView] = useState<PanelView>(null);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [previousGameState, setPreviousGameState] = useState<GameState | null>(null);
  const [narrative, setNarrative] = useState<string>('');
  const [choices, setChoices] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [memoryCount, setMemoryCount] = useState(0);
  const [serverStatus, setServerStatus] = useState('checking...');
  const [debugInfo, setDebugInfo] = useState<{
    prompt?: string;
    aiResponse?: string;
    parsedResult?: any;
    error?: string;
  }>({});
  const [showDebug, setShowDebug] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const [characterData, setCharacterData] = useState<CharacterData>({
    gender: 'Nam',
    talent: 'Thiên Linh Căn',
    race: 'Nhân Tộc',
    background: 'Gia Đình Tu Tiên',
    physique_id: undefined,
  });

  useEffect(() => {
    checkServer();
  }, []);

  async function checkServer() {
    try {
      const result = await api.checkHealth();
      if (result.status === 'healthy' || result.status === 'connected') {
        setServerStatus('connected');
      } else {
        setServerStatus(`error: ${(result as any).error || 'unknown'}`);
      }
    } catch (error: any) {
      setServerStatus(`disconnected: ${error.message || 'Cannot reach server'}`);
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
      // First check if server is available
      const health = await api.checkHealth();
      if (health.status !== 'healthy' && health.status !== 'connected') {
        throw new Error(`Server is not ready: ${(health as any).error || 'Unknown error'}`);
      }
      
      const result = await api.newGame('Người Tu Tiên', characterData);
      setGameState(result.game_state);
      setNarrative(result.narrative);
      setChoices(result.choices);
      setCurrentView('game');
      await loadMemoryCount();
    } catch (error: any) {
      const errorMessage = error.message || 'Unknown error';
      alert(`Không thể khởi tạo game!\n\nLỗi: ${errorMessage}\n\nHãy kiểm tra:\n1. Server đang chạy ở port 8001\n2. Xem log file trong thư mục logs/\n3. Kiểm tra console để biết thêm chi tiết`);
      console.error('Game creation error:', error);
    } finally {
      setIsLoading(false);
    }
  }

  async function selectChoice(choiceIndex: number) {
    if (isLoading) return;

    const selectedChoice = choices[choiceIndex];
    console.log(`🎮 Player selected choice ${choiceIndex + 1}: "${selectedChoice}"`);

    setIsLoading(true);
    // Clear old narrative immediately to show loading state
    setNarrative('');
    setChoices([]);
    
    try {
      console.log('📡 Sending action to server...');
      const result = await api.sendAction((choiceIndex + 1).toString());
      
      console.log('✅ Server response received:');
      console.log(`  - Narrative length: ${result.narrative?.length || 0}`);
      console.log(`  - Narrative preview: ${result.narrative?.substring(0, 100)}...`);
      console.log(`  - Choices count: ${result.choices?.length || 0}`);
      console.log(`  - Full response:`, result);
      
      // Update debug info from response
      const responseAny = result as any;
      let currentDebugInfo = debugInfo;
      if (responseAny.debug_info) {
        currentDebugInfo = {
          prompt: responseAny.debug_info.prompt,
          aiResponse: responseAny.debug_info.ai_raw_response || responseAny.debug_info.raw_response,
          parsedResult: responseAny.debug_info.parsed_result,
          error: responseAny.debug_info.error
        };
        setDebugInfo(currentDebugInfo);
        console.log('🔍 Debug info updated:', responseAny.debug_info);
      }
      
      // Only update if we got valid response
      if (result.narrative) {
        console.log('✅ Setting narrative:', result.narrative.substring(0, 100));
        setNarrative(result.narrative);
      } else {
        console.warn('⚠️ No narrative in response!');
      }
      
      if (result.choices && result.choices.length > 0) {
        console.log('✅ Setting choices:', result.choices);
        setChoices(result.choices);
      } else {
        console.warn('⚠️ No choices in response!');
      }
      
      if (result.game_state) {
        // Save previous state for comparison
        setPreviousGameState(gameState);
        setGameState(result.game_state);
        
        // Add to history
        const historyEntry: HistoryEntry = {
          timestamp: new Date().toLocaleString('vi-VN'),
          prompt: currentDebugInfo.prompt,
          response: currentDebugInfo.aiResponse,
          narrative: result.narrative,
          choices: result.choices,
          error: currentDebugInfo.error,
        };
        setHistory((prev) => [...prev, historyEntry].slice(-50)); // Keep last 50 entries
      }
      await loadMemoryCount();
    } catch (error: any) {
      const errorMessage = error.message || 'Unknown error';
      console.error('❌ Failed to process choice:', error);
      console.error('❌ Error details:', error);
      setNarrative(`Lỗi: ${errorMessage}\n\nVui lòng thử lại hoặc kiểm tra server.`);
      alert(`Lỗi xử lý lựa chọn!\n\nLỗi: ${errorMessage}\n\nHãy kiểm tra server và log file.`);
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
  const [saves, setSaves] = useState<any[]>([]);
  const [showSaves, setShowSaves] = useState(false);

  async function loadSavesList() {
    try {
      const result = await api.listSaves();
      setSaves(result.saves || []);
    } catch (error: any) {
      console.error('Failed to load saves:', error);
    }
  }

  async function loadSaveGame(saveId: string) {
    try {
      setIsLoading(true);
      const result = await api.loadSave(saveId);
      setGameState(result.game_state);
      setNarrative(result.narrative);
      setChoices(result.choices);
      setCurrentView('game');
      setShowSaves(false);
    } catch (error: any) {
      alert(`Không thể tải save: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (showSaves) {
      loadSavesList();
    }
  }, [showSaves]);

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
            
            <button
              onClick={() => setShowSaves(true)}
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-blue-600/20 to-indigo-600/20 border-2 border-blue-500 hover:border-blue-400 text-blue-400 hover:text-blue-300 font-bold py-6 px-8 rounded-lg transition-all disabled:opacity-50 flex items-center justify-center gap-3"
            >
              <span>💾</span>
              <span className="text-xl">Tiếp Tục Game</span>
            </button>
          </div>

          {/* Saves List Modal */}
          {showSaves && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <div className="bg-slate-900 border-2 border-amber-500/50 rounded-lg w-full max-w-4xl h-[80vh] flex flex-col">
                <div className="p-4 border-b border-amber-500/30 flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-amber-400">💾 Danh Sách Save</h2>
                  <button
                    onClick={() => setShowSaves(false)}
                    className="px-4 py-2 bg-red-600/20 border border-red-600/50 hover:bg-red-600/30 text-red-400 rounded-lg transition-all"
                  >
                    ✕ Đóng
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto p-4">
                  {saves.length === 0 ? (
                    <div className="text-center text-gray-500 mt-8">
                      <p className="text-lg">Chưa có save nào</p>
                      <p className="text-sm mt-2">Tạo game mới để bắt đầu</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {saves.map((save) => (
                        <div
                          key={save.save_id}
                          className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:border-amber-500/50 transition-all"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h3 className="font-bold text-amber-400 text-lg">{save.character_name}</h3>
                              <p className="text-sm text-gray-400">Tuổi: {save.age}</p>
                            </div>
                            <span className="text-xs text-gray-500">{save.save_id}</span>
                          </div>
                          <div className="text-sm text-gray-300 space-y-1 mb-3">
                            <p>Giới tính: {save.gender}</p>
                            <p>Thiên phú: {save.talent}</p>
                            {save.updated_at && (
                              <p className="text-xs text-gray-500">Cập nhật: {new Date(save.updated_at).toLocaleString('vi-VN')}</p>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => loadSaveGame(save.save_id)}
                              className="flex-1 px-4 py-2 bg-blue-600/20 border border-blue-600/50 hover:bg-blue-600/30 text-blue-400 rounded-lg transition-all text-sm font-semibold"
                            >
                              ⚡ Tiếp Tục
                            </button>
                            <button
                              onClick={async () => {
                                if (confirm(`Xóa save "${save.character_name}"?`)) {
                                  try {
                                    await api.deleteSave(save.save_id);
                                    await loadSavesList();
                                  } catch (error: any) {
                                    alert(`Không thể xóa: ${error.message}`);
                                  }
                                }
                              }}
                              className="px-4 py-2 bg-red-600/20 border border-red-600/50 hover:bg-red-600/30 text-red-400 rounded-lg transition-all text-sm"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="text-center mt-12 space-y-3">
            <div className="text-gray-500 text-sm">
              Hỗ trợ bởi Gemini 2.0 Flash • Phát triển với React + Vite
            </div>
            <div className={`text-xs ${serverStatus.includes('disconnected') || serverStatus.includes('error') ? 'text-red-400' : 'text-emerald-400'}`}>
              Máy chủ: {serverStatus.includes('disconnected') || serverStatus.includes('error') ? `Mất kết nối (${serverStatus})` : 'Đã kết nối'}
            </div>
            <button
              onClick={checkServer}
              className="text-xs text-blue-400 hover:text-blue-300 underline mt-1"
            >
              Kiểm tra lại server
            </button>
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
              <div className="grid grid-cols-2 gap-3 max-h-64 overflow-y-auto p-2">
                {[
                  { name: 'Thiên Linh Căn', emoji: '⭐', desc: 'Thiên phú trời ban, hấp thu linh khí tự nhiên' },
                  { name: 'Nghiêng Nước Nghiêng Thành', emoji: '💋', desc: 'Dung nhan tuyệt thế, dễ được yêu mến' },
                  { name: 'Thiên Văn Chi Tử', emoji: '🔮', desc: 'Nhìn thấy vận mệnh trong các vì sao' },
                  { name: 'Vạn Thú Chi Tử', emoji: '🐺', desc: 'Giao tiếp với muôn thú, được linh thú yêu mến' },
                  { name: 'Dược Thiên Chi Tử', emoji: '🌿', desc: 'Cảm nhận và phân biệt dược thảo quý hiếm' },
                  { name: 'Khí Vận Chi Tử', emoji: '🌀', desc: 'Cảm nhận khí vận, tránh nguy hiểm' },
                  { name: 'Âm Dương Nhị Chi Tử', emoji: '☯️', desc: 'Điều hòa âm dương, chữa trị' },
                  { name: 'Hoa Nguyệt Chi Tử', emoji: '🎨', desc: 'Tài năng nghệ thuật, tạo vẻ đẹp' },
                  { name: 'Thiên Nhân Chi Tử', emoji: '💝', desc: 'Cảm nhận cảm xúc, an ủi người khác' },
                  { name: 'Vô Ngôn Chi Tử', emoji: '🤐', desc: 'Giao tiếp không lời, hiểu ý nghĩ' },
                  { name: 'Hỗn Độn Thể', emoji: '💫', desc: 'Hấp thu mọi loại linh khí' },
                  { name: 'Phàm Thể', emoji: '✨', desc: 'Bình thường nhưng ý chí kiên định' }
                ].map((t) => (
                  <button
                    key={t.name}
                    onClick={() => setCharacterData({ ...characterData, talent: t.name })}
                    className={`py-3 px-4 rounded-lg font-semibold transition-all text-sm border-2 text-left ${characterData.talent === t.name
                      ? 'bg-purple-600/30 border-purple-500 text-purple-300 glow-spiritual'
                      : 'bg-slate-800/50 border-slate-700 text-gray-400 hover:border-purple-700'
                      }`}
                    title={t.desc}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{t.emoji}</span>
                      <span className="font-bold">{t.name}</span>
                    </div>
                    <div className="text-xs text-gray-400 italic">{t.desc}</div>
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
                onClick={async () => {
                  // Check server first
                  await checkServer();
                  if (serverStatus.includes('disconnected') || serverStatus.includes('error')) {
                    alert(`Server không sẵn sàng!\n\nTrạng thái: ${serverStatus}\n\nVui lòng:\n1. Kiểm tra server đang chạy ở port 8001\n2. Xem cửa sổ "Cultivation Simulator Server"\n3. Kiểm tra log file trong thư mục logs/`);
                    return;
                  }
                  await startNewGame();
                }}
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
      <div className="min-h-screen flex spiritual-particles">
        {/* Attributes Panel - Left Side */}
        <AttributesPanel
          attributes={gameState.attributes || undefined}
          previousAttributes={previousGameState?.attributes || undefined}
          gameState={gameState}
        />
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
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
                onClick={() => setPanelView('shop')}
                className="px-4 py-2 bg-purple-600/20 border border-purple-600/50 hover:bg-purple-600/30 text-purple-400 rounded-lg transition-all flex items-center gap-2"
              >
                <span>🛒</span>
                <span className="text-sm font-semibold">Cửa Hàng</span>
              </button>
              <button
                onClick={() => setPanelView('skills')}
                className="px-4 py-2 bg-blue-600/20 border border-blue-600/50 hover:bg-blue-600/30 text-blue-400 rounded-lg transition-all flex items-center gap-2"
              >
                <span>⚔️</span>
                <span className="text-sm font-semibold">Kỹ Năng</span>
              </button>
              <button
                onClick={() => setPanelView('quests')}
                className="px-4 py-2 bg-green-600/20 border border-green-600/50 hover:bg-green-600/30 text-green-400 rounded-lg transition-all flex items-center gap-2"
              >
                <span>📜</span>
                <span className="text-sm font-semibold">Nhiệm Vụ</span>
              </button>
              <button
                onClick={() => setShowHistory(true)}
                className="px-4 py-2 bg-purple-600/20 border border-purple-600/50 hover:bg-purple-600/30 text-purple-400 rounded-lg transition-all flex items-center gap-2"
              >
                <span>📚</span>
                <span className="text-sm font-semibold">Lịch Sử</span>
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
            {/* Debug Panel */}
            <div className="mb-4">
              <button
                onClick={() => setShowDebug(!showDebug)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-bold"
              >
                {showDebug ? '🔽 Ẩn Debug' : '🔺 Hiện Debug Info'}
              </button>
            </div>
            
            {showDebug && (
              <div className="bg-gray-900/90 backdrop-blur-xl border-2 border-yellow-500/30 rounded-2xl p-6 mb-8 text-xs font-mono">
                <h3 className="text-yellow-400 font-bold mb-4 text-lg">🔍 DEBUG INFO</h3>
                
                {debugInfo.error && (
                  <div className="mb-4 p-3 bg-red-900/30 border border-red-500 rounded">
                    <div className="text-red-400 font-bold mb-2">❌ ERROR:</div>
                    <pre className="text-red-300 whitespace-pre-wrap break-words max-h-40 overflow-y-auto">{debugInfo.error}</pre>
                  </div>
                )}
                
                {debugInfo.prompt && (
                  <div className="mb-4">
                    <div className="text-blue-400 font-bold mb-2">📤 PROMPT GỬI CHO AI ({debugInfo.prompt.length} ký tự):</div>
                    <pre className="text-gray-300 whitespace-pre-wrap break-words bg-gray-800 p-3 rounded max-h-60 overflow-y-auto">
                      {debugInfo.prompt}
                    </pre>
                  </div>
                )}
                
                {debugInfo.aiResponse && (
                  <div className="mb-4">
                    <div className="text-green-400 font-bold mb-2">🤖 AI RAW RESPONSE ({debugInfo.aiResponse.length} ký tự):</div>
                    <pre className="text-gray-300 whitespace-pre-wrap break-words bg-gray-800 p-3 rounded max-h-60 overflow-y-auto">
                      {debugInfo.aiResponse}
                    </pre>
                  </div>
                )}
                
                {debugInfo.parsedResult && (
                  <div className="mb-4">
                    <div className="text-purple-400 font-bold mb-2">✅ PARSED RESULT:</div>
                    <pre className="text-gray-300 whitespace-pre-wrap break-words bg-gray-800 p-3 rounded max-h-60 overflow-y-auto">
                      {JSON.stringify(debugInfo.parsedResult, null, 2)}
                    </pre>
                  </div>
                )}
                
                {!debugInfo.prompt && !debugInfo.aiResponse && !debugInfo.error && (
                  <div className="text-gray-400 italic">Chưa có debug info. Chọn một lựa chọn để xem.</div>
                )}
              </div>
            )}

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
                {isLoading ? 'AI ĐANG SUY NGHĨ...' : `NĂM THỨ ${gameState.age}`}
              </h2>
              {isLoading && !narrative ? (
                <div className="text-gray-300 leading-relaxed text-lg min-h-[60px] flex items-center justify-center gap-3" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                  <Loader2 className="animate-spin text-2xl text-amber-400" />
                  <span className="text-amber-400 text-xl">AI đang suy nghĩ và tạo câu chuyện...</span>
                </div>
              ) : narrative ? (
                <p className="text-gray-200 leading-relaxed text-lg min-h-[60px]" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                  <Typewriter text={narrative} />
                </p>
              ) : (
                <p className="text-gray-400 leading-relaxed text-lg min-h-[60px] italic" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                  Đang chờ câu chuyện...
                </p>
              )}
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
                {isLoading && choices.length === 0 && (
                  <div className="text-center mt-6 text-amber-400 flex items-center justify-center gap-3 text-lg">
                    <Loader2 className="animate-spin text-2xl" />
                    <span style={{ fontFamily: "'Noto Serif SC', serif" }}>AI đang tạo lựa chọn mới...</span>
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

        {/* Panel Overlays */}
        {panelView === 'shop' && (
          <ShopPanel onClose={() => setPanelView(null)} />
        )}
        {panelView === 'skills' && (
          <SkillsPanel onClose={() => setPanelView(null)} />
        )}
        {panelView === 'quests' && (
          <QuestsPanel onClose={() => setPanelView(null)} />
        )}
        
        {/* History Panel */}
        {showHistory && (
          <HistoryPanel history={history} onClose={() => setShowHistory(false)} />
        )}
        </div>
      </div>
    );
  }

  return null;
}

export default App;
