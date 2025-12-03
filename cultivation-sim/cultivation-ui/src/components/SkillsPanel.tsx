import { useState, useEffect } from 'react';
import { api } from '../api';

interface Skill {
  id: string;
  name: string;
  type: string;
  tier: string;
  description: string;
  requirements: Record<string, any>;
  learning_cost: Record<string, any>;
  effects: Record<string, any>;
  can_learn: boolean;
}

interface SkillsPanelProps {
  onClose: () => void;
}

export function SkillsPanel({ onClose }: SkillsPanelProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [playerRealm, setPlayerRealm] = useState('');
  const [playerLevel, setPlayerLevel] = useState(0);
  const [playerMoney, setPlayerMoney] = useState(0);
  const [loading, setLoading] = useState(true);
  const [learning, setLearning] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadAvailableSkills();
  }, []);

  async function loadAvailableSkills() {
    try {
      setLoading(true);
      const data = await api.getAvailableSkills();
      setSkills(data.skills || []);
      setPlayerRealm(data.player_realm || '');
      setPlayerLevel(data.player_level || 0);
      setPlayerMoney(data.player_money || 0);
    } catch (error: any) {
      setMessage({ type: 'error', text: `Lỗi: ${error.message || 'Không thể tải kỹ năng'}` });
    } finally {
      setLoading(false);
    }
  }

  async function learnSkill(skillId: string) {
    try {
      setLearning(skillId);
      setMessage(null);
      const result = await api.learnSkill(skillId);
      
      if (result.success) {
        setMessage({ type: 'success', text: result.message || 'Học thành công!' });
        setPlayerMoney(result.remaining_money || 0);
        // Reload skills to update can_learn status
        await loadAvailableSkills();
      } else {
        setMessage({ type: 'error', text: result.message || 'Học thất bại!' });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: `Lỗi: ${error.message || 'Không thể học kỹ năng'}` });
    } finally {
      setLearning(null);
    }
  }

  const getTierColor = (tier: string) => {
    if (tier.includes('Nhân')) return 'text-gray-400';
    if (tier.includes('Hoàng')) return 'text-yellow-400';
    if (tier.includes('Địa')) return 'text-blue-400';
    if (tier.includes('Thiên')) return 'text-purple-400';
    return 'text-gray-400';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 p-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <span>⚔️</span> Kỹ Năng
          </h2>
          <button
            onClick={onClose}
            className="text-white hover:bg-white hover:bg-opacity-20 rounded px-3 py-1 transition"
          >
            ✕
          </button>
        </div>

        {/* Player Info */}
        <div className="bg-slate-800 p-3 border-b border-slate-700">
          <div className="flex items-center justify-between text-sm">
            <div className="flex gap-4">
              <span className="text-slate-300">
                Cảnh giới: <span className="text-white font-semibold">{playerRealm}</span>
              </span>
              <span className="text-slate-300">
                Level: <span className="text-white font-semibold">{playerLevel}</span>
              </span>
            </div>
            <span className="text-yellow-400 font-bold">
              💰 {playerMoney.toLocaleString()} Spirit Stones
            </span>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`p-3 mx-4 mt-2 rounded ${
            message.type === 'success' ? 'bg-green-900 bg-opacity-50 text-green-300' : 'bg-red-900 bg-opacity-50 text-red-300'
          }`}>
            {message.text}
          </div>
        )}

        {/* Skills List */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="text-center py-8 text-slate-400">Đang tải...</div>
          ) : skills.length === 0 ? (
            <div className="text-center py-8 text-slate-400">Không có kỹ năng nào</div>
          ) : (
            <div className="space-y-3">
              {skills.map((skill) => (
                <div
                  key={skill.id}
                  className={`bg-slate-800 rounded-lg p-4 border-2 transition-all ${
                    skill.can_learn
                      ? 'border-slate-700 hover:border-blue-500'
                      : 'border-slate-700 opacity-60'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="text-lg font-semibold text-white">{skill.name}</h3>
                      <span className={`text-sm font-bold ${getTierColor(skill.tier)}`}>
                        {skill.tier}
                      </span>
                    </div>
                    <span className="text-xs text-slate-400">{skill.type}</span>
                  </div>
                  
                  <p className="text-sm text-slate-400 mb-3">{skill.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-slate-300">
                      <span>Chi phí: </span>
                      <span className="text-yellow-400 font-bold">
                        💰 {skill.learning_cost?.spirit_stones?.toLocaleString() || 0}
                      </span>
                    </div>
                    <button
                      onClick={() => learnSkill(skill.id)}
                      disabled={!skill.can_learn || learning === skill.id}
                      className={`px-4 py-2 rounded font-semibold transition ${
                        skill.can_learn
                          ? 'bg-blue-600 hover:bg-blue-700 text-white'
                          : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                      }`}
                    >
                      {learning === skill.id ? 'Đang học...' : 'Học'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

