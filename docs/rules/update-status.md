# Rule: Cập Nhật Trạng Thái Dự Án

## Khi Nào Cập Nhật PROJECT_STATUS.md

File này là **nguồn thông tin chính** về tiến độ dự án.

## Điều Kiện Cập Nhật

Cập nhật `PROJECT_STATUS.md` khi:

1. ✅ **Hoàn thành task** - Đánh dấu xong, update tiến độ phase
2. 🚀 **Bắt đầu phase mới** - Update trạng thái phase hiện tại
3. 🚧 **Gặp blockers** - Ghi lại vấn đề đang chặn tiến độ
4. 🏗️ **Thay đổi kiến trúc** - Ghi lại thay đổi gì và tại sao
5. 💾 **Kết thúc work session** - Tóm tắt đã làm được gì
6. 👀 **Trước khi review** - Đảm bảo status cập nhật

## Các Phần Cần Update

### Luôn Update
- `Last Updated` - timestamp ở đầu file
- `Current Phase` - nếu có thay đổi
- Checklist items - đánh dấu done/in-progress
- `Update Log` - thêm entry mới với ngày

### Update Nếu Có Thay Đổi
- `Current Status` section
- `Limitations` section
- `Known Issues` section
- `Next Immediate Steps`

### Hiếm Khi Update
- `Phase Progress` definitions - chỉ khi scope thay đổi
- `Success Metrics` - chỉ khi mục tiêu thay đổi

## Template Cập Nhật

Khi thêm vào Update Log:

```markdown
### [YYYY-MM-DD HH:MM] - [Tóm tắt ngắn]
**Đã hoàn thành**:
- Item 1
- Item 2

**Đang làm**:
- Item A
- Item B

**Blockers**:
- Mô tả blocker (hoặc "Không có")

**Tiếp theo**:
- Bước tiếp 1
- Bước tiếp 2
```

## Vị Trí File

- **File**: `d:\GameBuild\PROJECT_STATUS.md`
- **Loại**: Root-level status tracker
- **Quan trọng**: HIGH - luôn check trước khi làm việc

## Files Liên Quan

Khi update status, cân nhắc update thêm:
- `README.md` - nếu architecture thay đổi
- Docs của phase hiện tại - nếu có thay đổi lớn

---

**Nhớ**: PROJECT_STATUS.md là **nguồn chân lý** về "hiện tại chúng ta đang ở đâu?"
