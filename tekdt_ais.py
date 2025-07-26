# TekDT_AIS.py
import sys
import os
import json
import subprocess
import requests
import re
from packaging.version import parse as parse_version

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QScrollArea, QFrame, QSizePolicy, QSpacerItem, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPalette, QEnterEvent, QFont
from PyQt6.QtCore import (
    Qt, QSize, QThread, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve,
    QPoint
)

# --- CÁC HẰNG SỐ VÀ CẤU HÌNH ---
APP_NAME = "TekDT AIS"
APP_VERSION = "1.0.0"
CONFIG_FILE = "app_config.json"
REMOTE_APP_LIST_URL = "https://raw.githubusercontent.com/tekdt/tekdtais/main/app_list.json"
SELF_UPDATE_URL = "https://api.github.com/repos/tekdt/tekdtais/releases/latest"

# Đường dẫn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(BASE_DIR, "Apps")
IMAGES_DIR = os.path.join(BASE_DIR, "Images")
TOOLS_DIR = os.path.join(BASE_DIR, "Tools")
ARIA2_DIR = os.path.join(TOOLS_DIR, "aria2")
ARIA2_EXEC = os.path.join(ARIA2_DIR, "aria2c.exe")
SEVENZ_DIR = os.path.join(TOOLS_DIR, "7z")
SEVENZ_EXEC = os.path.join(SEVENZ_DIR, "7za.exe")

# --- LỚP QUẢN LÝ LOGIC (MODEL) ---
class AppManager:
    def __init__(self):
        self.config = self.load_config()
        self.ensure_dirs()

    def ensure_dirs(self):
        """Đảm bảo các thư mục cần thiết tồn tại."""
        os.makedirs(APPS_DIR, exist_ok=True)
        os.makedirs(IMAGES_DIR, exist_ok=True)
        os.makedirs(TOOLS_DIR, exist_ok=True)
        os.makedirs(ARIA2_DIR, exist_ok=True)
        os.makedirs(SEVENZ_DIR, exist_ok=True)

    def load_config(self):
        """Tải cấu hình từ file JSON."""
        if not os.path.exists(CONFIG_FILE):
            default_config = {"settings": {}, "app_items": {}}
            self.save_config(default_config)
            return default_config
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"settings": {}, "app_items": {}}

    def save_config(self, config_data=None):
        """Lưu cấu hình vào file JSON."""
        data_to_save = config_data if config_data else self.config
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)

    def check_internet(self):
        """Kiểm tra kết nối Internet."""
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def get_remote_app_list(self):
        """Lấy danh sách phần mềm từ Github."""
        try:
            response = requests.get(REMOTE_APP_LIST_URL, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, json.JSONDecodeError):
            return None
            
    def get_downloaded_apps(self):
        """Lấy danh sách các thư mục ứng dụng đã được tải về."""
        if not os.path.exists(APPS_DIR):
            return []
        return [d for d in os.listdir(APPS_DIR) if os.path.isdir(os.path.join(APPS_DIR, d))]


# --- LỚP THỰC THI TÁC VỤ NỀN (INSTALLER/DOWNLOADER) ---
class TaskWorker(QThread):
    progress = pyqtSignal(str, str, str)  # app_key, status ("downloading", "installing", "success", "failed"), message
    finished = pyqtSignal(int, int)  # success_count, fail_count

    def __init__(self, apps_to_process, manager):
        super().__init__()
        self.apps_to_process = apps_to_process
        self.manager = manager
        self.is_running = True
        self.success_count = 0
        self.fail_count = 0

    def run(self):
        """Bắt đầu thực thi các tác vụ."""
        for app_key, app_info in self.apps_to_process.items():
            if not self.is_running:
                break
            
            try:
                # 1. Tải về (nếu cần)
                app_path = os.path.join(APPS_DIR, app_key)
                installer_filename = os.path.basename(app_info['download_link'])
                installer_path = os.path.join(app_path, installer_filename)

                if not os.path.exists(installer_path):
                    self.progress.emit(app_key, "downloading", f"Đang tải {app_info['display_name']}...")
                    os.makedirs(app_path, exist_ok=True)
                    
                    # Sử dụng aria2 để tải
                    cmd = [
                        ARIA2_EXEC,
                        "--dir", app_path,
                        "--out", installer_filename,
                        "--max-connection-per-server=5",
                        "--min-split-size=1M",
                        "--continue=true",
                        app_info['download_link']
                    ]
                    # Thêm headers nếu có
                    if 'download_headers' in app_info and app_info['download_headers']:
                        for key, value in app_info['download_headers'].items():
                            cmd.append(f"--header={key}: {value}")
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
                    if result.returncode != 0:
                        self.progress.emit(app_key, "failed", f"Tải thất bại: {result.stderr}")
                        self.fail_count += 1
                        continue

                # Cập nhật app_config.json sau khi tải xong
                if app_key not in self.manager.config['app_items']:
                    self.manager.config['app_items'][app_key] = app_info
                    self.manager.save_config()

                # 2. Cài đặt (chỉ với type 'installer')
                if app_info['type'] == 'installer':
                    self.progress.emit(app_key, "installing", f"Đang cài đặt {app_info['display_name']}...")
                    
                    install_cmd = [installer_path]
                    if 'install_params' in app_info and app_info['install_params']:
                        install_cmd.extend(app_info['install_params'].split())

                    # Chạy tiến trình cài đặt
                    install_process = subprocess.Popen(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    install_process.wait() # Đợi cho đến khi cài đặt xong

                    if install_process.returncode == 0:
                        self.progress.emit(app_key, "success", "Cài đặt thành công!")
                        self.success_count += 1
                    else:
                        self.progress.emit(app_key, "failed", f"Cài đặt thất bại. Mã lỗi: {install_process.returncode}")
                        self.fail_count += 1
                else: # Portable app
                    self.progress.emit(app_key, "success", "Sẵn sàng để chạy (Portable).")
                    self.success_count += 1

            except Exception as e:
                self.progress.emit(app_key, "failed", f"Lỗi không xác định: {e}")
                self.fail_count += 1

        self.finished.emit(self.success_count, self.fail_count)

    def stop(self):
        """Gửi tín hiệu dừng tác vụ."""
        self.is_running = False

# --- WIDGET TÙY CHỈNH CHO MỖI PHẦN MỀM ---
class AppWidgetItem(QWidget):
    # Tín hiệu được phát ra khi nút được nhấn
    add_clicked = pyqtSignal(str)
    remove_clicked = pyqtSignal(str)
    run_clicked = pyqtSignal(str)
    download_clicked = pyqtSignal(str)

    def __init__(self, app_key, app_info, status="available"):
        super().__init__()
        self.app_key = app_key
        self.app_info = app_info
        self.status = status # available, added, not_downloaded, update_available

        self.setToolTip(app_info.get('description', 'Không có mô tả.'))
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Icon
        self.icon_label = QLabel()
        icon_path = os.path.join(IMAGES_DIR, app_info.get('icon_file', 'default.png'))
        if os.path.exists(icon_path):
            self.icon_label.setPixmap(QPixmap(icon_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(self.icon_label)

        # Tên và phiên bản
        v_layout = QVBoxLayout()
        v_layout.setSpacing(0)
        self.name_label = QLabel(app_info.get('display_name', app_key))
        self.name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        v_layout.addWidget(self.name_label)

        self.version_label = QLabel(f"Phiên bản: {app_info.get('version', 'N/A')}")
        self.version_label.setFont(QFont("Segoe UI", 8))
        v_layout.addWidget(self.version_label)
        layout.addLayout(v_layout)

        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Các nút hành động (ẩn mặc định)
        self.action_button = QPushButton()
        self.action_button.setFixedSize(70, 25)
        self.action_button.hide()
        layout.addWidget(self.action_button)
        
        self.setLayout(layout)
        self.update_appearance()

    def update_appearance(self):
        """Cập nhật giao diện dựa trên trạng thái."""
        self.name_label.setStyleSheet("")
        if self.status == "not_downloaded":
            self.name_label.setStyleSheet("color: orange;")
            self.action_button.setText("Tải")
            self.action_button.setToolTip(f"Tải {self.app_info['display_name']} về máy")
            self.action_button.clicked.connect(lambda: self.download_clicked.emit(self.app_key))
        elif self.status == "update_available":
            self.name_label.setStyleSheet("color: green;")
            self.action_button.setText("Thêm")
            self.action_button.setToolTip(f"Thêm {self.app_info['display_name']} vào danh sách cài đặt")
            self.action_button.clicked.connect(lambda: self.add_clicked.emit(self.app_key))
        elif self.status == "added":
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.gray)
            self.setPalette(palette)
            self.action_button.hide()
        elif self.app_info.get('type') == 'portable':
             self.action_button.setText("Chạy")
             self.action_button.setToolTip(f"Chạy {self.app_info['display_name']}")
             self.action_button.clicked.connect(lambda: self.run_clicked.emit(self.app_key))
        else: # available
             self.action_button.setText("Thêm")
             self.action_button.setToolTip(f"Thêm {self.app_info['display_name']} vào danh sách cài đặt")
             self.action_button.clicked.connect(lambda: self.add_clicked.emit(self.app_key))

    def enterEvent(self, event: QEnterEvent):
        """Sự kiện khi rê chuột vào widget."""
        if self.status != "added":
            self.action_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Sự kiện khi rê chuột ra khỏi widget."""
        self.action_button.hide()
        super().leaveEvent(event)
        
# --- CỬA SỔ CHÍNH (VIEW & CONTROLLER) ---
class MainWindow(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.all_apps_data = {} # Dữ liệu từ remote hoặc local
        self.selected_apps = {} # Dữ liệu các app trong khung bên phải

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()
        self.load_data_and_populate_lists()

    def init_ui(self):
        """Khởi tạo giao diện người dùng."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- Khung bên trái: Danh sách tất cả phần mềm ---
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout(left_panel)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Gõ để tìm kiếm (ít nhất 2 ký tự)...")
        self.search_input.textChanged.connect(self.filter_apps)
        search_layout.addWidget(self.search_input)
        
        self.total_apps_label = QLabel("Tổng số: 0")
        search_layout.addWidget(self.total_apps_label)
        left_layout.addLayout(search_layout)

        self.all_apps_list = QListWidget()
        self.all_apps_list.setStyleSheet("QListWidget::item { border-bottom: 1px solid #ddd; }")
        left_layout.addWidget(self.all_apps_list)
        
        # --- Khung bên phải: Danh sách phần mềm đã chọn ---
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        right_panel.setFixedWidth(400)
        right_layout = QVBoxLayout(right_panel)

        self.selected_apps_label = QLabel("Đã chọn: 0")
        right_layout.addWidget(self.selected_apps_label)

        self.selected_apps_list = QListWidget()
        right_layout.addWidget(self.selected_apps_list)

        # --- Khu vực điều khiển dưới cùng ---
        bottom_layout = QHBoxLayout()
        self.start_button = QPushButton("Bắt đầu")
        self.start_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.start_button.setMinimumHeight(40)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.toggle_installation)
        
        self.status_label = QLabel("Sẵn sàng.")
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        bottom_layout.addWidget(self.start_button)
        right_layout.addLayout(bottom_layout)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.worker = None

    def load_data_and_populate_lists(self):
        """Tải dữ liệu và điền vào các danh sách."""
        has_internet = self.manager.check_internet()
        
        if has_internet:
            remote_data = self.manager.get_remote_app_list()
            if remote_data:
                self.all_apps_data = remote_data.get('app_items', {})
                self.status_label.setText("Đã kết nối. Đang hiển thị danh sách mới nhất.")
            else:
                self.all_apps_data = self.manager.config.get('app_items', {})
                self.status_label.setText("Lỗi khi tải danh sách. Hiển thị các phần mềm đã có.")
        else:
            self.all_apps_data = self.manager.config.get('app_items', {})
            self.status_label.setText("Không có Internet. Chỉ hiển thị các phần mềm đã tải.")
            
        self.populate_all_apps_list()
        self.load_selection_from_config()

    def populate_all_apps_list(self, filter_text=""):
        """Điền dữ liệu vào danh sách bên trái, có thể lọc."""
        self.all_apps_list.clear()
        
        # Lọc ứng dụng nếu có filter_text
        apps_to_display = {}
        if len(filter_text) >= 2:
            for key, info in self.all_apps_data.items():
                if filter_text.lower() in info.get('display_name', '').lower() or \
                   filter_text.lower() in info.get('description', '').lower() or \
                   filter_text.lower() in info.get('category', '').lower():
                    apps_to_display[key] = info
        else:
            apps_to_display = self.all_apps_data

        # Nhóm theo danh mục
        categories = {}
        for key, info in apps_to_display.items():
            category = info.get('category', 'Chưa phân loại')
            if category not in categories:
                categories[category] = []
            categories[category].append((key, info))

        # Sắp xếp danh mục theo alphabet và hiển thị
        sorted_categories = sorted(categories.keys())
        
        item_count = 0
        for category in sorted_categories:
            # Thêm tiêu đề danh mục
            category_item = QListWidgetItem(category.upper())
            category_item.setFlags(Qt.ItemFlag.NoItemFlags)
            category_item.setBackground(QColor("#f0f0f0"))
            font = category_item.font()
            font.setBold(True)
            category_item.setFont(font)
            self.all_apps_list.addItem(category_item)

            # Thêm các app trong danh mục
            for app_key, app_info in sorted(categories[category], key=lambda x: x[1]['display_name']):
                self.add_app_to_list(self.all_apps_list, app_key, app_info)
                item_count += 1
                
        self.total_apps_label.setText(f"Tổng số: {item_count}")

    def add_app_to_list(self, list_widget, app_key, app_info):
        """Thêm một widget ứng dụng vào một QListWidget."""
        status = self.get_app_status(app_key, app_info)
        
        # Nếu đã có trong danh sách chọn, trạng thái là 'added'
        if app_key in self.selected_apps:
            status = "added"
            
        widget = AppWidgetItem(app_key, app_info, status)

        # Kết nối tín hiệu từ widget tới các hàm xử lý
        widget.add_clicked.connect(self.handle_add_app)
        widget.download_clicked.connect(self.handle_download_app)
        widget.run_clicked.connect(self.handle_run_app)
        # widget.remove_clicked sẽ được kết nối khi thêm vào danh sách bên phải

        list_item = QListWidgetItem(list_widget)
        list_item.setSizeHint(widget.sizeHint())
        list_widget.addItem(list_item)
        list_widget.setItemWidget(list_item, widget)

    def get_app_status(self, app_key, app_info):
        """Xác định trạng thái của một ứng dụng."""
        local_apps = self.manager.get_downloaded_apps()
        local_config_apps = self.manager.config['app_items']

        if app_key not in local_apps and app_key not in local_config_apps:
            return "not_downloaded"
            
        if app_key in local_config_apps:
            local_version = local_config_apps[app_key].get('version', '0')
            remote_version = app_info.get('version', '0')
            if parse_version(remote_version) > parse_version(local_version):
                return "update_available"
        
        return "available"
        
    def handle_add_app(self, app_key):
        """Xử lý khi người dùng nhấn nút 'Thêm'."""
        app_info = self.all_apps_data.get(app_key)
        if not app_info: return

        # Kiểm tra cập nhật
        status = self.get_app_status(app_key, app_info)
        if status == "update_available":
            reply = QMessageBox.question(self, 'Xác nhận cập nhật',
                                         f"{app_info['display_name']} có phiên bản mới. Bạn có muốn tải về và cập nhật không?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.No:
                 # Nếu không cập nhật, dùng thông tin cũ
                 app_info = self.manager.config['app_items'][app_key]
            # Nếu có, app_info đã là thông tin mới nhất từ remote

        # Thêm vào danh sách chọn (bên phải)
        self.selected_apps[app_key] = app_info
        self.populate_selected_list()
        
        # Cập nhật lại trạng thái ở danh sách bên trái
        self.update_app_item_status(app_key, "added")
        self.update_start_button_state()
        self.save_selection_to_config()

    def handle_remove_app(self, app_key):
        """Xử lý khi người dùng nhấn nút 'Bỏ'."""
        if app_key in self.selected_apps:
            del self.selected_apps[app_key]
        
        self.populate_selected_list()
        
        # Kích hoạt lại item ở danh sách bên trái
        app_info = self.all_apps_data.get(app_key)
        if app_info:
            status = self.get_app_status(app_key, app_info)
            self.update_app_item_status(app_key, status)
        
        self.update_start_button_state()
        self.save_selection_to_config()

    def handle_download_app(self, app_key):
        # Tạm thời chỉ thêm vào danh sách cài đặt để worker xử lý cả tải và cài
        self.handle_add_app(app_key)
        QMessageBox.information(self, "Thông báo", f"Đã thêm {self.all_apps_data[app_key]['display_name']} vào danh sách. Nhấn 'Bắt đầu' để tải về và cài đặt.")
        
    def handle_run_app(self, app_key):
        """Chạy một ứng dụng portable."""
        app_info = self.all_apps_data.get(app_key)
        if not app_info or app_info['type'] != 'portable':
            return
            
        app_dir = os.path.join(APPS_DIR, app_key)
        executable = os.path.join(app_dir, app_info['executable_name'])

        if os.path.exists(executable):
            try:
                # Chạy không đợi
                subprocess.Popen([executable], cwd=app_dir)
                self.status_label.setText(f"Đang chạy {app_info['display_name']}...")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể chạy {app_info['display_name']}: {e}")
        else:
             QMessageBox.warning(self, "Không tìm thấy", f"Không tìm thấy file thực thi: {executable}. Vui lòng tải về trước.")


    def populate_selected_list(self):
        """Điền dữ liệu vào danh sách bên phải."""
        self.selected_apps_list.clear()
        for app_key, app_info in self.selected_apps.items():
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 5, 5, 5)

            label = QLabel(app_info['display_name'])
            remove_button = QPushButton("Bỏ")
            remove_button.setFixedSize(50, 25)
            remove_button.clicked.connect(lambda _, k=app_key: self.handle_remove_app(k))
            
            layout.addWidget(label)
            layout.addStretch()
            layout.addWidget(remove_button)

            list_item = QListWidgetItem(self.selected_apps_list)
            list_item.setSizeHint(widget.sizeHint())
            self.selected_apps_list.addItem(list_item)
            self.selected_apps_list.setItemWidget(list_item, widget)
            
        self.selected_apps_label.setText(f"Đã chọn: {len(self.selected_apps)}")

    def update_app_item_status(self, app_key_to_update, new_status):
        """Cập nhật trạng thái của một item trong danh sách bên trái."""
        for i in range(self.all_apps_list.count()):
            item = self.all_apps_list.item(i)
            widget = self.all_apps_list.itemWidget(item)
            if isinstance(widget, AppWidgetItem) and widget.app_key == app_key_to_update:
                widget.status = new_status
                widget.update_appearance()
                break

    def filter_apps(self, text):
        """Lọc danh sách ứng dụng dựa trên text input."""
        self.populate_all_apps_list(filter_text=text)

    def update_start_button_state(self):
        """Cập nhật trạng thái của nút Bắt đầu."""
        self.start_button.setEnabled(len(self.selected_apps) > 0)
        
    def toggle_installation(self):
        """Bắt đầu hoặc dừng quá trình cài đặt."""
        if self.worker and self.worker.isRunning():
            # Dừng worker
            self.worker.stop()
            self.start_button.setText("Đang dừng...")
            self.start_button.setEnabled(False)
            QMessageBox.information(self, "Đang dừng", "Đang chờ tác vụ hiện tại hoàn tất. Các tác vụ còn lại trong hàng đợi sẽ bị hủy.")
        else:
            # Bắt đầu worker
            self.start_button.setText("Dừng")
            self.status_label.setText("Bắt đầu quá trình...")
            
            apps_to_process = self.selected_apps.copy()
            self.worker = TaskWorker(apps_to_process, self.manager)
            self.worker.progress.connect(self.update_installation_progress)
            self.worker.finished.connect(self.on_installation_finished)
            self.worker.start()

    def update_installation_progress(self, app_key, status, message):
        """Cập nhật giao diện khi có tiến trình từ worker."""
        self.status_label.setText(f"{self.all_apps_data[app_key]['display_name']}: {message}")
        
        for i in range(self.selected_apps_list.count()):
            item = self.selected_apps_list.item(i)
            widget = self.selected_apps_list.itemWidget(item)
            
            # Tìm widget tương ứng
            label = widget.findChild(QLabel)
            if label and label.text() == self.selected_apps[app_key]['display_name']:
                if status == "success":
                    widget.setStyleSheet("background-color: #d4edda;") # Greenish
                    label.setText(f"{label.text()} ✔")
                elif status == "failed":
                    widget.setStyleSheet("background-color: #f8d7da;") # Reddish
                    label.setText(f"{label.text()} ❌")
                break
                
    def on_installation_finished(self, success_count, fail_count):
        """Xử lý khi worker hoàn thành tất cả các tác vụ."""
        self.start_button.setText("Bắt đầu")
        self.start_button.setEnabled(len(self.selected_apps) > 0)
        self.status_label.setText(f"Hoàn tất! Thành công: {success_count}, Thất bại: {fail_count}")
        self.worker = None

    def save_selection_to_config(self):
        """Lưu danh sách đã chọn vào file config."""
        self.manager.config['settings']['selected_apps_for_install'] = list(self.selected_apps.keys())
        self.manager.save_config()

    def load_selection_from_config(self):
        """Tải danh sách đã chọn từ file config khi mở lại."""
        selected_keys = self.manager.config.get('settings', {}).get('selected_apps_for_install', [])
        for key in selected_keys:
            if key in self.all_apps_data:
                self.handle_add_app(key)
                
    def closeEvent(self, event):
        """Lưu cấu hình cửa sổ khi đóng."""
        self.manager.config['settings']['window_size'] = [self.size().width(), self.size().height()]
        self.save_selection_to_config()
        super().closeEvent(event)


# --- HÀM MAIN VÀ XỬ LÝ DÒNG LỆNH ---
def handle_cli(manager):
    """Xử lý các tham số dòng lệnh."""
    args = sys.argv[1:]
    if not args:
        return False # Không có tham số, chạy GUI

    # TODO: Triển khai logic cho /install, /update, /autoinstall, /help
    # Đây là một ví dụ đơn giản
    print("Chế độ dòng lệnh đang được phát triển.")
    print(f"Tham số nhận được: {args}")
    
    if "/help" in args:
        print("Hướng dẫn sử dụng dòng lệnh TekDT AIS:")
        print("  /install [app1|app2|...]  : Cài đặt các ứng dụng. Mặc định cài các app 'auto_install'.")
        print("  /update [app1|app2|...]   : Cập nhật các ứng dụng. Mặc định cập nhật tất cả.")
        print("  /autoinstall:true <app>    : Bật tự động cài đặt cho một ứng dụng.")
        print("  /autoinstall:false <app>   : Tắt tự động cài đặt cho một ứng dụng.")
        print("  /help                     : Hiển thị trợ giúp này.")
        
    # Xử lý các lệnh khác...

    return True # Đã xử lý, không chạy GUI

def main():
    """Hàm chính của chương trình."""
    manager = AppManager()

    if handle_cli(manager):
        sys.exit(0)

    app = QApplication(sys.argv)
    window = MainWindow(manager)
    
    # Khôi phục kích thước cửa sổ
    win_size = manager.config.get('settings', {}).get('window_size')
    if win_size:
        window.resize(win_size[0], win_size[1])
        
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()