import time
import subprocess
import psutil
import os
import logging

# Cấu hình logging
WATCHDOG_LOG = os.path.join(os.getenv('APPDATA'), "watchdog_log.txt")
logging.basicConfig(filename=WATCHDOG_LOG, level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')

# Đường dẫn đến bot
BOT_PATH = os.path.join(os.getenv('APPDATA'), "SystemUpdater.exe")
BOT_NAME = "SystemUpdater.exe"
STOP_FILE = os.path.join(os.getenv('APPDATA'), "stop_bot.txt")

def stop_existing_bots():
    """Dừng tất cả các tiến trình bot hiện có"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == BOT_NAME:
            try:
                pid = proc.info['pid']
                proc.kill()
                logging.info(f"[WATCHDOG] Đã dừng bot với PID: {pid}")
                time.sleep(1)  # Đợi 1 giây để đảm bảo tiến trình dừng
            except Exception as e:
                logging.error(f"[WATCHDOG] Lỗi khi dừng bot với PID {pid}: {e}")

def watchdog():
    """Chương trình giám sát và khởi động lại bot"""
    while True:
        if os.path.exists(STOP_FILE):
            logging.info("[WATCHDOG] Tín hiệu dừng nhận được, thoát.")
            break
        
        bot_running = False
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == BOT_NAME:
                bot_running = True
                logging.info(f"[WATCHDOG] Tìm thấy bot đang chạy với PID: {proc.info['pid']}")
        
        if not bot_running:
            stop_existing_bots()
            logging.info("[WATCHDOG] Bot không chạy, đang khởi động lại...")
            if os.path.exists(BOT_PATH):
                try:
                    process = subprocess.Popen([BOT_PATH], creationflags=subprocess.DETACHED_PROCESS)
                    logging.info(f"[WATCHDOG] Đã khởi động bot với PID: {process.pid}")
                except Exception as e:
                    logging.error(f"[WATCHDOG] Lỗi khi khởi động bot: {e}")
            else:
                logging.error(f"[WATCHDOG] Không tìm thấy {BOT_PATH} để khởi động!")
        
        time.sleep(20)  # Kiểm tra lại sau 20 giây

if __name__ == "__main__":
    logging.info("[WATCHDOG] Watchdog khởi động thành công!")
    watchdog()