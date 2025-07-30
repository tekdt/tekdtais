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
from packaging.version import parse as parse_version

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem, QLabel, QPushButton, QLineEdit,
                             QFrame, QScrollArea, QGraphicsOpacityEffect, QToolTip,
                             QMessageBox, QSizePolicy, QTextEdit)
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QMovie
from PyQt6.QtCore import (Qt, QSize, QThread, pyqtSignal, QObject, QPropertyAnimation,
                          QEasingCurve, QTimer)

# --- CÁC HẰNG SỐ VÀ CẤU HÌNH ---
APP_NAME = "TekDT AIS"
APP_VERSION = "1.0.0"
GITHUB_REPO_URL = "https://github.com/tekdt/tekdtais"
REMOTE_APP_LIST_URL = "https://raw.githubusercontent.com/tekdt/tekdtais/refs/heads/main/app_list.json"

# 1. APP_DATA_DIR: Thư mục LÀM VIỆC chính, nơi lưu trữ dữ liệu bền vững (Apps, Tools, Config).
#    - Khi chạy EXE, nó sẽ là thư mục chứa file .exe.
#    - Khi chạy script, nó là thư mục chứa file .py.
# 2. RESOURCE_DIR: Thư mục chứa tài nguyên được ĐÓNG GÓI vào file EXE.
#    - Khi chạy EXE, nó là thư mục tạm `_MEIPASS`.
#    - Khi chạy script, nó cũng là thư mục chứa file .py.
def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cho cả script và EXE. """
    try:
        # PyInstaller tạo một thư mục tạm và lưu đường dẫn trong _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # _MEIPASS không tồn tại khi chạy ở dạng script
        base_path = os.path.abspath(".")

    return str(Path(base_path) / relative_path)
# Xác định thư mục làm việc chính (nơi chứa file .exe hoặc .py)
if getattr(sys, 'frozen', False):
    # Chạy dưới dạng file EXE đã biên dịch
    APP_DATA_DIR = Path(sys.executable).parent
else:
    # Chạy dưới dạng file script Python
    APP_DATA_DIR = Path(__file__).resolve().parent

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
        # Kiểm tra xem công cụ đã có sẵn chưa
        tools_present = ARIA2_EXEC.exists() and SEVENZ_EXEC.exists()
        
        if not tools_present:
            try:
                self.progress_update.emit("Kiểm tra kết nối internet...")
                self.session.get("https://www.google.com", timeout=5)
            except requests.ConnectionError:
                self.finished.emit(False, "Không có internet và thiếu công cụ. Vui lòng kết nối mạng và khởi động lại.")
                return
        
        # Tiếp tục kiểm tra cập nhật nếu có internet
        try:
            self.progress_update.emit("Kiểm tra và cập nhật 7-Zip...")
            self._check_7zip()

            self.progress_update.emit("Kiểm tra và cập nhật aria2...")
            self._check_aria2()
            self.finished.emit(True, "Kiểm tra công cụ hoàn tất.")
        except requests.ConnectionError:
            if tools_present:
                self.finished.emit(True, "Không có internet, sử dụng công cụ có sẵn.")
            else:
                self.finished.emit(False, "Không có internet và thiếu công cụ. Vui lòng kết nối mạng và khởi động lại.")
        except Exception as e:
            if tools_present:
                self.finished.emit(True, f"Lỗi khi kiểm tra công cụ: {e}. Sử dụng công cụ có sẵn.")
            else:
                self.finished.emit(False, f"Lỗi khi kiểm tra công cụ: {e}. Thiếu công cụ cần thiết.")

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

class InstallWorker(QThread):
    def __init__(self, apps_to_process, action="install"):
        super().__init__()
        self.signals = WorkerSignals()
        self.apps_to_process = apps_to_process
        self.action = action
        self._is_stopped = False
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'TekDT-AIS-App'})

    def stop(self):
        self._is_stopped = True

    def run(self):
        try:
            for app_key, app_info in self.apps_to_process.items():
                if self._is_stopped:
                    self.signals.progress.emit(app_key, "stopped", "Tác vụ đã bị dừng.")
                    continue
                    
                self.signals.progress.emit(app_key, "processing", f"Chuẩn bị tải {app_info.get('display_name')}...")
                
                # Kiểm tra thông tin ứng dụng
                if not app_info.get('download_url'):
                    self.signals.progress.emit(app_key, "failed", f"Không có URL tải xuống cho {app_info.get('display_name')}.")
                    continue
                    
                # Logic tải xuống
                download_url = app_info.get('download_url')
                file_name = app_info.get('output_filename', Path(download_url).name)
                app_dir = APPS_DIR / app_key
                app_dir.mkdir(exist_ok=True)
                download_path = app_dir / file_name

                if not download_path.exists():
                    command = [
                        str(ARIA2_EXEC),
                        "--dir", str(app_dir),
                        "--out", file_name,
                        "--max-connection-per-server=16",
                        "--split=16",
                        "--min-split-size=1M",
                        "--show-console-readout=false",
                        "--summary-interval=1",
                        download_url
                    ]
                    if 'referer' in app_info:
                        command.extend(["--header", f"Referer: {app_info['referer']}"])
                    
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    percentage_pattern = re.compile(r'\[.*?\((\d+)%\)')
                    self.signals.progress.emit(app_key, "processing", f"Đang tải {app_info.get('display_name')}...")
                    while process.poll() is None:
                        if self._is_stopped:
                            process.terminate()
                            self.signals.progress.emit(app_key, "stopped", "Tải xuống đã bị dừng.")
                            break
                        line = process.stdout.readline()
                        if line:
                            match = percentage_pattern.search(line)
                            if match:
                                try:
                                    percentage = float(match.group(1))
                                    self.signals.progress_percentage.emit(app_key, percentage)
                                except ValueError:
                                    continue
                    process.wait()
                    if process.returncode != 0 and not self._is_stopped:
                        stderr = process.stderr.read()
                        self.signals.progress.emit(app_key, "failed", f"Tải {app_info.get('display_name')} thất bại: {stderr}")
                        continue
                
                if self._is_stopped:
                    continue

                self.signals.progress_percentage.emit(app_key, 100.0)
                
                # Download icon
                icon_url = app_info.get('icon_url')
                icon_filename = Path(icon_url).name if icon_url else 'default_icon.png'
                icon_path = app_dir / icon_filename
                if icon_url and not icon_path.exists():
                    self.signals.progress.emit(app_key, "processing", f"Đang tải biểu tượng cho {app_info.get('display_name')}...")
                    try:
                        icon_response = self.session.get(icon_url, timeout=10)
                        icon_response.raise_for_status()
                        with open(icon_path, 'wb') as f:
                            f.write(icon_response.content)
                    except requests.RequestException as e:
                        self.signals.progress.emit(app_key, "warning", f"Không thể tải biểu tượng: {e}")
                        icon_filename = 'default_icon.png'
                
                # Update local app config
                local_app_info = app_info.copy()
                local_app_info['icon_file'] = icon_filename
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                config['app_items'][app_key] = local_app_info
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                # Logic cài đặt
                if self.action == "install":
                    if app_info.get('type') == 'installer' and download_path.exists():
                        self.signals.progress.emit(app_key, "installing", f"Đang cài đặt {app_info.get('display_name')}...")
                        install_params = app_info.get('install_params', '')
                        if not install_params:
                            self.signals.progress.emit(app_key, "failed", f"Không có tham số cài đặt cho {app_info.get('display_name')}.")
                            continue
                        install_command = [str(download_path)] + install_params.split()
                        
                        try:
                            process = subprocess.run(
                                install_command,
                                capture_output=True,
                                text=True,
                                creationflags=subprocess.CREATE_NO_WINDOW
                            )
                            if process.returncode == 0:
                                self.signals.progress.emit(app_key, "success", f"Đã cài đặt {app_info.get('display_name')} thành công!")
                            else:
                                self.signals.progress.emit(app_key, "failed", f"Cài đặt {app_info.get('display_name')} thất bại: {process.stderr}")
                        except Exception as e:
                            self.signals.progress.emit(app_key, "failed", f"Lỗi khi cài đặt {app_info.get('display_name')}: {str(e)}")
                    elif app_info.get('type') == 'portable' and download_path.exists():
                        self.signals.progress.emit(app_key, "success", f"Đã tải {app_info.get('display_name')} (portable) thành công!")
                    else:
                        self.signals.progress.emit(app_key, "failed", f"Không thể cài đặt {app_info.get('display_name')}: Thiếu tệp hoặc loại ứng dụng không hợp lệ.")
                else:
                    self.signals.progress.emit(app_key, "success", f"Đã tải {app_info.get('display_name')} thành công!")

        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

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
        self.progress_overlay.setAutoFillBackground(True)
        
        self.setToolTip(app_info.get('description', 'Không có mô tả.'))

    def _on_action_button_clicked(self):
        if self.embed_mode:
            is_currently_auto_install = self.action_button.text() == "Xoá"
            new_state = not is_currently_auto_install
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
            self.status_label.setPixmap(QPixmap(resource_path('Images/success.png')).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.name_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12pt;")
            self.action_button.setEnabled(True) # Re-enable after process
            self._current_progress = 0
            self.progress_overlay.hide()
            self.status_label.show()
        elif status == "failed":
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
            installing_pixmap_path = resource_path('Images/loading.gif')
            if Path(installing_pixmap_path).exists():
                 self.status_label.setPixmap(QPixmap(installing_pixmap_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else: # Fallback text
                 self.status_label.setText("...")
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
        overlay_width = int(self.width() * (self._current_progress / 100.0))
        self.progress_overlay.setGeometry(0, 0, overlay_width, self.height())
        
        if self._current_progress > 0:
            self.progress_overlay.show()
            self.progress_overlay.raise_()
        else:
            self.progress_overlay.hide()
        self.update()

# --- CỬA SỔ CHÍNH ---
class TekDT_AIS(QMainWindow):
    def __init__(self, embed_mode=False, embed_size=None):
        super().__init__()
        self.embed_mode = embed_mode
        self.embed_size = embed_size
        self.config = {}
        self.remote_apps = {}
        self.local_apps = {}
        self.selected_for_install = []
        self.install_worker = None
        self.startup_label = None
        self.system_arch = platform.architecture()[0]
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'TekDT-AIS-App'})

        # Thiết lập biểu tượng cửa sổ
        icon_path = resource_path("logo.ico")
        if Path(icon_path).exists():
            self.setWindowIcon(QIcon(icon_path))

        if self.embed_mode:
            self.setup_embed_ui()
        else:
            self.setup_ui()
        self.tool_manager_thread = QThread()
        self.tool_manager = ToolManager()
        self.tool_manager.moveToThread(self.tool_manager_thread)
        self.tool_manager.finished.connect(self.on_tool_check_finished)
        self.tool_manager_thread.started.connect(self.tool_manager.run_checks)
        
        self.show_startup_status("Đang khởi tạo...")
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
                /* font-weight: bold; ĐÃ BỎ */
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
        if not self.startup_label:
            self.startup_label = QLabel(message, self)
            self.startup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.startup_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7); color: white; font-size: 14pt; border-radius: 10px; padding: 20px;")
            self.startup_label.setWordWrap(True)
            self.startup_label.setMinimumWidth(400)
            self.startup_label.setMinimumHeight(100)
            self.tool_manager.progress_update.connect(lambda msg: self.startup_label.setText(msg))
        
        self.startup_label.setText(message)
        self.startup_label.adjustSize()
        self.startup_label.move(int((self.width() - self.startup_label.width()) / 2), int((self.height() - self.startup_label.height()) / 2))
        self.startup_label.show()
        self.startup_label.raise_()

    def on_tool_check_finished(self, success, message):
        self.tool_manager_thread.quit()
        self.tool_manager_thread.wait()
        if self.startup_label:
            self.startup_label.hide()

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

    def handle_cli_args(self, args):
        if not args:
            return

        # Tải cấu hình và danh sách ứng dụng trước tiên
        self.load_config_and_apps()
        if not self.remote_apps.get('app_items'):
            self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi", "Không thể tải danh sách phần mềm. Không thể tiếp tục tác vụ dòng lệnh.")
            QApplication.quit()
            return

        apps_to_process = {}
        apps_for_install = {}
        apps_for_update = {}
        
        # Các danh sách tóm tắt
        install_summary = []
        update_summary = []
        auto_install_summary = []

        # --- Bước 1: Phân tích tất cả các tham số ---
        i = 0
        while i < len(args):
            cmd = args[i]
            app_keys_str = ""
            if i + 1 < len(args) and not args[i+1].startswith('/'):
                app_keys_str = args[i+1]

            # Xử lý /auto_install
            if cmd.startswith('/auto_install:'):
                if not app_keys_str:
                    self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi cú pháp", f"Tham số '{cmd}' bắt buộc phải có tên ứng dụng.")
                    QApplication.quit()
                    return
                
                value_part = cmd.replace('/auto_install:', '').lower()
                if value_part not in ['true', 'false']:
                    self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi cú pháp", f"Giá trị cho /auto_install phải là 'true' hoặc 'false', nhận được '{value_part}'.")
                    QApplication.quit()
                    return

                app_keys = app_keys_str.split('|')
                updated_apps = []
                for key in app_keys:
                    if key in self.remote_apps.get('app_items', {}):
                        self.config['app_items'].setdefault(key, {})['auto_install'] = (value_part == 'true')
                        updated_apps.append(key)
                    else:
                        auto_install_summary.append(f"-> Không tìm thấy ứng dụng '{key}' để đặt auto_install.")
                if updated_apps:
                    self.save_config()
                    auto_install_summary.append(f"-> Đã đặt auto_install = '{value_part}' cho: {', '.join(updated_apps)}.")
                i += 1

            # Xử lý /update
            elif cmd == '/update':
                try:
                    self.session.get("https://www.google.com", timeout=5)
                except requests.ConnectionError:
                    self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi mạng", "Không có kết nối Internet để kiểm tra cập nhật.")
                    QApplication.quit()
                    return

                keys_to_check = app_keys_str.split('|') if app_keys_str else list(self.config.get('app_items', {}).keys())
                update_summary.append("Kiểm tra cập nhật cho các phần mềm:")
                for key in keys_to_check:
                    local_info = self.config.get('app_items', {}).get(key)
                    remote_info = self.remote_apps.get('app_items', {}).get(key)
                    display_name = (local_info or remote_info or {'display_name': key}).get('display_name')

                    if local_info and remote_info:
                        local_ver = local_info.get('version', '0')
                        remote_ver = remote_info.get('version', '0')
                        if parse_version(remote_ver) > parse_version(local_ver):
                            apps_for_update[key] = remote_info
                            update_summary.append(f"-> Sẽ cập nhật {display_name}: {local_ver} -> {remote_ver}")
                        else:
                            update_summary.append(f"-> {display_name}: Đã ở phiên bản mới nhất.")
                    else:
                        update_summary.append(f"-> Cảnh báo: Không tìm thấy thông tin cho '{key}' để cập nhật.")
                if app_keys_str: i += 1

            # Xử lý /install
            elif cmd == '/install':
                if app_keys_str: # Cài đặt theo danh sách chỉ định
                    app_keys = app_keys_str.split('|')
                    install_summary.append("Chuẩn bị cài đặt các phần mềm được chỉ định:")
                    for key in app_keys:
                        if key in self.remote_apps.get('app_items', {}):
                            apps_for_install[key] = self.remote_apps['app_items'][key]
                            install_summary.append(f"-> {self.remote_apps['app_items'][key].get('display_name', key)}")
                        else:
                            install_summary.append(f"-> Cảnh báo: Không tìm thấy ứng dụng '{key}'.")
                    i += 1
                else: # Cài đặt theo auto_install: true
                    install_summary.append("Chuẩn bị cài đặt các phần mềm có auto_install=true:")
                    found_auto = False
                    for key, info in self.config.get('app_items', {}).items():
                        if info.get('auto_install') and key in self.remote_apps.get('app_items', {}):
                            apps_for_install[key] = self.remote_apps['app_items'][key]
                            install_summary.append(f"-> {self.remote_apps['app_items'][key].get('display_name', key)}")
                            found_auto = True
                    if not found_auto:
                        install_summary.append("-> Không tìm thấy phần mềm nào được đặt auto_install=true.")
            i += 1

        # --- Bước 2: Tổng hợp và quyết định hành động ---
        apps_to_process.update(apps_for_install)
        apps_to_process.update(apps_for_update) # Ghi đè, ưu tiên update

        # Xây dựng thông báo cuối cùng
        final_summary = []
        if auto_install_summary:
            final_summary.extend(["--- KẾT QUẢ CẬP NHẬT AUTO INSTALL ---", *auto_install_summary])
        if update_summary:
            final_summary.extend(["\n--- CHI TIẾT CẬP NHẬT ---", *update_summary])
        if install_summary:
            final_summary.extend(["\n--- CHI TIẾT CÀI ĐẶT ---", *install_summary])
        
        # Trường hợp 1: Chỉ có lệnh /auto_install, không có tác vụ nào khác
        if any(arg.startswith('/auto_install:') for arg in args) and not apps_to_process:
            msg = "\n".join(final_summary) if final_summary else "Không có thay đổi nào được thực hiện."
            self.show_styled_message_box(QMessageBox.Icon.Information, "Hoàn tất", msg)
            QApplication.quit()
            return

        # Trường hợp 2: Không có ứng dụng nào cần xử lý
        if not apps_to_process:
            msg = "\n".join(final_summary) if final_summary else "Không có tác vụ nào được chỉ định hoặc cần thực hiện."
            self.show_styled_message_box(QMessageBox.Icon.Information, "Thông báo", msg)
            QApplication.quit()
            return

        # --- Bước 3: Thực thi ---
        # Hiển thị cửa sổ để người dùng thấy tiến trình
        self.show()

        # Với /install, di chuyển app sang khung thứ 2
        for key, info in apps_for_install.items():
            if key in apps_to_process: # Đảm bảo chỉ di chuyển app sẽ được cài đặt
                 self.move_app_to_selection(key, info)

        # Bắt đầu worker
        self.start_installation()

        # Hàm xử lý sau khi worker hoàn thành
        def on_cli_finished():
            processed_keys = list(apps_to_process.keys())
            result_summary = ["\n--- KẾT QUẢ THỰC THI ---"]
            
            # Kiểm tra trạng thái của các app đã cập nhật (ở khung bên trái)
            for i in range(self.available_list_widget.count()):
                widget = self.available_list_widget.itemWidget(self.available_list_widget.item(i))
                if hasattr(widget, 'app_key') and widget.app_key in apps_for_update:
                    if "color: #4CAF50" in widget.name_label.styleSheet():
                        result_summary.append(f"✅ Cập nhật thành công: {widget.app_info.get('display_name')}")
                    else:
                        result_summary.append(f"❌ Cập nhật thất bại: {widget.app_info.get('display_name')}")

            # Kiểm tra trạng thái của các app đã cài đặt (ở khung bên phải)
            install_success_count = 0
            install_fail_count = 0
            for i in range(self.selected_list_widget.count()):
                widget = self.selected_list_widget.itemWidget(self.selected_list_widget.item(i))
                if hasattr(widget, 'app_key') and widget.app_key in apps_for_install:
                     if "color: #4CAF50" in widget.name_label.styleSheet():
                         install_success_count += 1
                     else:
                         install_fail_count += 1
            
            if apps_for_install: # Chỉ thêm mục này nếu có tác vụ cài đặt
                result_summary.append(f"\n-> Cài đặt: {install_success_count} thành công, {install_fail_count} thất bại.")
            
            # Gộp tất cả thông báo
            full_message = "\n".join(final_summary) + "\n" + "\n".join(result_summary)
            full_message += "\n\nCảm ơn bạn đã sử dụng TekDT AIS!"
            
            icon = QMessageBox.Icon.Information if install_fail_count == 0 else QMessageBox.Icon.Warning
            self.show_styled_message_box(icon, "Hoàn tất tác vụ dòng lệnh", full_message)
            QApplication.quit()

        self.install_worker.signals.finished.connect(on_cli_finished)

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
                    widget.action_button.hide()  # Ẩn nút "Bỏ"
                    widget.set_status("processing")  # Hiển thị icon "đang xử lý"
                else:
                    # Hiển thị lại nút "Bỏ" và ẩn trạng thái khi kết thúc
                    widget.action_button.show()
                    widget.set_status("")  # Trạng thái rỗng để ẩn icon
                widget.action_button.setEnabled(enabled)
    
    def load_config_and_apps(self):
        # Load local config
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.config = json.loads(content) if content else {}
            except json.JSONDecodeError:
                self.config = {}
        else:
            self.config = {}

        # Luôn đảm bảo các khóa chính tồn tại
        self.config.setdefault('settings', {})
        self.config.setdefault('app_items', {})

        self.local_apps = self.config.get("app_items", {})
        self.save_config()
        
        if not self.embed_mode:
            self.selected_for_install = self.config.get("settings", {}).get("selected_for_install", [])
            if not isinstance(self.selected_for_install, list):
                self.selected_for_install = []

        try:
            status_text = "Đang tải danh sách phần mềm từ máy chủ..."
            if hasattr(self, 'status_label') and self.status_label: self.status_label.setText(status_text)
            response = self.session.get(REMOTE_APP_LIST_URL, timeout=10)
            response.raise_for_status()
            self.remote_apps = response.json()
            status_text = "Tải danh sách thành công. Sẵn sàng."
            if hasattr(self, 'status_label') and self.status_label: self.status_label.setText(status_text)
        except requests.RequestException as e:
            self.show_styled_message_box(QMessageBox.Icon.Warning, "Lỗi mạng", f"Không thể tải danh sách phần mềm từ máy chủ: {e}\nChương trình sẽ chỉ hiển thị các phần mềm đã có thông tin cục bộ.")
            self.remote_apps = {"app_items": self.local_apps}
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText("Lỗi mạng. Hiển thị các phần mềm đã biết.")
        
        for key, local_info in self.local_apps.items():
            if key in self.remote_apps.get("app_items", {}):
                if 'icon_file' in local_info:
                    self.remote_apps["app_items"][key].update(local_info)
        
        self.populate_lists()
        
    def populate_lists(self):
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
                compatible_apps[key] = app_info
        
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

            for key, info in compatible_apps.items():
                if info.get('category', 'Chưa phân loại') == category:
                    self.add_app_to_list(self.available_list_widget, key, info)

        if not self.embed_mode:
            for key in list(self.selected_for_install):
                if key in compatible_apps:
                    self.move_app_to_selection(key, compatible_apps[key])
                else:
                    self.selected_for_install.remove(key)

        self.update_counts()

    def add_app_to_list(self, list_widget, key, info):
        if key in self.local_apps:
            info.update(self.local_apps[key])
        
        item_widget = AppItemWidget(key, info, embed_mode=self.embed_mode)
        
        if self.embed_mode:
            item_widget.auto_install_toggled.connect(self.on_auto_install_toggled)
        else:
            item_widget.add_requested.connect(self.move_app_to_selection)
            item_widget.remove_requested.connect(self.remove_app_from_selection)

        is_fully_downloaded = False
        app_dir = APPS_DIR / key
        download_url = info.get('download_url', '')
        file_name = info.get('output_filename', Path(download_url).name if download_url else '')
        if file_name and (app_dir / file_name).exists():
            is_fully_downloaded = True

        if not is_fully_downloaded:
            item_widget.action_button.setText("Tải")
            item_widget.action_button.setToolTip(f"Tải {info['display_name']} về")
            item_widget.name_label.setStyleSheet("color: #e67e22; font-weight: bold;")
            item_widget.action_button.setStyleSheet("background-color: #e67e22; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
            item_widget.action_button.clicked.connect(lambda _, k=key, i=info, w=item_widget: self.download_single_app(k, i, w))
        else:
            if self.embed_mode:
                is_auto = self.local_apps.get(key, {}).get('auto_install', False)
                item_widget.set_auto_install_button_state(is_auto)
            else:
                item_widget.action_button.setText("Thêm")
                item_widget.action_button.setToolTip(f"Thêm {info['display_name']} vào danh sách")
                item_widget.action_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
                
                local_ver = self.local_apps.get(key, {}).get('version', '0')
                remote_ver = info.get('version', '0')
                
                if parse_version(remote_ver) > parse_version(local_ver):
                    item_widget.name_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
                    item_widget.setToolTip(f"Có bản cập nhật: {remote_ver}. Phiên bản hiện tại: {local_ver}")
                    item_widget.action_button.setText("Cập nhật")
                    item_widget.action_button.clicked.connect(lambda _, k=key, i=info, w=item_widget, lv=local_ver, rv=remote_ver: self.confirm_update(k, i, w, lv, rv))

        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 70))
        list_item.setData(Qt.ItemDataRole.UserRole, key)
        
        list_widget.addItem(list_item)
        list_widget.setItemWidget(list_item, item_widget)

    def on_auto_install_toggled(self, key, state):
        self.config['app_items'].setdefault(key, {})
        self.config['app_items'][key]['auto_install'] = state
        self.save_config()

    def confirm_update(self, key, info, widget, local_ver, remote_ver):
        reply = self.show_styled_message_box(
            QMessageBox.Icon.Question,
            "Cập nhật phần mềm",
            f"Phiên bản mới hơn của {info['display_name']} ({remote_ver}) đã có. "
            f"Phiên bản hiện tại: {local_ver}.\nBạn có muốn cập nhật không?",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.download_single_app(key, info, widget)
        else:
            self.move_app_to_selection(key, info)

    def move_app_to_selection(self, key, info):
        self.update_available_item_state(key, is_selected=True)

        item_widget = AppItemWidget(key, info)
        item_widget.action_button.setText("Bỏ")
        item_widget.action_button.setToolTip(f"Bỏ {info['display_name']} khỏi danh sách")
        item_widget.action_button.setStyleSheet(
            "background-color: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
        )
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
                if is_selected:
                    widget.action_button.setDisabled(True)
                    widget.action_button.setStyleSheet(
                        "background-color: #95a5a6; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
                    )
                else:
                    widget.action_button.setDisabled(False)
                    widget.action_button.setText("Thêm")
                    widget.action_button.setToolTip(f"Thêm {widget.app_info['display_name']} vào danh sách")
                    widget.action_button.setStyleSheet(
                        "background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
                    )
                break

    def download_single_app(self, key, info, item_widget=None):
        reply = self.show_styled_message_box(
            QMessageBox.Icon.Question,
            "Xác nhận tải xuống",
            f"Bạn có muốn tải {info['display_name']} (Phiên bản {info['version']}) không?",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return

        apps_to_process = {key: info}
        self.install_worker = InstallWorker(apps_to_process, action="install")
        self.install_worker.signals.progress.connect(self.update_install_progress)
        self.install_worker.signals.finished.connect(self.on_single_download_finished)
        self.install_worker.signals.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)))
        if item_widget:
            self.install_worker.signals.progress_percentage.connect(item_widget.update_download_progress)
        
        self.install_worker.start()

    def on_single_download_finished(self):
        self.install_worker = None
        QTimer.singleShot(500, self.load_config_and_apps)

    def filter_apps(self, text):
        text = text.lower().strip()
        min_chars = 1 if self.embed_mode else 2
        
        if len(text) < min_chars:
            for i in range(self.available_list_widget.count()):
                self.available_list_widget.item(i).setHidden(False)
            return

        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            
            if not hasattr(widget, 'app_key'):
                item.setHidden(False)
                continue
                
            app_info = widget.app_info
            display_name = app_info.get('display_name', '').lower()
            
            if text in display_name:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def start_installation(self):
        if self.install_worker and self.install_worker.isRunning():
            reply = self.show_styled_message_box(QMessageBox.Icon.Question, "Dừng tác vụ",
                                                 "Bạn có chắc muốn dừng quá trình cài đặt không?",
                                                 buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.install_worker.stop()
                self.start_button.setText("ĐANG DỪNG...")
                self.start_button.setDisabled(True)
                # Chờ worker dừng và đặt lại giao diện
                self.install_worker.wait()
                self.reset_ui_after_completion()  # Đặt lại giao diện khi dừng
            return

        apps_to_install = {key: self.remote_apps['app_items'][key] for key in self.selected_for_install if key in self.remote_apps.get('app_items', {})}
        
        if not apps_to_install:
            self.show_styled_message_box(QMessageBox.Icon.Information, "Thông báo", "Vui lòng thêm ít nhất một phần mềm để cài đặt.")
            return

        # Vô hiệu hóa giao diện, ngoại trừ nút "Dừng"
        self.set_ui_interactive(False)
        self.start_button.setText("DỪNG")
        self.start_button.setEnabled(True)  # Đảm bảo nút "Dừng" luôn bật
        self.start_button.setStyleSheet("background-color: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;")

        self.install_worker = InstallWorker(apps_to_install, action="install")
        self.install_worker.signals.progress.connect(self.update_install_progress)
        self.install_worker.signals.finished.connect(self.on_installation_finished)
        self.install_worker.signals.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, "Lỗi Worker", str(e)))
        self.install_worker.start()

    def update_install_progress(self, app_key, status, message):
        target_widget = None
        if not self.embed_mode:
            for i in range(self.selected_list_widget.count()):
                item = self.selected_list_widget.item(i)
                widget = self.selected_list_widget.itemWidget(item)
                if hasattr(widget, 'app_key') and widget.app_key == app_key:
                    target_widget = widget
                    break
        
        if not target_widget:
            for i in range(self.available_list_widget.count()):
                item = self.available_list_widget.item(i)
                widget = self.available_list_widget.itemWidget(item)
                if hasattr(widget, 'app_key') and widget.app_key == app_key:
                    target_widget = widget
                    break

        if target_widget:
            display_name = target_widget.app_info.get('display_name', app_key)
            status_text = f"{display_name}: {message}"
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText(status_text)
            
            target_widget.set_status(status)
    
    def on_installation_finished(self):
        status_text = "Hoàn tất! Nhấn 'Xong' để tiếp tục."
        if not self.embed_mode:
            self.status_label.setText(status_text)
            self.start_button.setText("Xong")
            self.start_button.setEnabled(True)  # Đảm bảo nút "Xong" hoạt động
            self.start_button
            self.start_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
            
            # Ngắt kết nối tín hiệu cũ và kết nối với reset_ui_after_completion
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self.reset_ui_after_completion)
        
        self.install_worker = None

    def reset_ui_after_completion(self):
        if not self.embed_mode:
            self.set_ui_interactive(True) # Re-enable UI
            self.start_button.setText("BẮT ĐẦU CÀI ĐẶT")
            self.start_button.setStyleSheet("background-color: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;") # Blue button
            self.status_label.setText("Trạng thái: Sẵn sàng.")
            
            # Reconnect the original start_installation function
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self.start_installation)
        
        # Refresh lists to show updated states
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
        if self.install_worker and self.install_worker.isRunning():
            self.install_worker.stop()
            self.install_worker.wait(5000)
        if self.tool_manager_thread.isRunning():
            self.tool_manager_thread.quit()
            self.tool_manager_thread.wait(5000)
        self.save_config()
        super().closeEvent(event)

# KHỐI MỚI ĐỂ THAY THẾ
if __name__ == '__main__':
    # Phân tích tham số bằng shlex để hỗ trợ khoảng trắng
    raw_args = ' '.join(sys.argv[1:])
    parsed_args = shlex.split(raw_args)
    
    flags = [arg for arg in parsed_args if arg.startswith('--')]
    cli_args = [arg for arg in parsed_args if not arg.startswith('--')]
    
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
    main_win = TekDT_AIS(embed_mode=embed_mode, embed_size=embed_size)

    # Xử lý /help riêng biệt vì nó không cần giao diện
    if '/help' in cli_args:
        help_text = """Sử dụng TekDT AIS qua dòng lệnh:
  /help                       Hiển thị trợ giúp này.
  /install                  Tự động cài đặt các phần mềm có auto_install: true.
  /install app1|app2        Tự động cài đặt các phần mềm được chỉ định.
  /update                   Cập nhật tất cả phần mềm đã cài có phiên bản mới.
  /update app1|app2         Cập nhật các phần mềm được chỉ định.
  /auto_install:true app1   Đặt auto_install thành true cho các ứng dụng chỉ định.
  /auto_install:false app1  Đặt auto_install thành false cho các ứng dụng chỉ định.
Ghi chú: Tên phần mềm (app key) là định danh duy nhất, không phải tên hiển thị."""
        main_win.show_styled_message_box(QMessageBox.Icon.Information, "Trợ giúp dòng lệnh - TekDT AIS", help_text)
        sys.exit(0)

    is_cli_command = any(arg.startswith('/') for arg in cli_args)

    if is_cli_command:
        # Ở chế độ CLI, không ẩn cửa sổ nữa, handle_cli_args sẽ quyết định
        # và lên lịch cho tác vụ. Worker sẽ gọi QApplication.quit() khi xong.
        main_win.handle_cli_args(cli_args)
    else:
        # Chế độ GUI bình thường
        main_win.show()
    
    sys.exit(app.exec())