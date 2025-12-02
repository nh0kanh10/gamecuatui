---
description: Cleanup test files and temporary code
---

# Cleanup Test Files Workflow

Quy trình dọn dẹp files test và code tạm thời:

## 1. Review test folder
Kiểm tra folder `test/` để xem files nào cần giữ lại

## 2. Backup if needed
Nếu có code test hữu ích, backup trước khi xóa:
```powershell
Copy-Item -Path "test/" -Destination "test-backup-$(Get-Date -Format 'yyyyMMdd')" -Recurse
```

// turbo
## 3. Delete test folder
```powershell
Remove-Item -Path "test/" -Recurse -Force
```

// turbo
## 4. Clean temporary files
```powershell
Get-ChildItem -Path . -Include *.tmp,*.temp -Recurse | Remove-Item -Force
```

## 5. Verify cleanup
Kiểm tra lại structure để đảm bảo chỉ còn source code chính
