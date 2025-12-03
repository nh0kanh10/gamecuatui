# Hệ thống Logging - Cultivation Simulator

## Tổng quan

Hệ thống logging đã được tích hợp vào server và game để ghi lại tất cả các lỗi và hoạt động chi tiết.

## Vị trí file log

- **Thư mục**: `cultivation-sim/logs/`
- **Tên file**: `server_YYYYMMDD_HHMMSS.log`
- **Ví dụ**: `server_20251203_143022.log`

## Nội dung log

### Server Log (`server.py`)
- Tất cả HTTP requests và responses
- Thời gian xử lý mỗi request
- Lỗi khi khởi tạo game
- Lỗi khi xử lý actions
- Lỗi khi lấy game state
- Stack traces đầy đủ cho mọi lỗi

### Game Log (`game.py`)
- Khởi tạo game instance
- Character creation process
- Year turn processing
- ECS systems ticks
- Memory operations
- AI agent calls
- State updates và saves

## Cách xem log

### 1. Trong khi game đang chạy

File log được tạo tự động khi server khởi động. Bạn có thể:

```bash
# Xem log real-time (Windows PowerShell)
Get-Content logs\server_*.log -Wait -Tail 50

# Hoặc mở file log trong Notepad/VS Code
notepad logs\server_*.log
```

### 2. Tìm lỗi cụ thể

```bash
# Tìm tất cả lỗi ERROR
findstr /i "ERROR" logs\server_*.log

# Tìm lỗi liên quan đến GEMINI_API_KEY
findstr /i "GEMINI_API_KEY" logs\server_*.log

# Tìm lỗi liên quan đến AI agent
findstr /i "AI agent" logs\server_*.log
```

### 3. Xem log mới nhất

File log được sắp xếp theo thời gian, file mới nhất sẽ có timestamp mới nhất trong tên.

## Các loại log messages

- **INFO**: Thông tin bình thường (requests, successful operations)
- **WARNING**: Cảnh báo (missing data, fallback to defaults)
- **ERROR**: Lỗi nghiêm trọng (failed operations, exceptions)
- **CRITICAL**: Lỗi cực kỳ nghiêm trọng (server crash)

## Ví dụ log entries

```
2025-12-03 14:30:22 - __main__ - INFO - Starting Cultivation Simulator Server
2025-12-03 14:30:22 - __main__ - INFO - Log file: logs\server_20251203_143022.log
2025-12-03 14:30:25 - __main__ - INFO - Request: POST /game/new
2025-12-03 14:30:25 - game - INFO - Starting new game: player_name=Người Tu Tiên
2025-12-03 14:30:25 - game - INFO - Character creation: gender=Nam, talent=Thiên Linh Căn
2025-12-03 14:30:26 - game - ERROR - Error calling AI agent: API key not found
2025-12-03 14:30:26 - __main__ - ERROR - Failed to start game: API key not found
```

## Troubleshooting

### Server không khởi động được

1. Kiểm tra log file trong `logs/`
2. Tìm dòng có "ERROR" hoặc "CRITICAL"
3. Đọc stack trace để biết nguyên nhân

### Game không tạo được character

1. Kiểm tra log cho dòng "Character creation"
2. Tìm lỗi liên quan đến:
   - `GEMINI_API_KEY`
   - `CultivationAgent`
   - `World Database`
   - `Memory`

### Lỗi kết nối từ UI

1. Kiểm tra log cho HTTP requests
2. Xem status code (500 = server error)
3. Đọc error message trong log

## Lưu ý

- Log files có thể lớn nếu chơi lâu
- Xóa log cũ định kỳ để tiết kiệm dung lượng
- Log files chứa thông tin nhạy cảm (không commit vào git)

