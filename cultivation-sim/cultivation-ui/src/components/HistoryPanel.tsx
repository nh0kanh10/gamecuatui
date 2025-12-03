import { useState } from 'react';

export interface HistoryEntry {
  timestamp: string;
  prompt?: string;
  response?: string;
  narrative?: string;
  choices?: string[];
  error?: string;
}

interface HistoryPanelProps {
  history: HistoryEntry[];
  onClose: () => void;
}

export function HistoryPanel({ history, onClose }: HistoryPanelProps) {
  const [selectedEntry, setSelectedEntry] = useState<HistoryEntry | null>(null);
  const [filter, setFilter] = useState<'all' | 'prompts' | 'responses' | 'errors'>('all');

  const filteredHistory = history.filter((entry) => {
    if (filter === 'all') return true;
    if (filter === 'prompts') return !!entry.prompt;
    if (filter === 'responses') return !!entry.response || !!entry.narrative;
    if (filter === 'errors') return !!entry.error;
    return true;
  });

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border-2 border-amber-500/50 rounded-lg w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-amber-500/30 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-amber-400 flex items-center gap-2">
            <span>📜</span>
            Lịch Sử AI
          </h2>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-red-600/20 border border-red-600/50 hover:bg-red-600/30 text-red-400 rounded-lg transition-all"
          >
            ✕ Đóng
          </button>
        </div>

        {/* Filters */}
        <div className="p-4 border-b border-slate-700/50 flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded ${
              filter === 'all'
                ? 'bg-amber-600/30 border border-amber-600/50 text-amber-400'
                : 'bg-slate-800 border border-slate-700 text-gray-400 hover:bg-slate-700'
            }`}
          >
            Tất Cả ({history.length})
          </button>
          <button
            onClick={() => setFilter('prompts')}
            className={`px-3 py-1 rounded ${
              filter === 'prompts'
                ? 'bg-blue-600/30 border border-blue-600/50 text-blue-400'
                : 'bg-slate-800 border border-slate-700 text-gray-400 hover:bg-slate-700'
            }`}
          >
            Prompts ({history.filter((e) => e.prompt).length})
          </button>
          <button
            onClick={() => setFilter('responses')}
            className={`px-3 py-1 rounded ${
              filter === 'responses'
                ? 'bg-green-600/30 border border-green-600/50 text-green-400'
                : 'bg-slate-800 border border-slate-700 text-gray-400 hover:bg-slate-700'
            }`}
          >
            Responses ({history.filter((e) => e.response || e.narrative).length})
          </button>
          <button
            onClick={() => setFilter('errors')}
            className={`px-3 py-1 rounded ${
              filter === 'errors'
                ? 'bg-red-600/30 border border-red-600/50 text-red-400'
                : 'bg-slate-800 border border-slate-700 text-gray-400 hover:bg-slate-700'
            }`}
          >
            Errors ({history.filter((e) => e.error).length})
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* History List */}
          <div className="w-1/3 border-r border-slate-700/50 overflow-y-auto">
            {filteredHistory.length === 0 ? (
              <div className="p-4 text-gray-500 text-center">Không có lịch sử</div>
            ) : (
              filteredHistory.map((entry, index) => (
                <div
                  key={index}
                  onClick={() => setSelectedEntry(entry)}
                  className={`p-3 border-b border-slate-700/30 cursor-pointer hover:bg-slate-800/50 transition-all ${
                    selectedEntry === entry ? 'bg-amber-900/20 border-l-4 border-l-amber-500' : ''
                  }`}
                >
                  <div className="text-xs text-gray-500 mb-1">{entry.timestamp}</div>
                  <div className="text-sm font-semibold text-white truncate">
                    {entry.error ? (
                      <span className="text-red-400">❌ Error</span>
                    ) : entry.prompt ? (
                      <span className="text-blue-400">📤 Prompt</span>
                    ) : entry.narrative ? (
                      <span className="text-green-400">📥 Response</span>
                    ) : (
                      'Entry'
                    )}
                  </div>
                  {entry.narrative && (
                    <div className="text-xs text-gray-400 mt-1 line-clamp-2">
                      {entry.narrative.substring(0, 100)}...
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Entry Detail */}
          <div className="flex-1 overflow-y-auto p-4">
            {selectedEntry ? (
              <div className="space-y-4">
                <div>
                  <div className="text-xs text-gray-500 mb-2">Thời gian</div>
                  <div className="text-sm text-white">{selectedEntry.timestamp}</div>
                </div>

                {selectedEntry.prompt && (
                  <div>
                    <div className="text-sm font-semibold text-blue-400 mb-2 flex items-center gap-2">
                      <span>📤</span>
                      Prompt (Gửi đến AI)
                    </div>
                    <div className="bg-slate-800/50 border border-blue-500/30 rounded-lg p-4">
                      <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono">
                        {selectedEntry.prompt}
                      </pre>
                    </div>
                  </div>
                )}

                {selectedEntry.response && (
                  <div>
                    <div className="text-sm font-semibold text-green-400 mb-2 flex items-center gap-2">
                      <span>📥</span>
                      Raw Response (Từ AI)
                    </div>
                    <div className="bg-slate-800/50 border border-green-500/30 rounded-lg p-4">
                      <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono">
                        {selectedEntry.response}
                      </pre>
                    </div>
                  </div>
                )}

                {selectedEntry.narrative && (
                  <div>
                    <div className="text-sm font-semibold text-amber-400 mb-2 flex items-center gap-2">
                      <span>📖</span>
                      Narrative (Câu chuyện)
                    </div>
                    <div className="bg-slate-800/50 border border-amber-500/30 rounded-lg p-4">
                      <div className="text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
                        {selectedEntry.narrative}
                      </div>
                    </div>
                  </div>
                )}

                {selectedEntry.choices && selectedEntry.choices.length > 0 && (
                  <div>
                    <div className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
                      <span>🎯</span>
                      Choices (Lựa chọn)
                    </div>
                    <div className="bg-slate-800/50 border border-purple-500/30 rounded-lg p-4">
                      <ul className="space-y-2">
                        {selectedEntry.choices.map((choice, idx) => (
                          <li key={idx} className="text-sm text-gray-300">
                            {idx + 1}. {choice}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {selectedEntry.error && (
                  <div>
                    <div className="text-sm font-semibold text-red-400 mb-2 flex items-center gap-2">
                      <span>❌</span>
                      Error
                    </div>
                    <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4">
                      <pre className="text-xs text-red-300 whitespace-pre-wrap font-mono">
                        {selectedEntry.error}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center text-gray-500 mt-8">
                Chọn một entry từ danh sách để xem chi tiết
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

