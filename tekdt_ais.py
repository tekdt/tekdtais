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

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem, QLabel, QPushButton, QLineEdit,
                             QFrame, QScrollArea, QGraphicsOpacityEffect, QToolTip,
                             QMessageBox, QSizePolicy, QTextEdit)
from PySide6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QMovie
from PySide6.QtCore import (Qt, QSize, QThread, Signal, QObject, QPropertyAnimation,
                          QEasingCurve, QTimer, QRect, QCoreApplication)

# --- CÁC HẰNG SỐ VÀ CẤU HÌNH ---
APP_NAME = "TekDT AIS"
APP_VERSION = "1.0.2"
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
ODT_SETUP_URL = "https://download.microsoft.com/download/6c1eeb25-cf8b-41d9-8d0d-cc1dbc032140/officedeploymenttool_19029-20136.exe"
ODT_DIR = TOOLS_DIR / "ODT"
ODT_EXEC = ODT_DIR / "setup.exe"
EXTRACTION_BASE_DIR = Path("C:/TEKDT_AIS")

# Create storage directories if they don't exist
def initialize_directories_and_tools():
    """ Tạo các thư mục cần thiết và sao chép công cụ từ gói EXE (nếu cần) """
    # Tạo các thư mục lưu trữ bền vững
    for dir_path in [APPS_DIR, TOOLS_DIR, IMAGES_DIR_DATA, ARIA2_DIR, SEVENZ_DIR, EXTRACTION_BASE_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Nếu chạy dưới dạng EXE, kiểm tra và sao chép các công cụ đi kèm vào thư mục Tools
    if getattr(sys, 'frozen', False):
        bundled_tools = {
            resource_path("Tools/aria2/aria2c.exe"): ARIA2_EXEC,
            resource_path("Tools/7z/7za.exe"): SEVENZ_EXEC,
            resource_path("Tools/ODT/setup.exe"): ODT_EXEC
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
    progress_update = Signal(str)
    finished = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        # GitHub API cần User-Agent
        self.session.headers.update({'User-Agent': 'TekDT-AIS-App'})

    def run_checks(self):
        tools_present = ARIA2_EXEC.exists() and SEVENZ_EXEC.exists() and ODT_EXEC.exists()
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
                self._check_odt()
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
            
    def _check_odt(self):
        """Kiểm tra và tải Office Deployment Tool nếu cần."""
        if ODT_EXEC.exists():
            self.progress_update.emit("Office Deployment Tool đã có sẵn.")
            return

        self.progress_update.emit("Đang tải Office Deployment Tool...")
        try:
            # Tải file .exe chứa ODT
            response = self.session.get(ODT_SETUP_URL, stream=True)
            response.raise_for_status()

            # ODT là một self-extracting archive, cần chạy nó để giải nén
            temp_odt_installer = TOOLS_DIR / "odt_installer.exe"
            with open(temp_odt_installer, 'wb') as f:
                shutil.copyfileobj(response.raw, f)

            self.progress_update.emit("Đang giải nén Office Deployment Tool...")
            ODT_DIR.mkdir(exist_ok=True)
            
            # Lệnh giải nén tự động vào thư mục ODT_DIR
            # /quiet: chạy ẩn, /extract: giải nén, /log: ghi log (tùy chọn)
            command = [str(temp_odt_installer), f'/extract:{str(ODT_DIR)}', '/quiet']
            print(command)
            process = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
            
            print("returncode:", process.returncode)
            print("stdout:", process.stdout)
            print("stderr:", process.stderr)

            # subprocess.run sẽ đợi tiến trình con hoàn thành
            if process.returncode != 0:
                raise Exception(f"Giải nén ODT thất bại: {process.stderr}")

            # Dọn dẹp file cài đặt tạm SAU KHI đã chắc chắn giải nén xong
            temp_odt_installer.unlink()
            self.progress_update.emit("Office Deployment Tool đã sẵn sàng.")

        except Exception as e:
            raise Exception(f"Lỗi khi xử lý ODT: {e}")    

class AriaDownloader(QThread):
    # Tín hiệu trả về app_key để biết tiến trình của app nào
    progress_percentage = Signal(str, float)
    finished = Signal(str, bool) # app_key, success

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
    finished = Signal()
    progress = Signal(str, str, str)
    error = Signal(str)
    progress_percentage = Signal(str, float)
    update_widget_status = Signal(str, str)
    tasks_batch_completed = Signal(dict)
    
    def __init__(self, worker_tasks):
        super().__init__()
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
            # Tách biệt các tác vụ Office và tác vụ thông thường
            office_tasks = {}
            download_tasks = {}
            for key, task in self.worker_tasks.items():
                app_info = task['info']
                if app_info.get('type') == 'office_suite':
                    office_tasks[key] = task
                else:
                    download_path = APPS_DIR / key / app_info.get('output_filename', Path(app_info.get('download_url', '')).name)
                    
                    # Chỉ tải nếu file chưa tồn tại, hoặc nếu hành động là 'update'
                    needs_download = not download_path.exists() or task['action'] == 'update'
                    
                    if needs_download:
                        download_tasks[key] = task
                    else:
                        # Nếu không cần tải, đưa thẳng vào danh sách xử lý sau
                        self.tasks_to_process_after_download[key] = task

            for app_key, task_def in office_tasks.items():
                if self._is_stopped: break
                # Chỉ xử lý nếu hành động là 'download' hoặc 'update'
                if task_def['action'] in ['download', 'update']:
                    self._handle_office_download(app_key, task_def['info'])
                else:
                    # Nếu không phải download, đưa vào danh sách xử lý sau (để cài đặt)
                    self.tasks_to_process_after_download[app_key] = task_def
            
            if not download_tasks and not self.tasks_to_process_after_download:
                pass

            elif download_tasks:
                self.active_downloads = len(download_tasks)
                for app_key, task_def in download_tasks.items():
                    if self._is_stopped: break
                    
                    self.progress.emit(app_key, "processing", f"Chuẩn bị tải...")
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
                    downloader.progress_percentage.connect(self.progress_percentage)
                    downloader.finished.connect(self._on_download_finished)
                    
                    self.downloaders.append(downloader)
                    downloader.start()
            else:
                # Nếu không có gì để tải, chuyển ngay đến bước xử lý sau
                self._process_remaining_tasks()

            if self.active_downloads > 0:
                self.exec() # Bắt đầu vòng lặp sự kiện, giữ luồng tồn tại
            else:
                # Nếu không có gì để tải, xử lý các tác vụ còn lại và kết thúc
                self._process_remaining_tasks()
                self.finished.emit()

        except Exception as e:
            self.error.emit(f"Lỗi nghiêm trọng khi khởi tạo Worker: {e}")
            if self.isRunning(): # Đảm bảo quit() nếu có lỗi
                self.quit()
            self.finished.emit()

    def _extract_archive(self, archive_path, destination_dir):
        """
        Sử dụng 7za.exe để giải nén file.
        Hỗ trợ ghi đè (-y) và trích xuất với đầy đủ đường dẫn (x).
        """
        self.progress.emit(self.app_key, "installing", f"Đang giải nén file...")
        try:
            # Lệnh: 7za x <archive_path> -o<destination_dir> -y
            # x: giải nén với đường dẫn đầy đủ
            # -o: chỉ định thư mục đầu ra (viết liền không có khoảng trắng)
            # -y: tự động đồng ý với mọi câu hỏi (ghi đè file)
            command = [
                str(SEVENZ_EXEC),
                'x',
                str(archive_path),
                f'-o{str(destination_dir)}',
                '-y'
            ]
            process = subprocess.run(command, capture_output=True, text=True, timeout=300, check=False, creationflags=subprocess.CREATE_NO_WINDOW)

            if process.returncode != 0:
                error_message = process.stderr or process.stdout
                raise Exception(f"Giải nén thất bại: {error_message}")
            return True
        except Exception as e:
            self.progress.emit(self.app_key, "failed", f"Lỗi giải nén: {e}")
            return False

    def _find_executable(self, search_dir, pattern):
        """
        Tìm kiếm file thực thi theo pattern.
        Ưu tiên tìm ở thư mục gốc, sau đó tìm đệ quy trong các thư mục con.
        """
        search_path = Path(search_dir)
        
        # 1. Tìm trong thư mục gốc trước
        found_files = list(search_path.glob(pattern))
        if found_files:
            return found_files[0] # Trả về file đầu tiên tìm thấy

        # 2. Nếu không thấy, tìm đệ quy (recursive glob)
        found_files_recursive = list(search_path.rglob(pattern))
        if found_files_recursive:
            return found_files_recursive[0] # Trả về file đầu tiên tìm thấy
            
        return None # Không tìm thấy file nào
    
    def _handle_office_download(self, app_key, app_info):
        """Thực hiện tải bộ cài Office bằng ODT."""
        # self.update_widget_status.emit(app_key, "processing")
        self.progress.emit(app_key, "processing", "Đang tạo file cấu hình...")
        
        app_dir = APPS_DIR / app_key
        app_dir.mkdir(exist_ok=True)
        
        # Xóa file đánh dấu cũ nếu có (trường hợp update)
        marker_file = app_dir / "_download_completed.marker"
        if marker_file.exists():
            marker_file.unlink()

        # Tạo file XML để download
        xml_content = f"""
<Configuration>
  <Add OfficeClientEdition="{app_info['architecture'][1:]}" Channel="{app_info['channel']}">
    <Product ID="{app_info['product_id']}">
      <Language ID="vi-vn" />
    </Product>
  </Add>
  <Property Name="FORCEAPPSHUTDOWN" Value="FALSE" />
</Configuration>
"""
        config_path = app_dir / "download_config.xml"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(xml_content.strip())

        self.progress.emit(app_key, "processing", "Bắt đầu tải Office (có thể mất vài phút)...")
        self.update_widget_status.emit(app_key, "downloading_office")
        command = [str(ODT_EXEC), '/download', str(config_path)]
        
        try:
            # Chạy tiến trình tải về và chờ
            process = subprocess.Popen(command, cwd=app_dir, creationflags=subprocess.CREATE_NO_WINDOW)
            process.wait(timeout=3600) # Chờ tối đa 1 tiếng

            if self._is_stopped:
                self.update_widget_status.emit(app_key, "stopped")
                return

            if process.returncode == 0:
                # Tải thành công -> Tạo file đánh dấu
                with open(marker_file, 'w') as f:
                    f.write('done')
                self.update_widget_status.emit(app_key, "success")
                self.progress.emit(app_key, "success", "Tải Office thành công!")
                # Ghi config
                self._commit_config_changes({app_key: {'info': app_info, 'action': 'download'}})
            else:
                raise Exception(f"ODT download exited with code {process.returncode}")

        except Exception as e:
            self.update_widget_status.emit(app_key, "failed")
            self.progress.emit(app_key, "failed", f"Lỗi tải Office: {e}")
    
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
        with self.lock:
            task_def = self.worker_tasks[app_key]
            
            if success:
                self.update_widget_status.emit(app_key, "success")
                self._commit_config_changes({app_key: task_def})
            else:
                status = "stopped" if self._is_stopped else "failed"
                self.update_widget_status.emit(app_key, status) # Cập nhật UI thất bại
                self.progress.emit(app_key, status, f"Tải thất bại.")

            self.active_downloads -= 1
            if self.active_downloads == 0:
                # Xử lý các tác vụ không cần tải (nếu có)
                self._process_remaining_tasks() 
                self.quit()
                self.finished.emit() # Báo hiệu worker đã xong việc

    def _process_single_task(self, app_key, task_def):
        if self._is_stopped: return

        app_info = task_def['info']
        action = task_def['action'] # 'install' hoặc 'update'
        display_name = app_info.get('display_name', app_key)
        task_successful = False

        self._download_icon_if_needed(app_key, app_info)

        # Logic xử lý chính: Dù là 'install' hay 'update', cuối cùng cũng sẽ chạy trình cài đặt
        # nếu đó là loại 'installer'.
        if app_info.get('type') == 'installer':
            download_path = APPS_DIR / app_key / app_info.get('output_filename', Path(app_info['download_url']).name)
            if not download_path.exists():
                self.update_widget_status.emit(app_key, "failed")
                self.progress.emit(app_key, "failed", f"Lỗi: Không tìm thấy file đã tải của {display_name}.")
                return

            self.update_widget_status.emit(app_key, "installing")
            self.progress.emit(app_key, "installing", f"Đang cài đặt {display_name}...")

            install_params = app_info.get('install_params', '')
            install_command = [str(download_path)] + shlex.split(install_params)
            try:
                # Chạy tiến trình cài đặt
                install_process = subprocess.Popen(install_command, creationflags=subprocess.CREATE_NO_WINDOW)
                install_process.wait(timeout=600) # Chờ tối đa 10 phút

                if install_process.returncode == 0:
                    self.update_widget_status.emit(app_key, "success")
                    self.progress.emit(app_key, "success", f"Đã xử lý {display_name} thành công!")
                    task_successful = True
                else:
                    self.update_widget_status.emit(app_key, "failed")
                    self.progress.emit(app_key, "failed", f"Cài đặt thất bại (mã lỗi: {install_process.returncode}).")
            except subprocess.TimeoutExpired:
                self.update_widget_status.emit(app_key, "failed")
                self.progress.emit(app_key, "failed", f"Cài đặt quá thời gian cho phép.")
            except Exception as e:
                self.update_widget_status.emit(app_key, "failed")
                self.progress.emit(app_key, "failed", f"Lỗi khi chạy cài đặt: {e}")
                
        elif app_info.get('type') == 'portable' or action == 'download':
            # Đối với portable hoặc chỉ download, tải xong là thành công
            self.update_widget_status.emit(app_key, "success")
            self.progress.emit(app_key, "success", f"Đã xử lý {display_name} thành công!")
            task_successful = True
    
    def _process_remaining_tasks(self):
        """Xử lý các tác vụ còn lại như cài đặt, cập nhật icon..."""
        if self._is_stopped:
            self.finished.emit()
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

            if app_info.get('type') == 'office_suite' and action in ["install", "update"]:
                # --- LOGIC CÀI ĐẶT OFFICE ---
                self.update_widget_status.emit(app_key, "installing")
                self.progress.emit(app_key, "installing", f"Đang cài đặt {display_name}...")
                
                app_dir = APPS_DIR / app_key
                # Tạo file XML để install
                xml_content = f"""
<Configuration>
  <Add OfficeClientEdition="{app_info['architecture'][1:]}" Channel="{app_info['channel']}" SourcePath="{app_dir}">
    <Product ID="{app_info['product_id']}">
      <Language ID="vi-vn" />
    </Product>
  </Add>
  <Display Level="None" AcceptEULA="TRUE" />
  <Property Name="FORCEAPPSHUTDOWN" Value="TRUE" />
</Configuration>
"""
                config_path = app_dir / "install_config.xml"
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content.strip())
                
                command = [str(ODT_EXEC), '/configure', str(config_path)]
                try:
                    install_process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
                    install_process.wait(timeout=1800) # Chờ 30 phút

                    if install_process.returncode == 0:
                        self.update_widget_status.emit(app_key, "success")
                        task_successful = True
                    else:
                        self.update_widget_status.emit(app_key, "failed")
                except Exception as e:
                     self.update_widget_status.emit(app_key, "failed")
            
            # --- Xử lý Cài đặt/Tải về ---
            if action == "download" or app_info.get('type') == 'portable':
                # Với 'download' hoặc portable, chỉ cần tải xong là thành công
                self.update_widget_status.emit(app_key, "success")
                self.progress.emit(app_key, "success", f"Đã xử lý {display_name} thành công!")
                task_successful = True

            elif (action == "install" or action == "update") and app_info.get('type') == 'installer':
                output_filename_str = app_info.get('output_filename', Path(app_info.get('download_url', '')).name)
                
                # 1. Phân tích output_filename để lấy file nén và file thực thi
                archive_name = output_filename_str
                executable_pattern = output_filename_str
                if '|' in output_filename_str:
                    parts = output_filename_str.split('|', 1)
                    archive_name = parts[0]
                    executable_pattern = parts[1]

                download_path = APPS_DIR / app_key / archive_name
                
                if not download_path.exists():
                    self.update_widget_status.emit(app_key, "failed")
                    self.progress.emit(app_key, "failed", f"Lỗi: Không tìm thấy file đã tải '{archive_name}'.")
                    continue

                search_base_dir = APPS_DIR / app_key # Mặc định tìm trong thư mục app
                is_archive = any(archive_name.lower().endswith(ext) for ext in ['.zip', '.7z', '.rar', '.tar', '.iso', '.img'])

                # 2. Nếu là file nén, giải nén ra C:\TEKDT_AIS\<app_key>
                if is_archive:
                    extraction_dir = EXTRACTION_BASE_DIR / app_key
                    extraction_dir.mkdir(parents=True, exist_ok=True)
                    
                    if not self._extract_archive(download_path, extraction_dir):
                        # Hàm _extract_archive đã tự gửi tín hiệu lỗi, nên chỉ cần continue
                        continue
                    
                    search_base_dir = extraction_dir # Cập nhật lại đường dẫn tìm kiếm

                # 3. Tìm file thực thi dựa trên pattern (hỗ trợ wildcard *)
                self.progress.emit(app_key, "installing", f"Đang tìm file thực thi '{executable_pattern}'...")
                executable_path = self._find_executable(search_base_dir, executable_pattern)

                if not executable_path:
                    self.update_widget_status.emit(app_key, "failed")
                    self.progress.emit(app_key, "failed", f"Không tìm thấy file thực thi '{executable_pattern}'.")
                    continue

                # 4. Chạy file thực thi đã tìm được với các tham số
                self.update_widget_status.emit(app_key, "installing")
                self.progress.emit(app_key, "installing", f"Đang cài đặt {display_name}...")
                
                install_params = app_info.get('install_params', '')
                install_command = [str(executable_path)] + shlex.split(install_params)
                
                try:
                    install_process = subprocess.Popen(install_command, creationflags=subprocess.CREATE_NO_WINDOW)
                    install_process.wait(timeout=600)

                    if install_process.returncode == 0:
                        self.update_widget_status.emit(app_key, "success")
                        self.progress.emit(app_key, "success", f"Đã xử lý {display_name} thành công!")
                        task_successful = True
                    else:
                        self.update_widget_status.emit(app_key, "failed")
                        self.progress.emit(app_key, "failed", f"Cài đặt thất bại (mã lỗi: {install_process.returncode}).")
                except subprocess.TimeoutExpired:
                    self.update_widget_status.emit(app_key, "failed")
                    self.progress.emit(app_key, "failed", f"Cài đặt quá thời gian cho phép.")
                except Exception as e:
                    self.update_widget_status.emit(app_key, "failed")
                    self.progress.emit(app_key, "failed", f"Lỗi khi chạy cài đặt: {e}")

            # Nếu tác vụ thành công, thêm vào danh sách để cập nhật config
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

                    # Thêm vào dictionary để gửi đi qua tín hiệu
                    updated_items_for_signal[app_key] = existing_item_info

                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                # Phát tín hiệu MỘT LẦN với TẤT CẢ các mục đã cập nhật
                if updated_items_for_signal:
                    self.tasks_batch_completed.emit(updated_items_for_signal)

            except (IOError, json.JSONDecodeError) as e:
                self.error.emit(f"Lỗi nghiêm trọng khi ghi file config: {e}")

# --- WIDGET TÙY CHỈNH CHO MỖI PHẦN MỀM ---
class AppItemWidget(QWidget):
    add_requested = Signal(str, dict)
    remove_requested = Signal(str, dict)
    auto_install_toggled = Signal(str, bool)
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
        if not isinstance(icon_file, str):
            icon_file = ''
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
        
    def reset_status_ui(self):
        """Hàm call-back an toàn để reset trạng thái UI."""
        self.set_status("")
    
    # def set_status(self, status):
        # self.status_label.setMovie(None)
        # self.status_label.setPixmap(QPixmap())

        # if status == "success":
            # self._progress_animation.stop()
            # self.status_label.setPixmap(QPixmap(resource_path('Images/success.png')).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            # self.name_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12pt;")
            # self.action_button.setEnabled(True) # Re-enable after process
            # self._current_progress = 0
            # self.progress_overlay.hide()
            # self.progress_overlay.setGeometry(0, 0, 0, self.height())
            # self.status_label.show()
            # # QTimer.singleShot(2000, self.reset_status_ui)
            # timer = QTimer(self)
            # timer.setSingleShot(True)
            # timer.timeout.connect(self.reset_status_ui)
            # timer.start(2000)
        # elif status == "failed":
            # self._progress_animation.stop()
            # self.status_label.setPixmap(QPixmap(resource_path('Images/failed.png')).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            # self.name_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 12pt;")
            # self.action_button.setEnabled(True) # Re-enable after process
            # self._current_progress = 0
            # self.progress_overlay.hide()
            # self.status_label.show()
        # elif status == "processing": # Downloading
            # movie = QMovie(resource_path('Images/loading.gif'))
            # self.status_label.setMovie(movie)
            # movie.start()
            # self.action_button.setEnabled(False)
            # self.status_label.show()
        # elif status == "installing": # Installing (new status)
            # movie = QMovie(resource_path('Images/loading.gif'))
            # self.status_label.setMovie(movie)
            # movie.start()
            # self.action_button.setEnabled(False)
            # self.status_label.show()
        # else: # Idle
            # self.status_label.hide()
            # self.name_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
            # self.action_button.setEnabled(True)
            # self._current_progress = 0
            # self.progress_overlay.hide()

    def set_status(self, status):
        # Dừng mọi animation và movie cũ trước khi bắt đầu cái mới
        self._progress_animation.stop()
        self.status_label.setMovie(None)
        self.status_label.setPixmap(QPixmap())

        if status == "success":
            self.status_label.setPixmap(QPixmap(resource_path('Images/success.png')).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.name_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12pt;")
            self.action_button.setEnabled(True)
            self._current_progress = 0
            self.progress_overlay.hide()
            self.progress_overlay.setGeometry(0, 0, 0, self.height())
            self.status_label.show()
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self.reset_status_ui)
            timer.start(2000)
        elif status == "failed":
            self.status_label.setPixmap(QPixmap(resource_path('Images/failed.png')).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.name_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 12pt;")
            self.action_button.setEnabled(True)
            self._current_progress = 0
            self.progress_overlay.hide()
            self.status_label.show()
        elif status == "processing" or status == "installing":
            movie = QMovie(resource_path('Images/loading.gif'))
            self.status_label.setMovie(movie)
            movie.start()
            self.action_button.setEnabled(False)
            self.status_label.show()
            self.progress_overlay.hide() # Ẩn lớp phủ tiến trình cũ
        elif status == "downloading_office": # <--- LOGIC MỚI CHO HIỆU ỨNG OFFICE
            self.action_button.setEnabled(False)
            self.status_label.hide() # Ẩn icon loading gif đi
            self.progress_overlay.show()
            self.progress_overlay.raise_()

            # Cấu hình animation chạy lặp vô hạn
            self._progress_animation.setDuration(1500) # Tốc độ chạy của lớp phủ
            self._progress_animation.setLoopCount(-1) # Lặp lại vô hạn
            self._progress_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            # Điểm bắt đầu: lớp phủ rộng 30% và ở ngoài bên trái
            start_rect = QRect(-int(self.width() * 0.3), 0, int(self.width() * 0.3), self.height())
            # Điểm kết thúc: lớp phủ ở ngoài bên phải
            end_rect = QRect(self.width(), 0, int(self.width() * 0.3), self.height())
            
            self._progress_animation.setStartValue(start_rect)
            self._progress_animation.setEndValue(end_rect)
            self._progress_animation.start()
        else: # Trạng thái chờ (Idle)
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
            QTimer.singleShot(500, lambda: self.set_status("success"))

# --- CỬA SỔ CHÍNH ---
class TekDT_AIS(QMainWindow):
    def __init__(self, embed_mode=False, embed_size=None, is_cli_mode=False, cli_args=None):
        super().__init__()
        self.embed_mode = embed_mode
        if embed_mode:
            threading.Thread(target=self.check_shutdown_signal, daemon=True).start()
        self.embed_size = embed_size
        
        self.is_cli_mode = is_cli_mode
        self.cli_args = cli_args if cli_args is not None else []
        
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
        self.cli_target_apps = []        
        self._scroll_positions = {}
        self.is_cli_mode = False
        self.is_processing = False
        self.central_widget_ref = None
        self.install_worker = None

        if self.embed_mode:
            self.setup_embed_ui()
        else:
            self.setup_ui()
            
        # Vô hiệu hóa UI và hiển thị trạng thái khởi động
        self.central_widget_ref = self.centralWidget()
        self.central_widget_ref.setEnabled(False)
        self.show_startup_status("Đang khởi tạo...")
        
        QTimer.singleShot(50, self.start_tool_check)
        
        
    def start_tool_check(self):
        """Khởi tạo và chạy ToolManager trong một luồng riêng."""
        self.tool_manager_thread = QThread()
        self.tool_manager = ToolManager()
        self.tool_manager.moveToThread(self.tool_manager_thread)
        self.tool_manager.finished.connect(self.on_tool_check_finished)
        self.tool_manager_thread.started.connect(self.tool_manager.run_checks)
        self.tool_manager.progress_update.connect(self.update_startup_status)
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
        
        # Ẩn overlay khởi động
        if hasattr(self, 'startup_overlay'):
            self.startup_overlay.hide()
        
        if not success:
            self.show_styled_message_box(QMessageBox.Icon.Warning, "Lỗi công cụ", message)
            if not (ARIA2_EXEC.exists() and SEVENZ_EXEC.exists()):
                QApplication.quit()
                return
        
        # Bật lại giao diện chính
        if self.central_widget_ref:
            self.central_widget_ref.setEnabled(True)

        # --- LOGIC QUYẾT ĐỊNH CHẾ ĐỘ CHẠY ---
        if self.is_cli_mode:
            # Nếu là chế độ dòng lệnh, gọi hàm xử lý CLI
            # Dùng QTimer để đảm bảo giao diện được vẽ xong trước khi bắt đầu xử lý nặng
            QTimer.singleShot(100, lambda: self.handle_cli_args(self.cli_args))
        else:
            # Nếu là chế độ giao diện thông thường, tải danh sách ứng dụng
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

    def _generate_office_suites_info(self):
        """
        Tạo thông tin cho các bộ Office để hiển thị trong danh sách.
        """
        suites = {
            # Microsoft 365 Apps
            "O365ProPlusRetail": {"display_name": "Microsoft 365 Apps for enterprise", "channel": "Current"},
            "O365BusinessRetail": {"display_name": "Microsoft 365 Apps for business", "channel": "Current"},
            "O365ProPlusEEANoTeamsRetail": {"display_name": "M365 Apps for enterprise (No Teams)", "channel": "Current"},
            "O365BusinessEEANoTeamsRetail": {"display_name": "M365 Apps for business (No Teams)", "channel": "Current"},

            # Microsoft 365 Other Channels
            "O365ProPlusMonthlyEnterprise": {"display_name": "Microsoft 365 Apps for enterprise (Monthly Enterprise Channel)", "channel": "MonthlyEnterprise"},
            "O365ProPlusSemiAnnual": {"display_name": "Microsoft 365 Apps for enterprise (Semi-Annual Channel)", "channel": "SemiAnnual"},

            # Non-365 Retail Suites
            "HomeBusinessRetail": {"display_name": "Office Home Business (Retail)", "channel": "Retail"},
            "HomeBusiness2019Retail": {"display_name": "Office Home Business 2019", "channel": "Retail"},
            "HomeBusiness2021Retail": {"display_name": "Office Home Business 2021", "channel": "Retail"},
            "HomeBusiness2024Retail": {"display_name": "Office Home Business 2024", "channel": "Retail"},
            "HomeStudentRetail": {"display_name": "Office Home Student (Retail)", "channel": "Retail"},
            "HomeStudent2019Retail": {"display_name": "Office Home Student 2019", "channel": "Retail"},
            "HomeStudent2021Retail": {"display_name": "Office Home Student 2021", "channel": "Retail"},
            "Home2024Retail": {"display_name": "Office Home 2024 (Retail)", "channel": "Retail"},
            "O365HomePremRetail": {"display_name": "Office 365 Home Premium", "channel": "Retail"},
            "ProfessionalRetail": {"display_name": "Office Professional (Retail)", "channel": "Retail"},
            "Professional2019Retail": {"display_name": "Office Professional 2019", "channel": "Retail"},
            "Personal2019Retail": {"display_name": "Office Personal 2019", "channel": "Retail"},

            # Component Apps Retail
            "AccessRetail": {"display_name": "Access (Retail)", "channel": "Retail"},
            "Access2019Retail": {"display_name": "Access 2019", "channel": "Retail"},
            "Access2021Retail": {"display_name": "Access 2021", "channel": "Retail"},
            "Access2024Retail": {"display_name": "Access 2024", "channel": "Retail"},
            "ExcelRetail": {"display_name": "Excel (Retail)", "channel": "Retail"},
            "Excel2019Retail": {"display_name": "Excel 2019", "channel": "Retail"},
            "Excel2021Retail": {"display_name": "Excel 2021", "channel": "Retail"},
            "Excel2024Retail": {"display_name": "Excel 2024", "channel": "Retail"},
            "OutlookRetail": {"display_name": "Outlook (Retail)", "channel": "Retail"},
            "Outlook2019Retail": {"display_name": "Outlook 2019", "channel": "Retail"},
            "Outlook2021Retail": {"display_name": "Outlook 2021", "channel": "Retail"},
            "Outlook2024Retail": {"display_name": "Outlook 2024", "channel": "Retail"},
            "PowerPointRetail": {"display_name": "PowerPoint (Retail)", "channel": "Retail"},
            "PowerPoint2019Retail": {"display_name": "PowerPoint 2019", "channel": "Retail"},
            "PowerPoint2021Retail": {"display_name": "PowerPoint 2021", "channel": "Retail"},
            "PowerPoint2024Retail": {"display_name": "PowerPoint 2024", "channel": "Retail"},
            "OneNoteRetail": {"display_name": "OneNote (Retail)", "channel": "Retail"},
            "OneNoteFreeRetail": {"display_name": "OneNote Free (Retail)", "channel": "Retail"},
            "PublisherRetail": {"display_name": "Publisher (Retail)", "channel": "Retail"},

            # Volume / LTSC Suites 2019
            "ProPlus2019Volume": {"display_name": "Office Professional Plus 2019 (Volume)", "channel": "PerpetualVL2019"},
            "Standard2019Volume": {"display_name": "Office Standard 2019 (Volume)", "channel": "PerpetualVL2019"},
            "VisioPro2019Volume": {"display_name": "Visio Professional 2019 (Volume)", "channel": "PerpetualVL2019"},
            "VisioStd2019Volume": {"display_name": "Visio Standard 2019 (Volume)", "channel": "PerpetualVL2019"},
            "ProjectPro2019Volume": {"display_name": "Project Professional 2019 (Volume)", "channel": "PerpetualVL2019"},
            "ProjectStd2019Volume": {"display_name": "Project Standard 2019 (Volume)", "channel": "PerpetualVL2019"},

            # Office 2021 Volume / LTSC
            "Office2021Volume": {"display_name": "Office LTSC Professional Plus 2021", "channel": "PerpetualVL2021"},
            "Standard2021Volume": {"display_name": "Office Standard 2021 (Volume)", "channel": "PerpetualVL2021"},
            "VisioPro2021Volume": {"display_name": "Visio Professional 2021 (Volume)", "channel": "PerpetualVL2021"},
            "VisioStd2021Volume": {"display_name": "Visio Standard 2021 (Volume)", "channel": "PerpetualVL2021"},
            "ProjectPro2021Volume": {"display_name": "Project Professional 2021 (Volume)", "channel": "PerpetualVL2021"},
            "ProjectStd2021Volume": {"display_name": "Project Standard 2021 (Volume)", "channel": "PerpetualVL2021"},

            # Office 2016 Volume
            "ProPlus2016Volume": {"display_name": "Office Professional Plus 2016 (Volume)", "channel": "PerpetualVL2016"},
            "Standard2016Volume": {"display_name": "Office Standard 2016 (Volume)", "channel": "PerpetualVL2016"},
            "VisioPro2016Volume": {"display_name": "Visio Professional 2016 (Volume)", "channel": "PerpetualVL2016"},
            "VisioStd2016Volume": {"display_name": "Visio Standard 2016 (Volume)", "channel": "PerpetualVL2016"},
            "ProjectPro2016Volume": {"display_name": "Project Professional 2016 (Volume)", "channel": "PerpetualVL2016"},
            "ProjectStd2016Volume": {"display_name": "Project Standard 2016 (Volume)", "channel": "PerpetualVL2016"},

            # Office 2013 Volume
            "ProPlus2013Volume": {"display_name": "Office Professional Plus 2013 (Volume)", "channel": "PerpetualVL2013"},
            "Standard2013Volume": {"display_name": "Office Standard 2013 (Volume)", "channel": "PerpetualVL2013"},
            "VisioPro2013Volume": {"display_name": "Visio Professional 2013 (Volume)", "channel": "PerpetualVL2013"},
            "VisioStd2013Volume": {"display_name": "Visio Standard 2013 (Volume)", "channel": "PerpetualVL2013"},
            "ProjectPro2013Volume": {"display_name": "Project Professional 2013 (Volume)", "channel": "PerpetualVL2013"},
            "ProjectStd2013Volume": {"display_name": "Project Standard 2013 (Volume)", "channel": "PerpetualVL2013"},

            # Proofing Tools
            "ProofingTools": {"display_name": "Proofing Tools (Office 2019)", "channel": "Retail"},
            "ProofingTools2021": {"display_name": "Proofing Tools (Office 2021)", "channel": "Retail"},
            "ProofingTools2024": {"display_name": "Proofing Tools (Office 2024)", "channel": "Retail"},

            # LTSC 2024 Volume
            "ProPlus2024Volume": {"display_name": "Office Professional Plus 2024 (Volume)", "channel": "PerpetualVL2024"},
            "Standard2024Volume": {"display_name": "Office Standard 2024 (Volume)", "channel": "PerpetualVL2024"},
            "VisioPro2024Volume": {"display_name": "Visio Professional 2024 (Volume)", "channel": "PerpetualVL2024"},
            "VisioStd2024Volume": {"display_name": "Visio Standard 2024 (Volume)", "channel": "PerpetualVL2024"},
            "ProjectPro2024Volume": {"display_name": "Project Professional 2024 (Volume)", "channel": "PerpetualVL2024"},
            "ProjectStd2024Volume": {"display_name": "Project Standard 2024 (Volume)", "channel": "PerpetualVL2024"},
        }


        office_apps = {}
        for product_id, info in suites.items():
            for arch in ["64", "32"]:
                app_key = f"{product_id}_{arch}bit"
                display_name_with_arch = f"{info['display_name']} (x{arch})"
                
                office_apps[app_key] = {
                    "display_name": display_name_with_arch,
                    "version": "1.0.0.0", # Office tự quản lý phiên bản
                    "description": f"Bộ cài đặt {display_name_with_arch} qua Office Deployment Tool.",
                    "category": "Văn phòng",
                    "type": "office_suite",  # Key đặc biệt để nhận diện
                    "icon_url": "https://img.icons8.com/color/96/microsoft-office-2019.png", # Icon chung
                    "product_id": product_id,
                    "architecture": f"x{arch}",
                    "channel": info['channel'],
                }
        return office_apps
    
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
        # --- Logic riêng cho Office ---
        if app_info.get('type') == 'office_suite':
            marker_file = APPS_DIR / app_key / "_download_completed.marker"
            return marker_file.exists()
        
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
        # Tải dữ liệu remote và local mà không vẽ lại giao diện
        self.load_config_and_apps(populate=False) 
        if not self.remote_apps.get('app_items'):
            self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi", "Không thể tải danh sách phần mềm. Không thể tiếp tục.")
            QApplication.quit()
            return

        # Xác định hành động người dùng yêu cầu
        is_install_action = '/install' in args
        is_update_action = '/update' in args
        
        # --- BƯỚC 1: Xác định danh sách phần mềm mục tiêu (target_keys) ---
        target_keys = set()
        app_names_str = ""
        for arg in args:
            if not arg.startswith('/'):
                app_names_str = arg.strip('\'"')
                break

        if app_names_str:
            # Trường hợp 1: Có cung cấp tên cụ thể (vd: /install "app1|app2")
            target_keys = set(app_names_str.split('|'))
        elif is_install_action and not app_names_str:
            # Trường hợp 2: /install hoặc /install /update không có tên -> lấy app có auto_install=true
            for key, info in self.local_apps.items():
                if info.get('auto_install', False):
                    target_keys.add(key)
        elif is_update_action and not is_install_action and not app_names_str:
            # Trường hợp 3: Chỉ có /update không có tên -> lấy tất cả app đã tải
            for key in self.local_apps:
                target_keys.add(key)
                
        # Gán danh sách mục tiêu này để giao diện sử dụng
        self.cli_target_apps = list(target_keys)

        # --- BƯỚC 2: Xây dựng danh sách tác vụ cho Worker (worker_tasks) ---
        worker_tasks = {}
        self.cli_task_results = {} # Reset kết quả
        
        # Chuẩn bị cho báo cáo cuối cùng
        report = {
            'update': {'success': 0, 'fail': 0, 'skipped': []},
            'install': {'success': 0, 'fail': 0, 'skipped': []}
        }

        for key in target_keys:
            remote_info = self.remote_apps.get('app_items', {}).get(key)
            local_info = self.local_apps.get(key, {})

            # Bỏ qua nếu không tìm thấy thông tin phần mềm trên server
            if not remote_info:
                report['update']['skipped'].append(key)
                report['install']['skipped'].append(key)
                continue
            
            # Bỏ qua nếu phần mềm CHƯA được tải về
            if not self.is_app_downloaded(key, remote_info):
                report['update']['skipped'].append(key)
                report['install']['skipped'].append(key)
                continue

            # Logic xác định hành động
            needs_update = False
            if is_update_action:
                local_version = local_info.get('version', '0')
                remote_version = remote_info.get('version', '0')
                if parse_version(remote_version) > parse_version(local_version):
                    needs_update = True
            
            # Quyết định tác vụ cuối cùng
            if needs_update:
                # Nếu cần cập nhật, hành động sẽ là 'update'.
                # Worker sẽ tự xử lý việc tải phiên bản mới.
                # Sau khi update xong, nếu có /install, worker sẽ cài đặt.
                worker_tasks[key] = {'info': remote_info, 'action': 'update'}
            elif is_install_action:
                # Nếu không cần update nhưng có lệnh /install, hành động là 'install'
                worker_tasks[key] = {'info': remote_info, 'action': 'install'}

        if not worker_tasks:
            self.show_styled_message_box(QMessageBox.Icon.Information, "Thông báo", "Không có tác vụ nào cần thực hiện (phần mềm không tồn tại, chưa được tải về, hoặc đã là phiên bản mới nhất).")
            QApplication.quit()
            return

        # --- BƯỚC 3: Hiển thị giao diện và khởi chạy Worker ---
        self.show()
        # QUAN TRỌNG: Gọi populate_lists SAU KHI đã xác định self.cli_target_apps
        self.populate_lists() 
        
        self.set_ui_interactive(False) # Vô hiệu hóa tương tác
        self.start_button.hide() # Ẩn nút "Bắt đầu" đi là đúng yêu cầu
        
        self.install_worker = InstallWorker(worker_tasks)

        # --- BƯỚC 4: Xử lý khi Worker hoàn thành ---
        def on_cli_finished():
            # Khởi tạo lại một đối tượng report sạch để đếm lại từ đầu
            final_report = {
                'update': {'success': 0, 'fail': 0},
                'install': {'success': 0, 'fail': 0}
            }

            # Duyệt qua danh sách kết quả cuối cùng
            for key, result in self.cli_task_results.items():
                action = result.get('action')
                status = result.get('status')
                
                # Chỉ quan tâm đến kết quả cuối cùng là thành công hoặc thất bại
                if status not in ['success', 'failed']:
                    continue

                # Phân loại kết quả vào report
                if action == 'update':
                    if status == 'success':
                        final_report['update']['success'] += 1
                    else:
                        final_report['update']['fail'] += 1
                elif action == 'install':
                    if status == 'success':
                        final_report['install']['success'] += 1
                    else:
                        final_report['install']['fail'] += 1

            # Xây dựng thông báo tổng kết từ final_report đã được đếm chính xác
            summary_lines = []
            if is_update_action:
                s = final_report['update']['success']
                f = final_report['update']['fail']
                # Lấy số lượng app bị bỏ qua từ report ban đầu
                skip = len(report['update'].get('skipped', []))
                summary_lines.append(f"--- Cập nhật ---\nThành công: {s} | Thất bại: {f} | Bỏ qua: {skip}")
            
            if is_install_action:
                s = final_report['install']['success']
                f = final_report['install']['fail']
                # Lấy số lượng app bị bỏ qua từ report ban đầu
                skip = len(report['install'].get('skipped', []))
                summary_lines.append(f"--- Cài đặt ---\nThành công: {s} | Thất bại: {f} | Bỏ qua: {skip}")

            final_message = "\n\n".join(summary_lines) if summary_lines else "Không có tác vụ nào được thực hiện."
            self.show_styled_message_box(QMessageBox.Icon.Information, "Hoàn tất tác vụ dòng lệnh", final_message)
            QApplication.quit()
        
        # Kết nối các signals từ worker
        self.install_worker.progress.connect(self.update_and_record_progress, Qt.ConnectionType.QueuedConnection)
        self.install_worker.progress_percentage.connect(self.update_download_progress_anywhere, Qt.ConnectionType.QueuedConnection)
        self.install_worker.finished.connect(on_cli_finished, Qt.ConnectionType.QueuedConnection)
        self.install_worker.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)), Qt.ConnectionType.QueuedConnection)
        self.install_worker.update_widget_status.connect(self.update_widget_status, Qt.ConnectionType.QueuedConnection)
        self.install_worker.tasks_batch_completed.connect(self.on_tasks_batch_completed, Qt.ConnectionType.QueuedConnection)
        self.install_worker.start()

    def update_and_record_progress(self, app_key, status, message):
        """Cập nhật giao diện và ghi lại kết quả cuối cùng cho các tác vụ CLI."""
        self.update_install_progress(app_key, status, message)
        
        if self.is_cli_mode and status in ["success", "failed", "stopped"]:
            if self.install_worker and app_key in self.install_worker.worker_tasks:
                original_action = self.install_worker.worker_tasks[app_key]['action']
                
                # Logic mới để ghi nhận kết quả chính xác
                # Nếu hành động gốc là 'update'
                if original_action == 'update':
                    # Nếu tải về thất bại, thì cả update và install đều thất bại
                    if status == 'failed' and message == "Tải thất bại.":
                        self.cli_task_results[app_key] = {'status': 'failed', 'action': 'update'}
                    # Nếu cài đặt thất bại sau khi update
                    elif status == 'failed':
                        self.cli_task_results[app_key] = {'status': 'failed', 'action': 'install'}
                    # Nếu thành công
                    elif status == 'success':
                        # Ghi nhận thành công cho cả hai nếu có lệnh /install
                        is_install_requested = '/install' in self.cli_args
                        self.cli_task_results[f"{app_key}_update"] = {'status': 'success', 'action': 'update'}
                        if is_install_requested:
                             self.cli_task_results[f"{app_key}_install"] = {'status': 'success', 'action': 'install'}

                # Nếu hành động gốc là 'install'
                elif original_action == 'install':
                    self.cli_task_results[app_key] = {'status': status, 'action': 'install'}

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
        self.search_box.setEnabled(enabled)
        self.available_list_widget.setEnabled(enabled)
        
        # Cập nhật các mục trong danh sách đã chọn
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            widget = self.selected_list_widget.itemWidget(item)
            if hasattr(widget, 'action_button'):
                if not enabled:
                    # Ẩn nút "Bỏ" đi thay vì chỉ vô hiệu hóa
                    widget.action_button.hide()
                    widget.set_status("processing")
                else:
                    # Hiển thị lại nút "Bỏ"
                    widget.action_button.show()
                    widget.set_status("")
        
        # Giữ nút "Bắt đầu cài đặt" luôn hiển thị, nhưng đổi text nếu không enabled
        if not enabled:
            self.start_button.setText("DỪNG")
            self.start_button.setEnabled(True)  # Cho phép click để dừng
            self.start_button.setStyleSheet("background-color: #e74c3c; color: white;")
        else:
            self.start_button.setText("BẮT ĐẦU CÀI ĐẶT")
            self.start_button.setStyleSheet("background-color: #3498db; color: white;")
    
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
        
        if is_online: # Chỉ hiển thị các bộ Office khi có mạng
            generated_office_apps = self._generate_office_suites_info()
            self.remote_apps.get("app_items", {}).update(generated_office_apps)
        
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
        
    def update_single_app_widget(self, app_key):
        """Tìm và cập nhật trạng thái của chỉ một AppItemWidget mà không vẽ lại toàn bộ danh sách."""
        widget = self.find_widget_by_key(app_key)
        if not widget:
            print(f"Không tìm thấy widget cho {app_key} để cập nhật.")
            return

        # Tải thông tin mới nhất của phần mềm (đã được worker cập nhật trong config)
        app_info = self.remote_apps.get('app_items', {}).get(app_key, {})
        local_info = self.local_apps.get(app_key, {})
        app_info.update(local_info)
        widget.app_info = app_info # Cập nhật thông tin trong widget

        # Lấy lại trạng thái mới
        is_downloaded = self.is_app_downloaded(app_key, app_info) # Bây giờ phải là True
        local_ver_str = self.local_apps.get(app_key, {}).get('version', '0')
        remote_ver_str = self.remote_apps.get('app_items', {}).get(app_key, {}).get('version', '0')
        is_update_available = is_downloaded and parse_version(remote_ver_str) > parse_version(local_ver_str)

        # Cập nhật lại nhãn phiên bản
        widget.version_label.setText(f"Phiên bản: {app_info.get('version', 'N/A')}")
        widget.version_label.setStyleSheet("color: #bdc3c7; font-size: 10pt;") # Reset về style mặc định
        if is_update_available:
            widget.version_label.setText(f"Cập nhật: {local_ver_str} -> {remote_ver_str}")
            widget.version_label.setStyleSheet("color: #2ecc71; font-weight: bold;")

        # Ngắt kết nối cũ của nút để tránh gọi nhiều lần
        try:
            widget.action_button.clicked.disconnect()
        except (TypeError, RuntimeError):
            pass # Bỏ qua nếu không có kết nối nào

        # Thiết lập lại nút bấm với hành động mới ("Thêm" thay vì "Tải")
        widget.action_button.setText("Thêm")
        widget.action_button.setToolTip(f"Thêm {app_info['display_name']} vào danh sách")
        widget.action_button.setStyleSheet("background-color: #4CAF50; color: white;")
        widget.action_button.setEnabled(True)

        # Kết nối lại hành động mới cho nút
        on_complete_action = lambda k=app_key, i=app_info: self.move_app_to_selection(k, i)
        if is_update_available:
            widget.action_button.clicked.connect(lambda _, k=app_key, i=app_info, w=widget, lv=local_ver_str, rv=remote_ver_str, cb=on_complete_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
        else:
            widget.action_button.clicked.connect(on_complete_action)
    
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
            valid_selected = []
            if self.is_cli_mode:
                # Nếu là chế độ CLI, danh sách chọn là cli_target_apps
                valid_selected = [key for key in self.cli_target_apps if key in compatible_apps]
            else:
                # Nếu là chế độ GUI thường, lấy từ config
                valid_selected = [key for key in self.selected_for_install if key in compatible_apps]
            
            # Gán lại self.selected_for_install để đồng bộ
            self.selected_for_install = valid_selected
            
            for key in valid_selected:
                # Lấy thông tin mới nhất của app để đưa vào khung
                app_info_to_move = compatible_apps.get(key)
                if app_info_to_move:
                    self.move_app_to_selection(key, app_info_to_move)

        self.update_counts()
        self.restore_scroll_positions()

    def add_app_to_list(self, list_widget, key, info):
        item_widget = AppItemWidget(key, info, embed_mode=self.embed_mode)
        is_downloaded = self.is_app_downloaded(key, info)
        local_ver_str = self.local_apps.get(key, {}).get('version', '0')
        remote_ver_str = self.remote_apps.get('app_items', {}).get(key, {}).get('version', '0')
        
        is_update_available = False
        # Chỉ so sánh phiên bản cho các ứng dụng không phải là Office
        if info.get('type') != 'office_suite':
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
            worker.progress.connect(self.update_install_progress)
            worker.progress_percentage.connect(self.update_download_progress_anywhere)
            worker.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)))
            worker.update_widget_status.connect(self.update_widget_status)
            worker.tasks_batch_completed.connect(self.on_tasks_batch_completed)

            # THAY ĐỔI QUAN TRỌNG:
            # Kết nối tín hiệu finished tới hàm xử lý mới (on_worker_finished).
            # Dùng lambda để truyền app_key, đảm bảo hàm xử lý biết worker nào đã xong.
            worker.tasks_batch_completed.connect(
                lambda completed_items: self.on_worker_finished(list(completed_items.keys())[0])
            )
            
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
            worker.progress.connect(self.update_install_progress)
            worker.progress_percentage.connect(self.update_download_progress_anywhere)
            worker.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)))
            worker.update_widget_status.connect(self.update_widget_status)
            worker.tasks_batch_completed.connect(self.on_tasks_batch_completed)
            
            # THAY ĐỔI QUAN TRỌNG:
            # Khi worker xong, nó sẽ tự gọi on_worker_finished để làm mới giao diện.
            # Sau đó, chúng ta mới thực hiện hành động 'on_complete' (như chuyển sang khung bên phải).
            # Việc này đảm bảo giao diện được cập nhật đúng trước khi có hành động tiếp theo.
            def on_update_and_action():
                self.on_worker_finished(key)
                if on_complete:
                    on_complete()
            
            worker.finished.connect(on_update_and_action)
            
            # Lưu worker và bắt đầu
            self.active_workers[key] = worker
            worker.start()

    # Trong class TekDT_AIS, thay thế hoàn toàn hàm cũ bằng hàm này
    def _update_office_selection_state(self):
        """Vô hiệu hóa hoặc kích hoạt lại các lựa chọn Office."""
        is_office_selected = any(
            self.remote_apps.get('app_items', {}).get(key, {}).get('type') == 'office_suite'
            for key in self.selected_for_install
        )

        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if hasattr(widget, 'app_info') and widget.app_info.get('type') == 'office_suite':
                # Nếu đã có Office được chọn VÀ widget này không phải là cái đã được chọn
                if is_office_selected and widget.app_key not in self.selected_for_install:
                    widget.action_button.setDisabled(True)
                    widget.action_button.setToolTip("Chỉ có thể chọn một phiên bản Office để cài đặt.")
                # Nếu không có Office nào được chọn, KHÔI PHỤC HOÀN TOÀN TRẠNG THÁI NÚT
                elif not is_office_selected:
                    widget.action_button.setDisabled(False)
                    # Logic khôi phục nút (quan trọng nhất)
                    is_downloaded = self.is_app_downloaded(widget.app_key, widget.app_info)
                    if is_downloaded:
                        widget.action_button.setText("Thêm")
                        widget.action_button.setToolTip(f"Thêm {widget.app_info['display_name']} vào danh sách")
                        widget.action_button.setStyleSheet("background-color: #4CAF50; color: white;")
                    else:
                        widget.action_button.setText("Tải")
                        widget.action_button.setToolTip(f"Tải về {widget.app_info['display_name']}")
                        widget.action_button.setStyleSheet("background-color: #f39c12; color: white;")
    
    def move_app_to_selection(self, key, info):
        if self.is_cli_mode and key not in self.cli_target_apps:
            return
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
        self._update_office_selection_state()

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
        self._update_office_selection_state()
        
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
        Cập nhật trạng thái trong bộ nhớ một cách trực tiếp và mạnh mẽ.
        """
        # Xóa worker khỏi danh sách quản lý
        if app_key in self.active_workers:
            del self.active_workers[app_key]

        # --- THAY ĐỔI QUAN TRỌNG ---
        # Lấy thông tin mới nhất của phần mềm từ danh sách remote
        remote_info = self.remote_apps.get("app_items", {}).get(app_key)
        if remote_info:
            # GHI ĐÈ TRỰC TIẾP phiên bản mới vào bộ nhớ (self.local_apps)
            # Bước này đảm bảo trạng thái trong bộ nhớ là MỚI NHẤT
            # trước khi cập nhật giao diện.
            self.local_apps.setdefault(app_key, {}).update(remote_info)
            
            # Đồng bộ cả vào self.config để nhất quán
            self.config['app_items'].setdefault(app_key, {}).update(remote_info)

        # Bây giờ, gọi hàm cập nhật widget.
        # Nó sẽ đọc trạng thái mới nhất mà chúng ta vừa ghi đè ở trên.
        self.update_single_app_widget(app_key)
    
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
        if self.start_button.text() == "Xong":
            self.reset_ui_after_completion()
            return
        if self.install_worker and self.install_worker.isRunning():
            reply = self.show_styled_message_box(QMessageBox.Icon.Question, "Dừng tác vụ",
                                                 "Bạn có chắc muốn dừng quá trình cài đặt không?",
                                                 buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.install_worker.stop()
                self.start_button.setText("ĐANG DỪNG...")
                self.start_button.setDisabled(True)
            return
        
        self.is_processing = True
        
        # Nếu nút đang ở trạng thái "Xong"
        if self.start_button.text() == "Xong":
            self.reset_ui_after_completion()
            return

        apps_to_process = {}
        for key in self.selected_for_install:
            if key in self.remote_apps.get('app_items', {}):
                remote_info = self.remote_apps['app_items'][key]
                local_info = self.local_apps.get(key, {})
                # Mặc định là 'install', nhưng nếu có phiên bản mới thì là 'update'
                action = 'install'
                if self.is_app_downloaded(key, remote_info) and parse_version(remote_info.get('version', '0')) > parse_version(local_info.get('version', '0')):
                    action = 'update'
                apps_to_process[key] = {'info': remote_info, 'action': action}


        if not apps_to_process:
            self.show_styled_message_box(QMessageBox.Icon.Information, "Thông báo", "Vui lòng thêm ít nhất một phần mềm để cài đặt.")
            return

        # Vô hiệu hóa giao diện, ngoại trừ nút "Dừng"
        self.search_box.setEnabled(False)
        self.available_list_widget.setEnabled(False)

        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            widget = self.selected_list_widget.itemWidget(item)
            if hasattr(widget, 'action_button'):
                widget.action_button.hide() # Ẩn nút "Bỏ"
                widget.set_status("processing") # Hiển thị trạng thái chờ
        self.start_button.setText("DỪNG")
        self.start_button.setEnabled(True)
        self.start_button.setStyleSheet("background-color: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;")

        self.install_worker = InstallWorker(apps_to_process)
        self.install_worker.progress.connect(self.update_install_progress)
        self.install_worker.progress_percentage.connect(self.update_download_progress_anywhere)
        self.install_worker.finished.connect(self.on_installation_finished)
        self.install_worker.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)))
        self.install_worker.update_widget_status.connect(self.update_widget_status)
        self.install_worker.tasks_batch_completed.connect(self.on_tasks_batch_completed)
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
        self.is_processing = False
        if self.install_worker and not self.install_worker._is_stopped:
            status_text = "Hoàn tất! Nhấn 'Xong' để tiếp tục."
            if not self.embed_mode:
                self.status_label.setText(status_text)
                self.start_button.setText("Xong") # Đổi text thành "Xong"
                self.start_button.setEnabled(True)
                # Đổi màu nút thành màu xanh lá cây để báo hiệu thành công
                self.start_button.setStyleSheet("background-color: #4CAF50; color: white;") 
        elif self.install_worker and self.install_worker._is_stopped and not self.is_cli_mode:
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
        self.is_processing = False
        if not self.embed_mode:
            self.set_ui_interactive(True) # Bật lại tương tác
            self.start_button.setText("BẮT ĐẦU CÀI ĐẶT")
            self.start_button.setStyleSheet("background-color: #3498db; color: white;")
            self.status_label.setText("Trạng thái: Sẵn sàng.")
            
            # Lặp qua các widget và reset trạng thái của chúng
            for i in range(self.selected_list_widget.count()):
                item = self.selected_list_widget.item(i)
                widget = self.selected_list_widget.itemWidget(item)
                if hasattr(widget, 'action_button'):
                    widget.set_status("") # Ẩn icon success/failed
                    widget.action_button.show() # Hiện lại nút "Bỏ"

    def update_counts(self):
        if self.embed_mode: return
        compatible_count = sum(1 for i in range(self.available_list_widget.count()) if hasattr(self.available_list_widget.itemWidget(self.available_list_widget.item(i)), 'app_key'))
        selected_count = self.selected_list_widget.count()
        
        self.available_count_label.setText(f"Tổng số phần mềm: {compatible_count}")
        self.selected_count_label.setText(f"Đã chọn: {selected_count}")

    def save_config(self):
        if not self.embed_mode and not self.is_cli_mode:
            self.config['settings']['selected_for_install'] = self.selected_for_install
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Không thể lưu cấu hình: {e}")
            
    def closeEvent(self, event):
        if self.is_processing or self.active_workers:
            reply = self.show_styled_message_box(
                QMessageBox.Icon.Warning,
                "Xác nhận thoát",
                "Các tác vụ vẫn đang chạy. Bạn có chắc chắn muốn thoát không?\n"
                "Việc này có thể làm gián đoạn quá trình tải hoặc cài đặt.",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore() # Hủy sự kiện đóng cửa sổ
                return
            else:
                # Nếu người dùng vẫn muốn thoát, hãy dừng các worker
                if self.install_worker and self.install_worker.isRunning():
                    self.install_worker.stop()
                
                # Dừng các worker tải/cập nhật riêng lẻ
                for worker in list(self.active_workers.values()):
                    if worker and worker.isRunning():
                        worker.stop()

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
    
    cli_args = sys.argv[1:]
    
    if handle_auto_install_cli(cli_args):
        sys.exit(0)
    
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

    # --- THAY ĐỔI CHÍNH BẮT ĐẦU TỪ ĐÂY ---
    is_cli_command = any(arg in ['/install', '/update', '/help'] for arg in cli_command_args)

    # Truyền các tham số CLI vào class ngay từ đầu
    main_win = TekDT_AIS(
        embed_mode=embed_mode, 
        embed_size=embed_size,
        is_cli_mode=is_cli_command,
        cli_args=cli_command_args
    )

    # Xử lý /help riêng biệt vì nó không cần chờ
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
                QTimer.singleShot(100, lambda: main_win.handle_cli_args(cli_command_args))
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