import React from 'react';
import type { GameState } from './api';

// Icons
const User = () => <span className="text-lg">👤</span>;
const Flame = () => <span className="text-lg">🔥</span>;
const Gem = () => <span className="text-lg">💎</span>;
const Pill = () => <span className="text-lg">💊</span>;
const Book = () => <span className="text-lg">📖</span>;
const Backpack = () => <span className="text-lg">🎒</span>;
const Sword = () => <span className="text-lg">⚔️</span>;
const Scroll = () => <span className="text-lg">📜</span>;
const Close = () => <span className="text-2xl">✕</span>;
const Brain = () => <span className="text-lg">🧠</span>;
const MapPin = () => <span className="text-lg">📍</span>;
const YinYang = () => <span className="text-lg">☯️</span>;
const Sparkles = () => <span className="text-lg">✨</span>;
const Heart = () => <span className="text-lg">❤️</span>;
const Users = () => <span className="text-lg">👥</span>;

interface ModalProps {
    gameState: GameState;
    memoryCount: number;
    onClose: () => void;
}

export function ProfileModal({ gameState, memoryCount, onClose }: ModalProps) {
    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
            <div className="bg-slate-900/95 border-2 border-amber-500/50 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto glow-gold">
                {/* Header */}
                <div className="sticky top-0 bg-gradient-to-r from-amber-900/80 to-orange-900/80 backdrop-blur-xl p-6 border-b-2 border-amber-600/50 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <User />
                        <h2 className="text-2xl font-bold text-amber-300" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                            個人資料 / Hồ Sơ Cá Nhân
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors p-2"
                    >
                        <Close />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Character Info */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-slate-800/50 rounded-xl p-4 border border-amber-600/30">
                            <div className="text-xs text-gray-500 mb-1">Tên</div>
                            <div className="text-2xl font-bold text-amber-400 glow-text" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                                {gameState.character_name}
                            </div>
                        </div>
                        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-600">
                            <div className="text-xs text-gray-500 mb-1">Tuổi</div>
                            <div className="text-2xl font-bold text-white">{gameState.age} tuổi</div>
                        </div>
                        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-600">
                            <div className="text-xs text-gray-500 mb-1">Giới Tính</div>
                            <div className="text-lg text-gray-200">{gameState.gender}</div>
                        </div>
                        <div className="bg-slate-800/50 rounded-xl p-4 border border-purple-600/30">
                            <div className="text-xs text-gray-500 mb-1">Thiên Phú</div>
                            <div className="text-lg text-purple-400 font-semibold">{gameState.talent}</div>
                        </div>
                        <div className="bg-slate-800/50 rounded-xl p-4 border border-emerald-600/30">
                            <div className="text-xs text-gray-500 mb-1">Chủng Tộc</div>
                            <div className="text-lg text-emerald-400">{gameState.race}</div>
                        </div>
                        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-600">
                            <div className="text-xs text-gray-500 mb-1">Bối Cảnh</div>
                            <div className="text-sm text-gray-300">{gameState.background}</div>
                        </div>
                    </div>

                    {/* Cultivation Stats */}
                    {gameState.cultivation && (
                        <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 border-2 border-purple-600/50 rounded-xl p-6 glow-spiritual">
                            <h3 className="text-lg font-bold text-purple-300 mb-4 flex items-center gap-2">
                                <Flame />
                                Tu Luyện
                            </h3>

                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <div className="text-xs text-gray-500 mb-1">Cảnh Giới Hiện Tại</div>
                                    <div className="text-xl font-bold text-purple-300 glow-text">
                                        {gameState.cultivation.realm}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">
                                        Tầng {gameState.cultivation.realm_level}/10
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs text-gray-500 mb-1">Tuổi Tu Luyện</div>
                                    <div className="text-xl font-bold text-purple-400">
                                        {gameState.cultivation.cultivation_age} năm
                                    </div>
                                </div>
                            </div>

                            {/* Spiritual Power Bar */}
                            <div className="mb-4">
                                <div className="flex justify-between text-xs text-gray-400 mb-2">
                                    <span>Linh Lực</span>
                                    <span className="text-purple-400 font-bold">
                                        {gameState.cultivation.spiritual_power}/{gameState.cultivation.max_spiritual_power}
                                    </span>
                                </div>
                                <div className="progress-bar">
                                    <div
                                        className="progress-bar-fill bg-gradient-to-r from-purple-500 to-blue-500"
                                        style={{
                                            width: `${(gameState.cultivation.spiritual_power / gameState.cultivation.max_spiritual_power) * 100}%`,
                                        }}
                                    />
                                </div>
                            </div>

                            {/* Breakthrough Progress */}
                            <div className="mb-4">
                                <div className="flex justify-between text-xs text-gray-400 mb-2">
                                    <span>Tiến Độ Đột Phá</span>
                                    <span className="text-amber-400 font-bold">
                                        {gameState.cultivation.breakthrough_progress.toFixed(1)}%
                                    </span>
                                </div>
                                <div className="progress-bar">
                                    <div
                                        className="progress-bar-fill bg-gradient-to-r from-amber-500 to-orange-500"
                                        style={{
                                            width: `${gameState.cultivation.breakthrough_progress}%`,
                                        }}
                                    />
                                </div>
                            </div>

                            {/* Techniques */}
                            {gameState.cultivation.techniques && gameState.cultivation.techniques.length > 0 && (
                                <div className="mb-4">
                                    <div className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                        <Sword />
                                        Võ Công / Pháp Thuật
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {gameState.cultivation.techniques.map((tech, idx) => (
                                            <span
                                                key={idx}
                                                className="text-sm bg-purple-900/50 text-purple-300 px-3 py-2 rounded-lg border border-purple-700"
                                            >
                                                {tech}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Pills Stats */}
                            <div className="flex justify-between text-sm border-t border-purple-700/30 pt-3">
                                <span className="text-gray-500 flex items-center gap-1">
                                    <Pill />
                                    Đan Dược Đã Dùng:
                                </span>
                                <span className="text-emerald-400 font-bold">{gameState.cultivation.pills_consumed}</span>
                            </div>
                        </div>
                    )}

                    {/* World Info */}
                    {gameState.location && (
                        <div className="bg-slate-800/50 border-2 border-emerald-600/30 rounded-xl p-5 mb-6">
                            <h3 className="text-lg font-bold text-emerald-400 mb-3 flex items-center gap-2">
                                <MapPin />
                                Thông Tin Thế Giới
                            </h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <div className="text-xs text-gray-500 mb-1">Vị Trí Hiện Tại</div>
                                    <div className="font-bold text-emerald-300">{gameState.location.name}</div>
                                    <div className="text-xs text-gray-400 italic">{gameState.location.region}</div>
                                </div>
                                <div>
                                    <div className="text-xs text-gray-500 mb-1">Mật Độ Linh Khí</div>
                                    <div className="font-bold text-cyan-300">{gameState.location.qi_density}x</div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Sect Info */}
                    {gameState.sect_context && (
                        <div className="bg-slate-800/50 border-2 border-amber-600/30 rounded-xl p-5 mb-6">
                            <h3 className="text-lg font-bold text-amber-400 mb-3 flex items-center gap-2">
                                <YinYang />
                                Thông Tin Tông Môn
                            </h3>
                            <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                                {gameState.sect_context}
                            </p>
                        </div>
                    )}

                    {/* Needs Stats */}
                    {gameState.needs && (
                        <div className="bg-slate-800/50 border-2 border-rose-500/30 rounded-xl p-5 mb-6">
                            <h3 className="text-lg font-bold text-rose-400 mb-4 flex items-center gap-2">
                                <Heart />
                                Trạng Thái Cơ Thể
                            </h3>
                            <div className="space-y-3">
                                <div>
                                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                                        <span>No Bụng</span>
                                        <span className="text-rose-300">{Math.round(gameState.needs.hunger)}%</span>
                                    </div>
                                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-rose-500" style={{ width: `${gameState.needs.hunger}%` }} />
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                                        <span>Năng Lượng</span>
                                        <span className="text-yellow-300">{Math.round(gameState.needs.energy)}%</span>
                                    </div>
                                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-yellow-500" style={{ width: `${gameState.needs.energy}%` }} />
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                                        <span>Tâm Trạng</span>
                                        <span className="text-blue-300">{Math.round(gameState.needs.social)}%</span>
                                    </div>
                                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500" style={{ width: `${gameState.needs.social}%` }} />
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Relationships */}
                    {gameState.relationships && Object.keys(gameState.relationships).length > 0 && (
                        <div className="bg-slate-800/50 border-2 border-pink-500/30 rounded-xl p-5 mb-6">
                            <h3 className="text-lg font-bold text-pink-400 mb-4 flex items-center gap-2">
                                <Users />
                                Quan Hệ Xã Hội
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {Object.entries(gameState.relationships).map(([name, info]) => (
                                    <div key={name} className="bg-slate-900/50 border border-pink-500/20 rounded-lg p-3 flex justify-between items-center">
                                        <div>
                                            <div className="font-bold text-pink-300">{name}</div>
                                            <div className="text-xs text-gray-500 capitalize">{info.relationship_type}</div>
                                        </div>
                                        <div className="text-right">
                                            <div className={`text-sm font-bold ${info.affinity >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                {info.affinity > 0 ? '+' : ''}{info.affinity}
                                            </div>
                                            <div className="text-[10px] text-gray-600">Thiện cảm</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Character Story */}
                    {gameState.character_story && (
                        <div className="bg-slate-800/50 border-2 border-amber-600/30 rounded-xl p-5">
                            <h3 className="text-lg font-bold text-amber-400 mb-3 flex items-center gap-2">
                                <Scroll />
                                Tiểu Sử
                            </h3>
                            <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                                {gameState.character_story}
                            </p>
                        </div>
                    )}

                    {/* Game Stats */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="bg-slate-800/50 rounded-lg p-4 border border-cyan-600/30">
                            <div className="text-xs text-gray-500 mb-1">Số Lần Chơi</div>
                            <div className="text-2xl font-bold text-cyan-400">{gameState.turn_count}</div>
                        </div>
                        <div className="bg-slate-800/50 rounded-lg p-4 border border-indigo-600/30">
                            <div className="text-xs text-gray-500 mb-1 flex items-center gap-1">
                                <Brain />
                                Ký Ức
                            </div>
                            <div className="text-2xl font-bold text-indigo-400">{memoryCount}</div>
                        </div>
                        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-600">
                            <div className="text-xs text-gray-500 mb-1">Save ID</div>
                            <div className="text-[10px] text-gray-400 font-mono">{gameState.save_id}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export function InventoryModal({ gameState, onClose }: Omit<ModalProps, 'memoryCount'>) {
    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
            <div className="bg-slate-900/95 border-2 border-emerald-500/50 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto glow-jade">
                {/* Header */}
                <div className="sticky top-0 bg-gradient-to-r from-emerald-900/80 to-teal-900/80 backdrop-blur-xl p-6 border-b-2 border-emerald-600/50 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Backpack />
                        <h2 className="text-2xl font-bold text-emerald-300" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                            背包 / Balo
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors p-2"
                    >
                        <Close />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {gameState.resources ? (
                        <>
                            {/* Spirit Stones */}
                            <div className="bg-gradient-to-r from-emerald-900/30 to-teal-900/30 border-2 border-emerald-600/50 rounded-xl p-6">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <Gem />
                                        <div>
                                            <div className="text-sm text-gray-400">Linh Thạch</div>
                                            <div className="text-xs text-gray-500">Spirit Stones</div>
                                        </div>
                                    </div>
                                    <div className="text-4xl font-bold text-emerald-400">
                                        {gameState.resources.spirit_stones}
                                    </div>
                                </div>
                            </div>

                            {/* Pills */}
                            {gameState.resources.pills && Object.keys(gameState.resources.pills).length > 0 && (
                                <div>
                                    <h3 className="text-lg font-bold text-emerald-300 mb-3 flex items-center gap-2">
                                        <Pill />
                                        Đan Dược
                                    </h3>
                                    <div className="grid grid-cols-2 gap-3">
                                        {Object.entries(gameState.resources.pills).map(([name, qty]) => (
                                            <div key={name} className="bg-emerald-950/30 border border-emerald-700/50 rounded-lg p-4 flex justify-between items-center">
                                                <span className="text-gray-300">{name}</span>
                                                <span className="text-emerald-400 font-bold text-xl">x{qty}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Materials */}
                            {gameState.resources.materials && Object.keys(gameState.resources.materials).length > 0 && (
                                <div>
                                    <h3 className="text-lg font-bold text-teal-300 mb-3 flex items-center gap-2">
                                        <Scroll />
                                        Nguyên Liệu
                                    </h3>
                                    <div className="grid grid-cols-2 gap-3">
                                        {Object.entries(gameState.resources.materials).map(([name, qty]) => (
                                            <div key={name} className="bg-teal-950/30 border border-teal-700/50 rounded-lg p-4 flex justify-between items-center">
                                                <span className="text-gray-300">{name}</span>
                                                <span className="text-teal-400 font-bold text-xl">x{qty}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {(!gameState.resources.pills || Object.keys(gameState.resources.pills).length === 0) &&
                                (!gameState.resources.materials || Object.keys(gameState.resources.materials).length === 0) && (
                                    <div className="text-center py-12 text-gray-500">
                                        <Backpack />
                                        <p className="mt-4 italic">Balo trống. Hãy bắt đầu thu thập tài nguyên!</p>
                                    </div>
                                )}
                        </>
                    ) : (
                        <div className="text-center py-12 text-gray-500 italic">
                            Không có dữ liệu tài nguyên
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export function CodexModal({ gameState, memoryCount, onClose }: ModalProps) {
    const [activeTab, setActiveTab] = React.useState<'realms' | 'races' | 'talents' | 'pills' | 'world'>('realms');

    const categories = [
        { id: 'realms', label: 'Cảnh Giới', icon: <Flame /> },
        { id: 'races', label: 'Chủng Tộc', icon: <User /> },
        { id: 'talents', label: 'Thiên Phú', icon: <Sparkles /> },
        { id: 'pills', label: 'Đan Dược', icon: <Pill /> },
        { id: 'world', label: 'Thế Giới', icon: <MapPin /> },
    ];

    const realmsData = [
        { vn: 'Luyện Khí Kỳ', cn: 'Qi Refining', desc: 'Giai đoạn đầu tiên, cảm nhận và hấp thụ linh khí vào cơ thể. Chia làm 9 tầng.', power: '10 - 100' },
        { vn: 'Trúc Cơ Kỳ', cn: 'Foundation', desc: 'Nén linh khí dạng khí thành dạng lỏng, xây dựng nền móng đạo cơ. Tu thọ tăng lên 200 năm.', power: '100 - 1,000' },
        { vn: 'Kim Đan Kỳ', cn: 'Golden Core', desc: 'Linh lực hóa rắn thành Kim Đan. Bước vào ngưỡng cửa tu tiên thực sự. Tu thọ 500 năm.', power: '1,000 - 10,000' },
        { vn: 'Nguyên Anh Kỳ', cn: 'Nascent Soul', desc: 'Phá đan thành anh, linh hồn ngưng tụ thành thực thể. Có thể xuất hồn. Tu thọ 1,000 năm.', power: '10,000 - 100,000' },
        { vn: 'Hóa Thần Kỳ', cn: 'Spirit Transformation', desc: 'Nguyên anh hòa nhập thiên địa, sơ bộ nắm giữ quy tắc. Tu thọ 2,000 năm.', power: '100k - 1M' },
        { vn: 'Luyện Hư Kỳ', cn: 'Void Refinement', desc: 'Nhìn thấu hư không, phản hư quy chân. Tu thọ 5,000 năm.', power: '1M - 10M' },
    ];

    const racesData = [
        { name: 'Nhân Tộc', desc: 'Sinh ra yếu ớt nhưng có trí tuệ và khả năng lĩnh ngộ cao nhất. Tốc độ tu luyện nhanh, phù hợp mọi loại công pháp.', traits: ['Ngộ tính cao', 'Thể chất yếu'] },
        { name: 'Yêu Tộc', desc: 'Mang dòng máu thú, thể chất cường hãn, thọ nguyên dài lâu. Tu luyện chậm ở giai đoạn đầu nhưng cực mạnh về sau.', traits: ['Thể chất mạnh', 'Thọ nguyên cao'] },
        { name: 'Ma Tộc', desc: 'Hiếu chiến, tu luyện bằng cách hấp thụ ma khí hoặc đoạt lấy sinh cơ. Tiến cảnh cực nhanh nhưng dễ tẩu hỏa nhập ma.', traits: ['Sát phạt', 'Tiến cảnh nhanh'] },
        { name: 'Tiên Tộc', desc: 'Được trời đất ưu ái, sinh ra đã có linh lực. Số lượng cực hiếm, thường ẩn cư ở các tiên sơn.', traits: ['Linh lực thuần khiết', 'May mắn'] },
    ];

    const talentsData = [
        { name: 'Thiên Linh Căn', desc: 'Chỉ có một loại ngũ hành (Kim, Mộc, Thủy, Hỏa, Thổ). Tốc độ hấp thụ linh khí cực nhanh, không gặp nút thắt trước Nguyên Anh.', rarity: 'Cực Hiếm' },
        { name: 'Dị Linh Căn', desc: 'Biến dị từ ngũ hành (Lôi, Phong, Băng...). Sức chiến đấu vượt trội so với ngũ hành thông thường.', rarity: 'Hiếm' },
        { name: 'Song Linh Căn', desc: 'Có hai loại ngũ hành. Tốc độ tu luyện khá, là nòng cốt của các tông môn lớn.', rarity: 'Khá' },
        { name: 'Tam Linh Căn', desc: 'Có ba loại ngũ hành. Tốc độ trung bình, cần nhiều đan dược hỗ trợ.', rarity: 'Phổ biến' },
        { name: 'Tạp Linh Căn', desc: 'Bốn hoặc năm loại ngũ hành. Tạp chất nhiều, tu luyện cực khó khăn, thường dừng ở Luyện Khí.', rarity: 'Rất phổ biến' },
    ];

    const pillsData = [
        { name: 'Tụ Khí Đan', desc: 'Tăng tốc độ hấp thụ linh khí cho tu sĩ Luyện Khí Kỳ.', effect: '+Kinh nghiệm' },
        { name: 'Trúc Cơ Đan', desc: 'Đan dược trân quý giúp tăng tỷ lệ đột phá lên Trúc Cơ Kỳ.', effect: 'Đột phá Trúc Cơ' },
        { name: 'Tẩy Tủy Đan', desc: 'Loại bỏ tạp chất trong cơ thể, cải thiện tư chất tu luyện.', effect: '+Thiên phú' },
        { name: 'Hồi Huyết Đan', desc: 'Hồi phục thương thế nhanh chóng.', effect: 'Hồi máu' },
        { name: 'Định Nhan Đan', desc: 'Giữ gìn dung mạo trẻ mãi không già.', effect: 'Thẩm mỹ' },
    ];

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
            <div className="bg-slate-900/95 border-2 border-indigo-500/50 rounded-2xl max-w-5xl w-full h-[85vh] flex overflow-hidden glow-gold">
                {/* Sidebar */}
                <div className="w-64 bg-slate-950/50 border-r border-indigo-500/30 p-4 flex flex-col gap-2">
                    <div className="flex items-center gap-3 px-4 py-4 mb-2 border-b border-indigo-500/30">
                        <Book />
                        <h2 className="text-xl font-bold text-indigo-300" style={{ fontFamily: "'Noto Serif SC', serif" }}>
                            Bách Khoa
                        </h2>
                    </div>
                    {categories.map((cat) => (
                        <button
                            key={cat.id}
                            onClick={() => setActiveTab(cat.id as any)}
                            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-left ${activeTab === cat.id
                                ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/50 shadow-[0_0_10px_rgba(99,102,241,0.2)]'
                                : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
                                }`}
                        >
                            {cat.icon}
                            <span className="font-medium">{cat.label}</span>
                        </button>
                    ))}
                </div>

                {/* Content Area */}
                <div className="flex-1 flex flex-col min-w-0">
                    {/* Header */}
                    <div className="h-16 border-b border-indigo-500/30 flex items-center justify-between px-6 bg-slate-900/50 backdrop-blur-md">
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                            {categories.find(c => c.id === activeTab)?.icon}
                            {categories.find(c => c.id === activeTab)?.label}
                        </h3>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-full"
                        >
                            <Close />
                        </button>
                    </div>

                    {/* Scrollable Content */}
                    <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                        {activeTab === 'realms' && (
                            <div className="space-y-4">
                                <div className="bg-indigo-900/20 border border-indigo-500/30 rounded-lg p-4 mb-6">
                                    <p className="text-gray-300 italic">
                                        "Tu tiên là nghịch thiên cải mệnh. Mỗi cảnh giới là một lần lột xác, thoát thai hoán cốt, tiến gần hơn đến đại đạo."
                                    </p>
                                </div>
                                <div className="grid gap-4">
                                    {realmsData.map((realm, idx) => (
                                        <div key={idx} className="bg-slate-800/50 border border-indigo-500/20 rounded-xl p-4 hover:border-indigo-500/50 transition-colors">
                                            <div className="flex justify-between items-start mb-2">
                                                <div>
                                                    <div className="text-lg font-bold text-indigo-300">{idx + 1}. {realm.vn}</div>
                                                    <div className="text-xs text-gray-500 font-mono">{realm.cn}</div>
                                                </div>
                                                <div className="text-xs font-bold bg-indigo-950 px-2 py-1 rounded text-indigo-400 border border-indigo-500/30">
                                                    Lực chiến: {realm.power}
                                                </div>
                                            </div>
                                            <p className="text-sm text-gray-400">{realm.desc}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'races' && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {racesData.map((race, idx) => (
                                    <div key={idx} className="bg-slate-800/50 border border-emerald-500/20 rounded-xl p-5 hover:border-emerald-500/50 transition-colors">
                                        <div className="text-lg font-bold text-emerald-300 mb-2">{race.name}</div>
                                        <p className="text-sm text-gray-400 mb-4 min-h-[40px]">{race.desc}</p>
                                        <div className="flex flex-wrap gap-2">
                                            {race.traits.map((trait, tIdx) => (
                                                <span key={tIdx} className="text-xs bg-emerald-950/50 text-emerald-400 px-2 py-1 rounded border border-emerald-500/30">
                                                    {trait}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {activeTab === 'talents' && (
                            <div className="space-y-4">
                                {talentsData.map((talent, idx) => (
                                    <div key={idx} className="bg-slate-800/50 border border-purple-500/20 rounded-xl p-4 flex items-center gap-4 hover:border-purple-500/50 transition-colors">
                                        <div className="w-12 h-12 rounded-full bg-purple-900/30 flex items-center justify-center border border-purple-500/30 text-2xl">
                                            ⚡
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex justify-between items-center mb-1">
                                                <div className="font-bold text-purple-300">{talent.name}</div>
                                                <span className="text-xs text-purple-200 bg-purple-900/50 px-2 py-0.5 rounded border border-purple-500/30">
                                                    {talent.rarity}
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-400">{talent.desc}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {activeTab === 'pills' && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {pillsData.map((pill, idx) => (
                                    <div key={idx} className="bg-slate-800/50 border border-amber-500/20 rounded-xl p-4 flex gap-4 hover:border-amber-500/50 transition-colors">
                                        <div className="mt-1">
                                            <Pill />
                                        </div>
                                        <div>
                                            <div className="font-bold text-amber-300 mb-1">{pill.name}</div>
                                            <p className="text-xs text-gray-400 mb-2">{pill.desc}</p>
                                            <span className="text-xs font-bold text-emerald-400">
                                                Hiệu quả: {pill.effect}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {activeTab === 'world' && (
                            <div className="space-y-6">
                                <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-6">
                                    <h4 className="text-lg font-bold text-cyan-300 mb-4 flex items-center gap-2">
                                        <User />
                                        Nhân Vật Của Bạn
                                    </h4>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-slate-900/50 p-3 rounded border border-slate-700">
                                            <div className="text-xs text-gray-500">Tuổi Thọ Đã Sống</div>
                                            <div className="text-xl font-bold text-white">{gameState.age} năm</div>
                                        </div>
                                        <div className="bg-slate-900/50 p-3 rounded border border-slate-700">
                                            <div className="text-xs text-gray-500">Ký Ức Đã Ghi Nhớ</div>
                                            <div className="text-xl font-bold text-indigo-400">{memoryCount} sự kiện</div>
                                        </div>
                                    </div>
                                </div>

                                {gameState.location && (
                                    <div className="bg-slate-800/50 border border-emerald-500/30 rounded-xl p-6">
                                        <h4 className="text-lg font-bold text-emerald-300 mb-4 flex items-center gap-2">
                                            <MapPin />
                                            Vị Trí Hiện Tại
                                        </h4>
                                        <div className="space-y-2">
                                            <div className="flex justify-between border-b border-slate-700 pb-2">
                                                <span className="text-gray-400">Địa Danh</span>
                                                <span className="text-emerald-400 font-bold">{gameState.location.name}</span>
                                            </div>
                                            <div className="flex justify-between border-b border-slate-700 pb-2">
                                                <span className="text-gray-400">Khu Vực</span>
                                                <span className="text-gray-200">{gameState.location.region}</span>
                                            </div>
                                            <div className="flex justify-between border-b border-slate-700 pb-2">
                                                <span className="text-gray-400">Mật Độ Linh Khí</span>
                                                <span className="text-cyan-400">{gameState.location.qi_density}x</span>
                                            </div>
                                        </div>
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
