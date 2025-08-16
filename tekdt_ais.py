# tekdt_ais.py
import sys
import os
import json
import requests
import subprocess
import webbrowser
import shutil
import zipfile
import io
from pathlib import Path
import platform
import re
import shlex
import signal
import threading
import queue
import time
from packaging.version import parse as parse_version

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem, QLabel, QPushButton, QLineEdit,
                             QFrame, QScrollArea, QGraphicsOpacityEffect, QToolTip,
                             QMessageBox, QSizePolicy, QTextEdit)
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QMovie
from PyQt6.QtCore import (Qt, QSize, QThread, pyqtSignal, QObject, QPropertyAnimation,
                          QEasingCurve, QTimer, QRect, QCoreApplication)

# --- CÁC HẰNG SỐ VÀ CẤU HÌNH ---
APP_NAME = "TekDT AIS"
APP_VERSION = "1.0.1"
GITHUB_REPO_URL = "https://github.com/tekdt/tekdtais"
REMOTE_APP_LIST_URL = "https://raw.githubusercontent.com/tekdt/tekdtais/refs/heads/main/app_list.json"
    
APP_DATA_DIR = Path(sys.argv[0]).resolve().parent

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cho cả script và EXE. """
    try:
        # PyInstaller tạo một thư mục tạm và lưu đường dẫn trong _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Nuitka và script thông thường sẽ dùng thư mục làm việc hoặc thư mục chứa file script
        base_path = Path(__file__).resolve().parent

    return str(Path(base_path) / relative_path)

CONFIG_FILE = APP_DATA_DIR / "app_config.json"
APPS_DIR = APP_DATA_DIR / "Apps"
TOOLS_DIR = APP_DATA_DIR / "Tools"
IMAGES_DIR_DATA = APP_DATA_DIR / "Images"
ARIA2_DIR = TOOLS_DIR / "aria2"
SEVENZ_DIR = TOOLS_DIR / "7z"
ARIA2_EXEC = ARIA2_DIR / "aria2c.exe"
SEVENZ_EXEC = SEVENZ_DIR / "7za.exe"
ARIA2_API_URL = "https://api.github.com/repos/aria2/aria2/releases/latest"
SEVENZIP_API_URL = "https://api.github.com/repos/ip7z/7zip/releases/latest"

# Create storage directories if they don't exist
def initialize_directories_and_tools():
    """ Tạo các thư mục cần thiết và sao chép công cụ từ gói EXE (nếu cần) """
    # Tạo các thư mục lưu trữ bền vững
    for dir_path in [APPS_DIR, TOOLS_DIR, IMAGES_DIR_DATA, ARIA2_DIR, SEVENZ_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Nếu chạy dưới dạng EXE, kiểm tra và sao chép các công cụ đi kèm vào thư mục Tools
    if getattr(sys, 'frozen', False):
        bundled_tools = {
            resource_path("Tools/aria2/aria2c.exe"): ARIA2_EXEC,
            resource_path("Tools/7z/7za.exe"): SEVENZ_EXEC
        }
        for src_path_str, dest_path in bundled_tools.items():
            src_path = Path(src_path_str)
            # Chỉ sao chép nếu file đích chưa tồn tại và file nguồn (trong _MEIPASS) tồn tại
            if not dest_path.exists() and src_path.exists():
                try:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied bundled tool to {dest_path}")
                except (OSError, shutil.Error) as e:
                    print(f"Error copying bundled tool {src_path} to {dest_path}: {e}")

# Chạy hàm khởi tạo ngay lập tức
initialize_directories_and_tools()

class CliProgressWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tiến trình cài đặt - TekDT AIS")
        self.setGeometry(150, 150, 700, 400)
        layout = QVBoxLayout(self)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0; font-family: Consolas, monospace;")
        layout.addWidget(self.log_output)
        
    def append_message(self, message):
        self.log_output.append(message)
        # Tự động cuộn xuống dưới
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())


# --- NEW: Lớp quản lý và cập nhật công cụ ---
class ToolManager(QObject):
    progress_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        # GitHub API cần User-Agent
        self.session.headers.update({'User-Agent': 'TekDT-AIS-App'})

    def run_checks(self):
        tools_present = ARIA2_EXEC.exists() and SEVENZ_EXEC.exists()
        is_online = False

        # 1. Kiểm tra kết nối mạng một cách an toàn
        try:
            self.progress_update.emit("Kiểm tra kết nối internet...")
            self.session.get("https://www.google.com", timeout=5)
            is_online = True
            self.progress_update.emit("Đã kết nối internet. Kiểm tra cập nhật công cụ...")
        except requests.ConnectionError:
            self.progress_update.emit("Không có internet. Sử dụng công cụ có sẵn (nếu có).")
            is_online = False

        # 2. Xử lý logic dựa trên trạng thái online và sự tồn tại của công cụ
        if is_online:
            # Nếu online, luôn cố gắng cập nhật công cụ
            try:
                self._check_7zip()
                self._check_aria2()
                self.finished.emit(True, "Kiểm tra công cụ hoàn tất.")
            except Exception as e:
                # Nếu cập nhật thất bại nhưng công cụ đã có sẵn, vẫn có thể tiếp tục
                if tools_present:
                    self.finished.emit(True, f"Lỗi khi cập nhật công cụ: {e}. Sử dụng phiên bản có sẵn.")
                else: # Nếu cập nhật thất bại và cũng không có sẵn công cụ -> Lỗi nghiêm trọng
                    self.finished.emit(False, f"Lỗi tải công cụ cần thiết: {e}. Vui lòng kiểm tra mạng và thử lại.")
        else: # Nếu offline
            if tools_present:
                # Offline nhưng có công cụ -> OK để tiếp tục
                self.finished.emit(True, "Sử dụng công cụ có sẵn ở chế độ offline.")
            else:
                # Offline và thiếu công cụ -> Lỗi nghiêm trọng
                self.finished.emit(False, "Thiếu công cụ và không có internet để tải. Vui lòng kết nối mạng và khởi động lại.")

    def _check_7zip(self):
        tool_dir = SEVENZ_DIR
        exec_file = SEVENZ_EXEC
        tool_name = "7-Zip"
        api_url = SEVENZIP_API_URL
        asset_name = '7zr.exe'
        tool_dir.mkdir(exist_ok=True, parents=True)
        version_file = tool_dir / ".version"
        local_version = version_file.read_text().strip() if version_file.exists() else "0"
        response = self.session.get(api_url)
        response.raise_for_status()
        latest_release = response.json()
        remote_version = latest_release['tag_name']

        if remote_version != local_version or not exec_file.exists():
            self.progress_update.emit(f"Đang tìm {tool_name} phiên bản {remote_version}...")

            download_url = ""
            for asset in latest_release['assets']:
                if asset['name'] == asset_name:
                    download_url = asset['browser_download_url']
                    break

            if not download_url:
                raise Exception(f"Không tìm thấy file tải về '{asset_name}' cho {tool_name}")

            self.progress_update.emit(f"Đang tải {tool_name} ({asset_name})...")

            # Tải file thực thi
            file_response = self.session.get(download_url)
            file_response.raise_for_status()
            file_content = file_response.content

            for item in tool_dir.iterdir():
                if item.is_file(): item.unlink()
                elif item.is_dir(): shutil.rmtree(item)
            
            # Lưu trực tiếp file thực thi (7zr.exe) với tên là 7za.exe
            self.progress_update.emit(f"Đang cài đặt {tool_name}...")
            with open(exec_file, 'wb') as f:
                f.write(file_content)

            version_file.write_text(remote_version)
            self.progress_update.emit(f"Đã cập nhật {tool_name} thành công!")
        else:
            self.progress_update.emit(f"{tool_name} đã là phiên bản mới nhất.")

    def _check_aria2(self):
        tool_dir = ARIA2_DIR
        exec_file = ARIA2_EXEC
        tool_name = "aria2"
        api_url = ARIA2_API_URL
        asset_keyword = 'win-32bit'
        tool_dir.mkdir(exist_ok=True, parents=True)
        version_file = tool_dir / ".version"
        local_version = version_file.read_text().strip() if version_file.exists() else "0"

        response = self.session.get(api_url)
        response.raise_for_status()
        latest_release = response.json()
        remote_version = latest_release['tag_name']

        if remote_version != local_version or not exec_file.exists():
            self.progress_update.emit(f"Đang tải {tool_name} phiên bản {remote_version}...")
            
            download_url = ""
            for asset in latest_release['assets']:
                if asset_keyword in asset['name'] and asset['name'].endswith('.zip'):
                    download_url = asset['browser_download_url']
                    break
            
            if not download_url:
                raise Exception(f"Không tìm thấy file tải về phù hợp cho {tool_name}")
                
            # Tải file
            file_response = self.session.get(download_url)
            file_response.raise_for_status()
            file_content = file_response.content
            file_name = Path(download_url).name

            # Giải nén
            self.progress_update.emit(f"Đang giải nén {tool_name}...")
            if tool_dir.exists():
                shutil.rmtree(tool_dir)
            
            with zipfile.ZipFile(io.BytesIO(file_content)) as zf:
                # Tên thư mục bên trong file zip thường là tên file không có .zip
                extracted_folder_name = file_name.removesuffix('.zip')
                zf.extractall(TOOLS_DIR)
                (TOOLS_DIR / extracted_folder_name).rename(tool_dir)

            version_file.write_text(remote_version)
            self.progress_update.emit(f"Đã cập nhật {tool_name} thành công!")
        else:
            self.progress_update.emit(f"{tool_name} đã là phiên bản mới nhất.")


# --- LỚP CHO TÁC VỤ NỀN (DOWNLOAD, INSTALL) ---
class WorkerSignals(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str, str, str)
    error = pyqtSignal(str)
    progress_percentage = pyqtSignal(str, float)
    update_widget_status = pyqtSignal(str, str)
    tasks_batch_completed = pyqtSignal(dict) 

class AriaDownloader(QThread):
    # Tín hiệu trả về app_key để biết tiến trình của app nào
    progress_percentage = pyqtSignal(str, float)
    finished = pyqtSignal(str, bool) # app_key, success

    def __init__(self, app_key, command, cwd):
        super().__init__()
        self.app_key = app_key
        self.command = command
        self.cwd = cwd
        self._is_stopped = False
        self.process = None

    def stop(self):
        self._is_stopped = True
        if self.process:
            # Gửi tín hiệu terminate đến tiến trình aria2
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass # Tiến trình có thể đã kết thúc rồi

    def _enqueue_output(self, pipe, q):
        """
        Hàm này chạy trong một luồng riêng, chỉ đọc output từ pipe
        và đưa vào queue.
        """
        try:
            # Dùng iter để đọc từng dòng cho đến khi pipe được đóng
            for line in iter(pipe.readline, b''):
                q.put(line)
        finally:
            pipe.close()

    def run(self):
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, # Bắt cả stderr để gỡ lỗi
                cwd=self.cwd,
                # Quan trọng: không dùng text=True, chúng ta sẽ tự decode
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
            )

            # Tạo một queue để giao tiếp giữa luồng đọc và luồng chính
            q = queue.Queue()

            # Tạo và bắt đầu luồng đọc output (stdout)
            reader_thread = threading.Thread(target=self._enqueue_output, args=(self.process.stdout, q))
            reader_thread.daemon = True # Luồng sẽ tự thoát khi chương trình chính thoát
            reader_thread.start()
            
            # Tạo luồng đọc lỗi (stderr) để gỡ lỗi tốt hơn
            error_q = queue.Queue()
            error_reader_thread = threading.Thread(target=self._enqueue_output, args=(self.process.stderr, error_q))
            error_reader_thread.daemon = True
            error_reader_thread.start()

            percentage_pattern = re.compile(r'\[.*?\((\d+)%\)')
            
            # Vòng lặp chính: xử lý dữ liệu từ queue và kiểm tra trạng thái tiến trình
            # Vòng lặp này không bị block bởi I/O
            while self.process.poll() is None:
                if self._is_stopped:
                    break

                try:
                    # Lấy một dòng từ queue, không block.
                    # Nếu queue rỗng, nó sẽ ném ra lỗi queue.Empty
                    line_bytes = q.get_nowait()
                    line_str = line_bytes.decode('utf-8', errors='ignore')
                    
                    match = percentage_pattern.search(line_str)
                    if match:
                        self.progress_percentage.emit(self.app_key, float(match.group(1)))

                except queue.Empty:
                    # Queue rỗng, không sao cả, đợi một chút rồi thử lại
                    time.sleep(0.1)
            
            # Đợi các luồng đọc kết thúc
            reader_thread.join(timeout=1)
            error_reader_thread.join(timeout=1)

            # Sau khi tiến trình kết thúc, thu thập lỗi nếu có
            error_output = "".join(line.decode('utf-8', errors='ignore') for line in list(error_q.queue))

            if self._is_stopped:
                self.finished.emit(self.app_key, False)
                return

            if self.process.returncode == 0:
                self.progress_percentage.emit(self.app_key, 100.0)
                self.finished.emit(self.app_key, True)
            else:
                print(f"Lỗi tải {self.app_key} (mã lỗi: {self.process.returncode}): {error_output}")
                self.finished.emit(self.app_key, False)

        except Exception as e:
            print(f"Ngoại lệ trong AriaDownloader cho {self.app_key}: {e}")
            self.finished.emit(self.app_key, False)

class InstallWorker(QThread):
    def __init__(self, worker_tasks):
        super().__init__()
        self.main_win = main_win
        self.signals = WorkerSignals()
        self.worker_tasks = worker_tasks # {app_key: {'action': ..., 'info': ...}}
        self._is_stopped = False
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'TekDT-AIS-App'})

        # Các biến quản lý trạng thái
        self.downloaders = []
        self.tasks_to_process_after_download = {}
        self.active_downloads = 0
        self.lock = threading.Lock() # Để bảo vệ việc truy cập self.active_downloads
        self.config_lock = threading.Lock()

    def stop(self):
        self._is_stopped = True
        for downloader in self.downloaders:
            downloader.stop()

    def run(self):
        try:
            # --- BƯỚC 1: LỌC VÀ KHỞI CHẠY CÁC TÁC VỤ TẢI XUỐNG ĐỒNG THỜI ---
            download_tasks = {}
            for key, task in self.worker_tasks.items():
                app_info = task['info']
                download_path = APPS_DIR / key / app_info.get('output_filename', Path(app_info.get('download_url', '')).name)
                
                # Chỉ tải nếu file chưa tồn tại, hoặc nếu hành động là 'update'
                needs_download = not download_path.exists() or task['action'] == 'update'
                
                if needs_download:
                    download_tasks[key] = task
                else:
                    # Nếu không cần tải, đưa thẳng vào danh sách xử lý sau
                    self.tasks_to_process_after_download[key] = task

            if not download_tasks and not self.tasks_to_process_after_download:
                pass

            elif download_tasks:
                self.active_downloads = len(download_tasks)
                for app_key, task_def in download_tasks.items():
                    if self._is_stopped: break
                    
                    self.signals.progress.emit(app_key, "processing", f"Chuẩn bị tải...")
                    app_info = task_def['info']
                    app_dir = APPS_DIR / app_key
                    app_dir.mkdir(exist_ok=True)
                    
                    if task_def['action'] == 'update':
                        # Xóa file cũ trước khi tạo lệnh tải mới
                        file_name = app_info.get('output_filename', Path(app_info['download_url']).name)
                        if (app_dir / file_name).exists():
                            (app_dir / file_name).unlink()
                    
                    command = self._build_aria_command(app_info, app_dir)
                    downloader = AriaDownloader(app_key, command, app_dir)
                    
                    # Kết nối tín hiệu từ downloader con đến tín hiệu của worker chính
                    downloader.progress_percentage.connect(self.signals.progress_percentage)
                    downloader.finished.connect(self._on_download_finished)
                    
                    self.downloaders.append(downloader)
                    downloader.start()
            else:
                # Nếu không có gì để tải, chuyển ngay đến bước xử lý sau
                self._process_remaining_tasks()

        except Exception as e:
            self.signals.error.emit(f"Lỗi nghiêm trọng khi khởi tạo Worker: {e}")
        finally:
            # Chỉ phát tín hiệu finished nếu không có tác vụ tải nào đang hoạt động.
            # Nếu có, hàm _on_download_finished sẽ tự xử lý việc này sau.
            with self.lock:
                if self.active_downloads == 0:
                    self.signals.finished.emit()

    def _build_aria_command(self, app_info, app_dir):
        download_url = app_info['download_url']
        file_name = app_info.get('output_filename', Path(download_url).name)
        command = [
            str(ARIA2_EXEC), "--dir", str(app_dir), "--out", file_name,
            "--max-connection-per-server=16", "--split=16", "--min-split-size=1M",
            "--show-console-readout=false", "--summary-interval=1",
            download_url
        ]
        if 'referer' in app_info:
            command.extend(["--header", f"Referer: {app_info['referer']}"])
        return command

    def _on_download_finished(self, app_key, success):
        """Slot được gọi khi một AriaDownloader hoàn thành."""
        with self.lock:
            if success:
                # Process ngay per task thay vì đợi all
                self._process_single_task(app_key, self.worker_tasks[app_key])
            else:
                status = "stopped" if self._is_stopped else "failed"
                self.signals.update_widget_status.emit(app_key, "failed")
                self.signals.progress.emit(app_key, status, f"Tải thất bại.")

            self.active_downloads -= 1
            if self.active_downloads == 0:
                self.signals.finished.emit()  # Chỉ finished khi all done, nhưng process per task

    def _process_single_task(self, app_key, task_def):
        if self._is_stopped: return

        app_info = task_def['info']
        action = task_def['action']
        display_name = app_info.get('display_name', app_key)
        task_successful = False

        # --- Tải Icon (luôn thực hiện) ---
        self._download_icon_if_needed(app_key, app_info)

        # --- Xử lý Cài đặt/Tải về ---
        if action == "download" or app_info.get('type') == 'portable':
            # Với 'download' hoặc portable, chỉ cần tải xong là thành công
            self.signals.update_widget_status.emit(app_key, "success")
            self.signals.progress.emit(app_key, "success", f"Đã xử lý {display_name} thành công!")
            task_successful = True

        elif (action == "install" or action == "update") and app_info.get('type') == 'installer':
            download_path = APPS_DIR / app_key / app_info.get('output_filename', Path(app_info['download_url']).name)
            if not download_path.exists():
                self.signals.update_widget_status.emit(app_key, "failed")
                self.signals.progress.emit(app_key, "failed", f"Lỗi: Không tìm thấy file đã tải của {display_name}.")
                return

            self.signals.update_widget_status.emit(app_key, "installing")
            self.signals.progress.emit(app_key, "installing", f"Đang cài đặt {display_name}...")

            install_params = app_info.get('install_params', '')
            install_command = [str(download_path)] + shlex.split(install_params)
            try:
                install_process = subprocess.Popen(install_command, creationflags=subprocess.CREATE_NO_WINDOW)
                install_process.wait(timeout=600)

                if install_process.returncode == 0:
                    self.signals.update_widget_status.emit(app_key, "success")
                    self.signals.progress.emit(app_key, "success", f"Đã xử lý {display_name} thành công!")
                    task_successful = True
                else:
                    self.signals.update_widget_status.emit(app_key, "failed")
                    self.signals.progress.emit(app_key, "failed", f"Cài đặt thất bại (mã lỗi: {install_process.returncode}).")
            except subprocess.TimeoutExpired:
                self.signals.update_widget_status.emit(app_key, "failed")
                self.signals.progress.emit(app_key, "failed", f"Cài đặt quá thời gian cho phép.")
            except Exception as e:
                self.signals.update_widget_status.emit(app_key, "failed")
                self.signals.progress.emit(app_key, "failed", f"Lỗi khi chạy cài đặt: {e}")

        # Nếu thành công, ghi config ngay per task
        if task_successful:
            self._commit_config_changes({app_key: task_def})  # Gọi với dict chỉ 1 task
    
    def _process_remaining_tasks(self):
        """Xử lý các tác vụ còn lại như cài đặt, cập nhật icon..."""
        if self._is_stopped:
            self.signals.finished.emit()
            return

        successful_tasks = {} #CHANGED: Lưu các tác vụ thành công để xử lý config một lần

        for app_key, task_def in self.tasks_to_process_after_download.items():
            if self._is_stopped: break

            app_info = task_def['info']
            action = task_def['action']
            display_name = app_info.get('display_name', app_key)
            task_successful = False

            # --- Tải Icon (luôn thực hiện) ---
            self._download_icon_if_needed(app_key, app_info)

            # --- Xử lý Cài đặt/Tải về ---
            if action == "download" or app_info.get('type') == 'portable':
                # Với 'download' hoặc portable, chỉ cần tải xong là thành công
                self.signals.update_widget_status.emit(app_key, "success")
                self.signals.progress.emit(app_key, "success", f"Đã xử lý {display_name} thành công!")
                task_successful = True

            elif (action == "install" or action == "update") and app_info.get('type') == 'installer':
                download_path = APPS_DIR / app_key / app_info.get('output_filename', Path(app_info['download_url']).name)
                if not download_path.exists():
                    self.signals.update_widget_status.emit(app_key, "failed")
                    self.signals.progress.emit(app_key, "failed", f"Lỗi: Không tìm thấy file đã tải của {display_name}.")
                    continue # Bỏ qua tác vụ này

                self.signals.update_widget_status.emit(app_key, "installing")
                self.signals.progress.emit(app_key, "installing", f"Đang cài đặt {display_name}...")

                install_params = app_info.get('install_params', '')
                install_command = [str(download_path)] + shlex.split(install_params)
                try:
                    # Sử dụng Popen.wait() với timeout để tránh bị treo vô hạn
                    install_process = subprocess.Popen(install_command, creationflags=subprocess.CREATE_NO_WINDOW)
                    install_process.wait(timeout=600) # Timeout 10 phút

                    if install_process.returncode == 0:
                        self.signals.update_widget_status.emit(app_key, "success")
                        self.signals.progress.emit(app_key, "success", f"Đã xử lý {display_name} thành công!")
                        task_successful = True
                    else:
                        self.signals.update_widget_status.emit(app_key, "failed")
                        self.signals.progress.emit(app_key, "failed", f"Cài đặt thất bại (mã lỗi: {install_process.returncode}).")
                except subprocess.TimeoutExpired:
                    self.signals.update_widget_status.emit(app_key, "failed")
                    self.signals.progress.emit(app_key, "failed", f"Cài đặt quá thời gian cho phép.")
                except Exception as e:
                    self.signals.update_widget_status.emit(app_key, "failed")
                    self.signals.progress.emit(app_key, "failed", f"Lỗi khi chạy cài đặt: {e}")

            # CHANGED: Nếu tác vụ thành công, thêm vào danh sách để cập nhật config
            if task_successful:
                successful_tasks[app_key] = task_def

        # Sau khi vòng lặp kết thúc, ghi tất cả thay đổi vào config MỘT LẦN
        if successful_tasks:
            self._commit_config_changes(successful_tasks)

    def _download_icon_if_needed(self, app_key, app_info):
        """Hàm helper chỉ để tải icon."""
        icon_url = app_info.get('icon_url')
        if not icon_url: return
        
        icon_filename = Path(icon_url).name
        icon_path = APPS_DIR / app_key / icon_filename
        if not icon_path.exists():
            try:
                icon_response = self.session.get(icon_url, timeout=10)
                icon_response.raise_for_status()
                with open(icon_path, 'wb') as f: f.write(icon_response.content)
            except requests.RequestException:
                pass # Bỏ qua nếu tải icon lỗi
    
    def _commit_config_changes(self, completed_tasks):
        """
        Tổng hợp tất cả thay đổi từ các tác vụ đã hoàn thành,
        ghi vào file config và gửi một tín hiệu duy nhất chứa tất cả dữ liệu.
        """
        with self.config_lock:
            try:
                config = {}
                if CONFIG_FILE.exists():
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content: config = json.loads(content)

                config.setdefault('app_items', {})

                updated_items_for_signal = {} # Chuẩn bị dữ liệu để gửi đi

                # Duyệt qua các tác vụ đã hoàn thành thành công
                for app_key, task_def in completed_tasks.items():
                    app_info = task_def['info']
                    icon_filename = Path(app_info.get('icon_url', '')).name or 'default_icon.png'

                    # Cập nhật thông tin mới (quan trọng nhất là version) vào config
                    existing_item_info = config['app_items'].setdefault(app_key, {})
                    existing_item_info.update(app_info) 
                    existing_item_info['icon_file'] = icon_filename

                    # Thêm: Nếu action là 'download' (tải mới), force update version từ remote để tránh '0'
                    if task_def['action'] == 'download':
                        remote_version = app_info.get('version', '0')
                        existing_item_info['version'] = remote_version

                    # Thêm: Cập nhật ngay local_apps để đồng bộ bộ nhớ (tránh đè khi populate)
                    self.main_win.local_apps.setdefault(app_key, {}).update(existing_item_info)  # Giả sử self.parent là main_win, điều chỉnh nếu khác

                    # Thêm vào dictionary để gửi đi qua tín hiệu
                    updated_items_for_signal[app_key] = existing_item_info

                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                # Phát tín hiệu MỘT LẦN với TẤT CẢ các mục đã cập nhật
                if updated_items_for_signal:
                    self.signals.tasks_batch_completed.emit(updated_items_for_signal)

            except (IOError, json.JSONDecodeError) as e:
                self.signals.error.emit(f"Lỗi nghiêm trọng khi ghi file config: {e}")

# --- WIDGET TÙY CHỈNH CHO MỖI PHẦN MỀM ---
class AppItemWidget(QWidget):
    add_requested = pyqtSignal(str, dict)
    remove_requested = pyqtSignal(str, dict)
    auto_install_toggled = pyqtSignal(str, bool)
    def __init__(self, app_key, app_info, embed_mode=False, parent=None):
        super().__init__(parent)
        self.app_key = app_key
        self.app_info = app_info
        self.embed_mode = embed_mode
        self._current_progress = 0.0
        self.setMouseTracking(True)
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Layout chính
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_file = app_info.get('icon_file', '')
        icon_path = APPS_DIR / app_key / icon_file if icon_file else ''
        default_icon_path = resource_path('Images/default_icon.png')
        
        pixmap_path = str(icon_path) if icon_path and Path(icon_path).exists() else str(default_icon_path)
        icon = QIcon(pixmap_path)
        if not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(48, 48))
        else:
            self.icon_label.setText("?")
            self.icon_label.setStyleSheet("color: #ecf0f1; background-color: #34495e; border: 1px solid #3498db;")
        self.layout.addWidget(self.icon_label)
        
        # Thông tin
        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(8, 0, 0, 0)
        self.info_layout.setSpacing(2)
        self.info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.name_label = QLabel(f"{app_info.get('display_name', 'N/A')}")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        self.version_label = QLabel(f"Phiên bản: {app_info.get('version', 'N/A')}")
        self.version_label.setStyleSheet("color: #bdc3c7; font-size: 10pt;")
        
        self.info_layout.addWidget(self.name_label)
        self.info_layout.addWidget(self.version_label)
        self.layout.addWidget(self.info_widget, 1)
        
        # Nút hành động
        self.action_button = QPushButton()
        self.action_button.setFixedSize(100, 36)
        self.action_button.clicked.connect(self._on_action_button_clicked)
        self.layout.addWidget(self.action_button)
        
        # Dấu tick/X
        self.status_label = QLabel()
        self.status_label.setFixedSize(24, 24)
        self.layout.addWidget(self.status_label)
        self.status_label.hide()
        
        # Lớp phủ tiến độ
        self.progress_overlay = QWidget(self)
        self.progress_overlay.setStyleSheet("background-color: rgba(76, 175, 80, 100);")
        self.progress_overlay.setGeometry(0, 0, 0, self.height())
        self.progress_overlay.hide()
        self._progress_animation = QPropertyAnimation(self.progress_overlay, b"geometry", self)
        self._progress_animation.setDuration(500) # Thời gian chuyển động ngắn để tạo cảm giác real-time
        self._progress_animation.setEasingCurve(QEasingCurve.Type.Linear)
        
        self.setToolTip(app_info.get('description', 'Không có mô tả.'))

    def _on_action_button_clicked(self):
        if self.embed_mode:
            is_currently_set_for_auto_install = self.action_button.text() == "Xoá"
            new_state = not is_currently_set_for_auto_install
            self.auto_install_toggled.emit(self.app_key, new_state)
            self.set_auto_install_button_state(new_state)
        else:
            if self.action_button.text() == "Thêm":
                self.add_requested.emit(self.app_key, self.app_info)

    def set_auto_install_button_state(self, is_auto_install):
        if is_auto_install:
            self.action_button.setText("Xoá")
            self.action_button.setToolTip(f"Huỷ tự động cài đặt {self.app_info['display_name']}")
            self.action_button.setStyleSheet(
                "background-color: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
            ) # Màu đỏ
        else:
            self.action_button.setText("Thêm")
            self.action_button.setToolTip(f"Bật tự động cài đặt {self.app_info['display_name']}")
            self.action_button.setStyleSheet(
                "background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
            ) # Màu xanh
        self.action_button.setEnabled(True)
    
    def resizeEvent(self, event):
        if self._current_progress > 0:
            overlay_width = int(self.width() * (self._current_progress / 100.0))
            self.progress_overlay.setGeometry(0, 0, overlay_width, self.height())
        super().resizeEvent(event)
        
    def set_status(self, status):
        self.status_label.setMovie(None)
        self.status_label.setPixmap(QPixmap())

        if status == "success":
            self._progress_animation.stop()
            self.status_label.setPixmap(QPixmap(resource_path('Images/success.png')).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.name_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12pt;")
            self.action_button.setEnabled(True) # Re-enable after process
            self._current_progress = 0
            self.progress_overlay.hide()
            self.progress_overlay.setGeometry(0, 0, 0, self.height())
            self.status_label.show()
        elif status == "failed":
            self._progress_animation.stop()
            self.status_label.setPixmap(QPixmap(resource_path('Images/failed.png')).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.name_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 12pt;")
            self.action_button.setEnabled(True) # Re-enable after process
            self._current_progress = 0
            self.progress_overlay.hide()
            self.status_label.show()
        elif status == "processing": # Downloading
            movie = QMovie(resource_path('Images/loading.gif'))
            self.status_label.setMovie(movie)
            movie.start()
            self.action_button.setEnabled(False)
            self.status_label.show()
        elif status == "installing": # Installing (new status)
            movie = QMovie(resource_path('Images/loading.gif'))
            self.status_label.setMovie(movie)
            movie.start()
            self.action_button.setEnabled(False)
            self.status_label.show()
        else: # Idle
            self.status_label.hide()
            self.name_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
            self.action_button.setEnabled(True)
            self._current_progress = 0
            self.progress_overlay.hide()

    def update_download_progress(self, app_key, percentage):
        if app_key != self.app_key:
            return

        self._current_progress = float(percentage)

        if self.width() <= 0:
            return

        if not self.progress_overlay.isVisible():
            self.progress_overlay.show()
            self.progress_overlay.raise_()

        start_rect = self.progress_overlay.geometry()
        target_width = int(self.width() * (self._current_progress / 100.0))
        end_rect = QRect(0, 0, target_width, self.height())

        # Dừng animation cũ nếu đang chạy
        self._progress_animation.stop()
        # Thiết lập giá trị bắt đầu và kết thúc cho animation
        self._progress_animation.setStartValue(start_rect)
        self._progress_animation.setEndValue(end_rect)
        # Bắt đầu animation mới
        self._progress_animation.start()

        # Throttle update bằng QTimer để tránh overload khi batch (chỉ update mỗi 200ms)
        if not hasattr(self, '_progress_timer') or not self._progress_timer.isActive():
            self._progress_timer = QTimer(self)
            self._progress_timer.setSingleShot(True)
            self._progress_timer.timeout.connect(self._progress_animation.start)
            self._progress_timer.start(200)  # Giới hạn update mỗi 200ms
        else:
            self._progress_timer.start(200)  # Reset timer nếu đang chạy

        if self._current_progress >= 100:
            # Nếu đạt 100%, đảm bảo nó lấp đầy ngay lập tức
            QTimer.singleShot(self._progress_animation.duration(), lambda: self.progress_overlay.setGeometry(0, 0, self.width(), self.height()))

# --- CỬA SỔ CHÍNH ---
class TekDT_AIS(QMainWindow):
    def __init__(self, embed_mode=False, embed_size=None):
        super().__init__()
        self.embed_mode = embed_mode
        if embed_mode:
            threading.Thread(target=self.check_shutdown_signal, daemon=True).start()
        self.embed_size = embed_size
        self.config = {}
        self.remote_apps = {}
        self.local_apps = {}
        self.selected_for_install = []
        self.active_workers = {}
        self.startup_label = None
        self.system_arch = platform.architecture()[0]
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'TekDT-AIS-App'})
        self.cli_task_results = {}        
        self._scroll_positions = {}
        self.is_cli_mode = False
        self.is_processing = False
        self.central_widget_ref = None

        if self.embed_mode:
            self.setup_embed_ui()
        else:
            self.setup_ui()
            
        # Vô hiệu hóa UI và hiển thị trạng thái khởi động
        self.central_widget_ref = self.centralWidget()
        self.central_widget_ref.setEnabled(False)
        self.show_startup_status("Đang khởi tạo...")
        
        self.tool_manager_thread = QThread()
        self.tool_manager = ToolManager()
        self.tool_manager.moveToThread(self.tool_manager_thread)
        self.tool_manager.finished.connect(self.on_tool_check_finished)
        self.tool_manager_thread.started.connect(self.tool_manager.run_checks)
        
        self.tool_manager_thread.start()

    def show_styled_message_box(self, icon, title, text, detailed_text="", buttons=QMessageBox.StandardButton.Ok):
        msg_box = QMessageBox(self)
        msg_box.setWindowIcon(QIcon(resource_path("logo.ico")))
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        if detailed_text:
            msg_box.setInformativeText(detailed_text)
        
        msg_box.setStandardButtons(buttons)

        # Áp dụng stylesheet
        stylesheet = """
            QMessageBox {
                background-color: #2c3e50;
            }
            QMessageBox QLabel#qt_msgbox_label { /* Title Label */
                color: #ecf0f1;
                font-size: 12pt;
            }
            QMessageBox QLabel#qt_msgbox_informativetext { /* Detailed Text Label */
                color: #bdc3c7;
                font-size: 10pt;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
            QMessageBox QPushButton:pressed {
                background-color: #1f618d;
            }
        """
        msg_box.setStyleSheet(stylesheet)
        
        return msg_box.exec()

    def show_startup_status(self, message):
        # if not self.startup_label:
            # self.startup_label = QLabel(message, self)
            # self.startup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # self.startup_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7); color: white; font-size: 14pt; border-radius: 10px; padding: 20px;")
            # self.startup_label.setWordWrap(True)
            # self.startup_label.setMinimumWidth(400)
            # self.startup_label.setMinimumHeight(100)
            # self.tool_manager.progress_update.connect(lambda msg: self.startup_label.setText(msg))
        
        # self.startup_label.setText(message)
        # self.startup_label.adjustSize()
        # self.startup_label.move(int((self.width() - self.startup_label.width()) / 2), int((self.height() - self.startup_label.height()) / 2))
        # self.startup_label.show()
        # self.startup_label.raise_()
        
        if not self.startup_label:
            # Tạo một widget container cho overlay
            self.startup_overlay = QWidget(self)
            self.startup_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")
            self.startup_overlay.setAutoFillBackground(True)
            
            overlay_layout = QVBoxLayout(self.startup_overlay)
            overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Thêm ảnh GIF
            self.loading_movie_label = QLabel()
            movie = QMovie(resource_path('Images/loading.gif')) # Thay bằng tên GIF của bạn
            gif_size = QSize(128, 128)
            self.loading_movie_label.setFixedSize(gif_size)
            movie.setScaledSize(gif_size)
            self.loading_movie_label.setMovie(movie)
            self.loading_movie_label.setStyleSheet("background-color: transparent;")
            movie.start()
            
            # Label cho thông điệp
            self.startup_label = QLabel(message)
            self.startup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.startup_label.setStyleSheet("background-color: transparent; color: white; font-size: 14pt; padding: 10px;")
            self.startup_label.setWordWrap(True)

            overlay_layout.addWidget(self.loading_movie_label)
            overlay_layout.addWidget(self.startup_label)
        
        # Cập nhật kích thước và vị trí của overlay để lấp đầy cửa sổ
        self.startup_overlay.setGeometry(self.rect())
        self.startup_label.setText(message)
        self.startup_label.adjustSize()
        self.startup_label.move(int((self.width() - self.startup_label.width()) / 2), int((self.height() - self.startup_label.height()) / 2))
        self.startup_overlay.show()
        self.startup_overlay.raise_()

    # Hàm riêng để cập nhật text, tránh tạo lại widget
    def update_startup_status(self, message):
        if self.startup_label:
            self.startup_label.setText(message)

    # Ghi đè resizeEvent để overlay luôn vừa với cửa sổ
    def resizeEvent(self, event):
        if hasattr(self, 'startup_overlay') and self.startup_overlay.isVisible():
            self.startup_overlay.setGeometry(self.rect())
        super().resizeEvent(event)
    
    def save_scroll_positions(self):
        """Lưu vị trí hiện tại của các thanh cuộn."""
        self._scroll_positions['available'] = self.available_list_widget.verticalScrollBar().value()
        if not self.embed_mode:
            self._scroll_positions['selected'] = self.selected_list_widget.verticalScrollBar().value()

    def restore_scroll_positions(self):
        """Phục hồi vị trí của các thanh cuộn."""
        if 'available' in self._scroll_positions:
            QTimer.singleShot(0, lambda: self.available_list_widget.verticalScrollBar().setValue(self._scroll_positions['available']))
        if not self.embed_mode and 'selected' in self._scroll_positions:
            QTimer.singleShot(0, lambda: self.selected_list_widget.verticalScrollBar().setValue(self._scroll_positions['selected']))
    
    def on_tool_check_finished(self, success, message):
        self.tool_manager_thread.quit()
        self.tool_manager_thread.wait()
        # Ẩn overlay và kích hoạt lại UI
        if hasattr(self, 'startup_overlay'):
            self.startup_overlay.hide()
        if self.central_widget_ref:
            self.central_widget_ref.setEnabled(True)

        if not success:
            self.show_styled_message_box(QMessageBox.Icon.Warning, "Cảnh báo", message)
            # Thoát chương trình nếu không có công cụ
            if not (ARIA2_EXEC.exists() and SEVENZ_EXEC.exists()):
                QApplication.quit()
                return
        
        # Tiếp tục tải cấu hình và ứng dụng
        self.load_config_and_apps()

    def setup_embed_ui(self):
        self.setWindowTitle(f"{APP_NAME}")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Thiết lập để cửa sổ có thể được nhúng
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        if self.embed_size:
            self.resize(self.embed_size[0], self.embed_size[1])
        self.setStyleSheet("""
            QWidget { background-color: #2c3e50; }
            QLabel { color: #ecf0f1; font-size: 10pt; }
            QListWidget { background-color: #34495e; border: 1px solid #2c3e50; color: #ecf0f1; font-size: 11pt; }
            QListWidget::item { padding: 5px; border-bottom: 1px solid #2c3e50; }
            QPushButton { background-color: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #95a5a6; }
            QLineEdit { background-color: #34495e; border: 1px solid #2c3e50; padding: 8px; border-radius: 4px; color: white; }
            QToolTip { background-color: #34495e; color: white; border: 1px solid #3498db; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Chỉ giữ lại khung tìm kiếm và danh sách phần mềm
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Gõ để tìm kiếm...")
        self.search_box.textChanged.connect(self.filter_apps)
        
        self.available_list_widget = QListWidget()
        
        main_layout.addWidget(self.search_box)
        main_layout.addWidget(self.available_list_widget)

    def update_download_progress_anywhere(self, app_key, percentage):
        # Tìm widget ở available_list_widget
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if hasattr(widget, 'app_key') and widget.app_key == app_key:
                widget.update_download_progress(app_key, percentage)
                return
        # Nếu không tìm thấy, tìm ở selected_list_widget (nếu không embed)
        if not self.embed_mode:
            for i in range(self.selected_list_widget.count()):
                item = self.selected_list_widget.item(i)
                widget = self.selected_list_widget.itemWidget(item)
                if hasattr(widget, 'app_key') and widget.app_key == app_key:
                    widget.update_download_progress(app_key, percentage)
                    return
    
    def on_tasks_batch_completed(self, completed_items):
        """Cập nhật hàng loạt thông tin phần mềm vào bộ nhớ đệm."""
        self.local_apps.update(completed_items)
        # Cập nhật cả trong config đang chạy để đồng bộ
        self.config['app_items'].update(completed_items)
    
    def is_app_downloaded(self, app_key, app_info):
        """
        Kiểm tra xem tệp cài đặt của ứng dụng đã được tải về hoàn chỉnh hay chưa.
        """
        download_url = app_info.get('download_url', '')
        if not download_url:
            return False

        file_name = app_info.get('output_filename', Path(download_url).name)
        download_path = APPS_DIR / app_key / file_name
        
        # Tạo đường dẫn tới file control của aria2
        aria2_control_file = download_path.with_suffix(download_path.suffix + '.aria2')

        # Điều kiện mới: File cài đặt phải tồn tại VÀ file .aria2 không được tồn tại.
        return download_path.exists() and not aria2_control_file.exists()

    def handle_cli_args(self, args):
        """Xử lý các tham số dòng lệnh cho /install và /update."""
        self.load_config_and_apps(populate=False)
        if not self.remote_apps.get('app_items'):
            self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi", "Không thể tải danh sách phần mềm. Không thể tiếp tục.")
            QApplication.quit()
            return

        self.cli_task_results.clear()
        is_install_action = '/install' in args
        is_update_action = '/update' in args

        # Tìm danh sách tên phần mềm được cung cấp (nếu có)
        app_names_str = ""
        for arg in args:
            if not arg.startswith('/'):
                app_names_str = arg
                break

        # --- Xác định các phần mềm mục tiêu ---
        target_keys = set()
        if app_names_str:
            target_keys = set(app_names_str.split('|'))
        elif is_update_action and not is_install_action: # Chỉ /update
            # Lấy tất cả các app đã được tải về
            for key, info in self.local_apps.items():
                if self.is_app_downloaded(key, info): # Chỉ cập nhật app đã có file
                    target_keys.add(key)
        elif is_install_action: # /install hoặc /install /update không có tên app
            # Lấy các app có auto_install=true và đã được tải về
            for key, info in self.local_apps.items():
                if info.get('auto_install', False) and self.is_app_downloaded(key, info):
                     target_keys.add(key)
        
        # --- Xây dựng danh sách tác vụ cho Worker ---
        worker_tasks = {}
        report = {
            'update': {'success': 0, 'fail': 0, 'skipped_not_found': [], 'skipped_online': []},
            'install': {'success': 0, 'fail': 0, 'skipped_not_found': [], 'skipped_online': []}
        }
        
        for key in target_keys:
            remote_info = self.remote_apps.get('app_items', {}).get(key)
            if not remote_info:
                if is_update_action: report['update']['skipped_not_found'].append(key)
                if is_install_action: report['install']['skipped_not_found'].append(key)
                continue
            local_info = self.local_apps.get(key, {})
            if not self.is_app_downloaded(key, remote_info):
                if is_update_action: report['update']['skipped_online'].append(key)
                if is_install_action: report['install']['skipped_online'].append(key)
                continue
            
            needs_update = is_update_action and parse_version(remote_info.get('version', '0')) > parse_version(local_info.get('version', '0'))
            needs_install = is_install_action

            if needs_update:
                worker_tasks[key] = {'info': remote_info, 'action': 'update'}
            elif needs_install:
                worker_tasks[key] = {'info': remote_info, 'action': 'install'}

        if not worker_tasks:
            # Tạo thông báo nếu không có gì để làm
            summary_lines = []
            if is_update_action:
                total_skipped = len(report['update']['skipped_not_found']) + len(report['update']['skipped_online'])
                summary_lines.append(f"Cập nhật: 0 thành công, 0 thất bại, {total_skipped} bị bỏ qua.")
            if is_install_action:
                total_skipped = len(report['install']['skipped_not_found']) + len(report['install']['skipped_online'])
                summary_lines.append(f"Cài đặt: 0 thành công, 0 thất bại, {total_skipped} bị bỏ qua.")

            final_message = "\n".join(summary_lines) if summary_lines else "Không có tác vụ nào cần thực hiện."
            self.show_styled_message_box(QMessageBox.Icon.Information, "Hoàn tất", final_message)
            QApplication.quit()
            return

        # --- Hiển thị giao diện và bắt đầu Worker ---
        self.show()
        self.populate_lists()
        for key, task_def in worker_tasks.items():
            self.move_app_to_selection(key, task_def['info'])
        
        self.set_ui_interactive(False)
        
        self.install_worker = InstallWorker(worker_tasks)

        def on_cli_finished():
            for key, result in self.cli_task_results.items():
                action = result.get('action')
                status = result.get('status')
                if action and status:
                    if status == 'success':
                        report[action]['success'] += 1
                        # Nếu action là 'update' và lệnh install cũng được yêu cầu,
                        # thì cũng tính là một lần install thành công.
                        if action == 'update' and is_install_action:
                            report['install']['success'] += 1
                    else:  # 'failed' or 'stopped'
                        report[action]['fail'] += 1
            
            # Xây dựng thông báo tổng kết
            summary_lines = []
            if is_update_action:
                s = report['update']['success']
                f = report['update']['fail']
                skip = len(report['update']['skipped_not_found']) + len(report['update']['skipped_online'])
                summary_lines.append(f"--- Cập nhật ---\nThành công: {s} | Thất bại: {f} | Bỏ qua: {skip}")
            
            if is_install_action:
                s = report['install']['success']
                f = report['install']['fail']
                skip = len(report['install']['skipped_not_found']) + len(report['install']['skipped_online'])
                summary_lines.append(f"--- Cài đặt ---\nThành công: {s} | Thất bại: {f} | Bỏ qua: {skip}")

            final_message = "\n\n".join(summary_lines)
            self.show_styled_message_box(QMessageBox.Icon.Information, "Hoàn tất tác vụ dòng lệnh", final_message)
            self.load_config_and_apps(populate=False)
            QApplication.quit()

        self.install_worker.signals.progress.connect(self.update_and_record_progress)
        self.install_worker.signals.progress_percentage.connect(self.update_download_progress_anywhere)
        self.install_worker.signals.finished.connect(on_cli_finished)
        self.install_worker.signals.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)))
        self.install_worker.signals.update_widget_status.connect(self.update_widget_status)
        self.install_worker.signals.tasks_batch_completed.connect(self.on_tasks_batch_completed)
        self.install_worker.start()

    def update_and_record_progress(self, app_key, status, message):
        """Cập nhật giao diện và ghi lại kết quả cuối cùng cho các tác vụ CLI."""
        self.update_install_progress(app_key, status, message)
        
        # Chỉ ghi nhận khi tác vụ kết thúc (thành công, thất bại, hoặc bị dừng)
        if status in ["success", "failed", "stopped"]:
             # Đảm bảo worker và các tác vụ của nó vẫn tồn tại
             if self.install_worker and app_key in self.install_worker.worker_tasks:
                action_type = self.install_worker.worker_tasks[app_key]['action']
                self.cli_task_results[app_key] = {'status': status, 'action': action_type}

    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} - v{APP_VERSION}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #2c3e50; }
            QLabel { color: #ecf0f1; font-size: 10pt; }
            QListWidget { background-color: #34495e; border: 1px solid #2c3e50; color: #ecf0f1; font-size: 11pt; }
            QListWidget::item { padding: 5px; border-bottom: 1px solid #2c3e50; }
            QListWidget::item:hover { background-color: #4a627a; }
            QPushButton { background-color: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #95a5a6; }
            QLineEdit { background-color: #34495e; border: 1px solid #2c3e50; padding: 8px; border-radius: 4px; color: white; }
            QToolTip { background-color: #34495e; color: white; border: 1px solid #3498db; }
        """)

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # Panels Layout
        panels_layout = QHBoxLayout()
        
        # --- Left Panel (Available Apps) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Gõ để tìm kiếm (tối thiểu 2 ký tự)...")
        self.search_box.textChanged.connect(self.filter_apps)
        self.available_count_label = QLabel("Tổng số phần mềm: 0")
        self.available_list_widget = QListWidget()
        left_layout.addWidget(self.search_box)
        left_layout.addWidget(self.available_count_label)
        left_layout.addWidget(self.available_list_widget)
        
        # --- Right Panel (Selected Apps) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.selected_count_label = QLabel("Đã chọn: 0")
        self.selected_list_widget = QListWidget()
        right_layout.addWidget(self.selected_count_label)
        right_layout.addWidget(self.selected_list_widget)
        
        panels_layout.addWidget(left_panel)
        panels_layout.addWidget(right_panel)
        
        # --- Bottom Panel (Controls) ---
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        self.start_button = QPushButton("BẮT ĐẦU CÀI ĐẶT")
        self.start_button.clicked.connect(self.start_installation)
        self.start_button.setMinimumHeight(40)

        self.status_label = QLabel("Trạng thái: Sẵn sàng.")
        
        bottom_layout.addWidget(self.status_label, 1)
        bottom_layout.addWidget(self.start_button)
        
        main_layout.addLayout(panels_layout)
        main_layout.addWidget(bottom_panel)

    def set_ui_interactive(self, enabled):
        """Enable or disable all interactive UI elements except the stop button when disabled."""
        self.search_box.setEnabled(enabled)
        self.available_list_widget.setEnabled(enabled)
        
        # Cập nhật các mục trong danh sách đã chọn
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            widget = self.selected_list_widget.itemWidget(item)
            if hasattr(widget, 'action_button'):
                if not enabled:
                    # Ẩn nút "Bỏ" và hiển thị trạng thái "processing" khi bắt đầu cài đặt
                    widget.action_button.hide()
                    widget.set_status("processing")
                else:
                    # Hiển thị lại nút "Bỏ" và ẩn trạng thái khi kết thúc
                    widget.action_button.show()
                    widget.set_status("")
                widget.action_button.setEnabled(enabled)
    
    def load_config_and_apps(self, populate=True):
        # Load local config
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.config = json.loads(content) if content else {}
            except json.JSONDecodeError:
                self.config = {}
        else:
            self.config = {"settings": {}, "app_items": {}}
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

        # Luôn đảm bảo các khóa chính tồn tại
        self.config.setdefault('settings', {})
        self.config.setdefault('app_items', {})

        self.local_apps = self.config.get("app_items", {})
        
        if not self.embed_mode:
            self.selected_for_install = self.config.get("settings", {}).get("selected_for_install", [])
            if not isinstance(self.selected_for_install, list):
                self.selected_for_install = []
        
        is_online = False
        
        try:
            status_text = "Đang tải danh sách phần mềm từ máy chủ..."
            if hasattr(self, 'status_label') and self.status_label: self.status_label.setText(status_text)
            response = self.session.get(REMOTE_APP_LIST_URL, timeout=10)
            response.raise_for_status()
            self.remote_apps = response.json()
            is_online = True
            status_text = "Tải danh sách thành công. Sẵn sàng."
            if hasattr(self, 'status_label') and self.status_label: self.status_label.setText(status_text)
        except requests.RequestException as e:
            if not self.is_cli_mode:
                self.show_styled_message_box(QMessageBox.Icon.Warning, "Lỗi mạng", f"Không thể tải danh sách phần mềm từ máy chủ: {e}\nChương trình sẽ chỉ hiển thị các phần mềm đã có thông tin cục bộ.")
            else:
                print(f"Lưu ý: Không thể tải danh sách phần mềm từ máy chủ. Tiếp tục với dữ liệu cục bộ.")
            self.remote_apps = {"app_items": self.local_apps.copy()}
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText("Chế độ Offline. Hiển thị các phần mềm đã tải.")
        
        # Nếu đang ở chế độ offline, lọc danh sách để chỉ giữ lại các app đã được tải về.
        if not is_online:
            all_local_apps = self.remote_apps.get("app_items", {})
            downloaded_apps_only = {
                key: info for key, info in all_local_apps.items()
                if self.is_app_downloaded(key, info)
            }
            self.remote_apps["app_items"] = downloaded_apps_only
        
        # Chỉ populate list nếu được yêu cầu (tránh làm việc thừa khi chạy CLI)
        if populate:
            self.populate_lists()
        
    def populate_lists(self):
        if hasattr(self, '_populate_timer'):
            self._populate_timer.stop()
        if self.is_processing:
            return
        self.save_scroll_positions()
        self.available_list_widget.clear()
        if not self.embed_mode:
            self.selected_list_widget.clear()
        
        all_apps = self.remote_apps.get("app_items", {})
        
        # Lọc ứng dụng dựa trên cấu trúc hệ thống
        compatible_apps = {}
        for key, app_info in all_apps.items():
            compatible_os_arch = app_info.get('compatible_os_arch', 'both')
            if (self.system_arch == '64bit' and compatible_os_arch in ['64bit', 'both']) or \
               (self.system_arch == '32bit' and compatible_os_arch in ['32bit', 'both']):
                compatible_apps[key] = app_info.copy()
        
        for key, local_info in self.local_apps.items():
            if key in compatible_apps:
                compatible_apps[key].update(local_info)

        config_needs_saving = False
        try:
            self.session.get("https://www.google.com", timeout=3)
            for key, app_info in compatible_apps.items():
                icon_file = app_info.get('icon_file')
                icon_url = app_info.get('icon_url')
                if not icon_url: continue

                icon_filename = Path(icon_url).name
                app_dir = APPS_DIR / key
                icon_path = app_dir / icon_filename

                if not icon_file or not icon_path.exists():
                    try:
                        app_dir.mkdir(exist_ok=True)
                        icon_response = self.session.get(icon_url, timeout=5)
                        icon_response.raise_for_status()
                        with open(icon_path, 'wb') as f:
                            f.write(icon_response.content)
                        compatible_apps[key]['icon_file'] = icon_filename
                        self.config['app_items'].setdefault(key, {})
                        self.config['app_items'][key]['icon_file'] = icon_filename
                        config_needs_saving = True
                    except requests.RequestException:
                        compatible_apps[key]['icon_file'] = 'default_icon.png'
        except requests.ConnectionError:
            pass

        if config_needs_saving:
            self.save_config()

        categories = sorted(list(set(app.get('category', 'Chưa phân loại') for app in compatible_apps.values())))
        
        for category in categories:
            cat_item = QListWidgetItem(category.upper())
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            font = QFont()
            font.setBold(True)
            cat_item.setFont(font)
            cat_item.setForeground(QColor("#3498db"))
            self.available_list_widget.addItem(cat_item)

            for key, info in sorted(compatible_apps.items(), key=lambda item: item[1].get('display_name', '')):
                if info.get('category', 'Chưa phân loại') == category:
                    self.add_app_to_list(self.available_list_widget, key, info)

        if not self.embed_mode:
            # Xóa các mục đã chọn không còn tương thích
            valid_selected = [key for key in self.selected_for_install if key in compatible_apps]
            self.selected_for_install = valid_selected
            
            for key in self.selected_for_install:
                self.move_app_to_selection(key, compatible_apps[key])

        self.update_counts()
        self.restore_scroll_positions()

    def add_app_to_list(self, list_widget, key, info):
        item_widget = AppItemWidget(key, info, embed_mode=self.embed_mode)
        is_downloaded = self.is_app_downloaded(key, info)
        local_ver_str = self.local_apps.get(key, {}).get('version', '0')
        remote_ver_str = self.remote_apps.get('app_items', {}).get(key, {}).get('version', '0')
        is_update_available = is_downloaded and parse_version(remote_ver_str) > parse_version(local_ver_str)

        # Luôn hiển thị thông báo nếu có cập nhật
        if is_update_available:
            item_widget.version_label.setText(f"Cập nhật: {local_ver_str} -> {remote_ver_str}")
            item_widget.version_label.setStyleSheet("color: #2ecc71; font-weight: bold;") # Màu xanh lá

        # Ngắt kết nối mặc định để thiết lập lại cho từng trường hợp
        item_widget.action_button.clicked.disconnect()

        if not is_downloaded:
            # --- TRƯỜNG HỢP 1: CHƯA TẢI VỀ ---
            item_widget.action_button.setText("Tải")
            item_widget.action_button.setToolTip(f"Tải về {info['display_name']}")
            item_widget.action_button.setStyleSheet("background-color: #f39c12; color: white;") # Màu cam
            # Hành động tải không thay đổi giữa các chế độ
            item_widget.action_button.clicked.connect(lambda _, k=key, i=info, w=item_widget: self.confirm_download(k, i, w))

        elif self.embed_mode:
            # --- TRƯỜNG HỢP 2: ĐÃ TẢI VỀ (CHẾ ĐỘ EMBED) ---
            is_auto = self.local_apps.get(key, {}).get('auto_install', False)
            if is_auto:
                item_widget.set_auto_install_button_state(True) # Nút "Xoá"
                # Hành động Xoá: chỉ cần bật/tắt auto_install
                item_widget.action_button.clicked.connect(
                    lambda _, w=item_widget, k=key: (w.auto_install_toggled.emit(k, False), w.set_auto_install_button_state(False))
                )
            else:
                item_widget.set_auto_install_button_state(False) # Nút "Thêm"
                # Hành động Thêm:
                # 1. Kiểm tra cập nhật (nếu có)
                # 2. Sau đó bật auto_install = true
                on_complete_action = lambda: item_widget.auto_install_toggled.emit(key, True)
                if is_update_available:
                    # Nếu có cập nhật -> gọi confirm_update với hành động sau cùng là bật auto_install
                    item_widget.action_button.clicked.connect(lambda _, k=key, i=info, w=item_widget, lv=local_ver_str, rv=remote_ver_str, cb=on_complete_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
                else:
                    # Nếu không có cập nhật -> thực hiện hành động sau cùng ngay lập tức
                    item_widget.action_button.clicked.connect(
                        lambda _, w=item_widget, k=key: (w.auto_install_toggled.emit(k, True), w.set_auto_install_button_state(True))
                    )
            
            item_widget.auto_install_toggled.connect(self.on_auto_install_toggled)

        else: # Chế độ thông thường
            # --- TRƯỜNG HỢP 3: ĐÃ TẢI VỀ (CHẾ ĐỘ THƯỜNG) ---
            item_widget.action_button.setText("Thêm")
            item_widget.action_button.setToolTip(f"Thêm {info['display_name']} vào danh sách")
            item_widget.action_button.setStyleSheet("background-color: #4CAF50; color: white;")
            
            # Hành động Thêm:
            # 1. Kiểm tra cập nhật (nếu có)
            # 2. Sau đó chuyển sang khung bên phải
            on_complete_action = lambda: self.move_app_to_selection(key, info)
            if is_update_available:
                # Nếu có cập nhật -> gọi confirm_update với hành động sau cùng là chuyển khung
                item_widget.action_button.clicked.connect(lambda _, k=key, i=info, w=item_widget, lv=local_ver_str, rv=remote_ver_str, cb=on_complete_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
            else:
                item_widget.action_button.clicked.connect(on_complete_action)

        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 70))
        list_item.setData(Qt.ItemDataRole.UserRole, key)
        
        list_widget.addItem(list_item)
        list_widget.setItemWidget(list_item, item_widget)
        
        # Nếu đã có trong danh sách chọn, vô hiệu hóa nút
        if not self.embed_mode and key in self.selected_for_install:
            self.update_available_item_state(key, is_selected=True)

    def on_auto_install_toggled(self, key, state):
        self.config['app_items'].setdefault(key, {})
        self.config['app_items'][key]['auto_install'] = state
        self.save_config()
        if self.embed_mode:
            self.populate_lists()

    def find_widget_by_key(self, app_key):
        """Tìm widget trong available_list_widget hoặc selected_list_widget theo app_key."""
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if hasattr(widget, 'app_key') and widget.app_key == app_key:
                return widget
        if not self.embed_mode:
            for i in range(self.selected_list_widget.count()):
                item = self.selected_list_widget.item(i)
                widget = self.selected_list_widget.itemWidget(item)
                if hasattr(widget, 'app_key') and widget.app_key == app_key:
                    return widget
        return None
    
    def update_widget_status(self, app_key, status):
        """Xử lý signal cập nhật trạng thái widget."""
        widget = self.find_widget_by_key(app_key)
        if widget and widget.parent():  # Kiểm tra widget còn tồn tại và có parent
            widget.set_status(status)
    
    def confirm_download(self, key, info, widget):
        reply = self.show_styled_message_box(
            QMessageBox.Icon.Question,
            "Tải phần mềm",
            f"Bạn có muốn tải về {info['display_name']} không?\n\nSau khi tải xong, phần mềm sẽ tự động được thêm vào danh sách cài đặt.",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Không gán cho self.install_worker nữa, mà tạo worker cục bộ
            worker_tasks = {key: {'info': info, 'action': 'download'}}
            worker = InstallWorker(worker_tasks)
            
            # Kết nối các tín hiệu như cũ
            worker.signals.progress.connect(self.update_install_progress)
            worker.signals.progress_percentage.connect(self.update_download_progress_anywhere)
            worker.signals.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)))
            worker.signals.update_widget_status.connect(self.update_widget_status)
            worker.signals.tasks_batch_completed.connect(self.on_tasks_batch_completed)

            # THAY ĐỔI QUAN TRỌNG:
            # Kết nối tín hiệu finished tới hàm xử lý mới (on_worker_finished).
            # Dùng lambda để truyền app_key, đảm bảo hàm xử lý biết worker nào đã xong.
            worker.signals.finished.connect(lambda app_key=key: self.on_worker_finished(app_key))
            
            # Lưu worker vào dictionary quản lý và bắt đầu chạy
            self.active_workers[key] = worker
            worker.start()

    def confirm_update(self, key, info, widget, local_ver, remote_ver, on_complete):
        reply = self.show_styled_message_box(
            QMessageBox.Icon.Question,
            "Cập nhật phần mềm",
            f"Phiên bản mới hơn của {info['display_name']} ({remote_ver}) đã có. "
            f"Phiên bản hiện tại: {local_ver}.\n\nBạn có muốn cập nhật không?",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            if on_complete:
                on_complete()
            return

        if reply == QMessageBox.StandardButton.Yes:
            # Tương tự confirm_download, tạo worker cục bộ
            worker_tasks = {key: {'info': info, 'action': 'update'}}
            worker = InstallWorker(worker_tasks)
            
            # Kết nối các tín hiệu
            worker.signals.progress.connect(self.update_install_progress)
            worker.signals.progress_percentage.connect(self.update_download_progress_anywhere)
            worker.signals.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)))
            worker.signals.update_widget_status.connect(self.update_widget_status)
            worker.signals.tasks_batch_completed.connect(self.on_tasks_batch_completed)
            
            # THAY ĐỔI QUAN TRỌNG:
            # Khi worker xong, nó sẽ tự gọi on_worker_finished để làm mới giao diện.
            # Sau đó, chúng ta mới thực hiện hành động 'on_complete' (như chuyển sang khung bên phải).
            # Việc này đảm bảo giao diện được cập nhật đúng trước khi có hành động tiếp theo.
            def on_update_and_action():
                self.on_worker_finished(key)
                if on_complete:
                    on_complete()
            
            worker.signals.finished.connect(on_update_and_action)
            
            # Lưu worker và bắt đầu
            self.active_workers[key] = worker
            worker.start()

    def move_app_to_selection(self, key, info):
        # Kiểm tra xem item đã tồn tại trong danh sách chọn chưa
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            if item and self.selected_list_widget.itemWidget(item).app_key == key:
                return # Đã tồn tại, không thêm lại

        self.update_available_item_state(key, is_selected=True)

        item_widget = AppItemWidget(key, info)
        item_widget.action_button.setText("Bỏ")
        item_widget.action_button.setToolTip(f"Bỏ {info['display_name']} khỏi danh sách")
        item_widget.action_button.setStyleSheet(
            "background-color: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
        )
        item_widget.action_button.clicked.disconnect()
        item_widget.action_button.clicked.connect(lambda: item_widget.remove_requested.emit(key, info))
        item_widget.remove_requested.connect(self.remove_app_from_selection)
        
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 70))
        list_item.setData(Qt.ItemDataRole.UserRole, key)
        self.selected_list_widget.addItem(list_item)
        self.selected_list_widget.setItemWidget(list_item, item_widget)
        
        if key not in self.selected_for_install:
            self.selected_for_install.append(key)
        self.save_config()
        self.update_counts()

    def remove_app_from_selection(self, key, info):
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            if item and self.selected_list_widget.itemWidget(item).app_key == key:
                self.selected_list_widget.takeItem(i)
                break

        self.update_available_item_state(key, is_selected=False)
        
        if key in self.selected_for_install:
            self.selected_for_install.remove(key)
        self.save_config()
        self.update_counts()
        
    def update_available_item_state(self, key, is_selected):
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if hasattr(widget, 'app_key') and widget.app_key == key:
                widget.action_button.setDisabled(is_selected)
                if is_selected:
                    widget.action_button.setStyleSheet(
                        "background-color: #95a5a6; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
                    )
                    widget.action_button.setText("Đã chọn")
                else:
                    # Khi một item được bỏ chọn, tái tạo lại nút của nó ở danh sách bên trái
                    widget.action_button.setEnabled(True)
                    
                    is_downloaded = self.is_app_downloaded(key, widget.app_info)
                    local_ver_str = self.local_apps.get(key, {}).get('version', '0')
                    remote_ver_str = self.remote_apps.get('app_items', {}).get(key, {}).get('version', '0')
                    is_update_available = is_downloaded and parse_version(remote_ver_str) > parse_version(local_ver_str)
                    
                    # Ngắt kết nối cũ để tránh gọi nhiều lần
                    try: widget.action_button.clicked.disconnect()
                    except TypeError: pass

                    if not is_downloaded:
                        widget.action_button.setText("Tải")
                        widget.action_button.setToolTip(f"Tải về {widget.app_info['display_name']}")
                        widget.action_button.setStyleSheet("background-color: #f39c12; color: white;")
                        widget.action_button.clicked.connect(lambda _, k=key, i=widget.app_info, w=widget: self.confirm_download(k, i, w))
                    else: # Đã tải về
                        widget.action_button.setText("Thêm")
                        widget.action_button.setToolTip(f"Thêm {widget.app_info['display_name']} vào danh sách")
                        widget.action_button.setStyleSheet("background-color: #4CAF50; color: white;")
                        
                        on_complete_action = lambda: self.move_app_to_selection(key, widget.app_info)
                        if is_update_available:
                            widget.action_button.clicked.connect(lambda _, k=key, i=widget.app_info, w=widget, lv=local_ver_str, rv=remote_ver_str, cb=on_complete_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
                        else:
                            widget.action_button.clicked.connect(on_complete_action)
                break
    
    def on_worker_finished(self, app_key):
        """
        Được gọi khi một worker độc lập hoàn thành tác vụ.
        Hàm này đảm bảo chỉ cập nhật cho đúng app đã xong.
        """
        # Xóa worker khỏi danh sách quản lý để giải phóng bộ nhớ
        if app_key in self.active_workers:
            del self.active_workers[app_key]

        # Rất quan trọng: Tải lại config từ file vào bộ nhớ
        # để chắc chắn rằng dữ liệu là mới nhất trước khi làm mới giao diện.
        self.load_config_and_apps(populate=False)

        # Làm mới toàn bộ danh sách để cập nhật giao diện
        # (chuyển nút "Tải" -> "Thêm", cập nhật phiên bản, v.v.)
        if not hasattr(self, '_populate_timer') or not self._populate_timer.isActive():
            self._populate_timer = QTimer(self)
            self._populate_timer.setSingleShot(True)
            self._populate_timer.timeout.connect(self.populate_lists)
            self._populate_timer.start(50) # Chờ 50ms để gom các lệnh gọi
    
    def filter_apps(self, text):
        text = text.lower().strip()
        min_chars = 1 if self.embed_mode else 2
        
        visible_categories = set()
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if hasattr(widget, 'app_key'):
                app_info = widget.app_info
                display_name = app_info.get('display_name', '').lower()
                is_match = text in display_name or len(text) < min_chars
                item.setHidden(not is_match)
                if is_match:
                    visible_categories.add(app_info.get('category', 'Chưa phân loại'))
            
        # Ẩn/hiện category header
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if not hasattr(widget, 'app_key'): # Đây là category header
                category_name = item.text().title() # Chuyển về dạng 'Chưa Phân Loại'
                item.setHidden(category_name not in visible_categories and len(text) >= min_chars)

    def start_installation(self):
        if self.install_worker and self.install_worker.isRunning():
            reply = self.show_styled_message_box(QMessageBox.Icon.Question, "Dừng tác vụ",
                                                 "Bạn có chắc muốn dừng quá trình cài đặt không?",
                                                 buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.install_worker.stop()
                self.start_button.setText("ĐANG DỪNG...")
                self.start_button.setDisabled(True)
            return

        # Nếu nút đang ở trạng thái "Xong"
        if self.start_button.text() == "Xong":
            self.reset_ui_after_completion()
            return

        apps_to_process = {}
        for key in self.selected_for_install:
            if key in self.remote_apps.get('app_items', {}):
                remote_info = self.remote_apps['app_items'][key]
                # local_info = self.local_apps.get(key, {})
                # # Mặc định là 'install', nhưng nếu có phiên bản mới thì là 'update'
                # action = 'install'
                # if self.is_app_downloaded(key, remote_info) and parse_version(remote_info.get('version', '0')) > parse_version(local_info.get('version', '0')):
                    # action = 'update'
                apps_to_process[key] = {'info': remote_info, 'action': 'install'}


        if not apps_to_process:
            self.show_styled_message_box(QMessageBox.Icon.Information, "Thông báo", "Vui lòng thêm ít nhất một phần mềm để cài đặt.")
            return

        # Vô hiệu hóa giao diện, ngoại trừ nút "Dừng"
        self.set_ui_interactive(False)
        self.start_button.setText("DỪNG")
        self.start_button.setEnabled(True)
        self.start_button.setStyleSheet("background-color: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;")

        self.install_worker = InstallWorker(apps_to_process)
        self.install_worker.signals.progress.connect(self.update_install_progress)
        self.install_worker.signals.progress_percentage.connect(self.update_download_progress_anywhere)
        self.install_worker.signals.finished.connect(self.on_installation_finished)
        self.install_worker.signals.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)))
        self.install_worker.signals.update_widget_status.connect(self.update_widget_status)
        self.install_worker.signals.tasks_batch_completed.connect(self.on_tasks_batch_completed)
        self.install_worker.start()
        
    def update_download_progress_selected(self, app_key, percentage):
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            widget = self.selected_list_widget.itemWidget(item)
            if hasattr(widget, 'app_key') and widget.app_key == app_key and widget.parent():
                widget.update_download_progress(app_key, percentage)
                break

    def update_install_progress(self, app_key, status, message):
        target_widget = None
        if not self.embed_mode and self.selected_list_widget.count() > 0:
            for i in range(self.selected_list_widget.count()):
                widget = self.selected_list_widget.itemWidget(self.selected_list_widget.item(i))
                if hasattr(widget, 'app_key') and widget.app_key == app_key:
                    target_widget = widget
                    break
        
        if not target_widget:
            for i in range(self.available_list_widget.count()):
                widget = self.available_list_widget.itemWidget(self.available_list_widget.item(i))
                if hasattr(widget, 'app_key') and widget.app_key == app_key:
                    target_widget = widget
                    break

        if target_widget and target_widget.parent():
            display_name = target_widget.app_info.get('display_name', app_key)
            status_text = f"{display_name}: {message}"
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText(status_text)
            
            target_widget.set_status(status)
    
    def on_installation_finished(self):
        if self.install_worker and not self.install_worker._is_stopped:
            status_text = "Hoàn tất! Nhấn 'Xong' để tiếp tục."
            if not self.embed_mode:
                self.status_label.setText(status_text)
                self.start_button.setText("Xong")
                self.start_button.setEnabled(True)
                self.start_button.setStyleSheet("background-color: #4CAF50; color: white;")
        else:
            self.reset_ui_after_completion()

        self.install_worker = None

        # Force populate và reset trong embed_mode
        if self.embed_mode:
            self.populate_lists()
            for i in range(self.available_list_widget.count()):
                widget = self.available_list_widget.itemWidget(self.available_list_widget.item(i))
                if hasattr(widget, 'set_status'):
                    widget.set_status("success")
                    widget.action_button.setText("Thêm")
                    widget.action_button.setStyleSheet("background-color: #4CAF50; color: white;")
                    # Reconnect nếu cần

    def reset_ui_after_completion(self):
        if not self.embed_mode:
            self.set_ui_interactive(True) # Re-enable UI
            self.start_button.setText("BẮT ĐẦU CÀI ĐẶT")
            self.start_button.setStyleSheet("background-color: #3498db; color: white;") # Blue button
            self.status_label.setText("Trạng thái: Sẵn sàng.")
        self.selected_for_install.clear()
        self.save_config()
        self.load_config_and_apps()

    def update_counts(self):
        if self.embed_mode: return
        compatible_count = sum(1 for i in range(self.available_list_widget.count()) if hasattr(self.available_list_widget.itemWidget(self.available_list_widget.item(i)), 'app_key'))
        selected_count = self.selected_list_widget.count()
        
        self.available_count_label.setText(f"Tổng số phần mềm: {compatible_count}")
        self.selected_count_label.setText(f"Đã chọn: {selected_count}")

    def save_config(self):
        if not self.embed_mode:
            self.config['settings']['selected_for_install'] = self.selected_for_install
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Không thể lưu cấu hình: {e}")
            
    def closeEvent(self, event):
        # Dừng các worker đang hoạt động
        # Dùng list() để tạo bản sao, tránh thay đổi dict khi đang duyệt
        for worker in list(self.active_workers.values()):
            if worker and worker.isRunning():
                worker.stop()
                worker.wait(2000) # Cho worker 2 giây để dừng

        if self.tool_manager_thread.isRunning():
            self.tool_manager_thread.quit()
            self.tool_manager_thread.wait(5000)
        
        self.save_config()
        super().closeEvent(event)
        
    def check_shutdown_signal(self):
        while True:
            if os.path.exists("shutdown_signal.txt"):  # Tệp do A tạo để ra lệnh tắt
                print("Nhận tín hiệu tắt, đang thoát...")
                os._exit(0)
            time.sleep(1)

def handle_auto_install_cli(args):
    """Xử lý riêng cho tham số dòng lệnh /auto_install."""
    arg_string = " ".join(args)
    # Tìm kiếm mẫu /auto_install[=:]<value> <app_key>
    match = re.search(r'/auto_install[=:]\s*(true|false)\s+([a-zA-Z0-9_-]+)', arg_string, re.IGNORECASE)

    if not match:
        return False # Không phải lệnh auto_install, bỏ qua

    value_str = match.group(1).lower()
    app_key = match.group(2)
    new_value = value_str == 'true'

    try:
        # Tải cấu hình hiện tại
        config = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    config = json.loads(content)

        # Cập nhật giá trị
        config.setdefault('app_items', {}).setdefault(app_key, {})['auto_install'] = new_value

        # Lưu lại cấu hình
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"Thành công: Đã đặt 'auto_install' = {new_value} cho phần mềm '{app_key}'.")

    except Exception as e:
        print(f"Lỗi: Không thể cập nhật cấu hình cho '{app_key}'. Chi tiết: {e}")

    return True # Đã xử lý lệnh, nên thoát chương trình

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # Phân tích tham số bằng shlex để hỗ trợ khoảng trắng
    raw_args = ' '.join(sys.argv[1:])
    cli_args = sys.argv[1:]
    
    # Xử lý lệnh /auto_install trước tiên <<
    if handle_auto_install_cli(cli_args):
        sys.exit(0)
    
    # Tách flags (--embed) ra khỏi các tham số dòng lệnh (/)
    flags = [arg for arg in cli_args if arg.startswith('--')]
    cli_command_args = [arg for arg in cli_args if not arg.startswith('--')]
    
    embed_mode = False
    embed_size = None
    for flag in flags:
        if flag.startswith('--embed'):
            embed_mode = True
            parts = flag.split('=', 1)
            if len(parts) == 2 and 'x' in parts[1]:
                try:
                    width, height = map(int, parts[1].split('x'))
                    embed_size = (width, height)
                except (ValueError, IndexError):
                    print(f"Cảnh báo: Định dạng kích thước cho --embed không hợp lệ: '{parts[1]}'. Dùng WIDTHxHEIGHT.")
            break

    app = QApplication(sys.argv)
    icon_path_main = resource_path("logo.ico")
    if Path(icon_path_main).exists():
        app.setWindowIcon(QIcon(icon_path_main))
    main_win = TekDT_AIS(embed_mode=embed_mode, embed_size=embed_size)

    # Xử lý /help riêng biệt vì nó không cần giao diện
    if '/help' in cli_command_args:
        help_text = """Sử dụng TekDT AIS qua dòng lệnh:
  /help                       Hiển thị trợ giúp này.
  /install                  Cài đặt các phần mềm có auto_install=true đã được tải về.
  /install "app1|app2"      Cài đặt các phần mềm được chỉ định (phải được tải về trước).
  /update                   Kiểm tra và cập nhật tất cả phần mềm đã được tải về.
  /update "app1|app2"       Cập nhật các phần mềm được chỉ định.
  /auto_install:true|false "app1|app2"       Cập nhật giá trị để đánh dấu phần mềm sẽ được cài đặt tự động khi dùng tham số /install. True là bật, false là tắt.
  
Kết hợp tham số:
  /install /update          Cập nhật và cài đặt các phần mềm auto_install=true.
  /install /update "app1"   Cập nhật (nếu có) và cài đặt các phần mềm chỉ định.

Lưu ý:
- Tên phần mềm (app key) là định danh duy nhất, không phải tên hiển thị.
- Sử dụng "|" để ngăn cách nhiều tên ứng dụng trong dấu ngoặc kép.
- Các hành động chỉ áp dụng cho phần mềm đã được tải về.
- Chương trình sẽ luôn hiển thị giao diện để theo dõi và tự tắt sau khi hoàn thành."""
        main_win.show_styled_message_box(QMessageBox.Icon.Information, "Trợ giúp dòng lệnh - TekDT AIS", help_text)
        sys.exit(0)
    
    # Các lệnh như /auto_install có thể được xử lý ở đây nếu cần, nhưng hiện tại tập trung vào /install và /update
    
    is_cli_command = any(arg in ['/install', '/update'] for arg in cli_command_args)
    main_win.is_cli_mode = is_cli_command
    
    if is_cli_command:
        # Chế độ CLI: Chờ tool check xong rồi mới chạy handle_cli_args.
        # handle_cli_args sẽ quyết định mọi thứ, bao gồm hiển thị GUI và thoát.
        main_win.show()
        def start_cli_handler(success, msg):
            if success:
                main_win.handle_cli_args(cli_command_args)
            else:
                # Nếu tool check thất bại, hiển thị lỗi và thoát
                main_win.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi khởi tạo", msg)
                QApplication.quit()
        
        main_win.tool_manager.finished.connect(start_cli_handler)
    else:
        # Chế độ GUI bình thường
        pass
    if not is_cli_command:
        main_win.show()
    
    sys.exit(app.exec())