import time
import os
import logging

# Cấu hình logging
BOT_LOG = os.path.join(os.getenv('APPDATA'), "system_log.txt")
logging.basicConfig(filename=BOT_LOG, level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')

def main_task():
    """Nhiệm vụ chính của bot"""
    while True:
        try:
            print("Bot đang chạy bình thường")  
            logging.info("Bot đang chạy bình thường")  
            time.sleep(30)
        except Exception as e:
            logging.error(f"Lỗi trong main_task: {e}")

if __name__ == "__main__":
    print("[BOT] Bot khởi động thành công!")
    logging.info("[BOT] Bot khởi động thành công!")
    main_task()