import { useState, useEffect } from 'react';
import { api } from '../api';

interface ShopItem {
  id: string;
  name: string;
  type: string;
  price: number;
  description: string;
  rarity: string;
  can_afford: boolean;
  stats: Record<string, any>;
}

interface ShopPanelProps {
  onClose: () => void;
}

export function ShopPanel({ onClose }: ShopPanelProps) {
  const [items, setItems] = useState<ShopItem[]>([]);
  const [playerMoney, setPlayerMoney] = useState(0);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadShopItems();
  }, []);

  async function loadShopItems() {
    try {
      setLoading(true);
      const data = await api.getShopItems();
      setItems(data.items || []);
      setPlayerMoney(data.player_money || 0);
    } catch (error: any) {
      setMessage({ type: 'error', text: `Lỗi: ${error.message || 'Không thể tải cửa hàng'}` });
    } finally {
      setLoading(false);
    }
  }

  async function buyItem(itemId: string) {
    try {
      setBuying(itemId);
      setMessage(null);
      const result = await api.buyItem(itemId);
      
      if (result.success) {
        setMessage({ type: 'success', text: result.message || 'Mua thành công!' });
        setPlayerMoney(result.remaining_money || 0);
        // Reload items to update can_afford status
        await loadShopItems();
      } else {
        setMessage({ type: 'error', text: result.message || 'Mua thất bại!' });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: `Lỗi: ${error.message || 'Không thể mua vật phẩm'}` });
    } finally {
      setBuying(null);
    }
  }

  const getRarityColor = (rarity: string) => {
    switch (rarity.toLowerCase()) {
      case 'common': return 'text-gray-400';
      case 'uncommon': return 'text-green-400';
      case 'rare': return 'text-blue-400';
      case 'epic': return 'text-purple-400';
      case 'legendary': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <span>🛒</span> Cửa Hàng
          </h2>
          <button
            onClick={onClose}
            className="text-white hover:bg-white hover:bg-opacity-20 rounded px-3 py-1 transition"
          >
            ✕
          </button>
        </div>

        {/* Money Display */}
        <div className="bg-slate-800 p-3 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <span className="text-slate-300">Số tiền hiện có:</span>
            <span className="text-2xl font-bold text-yellow-400 flex items-center gap-2">
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

        {/* Items List */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="text-center py-8 text-slate-400">Đang tải...</div>
          ) : items.length === 0 ? (
            <div className="text-center py-8 text-slate-400">Không có vật phẩm nào</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {items.map((item) => (
                <div
                  key={item.id}
                  className={`bg-slate-800 rounded-lg p-4 border-2 transition-all ${
                    item.can_afford
                      ? 'border-slate-700 hover:border-purple-500'
                      : 'border-slate-700 opacity-60'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-white">{item.name}</h3>
                    <span className={`text-sm font-bold ${getRarityColor(item.rarity)}`}>
                      {item.rarity}
                    </span>
                  </div>
                  
                  <p className="text-sm text-slate-400 mb-3">{item.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-yellow-400 font-bold">
                      💰 {item.price.toLocaleString()}
                    </span>
                    <button
                      onClick={() => buyItem(item.id)}
                      disabled={!item.can_afford || buying === item.id}
                      className={`px-4 py-2 rounded font-semibold transition ${
                        item.can_afford
                          ? 'bg-purple-600 hover:bg-purple-700 text-white'
                          : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                      }`}
                    >
                      {buying === item.id ? 'Đang mua...' : 'Mua'}
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

