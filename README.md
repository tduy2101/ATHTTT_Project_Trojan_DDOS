# 🧮 Trojan Calculator

## 📌 Tổng Quan

Trojan Calculator là một **mô phỏng ứng dụng trojan** được ngụy trang dưới dạng **máy tính cầm tay**, trong khi chạy **bot ngầm** để thực hiện các hoạt động như:

- Ghi log hệ thống
- Tấn công DDoS (ở các phiên bản nâng cao)

Dự án minh họa cách thức một trojan hoạt động: **giao diện giả mạo**, **cơ chế tự duy trì**, và **khả năng tấn công mạng**.

> ⚠️ **Lưu ý**: Đây là dự án phục vụ **mục đích giáo dục**. Không được sử dụng để gây hại. Hãy tuân thủ **pháp luật và đạo đức** trong nghiên cứu và thử nghiệm.

---

## ✨ Tính Năng Chính

- 🧮 Giao diện máy tính (Tkinter) làm lớp ngụy trang
- 🤖 Bot ngầm thực hiện:
  - Ghi log
  - Tấn công DDoS: HTTP Flood, TCP Flood, UDP Flood, Slowloris
- 🔄 Cơ chế duy trì: tự động khởi động cùng hệ thống (Registry, Startup folder)
- 🛡️ Watchdog: đảm bảo bot luôn hoạt động, tự phục hồi khi bị tắt
- 📝 Ghi log hoạt động để theo dõi và gỡ lỗi

---

## 🧬 Các Phiên Bản

| Phiên bản | Tính năng chính |
|-----------|-----------------|
| **V1**    | Hiện cửa sổ console để theo dõi bot (chưa có icon) |
| **V2**    | Ẩn console, log ra file |
| **V3**    | Watchdog tách riêng, tự khởi động lại khi bị kill |
| **V4**    | Tích hợp bot DDoS vào trojan chính |

---

## ⚙️ Yêu Cầu

- Python 3.x
- Thư viện: `psutil`, `cryptography`, `tkinter`, `pywin32`
- **PyInstaller** để đóng gói thành `.exe`
- Hệ điều hành: **Windows**

---

## 🚀 Cài Đặt

```bash
# Clone repository
git clone https://github.com/yourusername/trojan-calculator.git
cd trojan-calculator

# Cài dependencies
pip install -r requirements.txt
```

> 📂 Chi tiết cách xây dựng và chạy từng phiên bản được mô tả trong các file README riêng trong từng thư mục phiên bản (V1, V2, V3).

## 🔐 An Toàn & Đạo Đức

- Dự án chỉ nhằm mục đích nghiên cứu và giáo dục.
- Không sử dụng mã nguồn cho các mục đích gây hại hoặc thử nghiệm trên hệ thống không được phép.
- Chỉ thực hiện mô phỏng trên hệ thống bạn sở hữu hoặc được sự cho phép rõ ràng.
