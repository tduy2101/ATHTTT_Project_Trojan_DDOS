# Trojan Calculator - Phiên Bản 3 (V3)

## Tổng Quan

Phiên bản 3 của dự án Trojan Calculator tách watchdog thành một tiến trình độc lập, cho phép tự khởi động lại bot (`SystemUpdater.exe`) khi bị kill trong Task Manager. Trojan tiếp tục ngụy trang dưới dạng máy tính cầm tay (GUI Tkinter) với icon tùy chỉnh.

## Tính Năng

- **Giao Diện Máy Tính Cầm Tay**: Giao diện tính toán cơ bản với icon tùy chỉnh.
- **Bot Ngầm (`SystemUpdater.exe`)**: 
  - Chạy ngầm, ghi log định kỳ vào `%APPDATA%\system_log.txt`.
  - Không chứa watchdog (đã tách ra).
- **Watchdog (`watchdog.exe`)**: 
  - Độc lập, giám sát và khởi động lại `SystemUpdater.exe` nếu bị dừng.
  - Ghi log vào `%APPDATA%\watchdog_log.txt`.
- **Cơ Chế Duy Trì**: Thêm `watchdog.exe` vào Registry hoặc Startup folder để chạy khi khởi động máy.
- **Tự Hủy**: Dọn dẹp khi thoát, xóa file và Registry.

## Cấu Trúc

- **`calculator_trojan_V3.py`**: Script chính, khởi chạy GUI, triển khai bot và watchdog, thiết lập persistence.
- **`bot_test_V3.py`**: Script bot (đóng gói thành `SystemUpdater.exe`) chạy ngầm và ghi log.
- **`watchdog.py`**: Script watchdog (đóng gói thành `watchdog.exe`) giám sát bot.

## Cách Xây Dựng và Chạy

### Đóng Gói `bot_test_V3.py`
```bash
pyinstaller --noconsole --onefile --icon=SystemUpdater.ico --hidden-import=psutil bot_test_V3.py
copy dist\bot_test_V3.exe SystemUpdater.exe
```

### Đóng Gói `watchdog.py`
```bash
pyinstaller --noconsole --onefile --icon=watchdog.ico --hidden-import=psutil watchdog.py
copy dist\watchdog.exe watchdog.exe
```

### Đóng Gói `calculator_trojan_V3.py`
- Đảm bảo `SystemUpdater.exe` và `watchdog.exe` đã có trong thư mục hiện tại.
```bash
pyinstaller --noconsole --onefile --icon=calculator.ico --add-data "SystemUpdater.exe;." --add-data "watchdog.exe;." --hidden-import=psutil --hidden-import=tkinter --hidden-import=pywin32 calculator_trojan_V3.py
```

### Chạy
- Chạy `calculator_trojan_V3.exe` để mở giao diện tính toán.
- Bot và watchdog sẽ chạy ngầm.
- Kiểm tra `%APPDATA%\system_log.txt` (bot) và `%APPDATA%\watchdog_log.txt` (watchdog) để theo dõi.

## Luồng Dữ Liệu

1. **Khởi Động Chương Trình**:
   - Chạy `calculator_trojan_V3.exe`.
   - Kiểm tra single instance: Ghi PID vào `%APPDATA%\calculator.pid`, thoát nếu PID cũ còn chạy.
   - Cấu hình log: Ghi vào `%APPDATA%\trojan.log`.
   - Thread `drop_bot()`:
     - Copy `SystemUpdater.exe` và `watchdog.exe` vào `%APPDATA%`.
     - Dừng tiến trình cũ bằng `psutil.process_iter()`.
     - Khởi động bot và watchdog với `subprocess.DETACHED_PROCESS`.
     - Thiết lập persistence: Thêm `watchdog.exe` vào Registry (`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`) hoặc Startup folder.
   - Chạy GUI calculator.

2. **Hoạt Động Bot (`SystemUpdater.exe`)**:
   - Chạy ngầm, ghi log "[MAIN_TASK] Bot đang chạy bình thường" vào `%APPDATA%\system_log.txt` mỗi 30 giây.

3. **Hoạt Động Watchdog (`watchdog.exe`)**:
   - Chạy ngầm, kiểm tra `SystemUpdater.exe` mỗi 20 giây.
   - Ghi log vào `%APPDATA%\watchdog_log.txt`.
   - Khởi động lại `SystemUpdater.exe` nếu bị kill.

4. **End Task và Khởi Động Lại**:
   - Kill `SystemUpdater.exe` trong Task Manager, watchdog phát hiện và khởi động lại sau tối đa 20 giây.

5. **Tự Hủy Khi Thoát**:
   - Nhấn "Exit" trên GUI, tạo `%APPDATA%\stop_bot.txt` với nội dung "stop".
   - Dừng `SystemUpdater.exe` và `watchdog.exe`, xóa file, Registry, và log.

6. **Khởi Động Lại Máy**:
   - `watchdog.exe` tự chạy từ Registry/Startup, khởi động `SystemUpdater.exe` nếu cần.

## Hạn Chế

- Bot vẫn chỉ ghi log, chưa có chức năng tấn công.
- Cần quyền Administrator để truy cập `%APPDATA%` và Registry.

## Lưu Ý

- Đảm bảo file icon `SystemUpdater.ico`, `watchdog.ico`, và `calculator.ico` có trong thư mục dự án.
