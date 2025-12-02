# ✅ Prompt Fix - Mô Tả Cụ Thể Thay Vì Câu Hỏi

## 🎯 Vấn Đề

AI thường kết thúc bằng câu hỏi tu từ thay vì mô tả cụ thể:
- ❌ "Liệu phía sau cánh cửa này là gì? Hy vọng, hay tuyệt vọng?"
- ❌ "Chỉ có bước qua nó, ngươi mới có thể biết được."

## ✅ Giải Pháp

Đã thêm **Rule #7: MÔ TẢ CỤ THỂ - KHÔNG ĐẶT CÂU HỎI** vào system instruction:

### Quy Tắc Vàng
- ✅ LUÔN mô tả những gì xảy ra
- ✅ Cho thông tin CỤ THỂ về môi trường mới
- ✅ Mô tả những gì player THẤY/NGHE/CẢM NHẬN
- ✅ Đưa ra LỰA CHỌN RÕ RÀNG nếu có nhiều hướng
- ❌ KHÔNG kết thúc bằng câu hỏi tu từ
- ❌ KHÔNG để player "tự đoán"

### Ví Dụ

**✅ ĐÚNG:**
```
Ngươi đẩy cánh cửa sắt nặng nề. Tiếng rít chói tai vang lên khi cánh cửa từ từ mở ra. 
Phía sau là một hành lang dài, tối tăm. Ánh sáng yếu ớt từ những ngọn đuốc trên tường 
chiếu xuống, để lộ những bức tranh cổ kính mô tả các cảnh chiến đấu đẫm máu. 
Không khí ẩm mốc, mang theo mùi tanh của máu cũ và xương mục. Ở cuối hành lang, 
ngươi thấy một cánh cửa khác, và từ khe cửa đó lọt ra ánh sáng đỏ rực cùng tiếng 
gầm gừ của thú dữ. Bên trái có một cầu thang dẫn lên tầng trên.
```

**❌ SAI:**
```
Liệu phía sau cánh cửa này là gì? Hy vọng, hay tuyệt vọng? Thiên đường, hay địa ngục? 
Chỉ có bước qua nó, ngươi mới có thể biết được.
```

## 📝 Files Updated

1. **engine/ai/gemini_agent.py**
   - Thêm Rule #7 vào system instruction
   - Thêm ví dụ cụ thể về di chuyển
   - Thêm reminder trong prompt

2. **data/prompts/game-master.md**
   - Cập nhật DO/DON'T guidelines
   - Thêm example về movement
   - Cập nhật checklist

## 🎮 Kết Quả Mong Đợi

Khi player di chuyển/khám phá, AI sẽ:
- ✅ Mô tả cụ thể cảnh vật, vật thể, NPCs
- ✅ Cho biết những gì player thấy/nghe/cảm nhận
- ✅ Liệt kê các lựa chọn rõ ràng (nếu có)
- ✅ Không kết thúc bằng câu hỏi tu từ

---

**Status**: ✅ Fixed - Ready to Test!



