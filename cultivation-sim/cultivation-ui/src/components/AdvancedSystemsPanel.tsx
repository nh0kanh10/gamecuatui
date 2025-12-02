import React, { useState } from 'react';
import { 
  Sword, ShoppingCart, Users, Zap, 
  Target, BookOpen, Layers, Trophy 
} from 'lucide-react';

interface AdvancedSystemsPanelProps {
  gameState: any;
  onAction: (action: string, data?: any) => void;
}

export const AdvancedSystemsPanel: React.FC<AdvancedSystemsPanelProps> = ({ 
  gameState, 
  onAction 
}) => {
  const [activeTab, setActiveTab] = useState<string>('skills');

  const tabs = [
    { id: 'skills', label: 'Kỹ Năng', icon: Sword },
    { id: 'economy', label: 'Kinh Tế', icon: ShoppingCart },
    { id: 'social', label: 'Xã Hội', icon: Users },
    { id: 'combat', label: 'Chiến Đấu', icon: Zap },
    { id: 'breakthrough', label: 'Đột Phá', icon: Target },
    { id: 'naming', label: 'Đặt Tên', icon: BookOpen },
    { id: 'formations', label: 'Trận Pháp', icon: Layers },
    { id: 'quests', label: 'Nhiệm Vụ', icon: Trophy },
  ];

  return (
    <div className="bg-gray-800 rounded-lg p-4 mb-4">
      <h3 className="text-lg font-bold mb-3 text-white">Hệ Thống Nâng Cao</h3>
      
      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-4">
        {tabs.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <Icon size={16} />
              <span className="text-sm">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="bg-gray-900 rounded p-4 min-h-[200px]">
        {activeTab === 'skills' && <SkillsTab gameState={gameState} onAction={onAction} />}
        {activeTab === 'economy' && <EconomyTab gameState={gameState} onAction={onAction} />}
        {activeTab === 'social' && <SocialTab gameState={gameState} onAction={onAction} />}
        {activeTab === 'combat' && <CombatTab gameState={gameState} onAction={onAction} />}
        {activeTab === 'breakthrough' && <BreakthroughTab gameState={gameState} onAction={onAction} />}
        {activeTab === 'naming' && <NamingTab gameState={gameState} onAction={onAction} />}
        {activeTab === 'formations' && <FormationsTab gameState={gameState} onAction={onAction} />}
        {activeTab === 'quests' && <QuestsTab gameState={gameState} onAction={onAction} />}
      </div>
    </div>
  );
};

// Skills Tab
const SkillsTab: React.FC<any> = ({ gameState, onAction }) => {
  const skills = gameState?.skills || [];

  return (
    <div>
      <h4 className="text-white font-semibold mb-3">Kỹ Năng</h4>
      <div className="space-y-2">
        {skills.map((skill: any) => (
          <div key={skill.id} className="bg-gray-800 p-3 rounded flex justify-between items-center">
            <div>
              <div className="text-white font-medium">{skill.name}</div>
              <div className="text-gray-400 text-sm">{skill.description}</div>
              <div className="text-gray-500 text-xs mt-1">
                MP: {skill.mana_cost} | Cooldown: {skill.cooldown}s
              </div>
            </div>
            <button
              onClick={() => onAction('cast_skill', { skill_id: skill.id })}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
            >
              Sử Dụng
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// Economy Tab
const EconomyTab: React.FC<any> = ({ gameState, onAction }) => {
  const economy = gameState?.economy || {};
  const prices = economy.prices || {};

  return (
    <div>
      <h4 className="text-white font-semibold mb-3">Kinh Tế</h4>
      <div className="mb-3">
        <span className="text-gray-400">Chu kỳ kinh tế: </span>
        <span className="text-white">{economy.economic_cycle || 'normal'}</span>
      </div>
      
      <div className="space-y-2">
        {Object.entries(prices).map(([itemId, priceInfo]: [string, any]) => (
          <div key={itemId} className="bg-gray-800 p-3 rounded">
            <div className="text-white font-medium">{itemId}</div>
            <div className="text-gray-400 text-sm">
              Giá: {priceInfo.current_price?.toFixed(2) || 'N/A'} 
              (x{priceInfo.price_multiplier?.toFixed(2) || '1.0'})
            </div>
            <div className="text-gray-500 text-xs">
              Tồn kho: {priceInfo.current_stock || 0} / {priceInfo.target_stock || 100}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Social Tab
const SocialTab: React.FC<any> = ({ gameState, onAction }) => {
  const social = gameState?.social_graph || {};
  const relationships = social.relationships || {};

  return (
    <div>
      <h4 className="text-white font-semibold mb-3">Xã Hội</h4>
      <div className="mb-3">
        <span className="text-gray-400">Độ ảnh hưởng: </span>
        <span className="text-white">{(social.centrality || 0).toFixed(3)}</span>
      </div>
      
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {Object.entries(relationships).map(([targetId, rel]: [string, any]) => (
          <div key={targetId} className="bg-gray-800 p-3 rounded">
            <div className="text-white font-medium">{targetId}</div>
            <div className="text-gray-400 text-sm">
              Quan điểm: {rel.opinion?.toFixed(1) || '0'} | 
              Độ thân: {rel.affinity || 0}
            </div>
            <div className="text-gray-500 text-xs">
              Loại: {rel.relationship_type || 'unknown'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Combat Tab
const CombatTab: React.FC<any> = ({ gameState, onAction }) => {
  return (
    <div>
      <h4 className="text-white font-semibold mb-3">Chiến Đấu</h4>
      <button
        onClick={() => onAction('start_combat')}
        className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
      >
        Bắt Đầu Chiến Đấu
      </button>
    </div>
  );
};

// Breakthrough Tab
const BreakthroughTab: React.FC<any> = ({ gameState, onAction }) => {
  const perks = gameState?.rewrite_destiny_perks || [];
  const taoSouls = gameState?.tao_souls || [];

  return (
    <div>
      <h4 className="text-white font-semibold mb-3">Đột Phá</h4>
      
      <div className="mb-4">
        <button
          onClick={() => onAction('attempt_breakthrough')}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded mb-3"
        >
          Thử Đột Phá
        </button>
      </div>

      {perks.length > 0 && (
        <div className="mb-4">
          <h5 className="text-white font-medium mb-2">Nghịch Thiên Cải Mệnh:</h5>
          <div className="space-y-2">
            {perks.map((perk: any, idx: number) => (
              <div key={idx} className="bg-gray-800 p-2 rounded">
                <div className="text-white text-sm">{perk.name}</div>
                <div className="text-gray-400 text-xs">{perk.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {taoSouls.length > 0 && (
        <div>
          <h5 className="text-white font-medium mb-2">Đạo Hồn:</h5>
          <div className="space-y-2">
            {taoSouls.map((soul: any) => (
              <div key={soul.soul_id} className="bg-gray-800 p-2 rounded">
                <div className="text-white text-sm">{soul.soul_type}</div>
                <div className="text-gray-400 text-xs">
                  Độ tinh khiết: {(soul.purity * 100).toFixed(1)}% | 
                  Sức mạnh: {soul.power}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Naming Tab
const NamingTab: React.FC<any> = ({ gameState, onAction }) => {
  const [nameType, setNameType] = useState('skill');
  const [generatedName, setGeneratedName] = useState('');

  const handleGenerate = () => {
    onAction('generate_name', { name_type: nameType });
    // In real implementation, would get name from API response
    setGeneratedName('Generated name will appear here');
  };

  return (
    <div>
      <h4 className="text-white font-semibold mb-3">Đặt Tên</h4>
      
      <div className="space-y-3">
        <div>
          <label className="text-gray-400 text-sm">Loại tên:</label>
          <select
            value={nameType}
            onChange={(e) => setNameType(e.target.value)}
            className="w-full bg-gray-700 text-white p-2 rounded mt-1"
          >
            <option value="skill">Kỹ Năng</option>
            <option value="character">Nhân Vật</option>
            <option value="sect">Tông Môn</option>
          </select>
        </div>
        
        <button
          onClick={handleGenerate}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded w-full"
        >
          Tạo Tên
        </button>
        
        {generatedName && (
          <div className="bg-gray-800 p-3 rounded text-white">
            {generatedName}
          </div>
        )}
      </div>
    </div>
  );
};

// Formations Tab
const FormationsTab: React.FC<any> = ({ gameState, onAction }) => {
  const formations = gameState?.formations || [];

  return (
    <div>
      <h4 className="text-white font-semibold mb-3">Trận Pháp</h4>
      
      <button
        onClick={() => onAction('create_formation')}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded mb-3"
      >
        Tạo Trận Pháp
      </button>

      <div className="space-y-2">
        {formations.map((formation: any) => (
          <div key={formation.id} className="bg-gray-800 p-3 rounded">
            <div className="text-white font-medium">Trận {formation.id}</div>
            <div className="text-gray-400 text-sm">
              Tấn công: +{((formation.bonus?.formation_bonus?.attack_bonus - 1) * 100 || 0).toFixed(1)}% | 
              Phòng thủ: +{((formation.bonus?.formation_bonus?.defense_bonus - 1) * 100 || 0).toFixed(1)}%
            </div>
            <div className="text-gray-500 text-xs">
              Ổn định: {formation.bonus?.is_stable ? 'Có' : 'Không'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Quests Tab
const QuestsTab: React.FC<any> = ({ gameState, onAction }) => {
  const quests = gameState?.quests || {};
  const pending = quests.pending || [];
  const active = quests.active || [];

  return (
    <div>
      <h4 className="text-white font-semibold mb-3">Nhiệm Vụ</h4>
      
      {pending.length > 0 && (
        <div className="mb-4">
          <h5 className="text-white font-medium mb-2">Chờ Nhận:</h5>
          <div className="space-y-2">
            {pending.map((quest: any) => (
              <div key={quest.quest_id} className="bg-gray-800 p-3 rounded">
                <div className="text-white font-medium">{quest.title}</div>
                <div className="text-gray-400 text-sm">{quest.description}</div>
                <button
                  onClick={() => onAction('accept_quest', { quest_id: quest.quest_id })}
                  className="mt-2 bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                >
                  Nhận Nhiệm Vụ
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {active.length > 0 && (
        <div>
          <h5 className="text-white font-medium mb-2">Đang Làm:</h5>
          <div className="space-y-2">
            {active.map((quest: any) => (
              <div key={quest.quest_id} className="bg-gray-800 p-3 rounded">
                <div className="text-white font-medium">{quest.title}</div>
                <div className="text-gray-400 text-sm">{quest.description}</div>
                <button
                  onClick={() => onAction('complete_quest', { quest_id: quest.quest_id })}
                  className="mt-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
                >
                  Hoàn Thành
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

