import { useState, useEffect } from 'react';
import { api, type QuestData } from '../api';

interface QuestsPanelProps {
  onClose: () => void;
}

export function QuestsPanel({ onClose }: QuestsPanelProps) {
  const [pending, setPending] = useState<QuestData[]>([]);
  const [active, setActive] = useState<QuestData[]>([]);
  const [completed, setCompleted] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQuests();
  }, []);

  async function loadQuests() {
    try {
      setLoading(true);
      const data = await api.getAvailableQuests();
      setPending(data.pending || []);
      setActive(data.active || []);
      setCompleted(data.completed || 0);
    } catch (error: any) {
      console.error('Error loading quests:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <span>📜</span> Nhiệm Vụ
          </h2>
          <button
            onClick={onClose}
            className="text-white hover:bg-white hover:bg-opacity-20 rounded px-3 py-1 transition"
          >
            ✕
          </button>
        </div>

        {/* Stats */}
        <div className="bg-slate-800 p-3 border-b border-slate-700">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-300">
              Đã hoàn thành: <span className="text-green-400 font-bold">{completed}</span>
            </span>
            <span className="text-slate-300">
              Đang làm: <span className="text-yellow-400 font-bold">{active.length}</span>
            </span>
            <span className="text-slate-300">
              Chờ nhận: <span className="text-blue-400 font-bold">{pending.length}</span>
            </span>
          </div>
        </div>

        {/* Quests List */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="text-center py-8 text-slate-400">Đang tải...</div>
          ) : (
            <div className="space-y-4">
              {/* Active Quests */}
              {active.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-yellow-400 mb-3 flex items-center gap-2">
                    <span>⚡</span> Đang Làm
                  </h3>
                  <div className="space-y-2">
                    {active.map((quest) => (
                      <div
                        key={quest.quest_id}
                        className="bg-slate-800 rounded-lg p-4 border-2 border-yellow-500"
                      >
                        <h4 className="text-lg font-semibold text-white mb-2">{quest.title}</h4>
                        <p className="text-sm text-slate-400">{quest.description}</p>
                        {quest.status && (
                          <span className="inline-block mt-2 px-2 py-1 bg-yellow-900 bg-opacity-50 text-yellow-300 text-xs rounded">
                            {quest.status}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Pending Quests */}
              {pending.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-blue-400 mb-3 flex items-center gap-2">
                    <span>📋</span> Chờ Nhận
                  </h3>
                  <div className="space-y-2">
                    {pending.map((quest) => (
                      <div
                        key={quest.quest_id}
                        className="bg-slate-800 rounded-lg p-4 border-2 border-blue-500"
                      >
                        <h4 className="text-lg font-semibold text-white mb-2">{quest.title}</h4>
                        <p className="text-sm text-slate-400">{quest.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Empty State */}
              {active.length === 0 && pending.length === 0 && (
                <div className="text-center py-8 text-slate-400">
                  Không có nhiệm vụ nào
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

