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

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem, QLabel, QPushButton, QLineEdit,
                             QFrame, QScrollArea, QGraphicsOpacityEffect, QToolTip,
                             QMessageBox, QSizePolicy)
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QMovie
from PyQt6.QtCore import (Qt, QSize, QThread, pyqtSignal, QObject, QPropertyAnimation,
                          QEasingCurve, QTimer)

# --- CÁC HẰNG SỐ VÀ CẤU HÌNH ---
APP_NAME = "TekDT AIS"
APP_VERSION = "1.0.0"
GITHUB_REPO_URL = "https://github.com/tekdt/tekdtais"
REMOTE_APP_LIST_URL = "https://raw.githubusercontent.com/tekdt/tekdtais/refs/heads/main/app_list.json"

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "app_config.json"
APPS_DIR = BASE_DIR / "Apps"
TOOLS_DIR = BASE_DIR / "Tools"
IMAGES_DIR = BASE_DIR / "Images"
ARIA2_DIR = TOOLS_DIR / "aria2"
SEVENZ_DIR = TOOLS_DIR / "7z"
ARIA2_EXEC = ARIA2_DIR / "aria2c.exe"
SEVENZ_EXEC = SEVENZ_DIR / "7za.exe"

ARIA2_API_URL = "https://api.github.com/repos/aria2/aria2/releases/latest"
SEVENZIP_API_URL = "https://api.github.com/repos/ip7z/7zip/releases/latest"

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
        try:
            self.progress_update.emit("Kiểm tra kết nối internet...")
            self.session.get("https://www.google.com", timeout=5)

            self.progress_update.emit("Kiểm tra và cập nhật 7-Zip...")
            self._check_7zip()

            self.progress_update.emit("Kiểm tra và cập nhật aria2...")
            self._check_aria2()
            self.finished.emit(True, "Kiểm tra công cụ hoàn tất.")
        except requests.ConnectionError:
            if not ARIA2_EXEC.exists() or not SEVENZ_EXEC.exists():
                self.finished.emit(False, "Thiếu công cụ và không có internet. Vui lòng kết nối mạng và khởi động lại.")
            else:
                self.finished.emit(True, "Không có internet, sử dụng công cụ có sẵn.")
        except Exception as e:
            self.finished.emit(False, f"Lỗi không xác định khi kiểm tra công cụ: {e}")

    def _check_7zip(self):
        tool_dir = SEVENZ_DIR
        exec_file = SEVENZ_EXEC
        tool_name = "7-Zip"
        api_url = SEVENZIP_API_URL
        asset_name = '7zr.exe'
        tool_dir.mkdir(exist_ok=True)
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
        tool_dir.mkdir(exist_ok=True)
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
    progress_percentage = pyqtSignal(str, float)  # New signal for download progress

class InstallWorker(QThread):
    def __init__(self, apps_to_process, action="install"):
        super().__init__()
        self.signals = WorkerSignals()
        self.apps_to_process = apps_to_process
        self.action = action
        self._is_stopped = False
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'TekDT-AIS-App'})

    def run(self):
        try:
            for app_key, app_info in self.apps_to_process.items():
                if self._is_stopped:
                    self.signals.progress.emit(app_key, "stopped", "Tác vụ đã bị dừng.")
                    continue
                
                self.signals.progress.emit(app_key, "processing", f"Bắt đầu xử lý {app_info.get('display_name')}...")
                
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
                                    continue  # Bỏ qua giá trị không hợp lệ
                    process.wait()
                    if process.returncode != 0:
                        stderr = process.stderr.read()
                        self.signals.progress.emit(app_key, "failed", f"Tải xuống thất bại: {stderr}")
                        continue
                    else:
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
                if self.action == "install" and app_info.get('type') == 'installer':
                    if not download_path.exists():
                        self.signals.progress.emit(app_key, "failed", f"File cài đặt không tồn tại: {download_path}")
                        continue
                    install_params = app_info.get('install_params', '').split()
                    install_command = [str(download_path)] + install_params
                    
                    try:
                        process = subprocess.run(install_command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        if process.returncode != 0:
                            self.signals.progress.emit(app_key, "failed", f"Cài đặt {app_key} thất bại: {process.stderr}")
                            continue
                    except Exception as e:
                        self.signals.progress.emit(app_key, "failed", f"Lỗi khi cài đặt {app_key}: {str(e)}")
                        continue
                
                self.signals.progress.emit(app_key, "success", "Hoàn thành!")

        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

    def stop(self):
        self._is_stopped = True

# --- WIDGET TÙY CHỈNH CHO MỖI PHẦN MỀM ---
class AppItemWidget(QWidget):
    add_requested = pyqtSignal(str, dict)
    remove_requested = pyqtSignal(str, dict)
    def __init__(self, app_key, app_info, parent=None):
        super().__init__(parent)
        self.app_key = app_key
        self.app_info = app_info
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # Icon
        self.icon_label = QLabel()
        icon_file = app_info.get('icon_file', '')
        icon_path = APPS_DIR / app_key / icon_file if icon_file else ''
        default_icon_path = IMAGES_DIR / 'default_icon.png'
        
        if icon_path and Path(icon_path).exists():
            icon = QIcon(str(icon_path))
            if not icon.isNull():
                pixmap = icon.pixmap(32, 32)
                self.icon_label.setPixmap(pixmap)
            else:
                self.icon_label.setFixedSize(32, 32)
                self.icon_label.setText("?")
                self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.icon_label.setStyleSheet("color: #ecf0f1; background-color: #34495e; border: 1px solid #3498db;")
        else:
            icon = QIcon(str(default_icon_path))
            if not icon.isNull():
                pixmap = icon.pixmap(32, 32)
                self.icon_label.setPixmap(pixmap)
            else:
                self.icon_label.setFixedSize(32, 32)
                self.icon_label.setText("?")
                self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.icon_label.setStyleSheet("color: #ecf0f1; background-color: #34495e; border: 1px solid #3498db;")
        self.layout.addWidget(self.icon_label)
        
        # Thông tin
        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(5)
        
        self.name_label = QLabel(f"{app_info.get('display_name', 'N/A')}")
        self.name_label.setStyleSheet("font-weight: bold;")
        self.version_label = QLabel(f"Phiên bản: {app_info.get('version', 'N/A')}")
        
        self.info_layout.addWidget(self.name_label)
        self.info_layout.addWidget(self.version_label)
        self.layout.addWidget(self.info_widget, 1)
        
        # Nút hành động
        self.action_button = QPushButton()
        self.action_button.setFixedSize(80, 30)
        self.action_button.hide()
        self.layout.addWidget(self.action_button)
        
        # Dấu tick/X
        self.status_label = QLabel()
        self.status_label.setFixedSize(24, 24)
        self.layout.addWidget(self.status_label)
        self.status_label.hide()
        
        self.setToolTip(app_info.get('description', 'Không có mô tả.'))

    def enterEvent(self, event):
        if self.action_button.isEnabled():
            self.action_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.action_button.hide()
        super().leaveEvent(event)
        
    def set_status(self, status):
        if status == "success":
            self.status_label.setPixmap(QPixmap(str(IMAGES_DIR / 'success.png')).scaled(16, 16))
            self.name_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.action_button.setText("Thêm")  # Đổi chữ nút thành "Thêm"
            self.action_button.setStyleSheet(
                "background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
            )
            self.status_label.show()
        elif status == "failed":
            self.status_label.setPixmap(QPixmap(str(IMAGES_DIR / 'failed.png')).scaled(16, 16))
            self.name_label.setStyleSheet("color: #F44336; font-weight: bold;")
            self.action_button.setStyleSheet(
                "background-color: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
            )
            self.status_label.show()
        elif status == "processing":
            movie = QMovie(str(IMAGES_DIR / 'loading.gif'))
            self.status_label.setMovie(movie)
            movie.start()
            self.status_label.show()
        else:
            self.status_label.hide()
            self.name_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
            self.action_button.setStyleSheet(
                "background-color: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
            )

    def update_download_progress(self, percentage):
        if self.action_button.text() == "Tải":
            # Interpolate between orange (#e67e22) and green (#4CAF50)
            orange = QColor(230, 126, 34)
            green = QColor(76, 175, 80)
            try:
                percentage = float(percentage)  # Ép kiểu percentage thành float
                if percentage < 0 or percentage > 100:
                    percentage = max(0.0, min(100.0, percentage))  # Giới hạn giá trị
                r = int(orange.red() + (green.red() - orange.red()) * (percentage / 100))
                g = int(orange.green() + (green.green() - orange.green()) * (percentage / 100))
                b = int(orange.blue() + (green.blue() - orange.blue()) * (percentage / 100))
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.action_button.setStyleSheet(
                    f"background-color: {color}; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
                )
            except (ValueError, TypeError):
                # Nếu percentage không hợp lệ, giữ màu cam mặc định
                self.action_button.setStyleSheet(
                    "background-color: #e67e22; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
                )

# --- CỬA SỔ CHÍNH ---
class TekDT_AIS(QMainWindow):
    def __init__(self):
        super().__init__()
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
        icon_path = BASE_DIR / "logo.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.setup_ui()
        self.tool_manager_thread = QThread()
        self.tool_manager = ToolManager()
        self.tool_manager.moveToThread(self.tool_manager_thread)
        self.tool_manager.finished.connect(self.on_tool_check_finished)
        self.tool_manager_thread.started.connect(self.tool_manager.run_checks)
        
        self.show_startup_status("Đang khởi tạo...")
        self.tool_manager_thread.start()

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

        if success:
            # Thông báo ngắn gọn trên thanh trạng thái thay vì popup
            self.status_label.setText(message)
            self.load_config_and_apps()
        else:
            QMessageBox.critical(self, "Lỗi nghiêm trọng", message)
            self.close()

    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} - v{APP_VERSION}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 10pt;
            }
            QListWidget {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                color: #ecf0f1;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2c3e50;
            }
            QListWidget::item:hover {
                background-color: #4a627a;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QLineEdit {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                padding: 8px;
                border-radius: 4px;
                color: white;
            }
            QToolTip {
                background-color: #34495e;
                color: white;
                border: 1px solid #3498db;
            }
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
            
    def load_config_and_apps(self):
        # Load local config
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content: # File trống
                        self.config = {}
                    else:
                        self.config = json.loads(content)
            except json.JSONDecodeError: # File hỏng
                self.config = {}
        else:
            self.config = {}

        # Luôn đảm bảo các khóa chính tồn tại
        if 'settings' not in self.config:
            self.config['settings'] = {}
        if 'app_items' not in self.config:
            self.config['app_items'] = {}

        self.local_apps = self.config.get("app_items", {})
        # Clean up invalid local apps
        for key in list(self.local_apps.keys()):
            app_info = self.local_apps[key]
            app_dir = APPS_DIR / key
            icon_file = app_info.get('icon_file', '')
            icon_path = app_dir / icon_file if icon_file else None
            if icon_path and not icon_path.exists():
                app_info['icon_file'] = 'default_icon.png'
                self.config['app_items'][key] = app_info
            if app_info.get('type') == 'portable':
                executable_path = app_dir / app_info.get('executable', '') if app_info.get('executable') else None
                if not executable_path or not executable_path.exists():
                    del self.local_apps[key]
                    self.config['app_items'].pop(key, None)
            else:
                download_url = app_info.get('download_url', '')
                file_name = app_info.get('output_filename', Path(download_url).name if download_url else '')
                installer_path = app_dir / file_name if file_name else None
                if not installer_path or not installer_path.exists():
                    del self.local_apps[key]
                    self.config['app_items'].pop(key, None)
        self.save_config()
        # Đảm bảo selected_for_install là một danh sách
        self.selected_for_install = self.config.get("settings", {}).get("selected_for_install", [])
        if not isinstance(self.selected_for_install, list):
            self.selected_for_install = []

        # Fetch remote app list
        try:
            response = self.session.get(REMOTE_APP_LIST_URL, timeout=10)
            response.raise_for_status()
            self.remote_apps = response.json()
        except requests.RequestException as e:
            QMessageBox.critical(self, "Lỗi mạng", 
                                 f"Không thể tải danh sách phần mềm từ máy chủ: {e}\n"
                                 "Chương trình sẽ chỉ hiển thị các phần mềm đã tải.")
            self.remote_apps = {"app_items": self.local_apps}
        
        # Merge local app info with remote app info
        for key, app_info in self.local_apps.items():
            if key in self.remote_apps.get("app_items", {}):
                self.remote_apps["app_items"][key].update({
                    'icon_file': app_info.get('icon_file', 'default_icon.png')
                })
        
        self.populate_lists()
        
    def populate_lists(self):
        self.available_list_widget.clear()
        self.selected_list_widget.clear()
        
        all_apps = self.remote_apps.get("app_items", {})
        
        # Filter apps based on system architecture
        compatible_apps = {}
        for key, app_info in all_apps.items():
            compatible_os_arch = app_info.get('compatible_os_arch', 'both')
            if (self.system_arch == '64bit' and compatible_os_arch in ['64bit', 'both']) or \
               (self.system_arch == '32bit' and compatible_os_arch == '32bit'):
                compatible_apps[key] = app_info
        
        # Download icons for apps not yet installed if online
        try:
            self.session.get("https://www.google.com", timeout=5)
            for key, app_info in compatible_apps.items():
                if key not in self.local_apps or not (APPS_DIR / key / app_info.get('icon_file', '')).exists():
                    icon_url = app_info.get('icon_url')
                    if icon_url:
                        icon_filename = Path(icon_url).name
                        icon_path = APPS_DIR / key / icon_filename
                        app_dir = APPS_DIR / key
                        app_dir.mkdir(exist_ok=True)
                        if not icon_path.exists():
                            try:
                                icon_response = self.session.get(icon_url, timeout=5)
                                icon_response.raise_for_status()
                                with open(icon_path, 'wb') as f:
                                    f.write(icon_response.content)
                                compatible_apps[key]['icon_file'] = icon_filename
                            except requests.RequestException:
                                compatible_apps[key]['icon_file'] = 'default_icon.png'
        except requests.ConnectionError:
            pass

        categories = sorted(list(set(app.get('category', 'Chưa phân loại') for app in compatible_apps.values())))
        
        for category in categories:
            # Add category header
            cat_item = QListWidgetItem(category.upper())
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            font = QFont()
            font.setBold(True)
            cat_item.setFont(font)
            cat_item.setForeground(QColor("#3498db"))
            self.available_list_widget.addItem(cat_item)

            # Add apps in this category
            for key, info in compatible_apps.items():
                if info.get('category', 'Chưa phân loại') == category:
                    if key in self.selected_for_install:
                        self.add_app_to_list(self.selected_list_widget, key, info)
                    else:
                        self.add_app_to_list(self.available_list_widget, key, info)
        for key in list(self.selected_for_install):
            if key in compatible_apps:
                self.move_app_to_selection(key, compatible_apps[key])
            else:
                self.selected_for_install.remove(key)

        self.update_counts()

    def add_app_to_list(self, list_widget, key, info):
        is_local = key in self.local_apps
        if is_local:
            app_dir = APPS_DIR / key
            if info.get('type') == 'portable':
                executable_path = app_dir / info.get('executable', '') if info.get('executable') else None
                is_local = executable_path and executable_path.exists()
            else:
                download_url = info.get('download_url', '')
                file_name = info.get('output_filename', Path(download_url).name if download_url else '')
                installer_path = app_dir / file_name if file_name else None
                is_local = installer_path and installer_path.exists()
            if not is_local:
                self.local_apps.pop(key, None)
                self.config['app_items'].pop(key, None)
                self.save_config()
        item_widget = AppItemWidget(key, info)
        
        # Tùy chỉnh trạng thái
        item_widget.add_requested.connect(self.move_app_to_selection)
        item_widget.remove_requested.connect(self.remove_app_from_selection)
        is_selected = key in self.selected_for_install
        
        if info.get('type') == 'portable' and is_local:
            item_widget.action_button.setText("Chạy")
            item_widget.action_button.setToolTip(f"Chạy {info['display_name']}")
            item_widget.action_button.clicked.connect(lambda _, k=key: self.run_portable(k))
        elif not is_local:
            item_widget.action_button.setText("Tải")
            item_widget.action_button.setToolTip(f"Tải {info['display_name']} về")
            item_widget.name_label.setStyleSheet("color: #e67e22;") # Orange
            item_widget.action_button.setStyleSheet("background-color: #e67e22; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;")
            item_widget.action_button.clicked.connect(lambda _, k=key, i=info: self.download_app(k, i, item_widget))
        else: # Is local and installer
            item_widget.action_button.setText("Thêm")
            item_widget.action_button.setToolTip(f"Thêm {info['display_name']} vào danh sách")
            
            local_ver = self.local_apps.get(key, {}).get('version', '0')
            remote_ver = info.get('version', '0')
            if remote_ver > local_ver:
                item_widget.name_label.setStyleSheet("color: #2ecc71;")
                item_widget.action_button.clicked.connect(
                    lambda: self.confirm_update(key, info, local_ver, remote_ver)
                )
            else:
                item_widget.action_button.clicked.connect(
                    lambda: item_widget.add_requested.emit(key, info)
                )

        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())
        list_item.setData(Qt.ItemDataRole.UserRole, key) # Store key for searching
        
        list_widget.addItem(list_item)
        list_widget.setItemWidget(list_item, item_widget)

    def confirm_update(self, key, info, local_ver, remote_ver):
        reply = QMessageBox.question(
            self, "Cập nhật phần mềm",
            f"Phiên bản mới hơn của {info['display_name']} ({remote_ver}) đã có. "
            f"Phiên bản hiện tại: {local_ver}. Bạn có muốn cập nhật không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.download_app(key, info)
        else:
            self.move_app_to_selection(key, info)
    def move_app_to_selection(self, key, info):
        # 1. Find and hide/disable in the available list
        self.update_available_item_state(key, is_selected=True)

        # 2. Add to the selected list
        item_widget = AppItemWidget(key, info)
        item_widget.action_button.setText("Bỏ")
        item_widget.action_button.setToolTip(f"Bỏ {info['display_name']} khỏi danh sách")
        item_widget.action_button.clicked.connect(lambda: item_widget.remove_requested.emit(key, info))
        item_widget.remove_requested.connect(self.remove_app_from_selection)
        
        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())
        list_item.setData(Qt.ItemDataRole.UserRole, key)
        self.selected_list_widget.addItem(list_item)
        self.selected_list_widget.setItemWidget(list_item, item_widget)
        
        # 3. Update config
        if key not in self.selected_for_install:
            self.selected_for_install.append(key)
        self.save_config()
        self.update_counts()

    def remove_app_from_selection(self, key, info):
        # 1. Find and remove from selected list
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            widget = self.selected_list_widget.itemWidget(item)
            if hasattr(widget, 'app_key') and widget.app_key == key:
                self.selected_list_widget.takeItem(i)
                break

        # 2. Re-enable in the available list
        self.update_available_item_state(key, is_selected=False)
        
        # 3. Update config
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
                op = QGraphicsOpacityEffect(widget)
                op.setOpacity(0.5 if is_selected else 1.0)
                widget.setGraphicsEffect(op)
                break
                
    def run_portable(self, key):
        app_info = self.local_apps.get(key)
        if app_info:
            executable_path = APPS_DIR / key / app_info.get('executable')
            if executable_path.exists():
                subprocess.Popen([str(executable_path)])
            else:
                QMessageBox.warning(self, "Lỗi", f"Không tìm thấy file thực thi: {executable_path}")
                self.local_apps.pop(key, None)
                self.config['app_items'].pop(key, None)
                self.save_config()
                self.populate_lists()
                
    def download_app(self, key, info, item_widget=None):
        reply = QMessageBox.question(
            self, "Xác nhận tải xuống",
            f"Bạn có muốn tải {info['display_name']} (Phiên bản {info['version']}) không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return
        apps_to_install = {key: info}
        self.start_button.setText("DỪNG")
        self.install_worker = InstallWorker(apps_to_install, action="install")
        self.install_worker.signals.progress.connect(self.update_install_progress)
        self.install_worker.signals.finished.connect(self.on_installation_finished)
        self.install_worker.signals.error.connect(lambda e: QMessageBox.critical(self, "Lỗi Worker", str(e)))
        if item_widget:
            self.install_worker.signals.progress_percentage.connect(item_widget.update_download_progress)
        self.install_worker.start()
        
    def filter_apps(self, text):
        text = text.lower().strip()
        if len(text) < 2:
            for i in range(self.available_list_widget.count()):
                self.available_list_widget.item(i).setHidden(False)
            return

        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            
            # Keep category headers visible
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
            reply = QMessageBox.question(self, "Dừng tác vụ", 
                                         "Bạn có chắc muốn dừng quá trình cài đặt không? "
                                         "Tác vụ đang chạy sẽ được hoàn tất.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.install_worker.stop()
                self.start_button.setText("ĐANG DỪNG...")
                self.start_button.setDisabled(True)
            return

        apps_to_install = {}
        for key in self.selected_for_install:
            if key in self.remote_apps['app_items']:
                app_info = self.remote_apps['app_items'][key]
                app_dir = APPS_DIR / key
                if app_info.get('type') == 'portable':
                    executable_path = app_dir / app_info.get('executable', '') if app_info.get('executable') else None
                    if executable_path and executable_path.exists():
                        continue
                else:
                    download_url = app_info.get('download_url', '')
                    file_name = app_info.get('output_filename', Path(download_url).name if download_url else '')
                    installer_path = app_dir / file_name if file_name else None
                    if installer_path and installer_path.exists():
                        continue
                apps_to_install[key] = app_info
        
        if not apps_to_install:
            QMessageBox.information(self, "Thông báo", "Vui lòng thêm ít nhất một phần mềm để cài đặt.")
            return

        self.start_button.setText("DỪNG")
        self.install_worker = InstallWorker(apps_to_install, action="install")
        self.install_worker.signals.progress.connect(self.update_install_progress)
        self.install_worker.signals.finished.connect(self.on_installation_finished)
        self.install_worker.signals.error.connect(lambda e: QMessageBox.critical(self, "Lỗi Worker", str(e)))
        self.install_worker.start()

    def update_install_progress(self, app_key, status, message):
        self.status_label.setText(f"[{app_key}] {status}: {message}")
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            widget = self.selected_list_widget.itemWidget(item)
            if hasattr(widget, 'app_key') and widget.app_key == app_key:
                widget.set_status(status)
                break
    
    def on_installation_finished(self):
        self.status_label.setText("Hoàn tất! Sẵn sàng cho tác vụ tiếp theo.")
        self.start_button.setText("BẮT ĐẦU CÀI ĐẶT")
        self.start_button.setDisabled(False)
        self.install_worker = None
        # Reload apps to reflect newly installed ones
        QTimer.singleShot(1000, self.load_config_and_apps)

    def update_counts(self):
        remote_count = len(self.remote_apps.get("app_items", {}))
        selected_count = self.selected_list_widget.count()
        
        self.available_count_label.setText(f"Tổng số phần mềm: {remote_count}")
        self.selected_count_label.setText(f"Đã chọn: {selected_count}")

    def save_config(self):
        self.config['settings']['selected_for_install'] = self.selected_for_install
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Không thể lưu cấu hình: {e}")
            
    def closeEvent(self, event):
        # Stop and wait for threads to finish
        if self.install_worker and self.install_worker.isRunning():
            self.install_worker.stop()
            self.install_worker.wait(5000)  # Wait up to 5 seconds
        if self.tool_manager_thread.isRunning():
            self.tool_manager_thread.quit()
            self.tool_manager_thread.wait(5000)  # Wait up to 5 seconds
        self.save_config()
        super().closeEvent(event)
        
# --- LOGIC DÒNG LỆNH (CLI) ---
def handle_cli(args):
    print(f"{APP_NAME} - CLI Mode")
    # Đây là một khung sườn, logic chi tiết cần được phát triển thêm
    if not args:
        print_cli_help()
        return

    command = args[0].lower()
    
    if command == '/help':
        print_cli_help()
    elif command == '/install':
        config = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        local_apps = config.get('app_items', {})
        session = requests.Session()
        session.headers.update({'User-Agent': 'TekDT-AIS-App'})
        try:
            response = session.get(REMOTE_APP_LIST_URL, timeout=10)
            response.raise_for_status()
            remote_apps = response.json().get('app_items', {})
        except requests.RequestException:
            print("Không thể tải danh sách phần mềm từ máy chủ.")
            return

        apps_to_install = {}
        if len(args) > 1:
            app_keys = args[1].split('|')
            for key in app_keys:
                if key in remote_apps:
                    app_info = remote_apps[key]
                    app_dir = APPS_DIR / key
                    if app_info.get('type') == 'portable':
                        executable_path = app_dir / app_info.get('executable', '') if app_info.get('executable') else None
                        if executable_path and executable_path.exists():
                            print(f"{app_info['display_name']} đã được cài đặt.")
                            continue
                    else:
                        download_url = app_info.get('download_url', '')
                        file_name = app_info.get('output_filename', Path(download_url).name if download_url else '')
                        installer_path = app_dir / file_name if file_name else None
                        if installer_path and installer_path.exists():
                            print(f"{app_info['display_name']} đã được cài đặt.")
                            continue
                    apps_to_install[key] = app_info
        else:
            for key, app_info in remote_apps.items():
                if app_info.get('auto_install', False):
                    app_dir = APPS_DIR / key
                    if app_info.get('type') == 'portable':
                        executable_path = app_dir / app_info.get('executable', '') if app_info.get('executable') else None
                        if executable_path and executable_path.exists():
                            continue
                    else:
                        download_url = app_info.get('download_url', '')
                        file_name = app_info.get('output_filename', Path(download_url).name if download_url else '')
                        installer_path = app_dir / file_name if file_name else None
                        if installer_path and installer_path.exists():
                            continue
                    apps_to_install[key] = app_info

        if not apps_to_install:
            print("Không có phần mềm nào cần cài đặt.")
            return

        worker = InstallWorker(apps_to_install, action="install")
        worker.signals.progress.connect(lambda k, s, m: print(f"[{k}] {s}: {m}"))
        worker.signals.error.connect(lambda e: print(f"Lỗi: {e}"))
        worker.start()
        worker.wait()
    elif command == '/update':
        print("Chức năng /update chưa được triển khai đầy đủ.")
        # Logic: Fetch remote list, compare versions, run worker for updates
    else:
        print(f"Lệnh không hợp lệ: {command}")
        print_cli_help()

def print_cli_help():
    print("Sử dụng TekDT AIS qua dòng lệnh:")
    print("  /help                     Hiển thị trợ giúp này.")
    print("  /install                  Cài đặt tất cả các phần mềm có 'auto_install' là true.")
    print("  /install app1|app2        Cài đặt các phần mềm được chỉ định.")
    print("  /update                   Kiểm tra và cập nhật tất cả phần mềm đã cài.")
    print("  /update app1|app2         Cập nhật các phần mềm được chỉ định.")
    print("  /autoinstall:true|false app1   Đặt trạng thái tự động cài đặt cho phần mềm.")

if __name__ == '__main__':
    # Kiểm tra xem có chạy từ dòng lệnh hay không
    cli_args = [arg for arg in sys.argv[1:] if arg.startswith('/')]
    
    if cli_args:
        handle_cli(cli_args)
        sys.exit(0)
    else:
        app = QApplication(sys.argv)
        # Tạo file icon mặc định nếu chưa có
        default_icon = IMAGES_DIR / 'default_icon.png'
        if not default_icon.exists():
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.gray)
            pixmap.save(str(default_icon))
        main_win = TekDT_AIS()
        main_win.show()
        sys.exit(app.exec())