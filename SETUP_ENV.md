# 🔑 Setup Environment Variables

## Tạo .env File

Tạo file `.env` trong root folder (`D:\GameBuild\.env`) với nội dung:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

## Lấy API Key

1. Truy cập: https://aistudio.google.com/app/apikey
2. Đăng nhập với Google account
3. Tạo API key mới
4. Copy và paste vào `.env` file

## Format .env File

```env
# Required
GEMINI_API_KEY=AIzaSy...your_key_here

# Optional
GEMINI_MODEL=gemini-2.0-flash
```

## ⚠️ Lưu Ý

- **KHÔNG** commit `.env` file vào git
- **KHÔNG** chia sẻ API key
- File `.env` phải ở **root folder** (cùng cấp với `server.py`)

## ✅ Verify

Sau khi tạo `.env`, restart server:
```bash
python server.py
```

Nếu thấy warning về API key → Kiểm tra lại `.env` file.

---

**Status**: ✅ Ready to Setup

