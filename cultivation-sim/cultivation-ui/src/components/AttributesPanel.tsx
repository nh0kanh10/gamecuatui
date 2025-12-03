import { useEffect, useState } from 'react';

export interface AttributesData {
  con?: number; // Căn cốt
  int?: number; // Ngộ tính
  per?: number; // Thần thức
  luk?: number; // Phúc duyên
  cha?: number; // Mị lực
  kar?: number; // Cơ duyên
  // Linh Căn (separate from Talent)
  ling_gen?: string; // Linh căn (Kim, Mộc, Thủy, Hỏa, Thổ, Linh, etc.)
  // Thể chất
  physique?: string; // Trời sinh thần lực, Thiên Linh Thể, ...
  physique_id?: string;
  physique_level?: number; // Cấp độ thể chất
  physique_element?: string;
  physique_tier?: string;
  physique_description?: string;
  // Nhan sắc
  appearance?: number; // Nhan sắc (0-100)
  // Luck
  luck?: number; // Vận may (0-100)
}

interface AttributeChange {
  key: string;
  oldValue: number;
  newValue: number;
  diff: number;
}

interface AttributesPanelProps {
  attributes?: AttributesData | null;
  previousAttributes?: AttributesData | null;
  gameState?: {
    talent?: string;
    cultivation?: {
      realm?: string;
      realm_level?: number;
      spiritual_power?: number;
      max_spiritual_power?: number;
      breakthrough_progress?: number;
    } | null;
    resources?: {
      spirit_stones?: number;
      pills?: Record<string, number>;
      materials?: Record<string, number>;
    } | null;
  } | null;
}

const attributeLabels: Record<string, { label: string; icon: string; color: string }> = {
  con: { label: 'Căn Cốt', icon: '💪', color: 'text-red-400' },
  int: { label: 'Ngộ Tính', icon: '🧠', color: 'text-blue-400' },
  per: { label: 'Thần Thức', icon: '👁️', color: 'text-purple-400' },
  luk: { label: 'Phúc Duyên', icon: '🍀', color: 'text-green-400' },
  cha: { label: 'Mị Lực', icon: '✨', color: 'text-pink-400' },
  kar: { label: 'Cơ Duyên', icon: '⭐', color: 'text-yellow-400' },
  appearance: { label: 'Nhan Sắc', icon: '🌸', color: 'text-rose-400' },
  luck: { label: 'Vận May', icon: '🎲', color: 'text-cyan-400' },
};


export function AttributesPanel({ attributes, previousAttributes, gameState }: AttributesPanelProps) {
  const [changes, setChanges] = useState<AttributeChange[]>([]);
  const [showChanges, setShowChanges] = useState(true);

  useEffect(() => {
    if (!attributes || !previousAttributes) {
      setChanges([]);
      return;
    }

    const newChanges: AttributeChange[] = [];
    const keys: (keyof AttributesData)[] = ['con', 'int', 'per', 'luk', 'cha', 'kar', 'appearance', 'luck'];

    keys.forEach((key) => {
      const oldVal = previousAttributes[key] as number | undefined;
      const newVal = attributes[key] as number | undefined;

      if (oldVal !== undefined && newVal !== undefined && oldVal !== newVal) {
        newChanges.push({
          key,
          oldValue: oldVal,
          newValue: newVal,
          diff: newVal - oldVal,
        });
      }
    });

    setChanges(newChanges);

    // Auto-hide changes after 5 seconds
    if (newChanges.length > 0) {
      const timer = setTimeout(() => {
        setShowChanges(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [attributes, previousAttributes]);

  if (!attributes) {
    return null;
  }

  const renderAttribute = (key: string, value: number | undefined) => {
    if (value === undefined) return null;

    const config = attributeLabels[key];
    if (!config) return null;

    const change = changes.find((c) => c.key === key);
    const isChanging = change && showChanges && change.diff !== 0;

    return (
      <div
        key={key}
        className={`flex items-center justify-between p-2 rounded-lg bg-slate-800/50 border ${
          isChanging ? 'border-green-500/50 bg-green-900/20 animate-pulse' : 'border-slate-700/50'
        } transition-all duration-300`}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{config.icon}</span>
          <span className="text-sm text-gray-400">{config.label}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`font-bold ${config.color}`}>{value.toFixed(1)}</span>
          {isChanging && (
            <span className="text-green-400 font-bold animate-bounce">
              +{change.diff > 0 ? '+' : ''}{change.diff.toFixed(1)}
            </span>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="w-72 bg-slate-900/95 backdrop-blur-xl border-r-2 border-amber-500/30 p-4 overflow-y-auto h-screen sticky top-0">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-amber-400 mb-2 flex items-center gap-2">
          <span>📊</span>
          Chỉ Số Nhân Vật
        </h3>
        {changes.length > 0 && showChanges && (
          <div className="text-xs text-green-400 mb-2 animate-pulse">
            ⚡ Có {changes.length} chỉ số thay đổi!
          </div>
        )}
      </div>

      {/* Thiên Phú (Talent) */}
      {gameState?.talent && (
        <div className="mb-4 pb-4 border-b border-slate-700/50">
          <h4 className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
            <span>⭐</span>
            Thiên Phú
          </h4>
          <div className="p-2 rounded-lg bg-purple-900/20 border border-purple-500/50">
            <div className="font-bold text-purple-300">{gameState.talent}</div>
          </div>
        </div>
      )}

      {/* Linh Căn (Separate from Talent) */}
      {attributes?.ling_gen && (
        <div className="mb-4 pb-4 border-b border-slate-700/50">
          <h4 className="text-sm font-semibold text-cyan-400 mb-2 flex items-center gap-2">
            <span>🌟</span>
            Linh Căn
          </h4>
          <div className="p-2 rounded-lg bg-cyan-900/20 border border-cyan-500/50">
            <div className="font-bold text-cyan-300">{attributes.ling_gen}</div>
          </div>
        </div>
      )}

      {/* Tu Luyện (Cultivation) */}
      {gameState?.cultivation && (
        <div className="mb-4 pb-4 border-b border-slate-700/50">
          <h4 className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
            <span>🔥</span>
            Tu Luyện
          </h4>
          <div className="space-y-2">
            <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
              <div className="text-xs text-gray-400 mb-1">Cảnh Giới</div>
              <div className="font-bold text-purple-300">
                {gameState.cultivation.realm || 'Mortal'} 
                {gameState.cultivation.realm_level ? ` Lv.${gameState.cultivation.realm_level}` : ''}
              </div>
            </div>
            <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
              <div className="text-xs text-gray-400 mb-1">Linh Khí</div>
              <div className="font-bold text-blue-300">
                {gameState.cultivation.spiritual_power || 0} / {gameState.cultivation.max_spiritual_power || 100}
              </div>
              {gameState.cultivation.max_spiritual_power && (
                <div className="w-full bg-slate-700 rounded-full h-1.5 mt-1">
                  <div 
                    className="bg-blue-500 h-1.5 rounded-full transition-all"
                    style={{ 
                      width: `${Math.min(100, ((gameState.cultivation.spiritual_power || 0) / gameState.cultivation.max_spiritual_power) * 100)}%` 
                    }}
                  ></div>
                </div>
              )}
            </div>
            {gameState.cultivation.breakthrough_progress !== undefined && (
              <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
                <div className="text-xs text-gray-400 mb-1">Tiến Độ Đột Phá</div>
                <div className="font-bold text-yellow-300">
                  {gameState.cultivation.breakthrough_progress.toFixed(1)}%
                </div>
                <div className="w-full bg-slate-700 rounded-full h-1.5 mt-1">
                  <div 
                    className="bg-yellow-500 h-1.5 rounded-full transition-all"
                    style={{ width: `${Math.min(100, gameState.cultivation.breakthrough_progress)}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tài Nguyên (Resources) */}
      {gameState?.resources && (
        <div className="mb-4 pb-4 border-b border-slate-700/50">
          <h4 className="text-sm font-semibold text-emerald-400 mb-2 flex items-center gap-2">
            <span>💎</span>
            Tài Nguyên
          </h4>
          <div className="space-y-2">
            <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
              <div className="text-xs text-gray-400 mb-1">Linh Thạch</div>
              <div className="font-bold text-emerald-300 flex items-center gap-2">
                <span>💎</span>
                {gameState.resources.spirit_stones || 0}
              </div>
            </div>
            {gameState.resources.pills && Object.keys(gameState.resources.pills).length > 0 && (
              <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
                <div className="text-xs text-gray-400 mb-1">Đan Dược</div>
                <div className="text-sm text-emerald-300">
                  {Object.entries(gameState.resources.pills).slice(0, 3).map(([name, qty]) => (
                    <div key={name} className="flex justify-between">
                      <span>{name}</span>
                      <span className="font-bold">x{qty}</span>
                    </div>
                  ))}
                  {Object.keys(gameState.resources.pills).length > 3 && (
                    <div className="text-xs text-gray-500 mt-1">
                      +{Object.keys(gameState.resources.pills).length - 3} loại khác
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chỉ Số (Attributes) */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-amber-400 mb-2 flex items-center gap-2">
          <span>⚔️</span>
          Chỉ Số
        </h4>
        <div className="space-y-2">
          {renderAttribute('con', attributes.con)}
          {renderAttribute('int', attributes.int)}
          {renderAttribute('per', attributes.per)}
          {renderAttribute('luk', attributes.luk)}
          {renderAttribute('cha', attributes.cha)}
          {renderAttribute('kar', attributes.kar)}
          {renderAttribute('appearance', attributes.appearance)}
          {renderAttribute('luck', attributes.luck)}
        </div>
      </div>

      {/* Thể Chất */}
      <div className="mb-4 pb-4 border-b border-slate-700/50">
        <h4 className="text-sm font-semibold text-purple-400 mb-2 flex items-center gap-2">
          <span>⚡</span>
          Thể Chất
        </h4>
        {attributes.physique || attributes.physique_id ? (
          <div className="p-2 rounded-lg bg-purple-900/20 border border-purple-500/50">
            <div className="font-bold text-purple-300">
              {attributes.physique || attributes.physique_id || 'Chưa có'}
            </div>
            {attributes.physique_level && (
              <div className="text-xs text-purple-400 mt-1">Cấp {attributes.physique_level}</div>
            )}
            {attributes.physique_element && (
              <div className="text-xs text-purple-400 mt-1">Hệ: {attributes.physique_element}</div>
            )}
            {attributes.physique_tier && (
              <div className="text-xs text-purple-400 mt-1">Tier: {attributes.physique_tier}</div>
            )}
            {attributes.physique_description && (
              <div className="text-xs text-gray-400 mt-2 italic">{attributes.physique_description}</div>
            )}
            {!attributes.physique && !attributes.physique_description && (
              <div className="text-xs text-gray-500 mt-2 italic">Đang tải thông tin thể chất...</div>
            )}
          </div>
        ) : (
          <div className="p-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
            <div className="text-sm text-gray-500 italic">Chưa có thể chất</div>
          </div>
        )}
      </div>

      {/* Tổng Quan */}
      <div className="mt-4 pt-4 border-t border-slate-700/50">
        <div className="text-xs text-gray-500 space-y-1">
          <div>💪 Căn Cốt: HP, Hồi phục</div>
          <div>🧠 Ngộ Tính: Tốc độ tu luyện</div>
          <div>👁️ Thần Thức: Tầm nhìn, Phát hiện</div>
          <div>🍀 Phúc Duyên: Drop rate, Crit</div>
          <div>✨ Mị Lực: Giá mua bán, Thiện cảm</div>
          <div>⭐ Cơ Duyên: Giới hạn cảnh giới</div>
        </div>
      </div>
    </div>
  );
}

