import time
import subprocess
import psutil
import os
import threading
import logging

# Cấu hình logging cho system_log.txt với mã hóa UTF-8
BOT_LOG = os.path.join(os.getenv('APPDATA'), "system_log.txt")
logging.basicConfig(filename=BOT_LOG, level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')

# Đường dẫn bot
BOT_PATH = os.path.join(os.getenv('APPDATA'), "SystemUpdater.exe")
BOT_NAME = "SystemUpdater.exe"
running_pids = set()

def stop_existing_bots():
    """Dừng tất cả các tiến trình bot hiện có, ngoại trừ tiến trình hiện tại"""
    current_pid = os.getpid()  # lấy PID của chính tiến trình hiện tại
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == BOT_NAME and proc.info['pid'] != current_pid:
            try:
                pid = proc.info['pid']
                proc.kill()
                proc.wait(timeout=5)  # đợi tiến trình thực sự kết thúc
                print(f"[WATCHDOG] Đã dừng bot với PID: {pid}")
                logging.info(f"[WATCHDOG] Đã dừng bot với PID: {pid}")
                if pid in running_pids:
                    running_pids.remove(pid)
            except Exception as e:
                print(f"[WATCHDOG] Lỗi khi dừng bot với PID {proc.info['pid']}: {e}")
                logging.error(f"Lỗi khi dừng bot với PID {proc.info['pid']}: {e}")

def watchdog():
    """Watchdog để khởi động lại bot nếu bị kill"""
    stop_file = os.path.join(os.getenv('APPDATA'), "stop_bot.txt")
    
    while True:
        if os.path.exists(stop_file):
            print("[WATCHDOG] Tín hiệu dừng nhận được, thoát.")
            logging.info("[WATCHDOG] Tín hiệu dừng nhận được, thoát.")
            break
        
        time.sleep(20)  # Thời gian chờ 20 giây
        try:
            bot_running = False
            current_pids = set()
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == BOT_NAME:
                    current_pids.add(proc.info['pid'])
                    bot_running = True
                    print(f"[WATCHDOG] Tìm thấy bot đang chạy với PID: {proc.info['pid']}")
                    logging.info(f"[WATCHDOG] Tìm thấy bot đang chạy với PID: {proc.info['pid']}")
            
            running_pids.clear()
            running_pids.update(current_pids)

            if not bot_running:
                stop_existing_bots()  # Dừng tất cả bot cũ trước khi khởi động lại
                print("[WATCHDOG] Bot không chạy, đang khởi động lại...")
                logging.info("[WATCHDOG] Bot không chạy, đang khởi động lại...")
                process = subprocess.Popen([BOT_PATH], creationflags=subprocess.CREATE_NEW_CONSOLE)
                running_pids.add(process.pid)
                print(f"[WATCHDOG] Đã khởi động bot với PID: {process.pid}")
                logging.info(f"[WATCHDOG] Đã khởi động bot với PID: {process.pid}")
        except Exception as e:
            print(f"[WATCHDOG] Lỗi: {e}")
            logging.error(f"Lỗi trong watchdog: {e}")

def main_task():
    """Nhiệm vụ chính của bot"""
    while True:
        try:
            print("[MAIN_TASK] Bot đang chạy bình thường")
            logging.info("Bot đang chạy bình thường")
            time.sleep(30)
        except Exception as e:
            print(f"[MAIN_TASK] Lỗi: {e}")
            logging.error(f"Lỗi trong main_task: {e}")

# Chạy các luồng
watchdog_thread = threading.Thread(target=watchdog, daemon=True)
main_thread = threading.Thread(target=main_task, daemon=True)

watchdog_thread.start()
main_thread.start()

# Giữ bot chạy ngầm
print("[BOT] Bot khởi động thành công!")
while True:
    print("[BOT] Đang hoạt động...")
    logging.info("Bot đang hoạt động...")
    time.sleep(5)