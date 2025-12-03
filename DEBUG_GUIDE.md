# 🔍 Debug Guide - Path Issues

## 📋 Test Scripts Created

### **1. TEST_PATH_DEBUG.bat**
Kiểm tra tất cả path operations:
- Current directory
- Script directory
- GAME_DIR setup
- pushd/popd operations
- Path validity

**Chạy:**
```batch
TEST_PATH_DEBUG.bat
```

---

### **2. TEST_START_COMMAND.bat**
Test start command với 2 methods:
- Method 1: pushd method (như trong scripts)
- Method 2: Direct path method

**Chạy:**
```batch
TEST_START_COMMAND.bat
```

**Sẽ mở 2 windows để test - xem window nào lỗi!**

---

### **3. TEST_SIMPLE.bat**
Test đơn giản nhất - chỉ cd và chạy npm:
- Không dùng start command
- Chạy trực tiếp trong current window

**Chạy:**
```batch
TEST_SIMPLE.bat
```

---

## 🔍 Manual Test Commands

### **Test 1: Check paths**
```batch
cd /d "D:\GameBuild\cultivation-sim"
echo %CD%
cd cultivation-ui
echo %CD%
```

### **Test 2: Test pushd**
```batch
cd /d "D:\GameBuild\cultivation-sim"
pushd cultivation-ui
echo %CD%
set "TEST_PATH=%CD%"
popd
echo After popd: %CD%
echo TEST_PATH: "%TEST_PATH%"
```

### **Test 3: Test start command**
```batch
cd /d "D:\GameBuild\cultivation-sim"
pushd cultivation-ui
set "UI_PATH=%CD%"
popd
start "TEST" cmd /k "cd /d "%UI_PATH%" && echo Path: && cd && pause"
```

### **Test 4: Direct start**
```batch
cd /d "D:\GameBuild\cultivation-sim\cultivation-ui"
start "TEST" cmd /k "cd /d "%CD%" && echo Path: && cd && pause"
```

---

## 📊 What to Look For

### **In TEST_PATH_DEBUG.bat:**
1. ✅ GAME_DIR có đúng không?
2. ✅ cultivation-sim folder có tồn tại không?
3. ✅ pushd có thành công không?
4. ✅ UI_FULL_PATH có được set đúng không?
5. ✅ Path có tồn tại không?
6. ✅ package.json có tồn tại không?

### **In TEST_START_COMMAND.bat:**
1. ✅ Window nào mở được?
2. ✅ Window nào báo lỗi?
3. ✅ Lỗi cụ thể là gì?

### **In TEST_SIMPLE.bat:**
1. ✅ cd có thành công không?
2. ✅ npm run dev có chạy được không?

---

## 🎯 Expected Results

### **If all OK:**
- ✅ All paths resolve correctly
- ✅ pushd/popd work
- ✅ start command opens window
- ✅ npm run dev starts

### **If error:**
- ❌ Check which step fails
- ❌ Note exact error message
- ❌ Check path format

---

## 📝 Report Back

Sau khi chạy tests, cho mình biết:

1. **TEST_PATH_DEBUG.bat output:**
   - GAME_DIR value?
   - pushd success?
   - UI_FULL_PATH value?
   - Path exists?

2. **TEST_START_COMMAND.bat:**
   - Window nào mở được?
   - Lỗi cụ thể là gì?

3. **TEST_SIMPLE.bat:**
   - npm run dev có chạy được không?

---

## 🔧 Quick Fixes Based on Results

### **If pushd fails:**
→ Có thể cultivation-ui không tồn tại hoặc permission issue

### **If start command fails:**
→ Có thể path có ký tự đặc biệt hoặc quote issue

### **If npm fails:**
→ Có thể node_modules chưa install

---

**Chạy các test scripts và báo lại kết quả!** 🔍

