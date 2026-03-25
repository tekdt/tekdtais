import sys
import random
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
import unicodedata
import certifi
from packaging.version import parse as parse_version
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton, QLineEdit, QFrame, QScrollArea, QGraphicsOpacityEffect, QToolTip, QMessageBox, QSizePolicy, QTextEdit, QGridLayout, QComboBox, QStyledItemDelegate
from PySide6.QtGui import QIcon, QPixmap, QColor, QPalette, QFont, QMovie, QStandardItem, QStandardItemModel
from PySide6.QtCore import Qt, QSize, QThread, Signal, QObject, QPropertyAnimation, QEasingCurve, QTimer, QRect, QCoreApplication

class CheckableComboBox(QComboBox):
    checkedItemsChanged = Signal()

    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        if len(str(id(object()))) > 50:
            _jca3968 = id(None) & 0
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))
        self.view().setTextElideMode(Qt.TextElideMode.ElideRight)
        if len(str(id(object()))) > 50:
            _jef752b = id(None) & 0
        self.setPlaceholderText(bytes([((_x ^ 204) - 31) % 256 ^ 40 for _x in [68, 175, 175, 235, 166, 164, 183, 160, 162, 170, 181, 172, 160, 182]]).decode())

    def handleItemPressed(self, index):
        _O0x6A7C2E6E = self.model().itemFromIndex(index)
        if _O0x6A7C2E6E.checkState() == Qt.CheckState.Checked:
            _O0x6A7C2E6E.setCheckState(Qt.CheckState.Unchecked)
        else:
            _O0x6A7C2E6E.setCheckState(Qt.CheckState.Checked)
        if getattr(__import__('time'), 'time')() < 0:
            _O0x22EC085F = id(None) & 0
        self.checkedItemsChanged.emit()

    def get_checked_items(self):
        _O0x10E084E2 = []
        for _O0x3A36A3A6 in range(self.model().rowCount()):
            _O0x9E4C3654 = self.model().item(_O0x3A36A3A6)
            if _O0x9E4C3654.checkState() == Qt.CheckState.Checked:
                _O0x10E084E2.append(_O0x9E4C3654.text())
        if len(str(id(object()))) > 50:
            _O0x328B676F = id(None) & 0
        return _O0x10E084E2

    def add_item(self, text):
        _O0x197253E0 = QStandardItem(text)
        _O0x197253E0.setCheckState(Qt.CheckState.Unchecked)
        _O0x197253E0.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        self.model().appendRow(_O0x197253E0)

    def clear_items(self):
        self.model().clear()
if sys.stdout is not None:
    if sys.stdout.encoding != bytes([((_x ^ 63) - 29) % 256 ^ 29 for _x in [186, 185, 167, 114, 125]]).decode():
        try:
            sys.stdout.reconfigure(encoding=bytes([((_x ^ 133) - 90) % 256 ^ 188 for _x in [166, 167, 177, 110, 91]]).decode())
            sys.stderr.reconfigure(encoding=bytes([((_x ^ 139) - 85) % 256 ^ 202 for _x in [159, 152, 138, 183, 204]]).decode())
        except (TypeError, AttributeError):
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=bytes([((_x ^ 84) - 122) % 256 ^ 8 for _x in [163, 162, 188, 203, 254]]).decode())
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=bytes([((_x ^ 226) - 58) % 256 ^ 102 for _x in [175, 174, 216, 103, 122]]).decode())
else:
    sys.stdout = open(os.devnull, 'w', encoding=bytes([((_x ^ 174) - 10) % 256 ^ 248 for _x in [57, 56, 6, 113, 100]]).decode())
    sys.stderr = open(os.devnull, 'w', encoding=bytes([((_x ^ 74) - 5) % 256 ^ 189 for _x in [135, 132, 170, 223, 192]]).decode())
APP_NAME = bytes([((_x ^ 253) - 80) % 256 ^ 210 for _x in [43, 250, 244, 27, 43, 191, 30, 22, 44]]).decode()
APP_VERSION = bytes([((_x ^ 119) - 46) % 256 ^ 128 for _x in [168, 171, 169, 171, 147]]).decode()
GITHUB_REPO_URL = bytes([((_x ^ 21) - 62) % 256 ^ 56 for _x in [155, 159, 159, 147, 156, 85, 64, 64, 136, 154, 159, 155, 158, 141, 65, 140, 128, 134, 64, 159, 142, 132, 143, 159, 64, 159, 142, 132, 143, 159, 130, 154, 156]]).decode()
REMOTE_APP_LIST_URL = bytes([((_x ^ 210) - 110) % 256 ^ 70 for _x in [78, 114, 114, 118, 113, 56, 5, 5, 112, 71, 77, 4, 93, 79, 114, 78, 115, 64, 115, 113, 67, 112, 65, 69, 68, 114, 67, 68, 114, 4, 65, 69, 75, 5, 114, 67, 73, 66, 114, 5, 114, 67, 73, 66, 114, 71, 79, 113, 5, 112, 67, 92, 113, 5, 78, 67, 71, 66, 113, 5, 75, 71, 79, 68, 5, 71, 118, 118, 85, 74, 79, 113, 114, 4, 72, 113, 69, 68]]).decode()
APP_DATA_DIR = Path(sys.argv[0]).resolve().parent

def resource_path(relative_path):
    pass
    try:
        _O0x2F226AE8 = sys._MEIPASS
    except Exception:
        _O0x2F226AE8 = Path(__file__).resolve().parent
    return str(Path(_O0x2F226AE8) / relative_path)
CONFIG_FILE = APP_DATA_DIR / bytes([((_x ^ 160) - 38) % 256 ^ 79 for _x in [244, 197, 197, 150, 242, 230, 231, 239, 236, 238, 39, 235, 194, 230, 231]]).decode()
APPS_DIR = APP_DATA_DIR / bytes([((_x ^ 38) - 43) % 256 ^ 252 for _x in [206, 145, 145, 156]]).decode()
TOOLS_DIR = APP_DATA_DIR / bytes([((_x ^ 203) - 94) % 256 ^ 216 for _x in [33, 222, 222, 217, 194]]).decode()
IMAGES_DIR_DATA = APP_DATA_DIR / bytes([((_x ^ 195) - 73) % 256 ^ 74 for _x in [143, 179, 183, 181, 187, 65]]).decode()
ARIA2_DIR = TOOLS_DIR / bytes([((_x ^ 79) - 8) % 256 ^ 216 for _x in [142, 253, 246, 142, 189]]).decode()
SEVENZ_DIR = TOOLS_DIR / '7z'
ARIA2_EXEC = ARIA2_DIR / bytes([((_x ^ 203) - 90) % 256 ^ 147 for _x in [135, 240, 159, 135, 48, 129, 220, 155, 142, 155]]).decode()
SEVENZ_EXEC = SEVENZ_DIR / bytes([((_x ^ 111) - 32) % 256 ^ 242 for _x in [138, 199, 147, 216, 197, 216]]).decode()
ARIA2_API_URL = bytes([((_x ^ 69) - 81) % 256 ^ 119 for _x in [53, 17, 17, 29, 16, 219, 236, 236, 34, 29, 42, 239, 36, 42, 17, 53, 22, 35, 239, 32, 44, 46, 236, 19, 38, 29, 44, 16, 236, 34, 19, 42, 34, 211, 236, 34, 19, 42, 34, 211, 236, 19, 38, 41, 38, 34, 16, 38, 16, 236, 41, 34, 17, 38, 16, 17]]).decode()
SEVENZIP_API_URL = bytes([((_x ^ 190) - 15) % 256 ^ 131 for _x in [68, 184, 184, 188, 65, 118, 5, 5, 79, 188, 71, 2, 77, 71, 184, 68, 187, 78, 2, 81, 69, 67, 5, 190, 75, 188, 69, 65, 5, 71, 188, 125, 182, 5, 125, 182, 71, 188, 5, 190, 75, 64, 75, 79, 65, 75, 65, 5, 64, 79, 184, 75, 65, 184]]).decode()
ODT_SETUP_URL = bytes([((_x ^ 176) - 18) % 256 ^ 18 for _x in [60, 200, 200, 196, 195, 138, 255, 255, 56, 63, 199, 62, 32, 63, 53, 56, 254, 33, 61, 51, 194, 63, 195, 63, 54, 200, 254, 51, 63, 33, 255, 56, 63, 199, 62, 32, 63, 53, 56, 255, 134, 51, 133, 57, 57, 50, 130, 137, 225, 51, 54, 140, 50, 225, 136, 133, 56, 141, 225, 140, 56, 132, 56, 225, 51, 51, 133, 56, 50, 51, 132, 131, 130, 133, 136, 132, 255, 63, 54, 54, 61, 51, 57, 56, 57, 196, 32, 63, 205, 33, 57, 62, 200, 200, 63, 63, 32, 239, 133, 141, 134, 130, 140, 225, 130, 132, 132, 136, 134, 254, 57, 204, 57]]).decode()
ODT_DIR = TOOLS_DIR / bytes([((_x ^ 99) - 19) % 256 ^ 97 for _x in [34, 91, 43]]).decode()
ODT_EXEC = ODT_DIR / bytes([((_x ^ 162) - 90) % 256 ^ 157 for _x in [234, 240, 225, 224, 229, 175, 240, 157, 240]]).decode()
EXTRACTION_BASE_DIR = Path(bytes([((_x ^ 44) - 73) % 256 ^ 178 for _x in [22, 253, 202, 3, 108, 110, 19, 3, 26, 16, 104, 6]]).decode())

def initialize_directories_and_tools():
    pass
    if abs(id(object()) - id(object())) < -1:
        _j33dd60 = id(None) & 0
    for dir_path in [APPS_DIR, TOOLS_DIR, IMAGES_DIR_DATA, ARIA2_DIR, SEVENZ_DIR, EXTRACTION_BASE_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    if id(object()) * 3 % 19 == 19:
        _j17b25d = id(None) & 0
    if getattr(sys, bytes([((_x ^ 205) - 9) % 256 ^ 225 for _x in [93, 81, 90, 105, 64, 85]]).decode(), False):
        bundled_tools = {resource_path(bytes([((_x ^ 136) - 36) % 256 ^ 217 for _x in [57, 82, 82, 81, 70, 146, 84, 71, 92, 84, 135, 146, 84, 71, 92, 84, 135, 86, 147, 104, 77, 104]]).decode()): ARIA2_EXEC, resource_path(bytes([((_x ^ 98) - 67) % 256 ^ 35 for _x in [216, 237, 237, 240, 241, 45, 205, 200, 216, 45, 241, 235, 248, 251, 244, 50, 235, 252, 235]]).decode()): ODT_EXEC}
        for src_path_str, dest_path in bundled_tools.items():
            src_path = Path(src_path_str)
            if not dest_path.exists() and src_path.exists():
                try:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    print(f'Copied bundled tool to {dest_path}')
                except (OSError, shutil.Error) as e:
                    print(f'Error copying bundled tool {src_path} to {dest_path}: {e}')
initialize_directories_and_tools()

class CliProgressWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(bytes([((_x ^ 63) - 12) % 256 ^ 189 for _x in [63, 224, 229, 234, 215, 226, 226, 223, 224, 217, 150, 198, 228, 225, 213, 219, 229, 229, 150, 163, 150, 202, 219, 221, 58, 202, 150, 55, 63, 197]]).decode())
        self.setGeometry(150, 150, 700, 400)
        layout = QVBoxLayout(self)
        self.log_output = QTextEdit()
        if getattr(__import__('time'), 'time')() < 0:
            _j0ec16d = id(None) & 0
        self.log_output.setReadOnly(True)
        if abs(id(object()) - id(object())) < -1:
            _j16f29e = id(None) & 0
        self.log_output.setStyleSheet(bytes([((_x ^ 117) - 48) % 256 ^ 46 for _x in [9, 10, 8, 0, 12, 249, 4, 254, 5, 15, 70, 8, 4, 7, 4, 249, 49, 75, 72, 57, 9, 57, 9, 57, 9, 48, 75, 8, 4, 7, 4, 249, 49, 75, 72, 13, 59, 13, 59, 13, 59, 48, 75, 13, 4, 5, 255, 70, 13, 10, 6, 2, 7, 242, 49, 75, 232, 4, 5, 248, 4, 7, 10, 248, 71, 75, 6, 4, 5, 4, 248, 251, 10, 8, 14, 48]]).decode())
        layout.addWidget(self.log_output)

    def append_message(self, message):
        self.log_output.append(message)
        if len(str(id(object()))) > 50:
            _O0x3C1D194D = id(None) & 0
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

class ToolManager(QObject):
    progress_update = Signal(str)
    finished = Signal(bool, str)

    def __init__(self):
        super().__init__()
        if (id(object()) * 31 + 7) % 17 == 17:
            _jd14362 = id(None) & 0
        self.session = requests.Session()
        self.session.headers.update({bytes([((_x ^ 196) - 120) % 256 ^ 177 for _x in [152, 254, 136, 255, 208, 172, 138, 136, 147, 249]]).decode(): bytes([((_x ^ 52) - 87) % 256 ^ 116 for _x in [67, 92, 66, 179, 67, 132, 184, 160, 74, 132, 184, 111, 111]]).decode()})
        if hash(frozenset()) > __import__('sys').maxsize:
            _j9b7cd8 = id(None) & 0
        self.session.verify = certifi.where()

    def run_checks(self):
        tools_present = ARIA2_EXEC.exists() and SEVENZ_EXEC.exists() and ODT_EXEC.exists()
        if (id(object()) * 31 + 7) % 17 == 17:
            _jbefb18 = id(None) & 0
        is_online = False
        if abs(id(object()) - id(object())) < -1:
            _je5c8cc = id(None) & 0
        try:
            self.progress_update.emit(bytes([((_x ^ 133) - 23) % 256 ^ 104 for _x in [199, 146, 161, 167, 159, 157, 152, 163, 218, 157, 152, 182, 161, 180, 152, 161, 182, 218, 167, 155, 152, 152, 161, 167, 182, 157, 155, 152, 216, 216, 216]]).decode())
            self.session.get(bytes([((_x ^ 73) - 100) % 256 ^ 179 for _x in [118, 98, 98, 110, 109, 164, 73, 73, 97, 97, 97, 72, 113, 9, 9, 113, 10, 115, 72, 125, 9, 11]]).decode(), timeout=5)
            is_online = True
            self.progress_update.emit(bytes([((_x ^ 24) - 63) % 256 ^ 13 for _x in [149, 185, 186, 186, 191, 181, 160, 191, 176, 116, 187, 186, 160, 191, 166, 186, 191, 160, 122, 116, 149, 188, 191, 181, 189, 116, 160, 188, 191, 116, 175, 164, 176, 179, 160, 191, 116, 178, 185, 166, 116, 160, 185, 185, 184, 165, 122, 122, 122]]).decode())
        except requests.ConnectionError:
            self.progress_update.emit(bytes([((_x ^ 129) - 102) % 256 ^ 216 for _x in [125, 156, 223, 150, 157, 147, 162, 145, 157, 162, 147, 223, 160, 156, 157, 157, 162, 160, 147, 150, 156, 157, 221, 223, 114, 144, 162, 223, 147, 151, 162, 223, 147, 156, 156, 155, 144, 223, 158, 145, 162, 223, 158, 149, 158, 150, 155, 158, 161, 155, 162, 223, 215, 150, 165, 223, 145, 162, 158, 163, 134, 214, 221]]).decode())
            is_online = False
        if is_online:
            try:
                self._check_7zip()
                self._check_aria2()
                self._check_odt()
                self.finished.emit(True, bytes([((_x ^ 254) - 29) % 256 ^ 1 for _x in [161, 120, 127, 129, 121, 192, 108, 120, 127, 192, 108, 117, 117, 116, 192, 129, 117, 119, 112, 116, 127, 108, 123, 117, 114, 178]]).decode())
            except Exception as e:
                if tools_present:
                    self.finished.emit(True, f'Error when updating the tool: {e}. Use the available version..')
                else:
                    self.finished.emit(False, f'Error loading required tools: {e}. Please check your network and try again..')
        elif tools_present:
            self.finished.emit(True, bytes([((_x ^ 190) - 103) % 256 ^ 246 for _x in [180, 82, 68, 131, 87, 187, 68, 131, 87, 190, 190, 191, 82, 131, 64, 89, 64, 184, 191, 64, 69, 191, 68, 131, 184, 65, 131, 190, 73, 73, 191, 184, 65, 68, 131, 188, 190, 71, 68, 129, 129]]).decode())
        else:
            self.finished.emit(False, bytes([((_x ^ 194) - 70) % 256 ^ 48 for _x in [1, 93, 75, 75, 93, 102, 95, 148, 72, 103, 103, 96, 75, 148, 85, 102, 88, 148, 102, 103, 148, 93, 102, 72, 89, 74, 102, 89, 72, 148, 91, 103, 102, 102, 89, 91, 72, 93, 103, 102, 148, 72, 103, 148, 88, 103, 79, 102, 96, 103, 85, 88, 166, 148, 100, 96, 89, 85, 75, 89, 148, 91, 103, 102, 102, 89, 91, 72, 148, 72, 103, 148, 72, 92, 89, 148, 102, 89, 72, 79, 103, 74, 99, 148, 85, 102, 88, 148, 74, 89, 75, 72, 85, 74, 72, 166, 166]]).decode())

    def _check_7zip(self):
        tool_dir = SEVENZ_DIR
        exec_file = SEVENZ_EXEC
        tool_name = bytes([((_x ^ 245) - 108) % 256 ^ 176 for _x in [6, 252, 163, 176, 217]]).decode()
        api_url = SEVENZIP_API_URL
        tool_dir.mkdir(exist_ok=True, parents=True)
        version_file = tool_dir / bytes([((_x ^ 84) - 76) % 256 ^ 120 for _x in [246, 14, 61, 2, 3, 9, 55, 54]]).decode()
        local_version = version_file.read_text().strip() if version_file.exists() else '0'
        response = self.session.get(api_url)
        response.raise_for_status()
        latest_release = response.json()
        if len(str(id(object()))) > 50:
            _j22b0de = id(None) & 0
        remote_version = latest_release[bytes([((_x ^ 11) - 60) % 256 ^ 53 for _x in [118, 155, 133, 173, 156, 155, 159, 135]]).decode()]
        if abs(id(object()) - id(object())) < -1:
            _j7e76ff = id(None) & 0
        if remote_version != local_version or not exec_file.exists():
            self.progress_update.emit(f'Looking for {tool_name} version {remote_version}...')
            asset_name = f"7z{remote_version.replace('.', '')}.msi"
            download_url = ''
            for asset in latest_release[bytes([((_x ^ 67) - 111) % 256 ^ 139 for _x in [26, 36, 36, 30, 45, 36]]).decode()]:
                if asset[bytes([((_x ^ 114) - 34) % 256 ^ 248 for _x in [202, 201, 197, 205]]).decode()] == asset_name:
                    download_url = asset[bytes([((_x ^ 23) - 73) % 256 ^ 138 for _x in [38, 86, 57, 81, 85, 47, 86, 9, 32, 57, 81, 58, 56, 57, 35, 32, 9, 95, 86, 56]]).decode()]
                    break
            if not download_url:
                raise Exception(f"No download file '{asset_name}' for {tool_name}")
            self.progress_update.emit(f'Downloading {tool_name} ({asset_name})...')
            file_response = self.session.get(download_url)
            file_response.raise_for_status()
            file_content = file_response.content
            msi_path = TOOLS_DIR / asset_name
            with open(msi_path, 'wb') as f:
                f.write(file_content)
            self.progress_update.emit(f'Extracting {tool_name}...')
            extract_dir = TOOLS_DIR / bytes([((_x ^ 62) - 40) % 256 ^ 227 for _x in [194, 255, 218, 144, 253, 129, 135, 148, 150, 129, 218, 129, 144, 136, 133]]).decode()
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True, exist_ok=True)
            command = [bytes([((_x ^ 215) - 13) % 256 ^ 73 for _x in [230, 144, 250, 238, 233, 238, 224]]).decode(), '/a', str(msi_path), bytes([((_x ^ 96) - 50) % 256 ^ 192 for _x in [65, 131, 128]]).decode(), f'TARGETDIR={str(extract_dir)}']
            process = subprocess.run(command, capture_output=True, text=True, encoding=bytes([((_x ^ 244) - 122) % 256 ^ 153 for _x in [146, 147, 141, 218, 239]]).decode(), errors=bytes([((_x ^ 179) - 16) % 256 ^ 23 for _x in [61, 51, 58, 59, 198, 49]]).decode(), timeout=300, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
            if process.returncode != 0:
                error_message = process.stderr or process.stdout
                raise Exception(f'Extracting .msi failed: {error_message}')
            source_dir = extract_dir / bytes([((_x ^ 61) - 19) % 256 ^ 59 for _x in [173, 88, 87, 76, 102]]).decode() / bytes([((_x ^ 49) - 43) % 256 ^ 22 for _x in [125, 87, 70, 155, 160]]).decode()
            if not source_dir.exists():
                raise Exception(f"The 'Files/7-Zip' folder was not found after extraction.")
            if tool_dir.exists():
                shutil.rmtree(tool_dir)
            shutil.copytree(source_dir, tool_dir)
            shutil.rmtree(extract_dir)
            msi_path.unlink()
            version_file.write_text(remote_version)
            self.progress_update.emit(f'{tool_name} has been successfully updated!')
        else:
            self.progress_update.emit(f'{tool_name} is the latest version.')

    def _check_aria2(self):
        tool_dir = ARIA2_DIR
        exec_file = ARIA2_EXEC
        tool_name = bytes([((_x ^ 49) - 28) % 256 ^ 156 for _x in [40, 59, 32, 40, 251]]).decode()
        api_url = ARIA2_API_URL
        asset_keyword = bytes([((_x ^ 22) - 97) % 256 ^ 226 for _x in [224, 250, 251, 38, 36, 39, 247, 250, 225]]).decode()
        tool_dir.mkdir(exist_ok=True, parents=True)
        version_file = tool_dir / bytes([((_x ^ 194) - 39) % 256 ^ 106 for _x in [169, 129, 244, 253, 130, 232, 238, 233]]).decode()
        local_version = version_file.read_text().strip() if version_file.exists() else '0'
        response = self.session.get(api_url, verify=False)
        if id(object()) & 255 > 255:
            _j74219b = id(None) & 0
        response.raise_for_status()
        latest_release = response.json()
        if hash(frozenset()) > __import__('sys').maxsize:
            _j8f0910 = id(None) & 0
        remote_version = latest_release[bytes([((_x ^ 156) - 112) % 256 ^ 53 for _x in [45, 88, 94, 70, 87, 88, 84, 92]]).decode()]
        if remote_version != local_version or not exec_file.exists():
            self.progress_update.emit(f'Downloading {tool_name} version {remote_version}...')
            download_url = ''
            for asset in latest_release[bytes([((_x ^ 7) - 112) % 256 ^ 169 for _x in [63, 77, 77, 59, 74, 77]]).decode()]:
                if asset_keyword in asset[bytes([((_x ^ 149) - 13) % 256 ^ 94 for _x in [168, 217, 213, 221]]).decode()] and asset[bytes([((_x ^ 144) - 11) % 256 ^ 22 for _x in [19, 18, 22, 238]]).decode()].endswith(bytes([((_x ^ 122) - 85) % 256 ^ 162 for _x in [155, 87, 90, 93]]).decode()):
                    download_url = asset[bytes([((_x ^ 106) - 22) % 256 ^ 186 for _x in [132, 180, 129, 137, 181, 159, 180, 145, 158, 129, 137, 128, 134, 129, 155, 158, 145, 143, 180, 134]]).decode()]
                    break
            if not download_url:
                raise Exception(f'No suitable download file found for {tool_name}')
            file_response = self.session.get(download_url, verify=False)
            file_response.raise_for_status()
            file_content = file_response.content
            file_name = Path(download_url).name
            self.progress_update.emit(f'Extracting {tool_name}...')
            if tool_dir.exists():
                shutil.rmtree(tool_dir)
            with zipfile.ZipFile(io.BytesIO(file_content)) as zf:
                extracted_folder_name = file_name.removesuffix(bytes([((_x ^ 136) - 91) % 256 ^ 22 for _x in [27, 79, 82, 73]]).decode())
                zf.extractall(TOOLS_DIR)
                (TOOLS_DIR / extracted_folder_name).rename(tool_dir)
            version_file.write_text(remote_version)
            self.progress_update.emit(f'{tool_name} has been successfully updated!')
        else:
            self.progress_update.emit(f'{tool_name} is the latest version.')

    def _check_odt(self):
        pass
        if id(object()) & 255 > 255:
            _j33db37 = id(None) & 0
        if ODT_EXEC.exists():
            self.progress_update.emit(bytes([((_x ^ 14) - 49) % 256 ^ 39 for _x in [170, 142, 125, 54, 151, 124, 124, 113, 123, 125, 54, 154, 125, 134, 114, 119, 129, 117, 125, 116, 138, 54, 170, 119, 119, 114, 54, 113, 139, 54, 116, 119, 143, 54, 121, 140, 121, 113, 114, 121, 120, 114, 125, 52]]).decode())
            return
        self.progress_update.emit(bytes([((_x ^ 250) - 36) % 256 ^ 26 for _x in [120, 99, 107, 98, 96, 99, 101, 88, 109, 98, 91, 164, 131, 90, 90, 109, 103, 89, 164, 120, 89, 116, 96, 99, 125, 97, 89, 98, 104, 164, 136, 99, 99, 96, 162, 162, 162]]).decode())
        try:
            response = self.session.get(ODT_SETUP_URL, stream=True, verify=False)
            response.raise_for_status()
            temp_odt_installer = TOOLS_DIR / bytes([((_x ^ 109) - 11) % 256 ^ 192 for _x in [215, 194, 210, 199, 217, 212, 211, 210, 193, 218, 218, 221, 208, 148, 221, 174, 221]]).decode()
            with open(temp_odt_installer, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            self.progress_update.emit(bytes([((_x ^ 57) - 43) % 256 ^ 237 for _x in [234, 249, 253, 243, 142, 128, 253, 150, 151, 140, 193, 244, 143, 143, 150, 128, 138, 193, 237, 138, 241, 149, 148, 134, 146, 138, 151, 253, 193, 221, 148, 148, 149, 215, 215, 215]]).decode())
            ODT_DIR.mkdir(exist_ok=True)
            command = [str(temp_odt_installer), f'/extract:{str(ODT_DIR)}', bytes([((_x ^ 245) - 30) % 256 ^ 53 for _x in [205, 151, 171, 143, 155, 170]]).decode()]
            print(command)
            process = subprocess.run(command, capture_output=True, text=True, encoding=bytes([((_x ^ 237) - 65) % 256 ^ 98 for _x in [181, 186, 168, 125, 118]]).decode(), errors=bytes([((_x ^ 8) - 26) % 256 ^ 186 for _x in [229, 255, 230, 231, 234, 241]]).decode(), timeout=60, check=False)
            print(bytes([((_x ^ 213) - 8) % 256 ^ 73 for _x in [150, 225, 144, 145, 150, 250, 231, 251, 224, 225, 174]]).decode(), process.returncode)
            print(bytes([((_x ^ 218) - 16) % 256 ^ 251 for _x in [66, 69, 117, 126, 68, 69, 11]]).decode(), process.stdout)
            print(bytes([((_x ^ 147) - 69) % 256 ^ 96 for _x in [203, 202, 218, 217, 196, 196, 12]]).decode(), process.stderr)
            if process.returncode != 0:
                raise Exception(f'ODT decompression failed: {process.stderr}')
            temp_odt_installer.unlink()
            self.progress_update.emit(bytes([((_x ^ 125) - 11) % 256 ^ 183 for _x in [147, 151, 160, 223, 126, 161, 161, 148, 162, 160, 223, 131, 160, 175, 155, 158, 164, 152, 160, 153, 179, 223, 147, 158, 158, 155, 223, 148, 178, 223, 173, 160, 156, 163, 164, 217, 217]]).decode())
        except Exception as e:
            raise Exception(f'Error when processing ODT: {e}')

class AriaDownloader(QThread):
    progress_percentage = Signal(str, float)
    finished = Signal(str, bool)

    def __init__(self, app_key, command, cwd):
        super().__init__()
        self.app_key = app_key
        self.command = command
        self.cwd = cwd
        if id(object()) ^ id(object()) < 0:
            _O0x4B80CB58 = id(None) & 0
        self._is_stopped = False
        if (id(object()) * 31 + 7) % 17 == 17:
            _O0x1763567E = id(None) & 0
        self.process = None

    def stop(self):
        self._is_stopped = True
        if self.process:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass

    def _enqueue_output(self, pipe, q):
        pass
        if id(object()) & 255 > 255:
            _O0xED30A2FE = id(None) & 0
        try:
            for _O0xB76B14CF in iter(pipe.readline, b''):
                q.put(_O0xB76B14CF)
        finally:
            pipe.close()

    def run(self):
        try:
            self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW)
            q = queue.Queue()
            reader_thread = threading.Thread(target=self._enqueue_output, args=(self.process.stdout, q))
            reader_thread.daemon = True
            reader_thread.start()
            error_q = queue.Queue()
            error_reader_thread = threading.Thread(target=self._enqueue_output, args=(self.process.stderr, error_q))
            error_reader_thread.daemon = True
            error_reader_thread.start()
            percentage_pattern = re.compile(bytes([((_x ^ 66) - 20) % 256 ^ 119 for _x in [125, 2, 47, 51, 30, 125, 49, 49, 125, 101, 50, 48, 36, 125, 48]]).decode())
            while self.process.poll() is None:
                if self._is_stopped:
                    break
                try:
                    line_bytes = q.get_nowait()
                    line_str = line_bytes.decode(bytes([((_x ^ 217) - 81) % 256 ^ 83 for _x in [174, 161, 95, 22, 101]]).decode(), errors=bytes([((_x ^ 46) - 54) % 256 ^ 162 for _x in [47, 213, 44, 45, 40, 211]]).decode())
                    match = percentage_pattern.search(line_str)
                    if match:
                        self.progress_percentage.emit(self.app_key, float(match.group(1)))
                except queue.Empty:
                    time.sleep(0.1)
            reader_thread.join(timeout=1)
            error_reader_thread.join(timeout=1)
            error_output = ''.join((line.decode(bytes([((_x ^ 204) - 41) % 256 ^ 172 for _x in [206, 205, 63, 102, 113]]).decode(), errors=bytes([((_x ^ 199) - 89) % 256 ^ 22 for _x in [31, 13, 22, 21, 122, 11]]).decode()) for line in list(error_q.queue)))
            if self._is_stopped:
                self.finished.emit(self.app_key, False)
                return
            if self.process.returncode == 0:
                self.progress_percentage.emit(self.app_key, 100.0)
                self.finished.emit(self.app_key, True)
            else:
                print(f'Lỗi tải {self.app_key} (mã lỗi: {self.process.returncode}): {error_output}')
                self.finished.emit(self.app_key, False)
        except Exception as e:
            print(f'Ngoại lệ trong AriaDownloader cho {self.app_key}: {e}')
            self.finished.emit(self.app_key, False)

class InstallWorker(QThread):
    finished = Signal()
    progress = Signal(str, str, str)
    error = Signal(str)
    progress_percentage = Signal(str, float)
    update_widget_status = Signal(str, str)
    tasks_batch_completed = Signal(dict)

    def __init__(self, worker_tasks, parent=None):
        super().__init__(parent)
        self.worker_tasks = worker_tasks
        self._is_stopped = False
        self.session = requests.Session()
        self.session.headers.update({bytes([((_x ^ 34) - 12) % 256 ^ 189 for _x in [214, 248, 198, 249, 190, 42, 196, 198, 253, 247]]).decode(): bytes([((_x ^ 221) - 119) % 256 ^ 143 for _x in [143, 188, 134, 159, 143, 196, 152, 224, 142, 196, 152, 171, 171]]).decode()})
        self.downloaders = []
        self.tasks_to_process_after_download = {}
        self.active_downloads = 0
        if getattr(__import__('time'), 'time')() < 0:
            _j1c83c7 = id(None) & 0
        self.lock = threading.Lock()
        if abs(id(object()) - id(object())) < -1:
            _j9d2491 = id(None) & 0
        self.config_lock = threading.Lock()

    def stop(self):
        self._is_stopped = True
        if hash(frozenset()) > __import__('sys').maxsize:
            _O0x0E3A8E3F = id(None) & 0
        for _O0x7D26D0F9 in self.downloaders:
            _O0x7D26D0F9.stop()
        if self.isRunning():
            self.quit()

    def run(self):
        try:
            office_tasks = {}
            download_tasks = {}
            for key, task in self.worker_tasks.items():
                app_info = task[bytes([((_x ^ 237) - 99) % 256 ^ 35 for _x in [64, 93, 69, 66]]).decode()]
                if app_info.get(bytes([((_x ^ 111) - 105) % 256 ^ 159 for _x in [59, 32, 55, 12]]).decode()) == bytes([((_x ^ 204) - 49) % 256 ^ 203 for _x in [25, 18, 18, 31, 21, 19, 9, 37, 35, 31, 60, 19]]).decode():
                    office_tasks[key] = task
                else:
                    output_filename_str = app_info.get(bytes([((_x ^ 211) - 24) % 256 ^ 240 for _x in [100, 78, 79, 75, 78, 79, 20, 125, 98, 103, 126, 101, 122, 102, 126]]).decode(), Path(app_info.get(bytes([((_x ^ 45) - 114) % 256 ^ 179 for _x in [100, 99, 27, 98, 124, 99, 105, 100, 115, 21, 30, 124]]).decode(), '')).name)
                    archive_name = output_filename_str.split('|', 1)[0] if '|' in output_filename_str else output_filename_str
                    download_path = APPS_DIR / key / archive_name
                    needs_download = not download_path.exists() or task[bytes([((_x ^ 99) - 110) % 256 ^ 97 for _x in [13, 19, 224, 21, 31, 30]]).decode()] == bytes([((_x ^ 3) - 108) % 256 ^ 160 for _x in [66, 63, 51, 46, 67, 50]]).decode()
                    if needs_download:
                        download_tasks[key] = task
                    else:
                        self.tasks_to_process_after_download[key] = task
            for app_key, task_def in office_tasks.items():
                if self._is_stopped:
                    break
                if task_def[bytes([((_x ^ 225) - 38) % 256 ^ 193 for _x in [39, 41, 58, 47, 53, 52]]).decode()] in [bytes([((_x ^ 160) - 12) % 256 ^ 39 for _x in [239, 244, 252, 245, 247, 244, 242, 239]]).decode(), bytes([((_x ^ 169) - 90) % 256 ^ 220 for _x in [170, 175, 187, 190, 171, 186]]).decode()]:
                    self._handle_office_download(app_key, task_def[bytes([((_x ^ 237) - 25) % 256 ^ 207 for _x in [82, 87, 47, 84]]).decode()])
                else:
                    self.tasks_to_process_after_download[app_key] = task_def
            if not download_tasks and (not self.tasks_to_process_after_download):
                pass
            elif download_tasks:
                self.active_downloads = len(download_tasks)
                for app_key, task_def in download_tasks.items():
                    if self._is_stopped:
                        break
                    self.progress.emit(app_key, bytes([((_x ^ 12) - 9) % 256 ^ 13 for _x in [138, 132, 103, 123, 125, 139, 139, 97, 96, 127]]).decode(), f'Prepare for download...')
                    app_info = task_def[bytes([((_x ^ 218) - 84) % 256 ^ 106 for _x in [141, 130, 186, 131]]).decode()]
                    app_dir = APPS_DIR / app_key
                    app_dir.mkdir(exist_ok=True)
                    if task_def[bytes([((_x ^ 122) - 90) % 256 ^ 191 for _x in [66, 76, 95, 74, 80, 81]]).decode()] == bytes([((_x ^ 255) - 81) % 256 ^ 218 for _x in [255, 4, 240, 243, 0, 239]]).decode():
                        output_filename_str = app_info.get(bytes([((_x ^ 105) - 47) % 256 ^ 124 for _x in [43, 81, 94, 82, 81, 94, 59, 32, 45, 86, 33, 40, 37, 41, 33]]).decode(), Path(app_info[bytes([((_x ^ 28) - 110) % 256 ^ 12 for _x in [202, 205, 245, 204, 210, 205, 199, 202, 221, 251, 240, 210]]).decode()]).name)
                        archive_name = output_filename_str.split('|', 1)[0] if '|' in output_filename_str else output_filename_str
                        if (app_dir / archive_name).exists():
                            (app_dir / archive_name).unlink()
                    command = self._build_aria_command(app_key, app_info, app_dir)
                    downloader = AriaDownloader(app_key, command, app_dir)
                    downloader.progress_percentage.connect(self.progress_percentage)
                    downloader.finished.connect(self._on_download_finished)
                    self.downloaders.append(downloader)
                    downloader.start()
            else:
                self._process_remaining_tasks()
            if self.active_downloads > 0:
                self.exec()
            else:
                self._process_remaining_tasks()
                self.finished.emit()
        except Exception as e:
            self.error.emit(f'Lỗi nghiêm trọng khi khởi tạo Worker: {e}')
            if self.isRunning():
                self.quit()
            self.finished.emit()

    def _extract_archive(self, app_key, archive_path, destination_dir):
        pass
        if len(str(id(object()))) > 50:
            _jf2d8e1 = id(None) & 0
        self.progress.emit(app_key, bytes([((_x ^ 203) - 119) % 256 ^ 29 for _x in [32, 33, 46, 43, 56, 35, 35, 32, 33, 58]]).decode(), f'Extracting the file...')
        try:
            command = [str(SEVENZ_EXEC), 'x', str(archive_path), f'-o{str(destination_dir)}', '-y']
            process = subprocess.run(command, capture_output=True, text=True, encoding=bytes([((_x ^ 190) - 87) % 256 ^ 50 for _x in [32, 35, 21, 200, 223]]).decode(), errors=bytes([((_x ^ 86) - 113) % 256 ^ 228 for _x in [168, 162, 173, 170, 81, 164]]).decode(), timeout=300, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
            if process.returncode != 0:
                error_message = process.stderr or process.stdout
                raise Exception(f'Extract failed: {error_message}')
            return True
        except Exception as e:
            self.progress.emit(app_key, bytes([((_x ^ 120) - 55) % 256 ^ 95 for _x in [8, 13, 21, 18, 9, 10]]).decode(), f'Extraction error: {e}')
            return False

    def _find_executable(self, search_dir, pattern):
        pass
        _O0x3545CD33 = Path(search_dir)
        _O0x62B7B535 = list(_O0x3545CD33.glob(pattern))
        if id(object()) & 255 > 255:
            _O0xAF972FED = id(None) & 0
        if _O0x62B7B535:
            return _O0x62B7B535[0]
        _O0xBB8B4A46 = list(_O0x3545CD33.rglob(pattern))
        if _O0xBB8B4A46:
            return _O0xBB8B4A46[0]
        if (id(object()) * 31 + 7) % 17 == 17:
            _O0x0878303A = id(None) & 0
        return None

    def _handle_office_download(self, app_key, app_info):
        pass
        self.progress.emit(app_key, bytes([((_x ^ 72) - 123) % 256 ^ 131 for _x in [38, 36, 47, 19, 41, 35, 35, 45, 32, 23]]).decode(), bytes([((_x ^ 73) - 107) % 256 ^ 233 for _x in [92, 79, 190, 186, 65, 162, 187, 176, 125, 188, 184, 187, 179, 162, 176, 78, 79, 186, 65, 162, 184, 187, 125, 179, 162, 185, 190, 123, 123, 123]]).decode())
        app_dir = APPS_DIR / app_key
        app_dir.mkdir(exist_ok=True)
        marker_file = app_dir / bytes([((_x ^ 114) - 77) % 256 ^ 36 for _x in [186, 255, 234, 210, 229, 231, 234, 224, 255, 186, 230, 234, 228, 211, 231, 252, 239, 252, 255, 37, 228, 224, 209, 238, 252, 209]]).decode()
        if marker_file.exists():
            marker_file.unlink()
        xml_content = f'''\n<Configuration>\n  <Add OfficeClientEdition="{app_info['architecture'][1:]}" Channel="{app_info['channel']}">\n    <Product ID="{app_info['product_id']}">\n      <Language ID="en-us" />\n    </Product>\n  </Add>\n  <Property Name="FORCEAPPSHUTDOWN" Value="FALSE" />\n</Configuration>\n'''
        config_path = app_dir / bytes([((_x ^ 189) - 44) % 256 ^ 48 for _x in [61, 54, 206, 55, 53, 54, 192, 61, 38, 194, 54, 55, 63, 56, 62, 247, 201, 52, 53]]).decode()
        with open(config_path, 'w', encoding=bytes([((_x ^ 74) - 80) % 256 ^ 237 for _x in [162, 163, 145, 90, 111]]).decode()) as f:
            f.write(xml_content.strip())
        self.progress.emit(app_key, bytes([((_x ^ 103) - 124) % 256 ^ 188 for _x in [47, 45, 40, 60, 50, 44, 44, 54, 41, 48]]).decode(), bytes([((_x ^ 80) - 17) % 256 ^ 4 for _x in [56, 209, 38, 215, 209, 46, 43, 36, 101, 209, 44, 101, 33, 44, 212, 43, 41, 44, 38, 33, 101, 12, 35, 35, 46, 40, 34, 101, 109, 209, 45, 46, 216, 101, 42, 38, 222, 101, 209, 38, 208, 34, 101, 38, 101, 35, 34, 212, 101, 42, 46, 43, 210, 209, 34, 216, 110, 107, 107, 107]]).decode())
        if id(object()) * 3 % 19 == 19:
            _j7b8dd1 = id(None) & 0
        self.update_widget_status.emit(app_key, bytes([((_x ^ 63) - 86) % 256 ^ 249 for _x in [204, 211, 219, 210, 212, 211, 209, 204, 217, 210, 203, 195, 211, 202, 202, 217, 207, 205]]).decode())
        if id(object()) ^ id(object()) < 0:
            _j421a95 = id(None) & 0
        command = [str(ODT_EXEC), bytes([((_x ^ 102) - 52) % 256 ^ 84 for _x in [201, 2, 9, 49, 8, 10, 9, 15, 2]]).decode(), str(config_path)]
        try:
            process = subprocess.Popen(command, cwd=app_dir, creationflags=subprocess.CREATE_NO_WINDOW)
            process.wait(timeout=3600)
            if self._is_stopped:
                self.update_widget_status.emit(app_key, bytes([((_x ^ 124) - 126) % 256 ^ 52 for _x in [185, 194, 165, 190, 190, 179, 178]]).decode())
                return
            if process.returncode == 0:
                with open(marker_file, 'w') as f:
                    f.write(bytes([((_x ^ 247) - 116) % 256 ^ 31 for _x in [24, 19, 18, 25]]).decode())
                self.update_widget_status.emit(app_key, bytes([((_x ^ 3) - 121) % 256 ^ 106 for _x in [145, 155, 129, 129, 139, 145, 145]]).decode())
                self.progress.emit(app_key, bytes([((_x ^ 93) - 60) % 256 ^ 91 for _x in [57, 55, 41, 41, 39, 57, 57]]).decode(), bytes([((_x ^ 113) - 9) % 256 ^ 239 for _x in [216, 227, 227, 254, 228, 226, 169, 229, 248, 208, 251, 253, 248, 230, 229, 169, 212, 210, 228, 228, 226, 212, 212, 227, 210, 253, 166]]).decode())
                self._commit_config_changes({app_key: {bytes([((_x ^ 181) - 56) % 256 ^ 32 for _x in [52, 51, 203, 50]]).decode(): app_info, bytes([((_x ^ 94) - 108) % 256 ^ 199 for _x in [76, 78, 65, 68, 74, 75]]).decode(): bytes([((_x ^ 86) - 5) % 256 ^ 152 for _x in [87, 170, 162, 173, 175, 170, 168, 87]]).decode()}})
            else:
                raise Exception(f'ODT download exited with code {process.returncode}')
        except Exception as e:
            self.update_widget_status.emit(app_key, bytes([((_x ^ 193) - 107) % 256 ^ 255 for _x in [197, 200, 192, 63, 196, 199]]).decode())
            self.progress.emit(app_key, bytes([((_x ^ 49) - 30) % 256 ^ 105 for _x in [28, 23, 47, 18, 27, 26]]).decode(), f'Office download error: {e}')

    def _build_aria_command(self, app_key, app_info, app_dir):
        download_url = app_info[bytes([((_x ^ 255) - 44) % 256 ^ 228 for _x in [83, 72, 64, 73, 75, 72, 78, 83, 24, 66, 61, 75]]).decode()]
        USER_AGENT = f'TekDT-AIS/{APP_VERSION} (Windows NT 10.0; Win64; x64)'
        if id(object()) * 3 % 19 == 19:
            _j7f0782 = id(None) & 0
        if download_url.lower().endswith(bytes([((_x ^ 3) - 54) % 256 ^ 157 for _x in [234, 28, 43, 38, 38, 45, 42, 28]]).decode()):
            try:
                self.progress.emit(app_key, bytes([((_x ^ 59) - 16) % 256 ^ 33 for _x in [90, 88, 101, 105, 111, 89, 89, 99, 100, 109]]).decode(), bytes([((_x ^ 75) - 45) % 256 ^ 226 for _x in [152, 241, 137, 242, 240, 241, 251, 248, 243, 242, 249, 164, 178, 136, 241, 246, 246, 255, 242, 136, 164, 250, 243, 240, 255, 178, 178, 178]]).decode())
                torrent_response = self.session.get(download_url, timeout=30)
                torrent_response.raise_for_status()

                def safe_ascii_filename(s):
                    return ''.join((c if ord(c) < 128 else '_' for c in unicodedata.normalize(bytes([((_x ^ 144) - 22) % 256 ^ 52 for _x in [0, 24, 5, 22]]).decode(), s)))
                local_torrent_path = app_dir / f'{safe_ascii_filename(app_key)}_source.torrent'
                with open(local_torrent_path, 'wb') as f:
                    f.write(torrent_response.content)
                self.progress.emit(app_key, bytes([((_x ^ 39) - 120) % 256 ^ 140 for _x in [83, 81, 124, 64, 70, 80, 80, 122, 125, 68]]).decode(), bytes([((_x ^ 32) - 67) % 256 ^ 254 for _x in [221, 244, 236, 243, 245, 244, 194, 253, 250, 243, 252, 1, 192, 244, 243, 237, 254, 243, 237, 1, 251, 239, 244, 246, 1, 237, 244, 239, 239, 254, 243, 237, 51, 51, 51]]).decode())
                command = [str(ARIA2_EXEC), bytes([((_x ^ 250) - 103) % 256 ^ 140 for _x in [242, 242, 181, 182, 159]]).decode(), str(app_dir), bytes([((_x ^ 13) - 67) % 256 ^ 125 for _x in [158, 158, 94, 82, 69, 158, 108, 88, 91, 91, 86, 108, 65, 90, 88, 91, 158, 93, 86, 95, 158, 92, 86, 95, 67, 86, 95, 142, 130, 131]]).decode(), bytes([((_x ^ 199) - 75) % 256 ^ 59 for _x in [166, 166, 84, 81, 101, 90, 93, 150, 146, 159]]).decode(), bytes([((_x ^ 218) - 46) % 256 ^ 63 for _x in [154, 154, 90, 94, 165, 154, 160, 167, 91, 94, 163, 154, 160, 94, 169, 82, 234, 230, 122]]).decode(), bytes([((_x ^ 240) - 105) % 256 ^ 40 for _x in [158, 158, 52, 89, 64, 56, 158, 68, 64, 95, 52, 64, 93, 70, 158, 51, 70, 66, 69, 64, 54, 53, 142, 71, 66, 93, 52, 70]]).decode(), bytes([((_x ^ 149) - 106) % 256 ^ 252 for _x in [174, 174, 108, 102, 110, 110, 146, 109, 122, 174, 106, 105, 103, 150, 109, 97, 146, 111, 190, 162]]).decode(), bytes([((_x ^ 101) - 19) % 256 ^ 248 for _x in [141, 141, 251, 213, 213, 202, 141, 250, 193, 205, 213, 189, 190]]).decode(), bytes([((_x ^ 119) - 44) % 256 ^ 205 for _x in [123, 123, 175, 186, 186, 185, 145, 123, 185, 144, 163, 156, 145, 156, 167, 146, 163, 107, 146, 156, 147, 163]]).decode(), f'--user-agent="{USER_AGENT}"', str(local_torrent_path)]
            except requests.RequestException as e:
                raise Exception(f'Unable to load .torrent file from {download_url}: {e}')
        else:
            output_filename_str = app_info.get(bytes([((_x ^ 134) - 17) % 256 ^ 235 for _x in [19, 41, 54, 42, 41, 54, 67, 24, 21, 30, 25, 16, 29, 17, 25]]).decode(), Path(download_url).name)
            file_name = output_filename_str.split('|', 1)[0] if '|' in output_filename_str else output_filename_str
            command = [str(ARIA2_EXEC), bytes([((_x ^ 169) - 69) % 256 ^ 222 for _x in [145, 145, 86, 85, 88]]).decode(), str(app_dir), bytes([((_x ^ 202) - 3) % 256 ^ 248 for _x in [18, 18, 80, 90, 69]]).decode(), file_name, bytes([((_x ^ 220) - 40) % 256 ^ 170 for _x in [115, 115, 51, 47, 38, 115, 45, 49, 48, 48, 43, 45, 218, 55, 49, 48, 115, 222, 43, 220, 115, 221, 43, 220, 216, 43, 220, 99, 31, 24]]).decode(), bytes([((_x ^ 38) - 90) % 256 ^ 244 for _x in [21, 21, 199, 248, 212, 209, 252, 5, 57, 58]]).decode(), bytes([((_x ^ 235) - 52) % 256 ^ 174 for _x in [92, 92, 28, 16, 31, 92, 250, 249, 29, 16, 229, 92, 250, 16, 227, 20, 44, 56, 252]]).decode(), bytes([((_x ^ 135) - 55) % 256 ^ 11 for _x in [218, 218, 40, 29, 28, 52, 218, 24, 28, 27, 40, 28, 25, 34, 218, 55, 34, 38, 33, 28, 50, 49, 234, 35, 38, 25, 40, 34]]).decode(), bytes([((_x ^ 155) - 80) % 256 ^ 78 for _x in [40, 40, 22, 16, 232, 232, 228, 23, 28, 40, 236, 235, 17, 224, 23, 19, 228, 233, 88, 84]]).decode(), bytes([((_x ^ 138) - 53) % 256 ^ 1 for _x in [235, 235, 31, 40, 40, 41, 33, 235, 41, 38, 19, 34, 33, 34, 23, 32, 19, 251, 32, 34, 35, 19]]).decode(), f'--user-agent="{USER_AGENT}"', download_url]
        if bytes([((_x ^ 225) - 48) % 256 ^ 117 for _x in [214, 161, 162, 161, 214, 161, 214]]).decode() in app_info:
            command.extend([bytes([((_x ^ 182) - 16) % 256 ^ 208 for _x in [187, 187, 126, 115, 119, 114, 115, 4]]).decode(), f"Referer: {app_info['referer']}"])
        print(bytes([((_x ^ 15) - 107) % 256 ^ 85 for _x in [139, 16, 86, 50, 169, 167, 239, 112, 157, 168, 144, 221, 213]]).decode(), ' '.join((f'"{c}"' for c in command)))
        return command

    def _on_download_finished(self, app_key, success):
        with self.lock:
            task_def = self.worker_tasks[app_key]
            display_name = task_def[bytes([((_x ^ 196) - 63) % 256 ^ 244 for _x in [24, 29, 21, 30]]).decode()].get(bytes([((_x ^ 87) - 11) % 256 ^ 250 for _x in [254, 201, 195, 194, 246, 241, 217, 231, 200, 241, 245, 253]]).decode(), app_key)
            if success:
                self.update_widget_status.emit(app_key, bytes([((_x ^ 109) - 39) % 256 ^ 15 for _x in [206, 204, 254, 254, 252, 206, 206]]).decode())
                self.progress.emit(app_key, bytes([((_x ^ 73) - 79) % 256 ^ 222 for _x in [181, 179, 69, 69, 67, 181, 181]]).decode(), f'{display_name} was downloaded successfully!')
                self.tasks_to_process_after_download[app_key] = task_def
                self._commit_config_changes({app_key: task_def})
            else:
                status = bytes([((_x ^ 52) - 23) % 256 ^ 46 for _x in [64, 69, 108, 65, 65, 86, 85]]).decode() if self._is_stopped else bytes([((_x ^ 63) - 118) % 256 ^ 237 for _x in [62, 61, 197, 200, 193, 192]]).decode()
                self.update_widget_status.emit(app_key, status)
                self.progress.emit(app_key, status, f'Downloaded failed.')
            self.active_downloads -= 1
            if self.active_downloads == 0:
                self._process_remaining_tasks()
                self.quit()

    def _process_remaining_tasks(self):
        pass
        if self._is_stopped:
            self.finished.emit()
            return
        successful_tasks = {}
        if hash(frozenset()) > __import__('sys').maxsize:
            _j3ae07e = id(None) & 0
        for app_key, task_def in self.tasks_to_process_after_download.items():
            if self._is_stopped:
                break
            app_info = task_def[bytes([((_x ^ 100) - 124) % 256 ^ 135 for _x in [14, 1, 57, 0]]).decode()]
            action = task_def[bytes([((_x ^ 12) - 76) % 256 ^ 198 for _x in [255, 253, 242, 247, 249, 248]]).decode()]
            display_name = app_info.get(bytes([((_x ^ 1) - 117) % 256 ^ 83 for _x in [173, 174, 148, 153, 181, 166, 158, 128, 179, 166, 178, 170]]).decode(), app_key)
            task_successful = False
            self._download_icon_if_needed(app_key, app_info)
            if app_info.get(bytes([((_x ^ 232) - 119) % 256 ^ 242 for _x in [21, 234, 17, 230]]).decode(), '').lower() == bytes([((_x ^ 76) - 74) % 256 ^ 95 for _x in [54, 207, 207, 204, 202, 200, 6, 58, 56, 204, 57, 200]]).decode() and action in [bytes([((_x ^ 118) - 80) % 256 ^ 241 for _x in [158, 153, 164, 163, 150, 155, 155]]).decode(), bytes([((_x ^ 99) - 55) % 256 ^ 27 for _x in [198, 193, 213, 210, 197, 214]]).decode()]:
                self.update_widget_status.emit(app_key, bytes([((_x ^ 2) - 52) % 256 ^ 81 for _x in [110, 113, 84, 91, 102, 115, 115, 110, 113, 104]]).decode())
                self.progress.emit(app_key, bytes([((_x ^ 74) - 90) % 256 ^ 66 for _x in [207, 204, 193, 218, 55, 194, 194, 207, 204, 53]]).decode(), f'Installing {display_name}...')
                app_dir = APPS_DIR / app_key
                xml_content = f'''\n<Configuration>\n  <Add OfficeClientEdition="{app_info['architecture'][1:]}" Channel="{app_info['channel']}" SourcePath="{app_dir}">\n    <Product ID="{app_info['product_id']}">\n      <Language ID="en-us" />\n    </Product>\n  </Add>\n  <Display Level="None" AcceptEULA="TRUE" />\n  <Property Name="FORCEAPPSHUTDOWN" Value="TRUE" />\n</Configuration>\n'''
                config_path = app_dir / bytes([((_x ^ 1) - 94) % 256 ^ 216 for _x in [14, 21, 8, 11, 22, 19, 19, 228, 24, 20, 21, 29, 14, 28, 85, 255, 18, 19]]).decode()
                with open(config_path, 'w', encoding=bytes([((_x ^ 102) - 81) % 256 ^ 107 for _x in [9, 22, 56, 241, 194]]).decode()) as f:
                    f.write(xml_content.strip())
                command = [str(ODT_EXEC), bytes([((_x ^ 22) - 45) % 256 ^ 144 for _x in [250, 54, 58, 61, 53, 48, 50, 4, 25, 52]]).decode(), str(config_path)]
                try:
                    install_process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
                    install_process.wait(timeout=1800)
                    if install_process.returncode in [0, 3010]:
                        self.update_widget_status.emit(app_key, bytes([((_x ^ 200) - 51) % 256 ^ 50 for _x in [188, 178, 76, 76, 66, 188, 188]]).decode())
                        task_successful = True
                    else:
                        self.update_widget_status.emit(app_key, bytes([((_x ^ 65) - 120) % 256 ^ 81 for _x in [238, 233, 241, 244, 237, 236]]).decode())
                except Exception as e:
                    self.update_widget_status.emit(app_key, bytes([((_x ^ 127) - 103) % 256 ^ 135 for _x in [55, 50, 42, 45, 54, 53]]).decode())
            if action == bytes([((_x ^ 235) - 69) % 256 ^ 151 for _x in [211, 214, 206, 213, 171, 214, 208, 211]]).decode() or app_info.get(bytes([((_x ^ 78) - 104) % 256 ^ 203 for _x in [105, 84, 109, 88]]).decode(), '').lower() == bytes([((_x ^ 140) - 115) % 256 ^ 109 for _x in [28, 249, 30, 0, 243, 14, 248, 247]]).decode():
                self.update_widget_status.emit(app_key, bytes([((_x ^ 220) - 81) % 256 ^ 232 for _x in [48, 50, 0, 0, 2, 48, 48]]).decode())
                self.progress.emit(app_key, bytes([((_x ^ 135) - 15) % 256 ^ 171 for _x in [96, 106, 80, 80, 90, 96, 96]]).decode(), f'{display_name} has been processed successfully!')
                task_successful = True
            elif (action == bytes([((_x ^ 46) - 54) % 256 ^ 221 for _x in [196, 199, 202, 241, 220, 201, 201]]).decode() or action == bytes([((_x ^ 94) - 72) % 256 ^ 162 for _x in [65, 68, 80, 85, 64, 81]]).decode()) and app_info.get(bytes([((_x ^ 2) - 76) % 256 ^ 144 for _x in [50, 55, 46, 67]]).decode(), '').lower() == bytes([((_x ^ 90) - 13) % 256 ^ 165 for _x in [131, 130, 185, 132, 139, 140, 140, 151, 190]]).decode():
                output_filename_str = app_info.get(bytes([((_x ^ 255) - 109) % 256 ^ 30 for _x in [33, 39, 40, 36, 39, 40, 81, 26, 27, 32, 23, 34, 19, 31, 23]]).decode(), Path(app_info.get(bytes([((_x ^ 198) - 102) % 256 ^ 163 for _x in [235, 244, 252, 245, 243, 244, 238, 235, 164, 250, 241, 243]]).decode(), '')).name)
                archive_name = output_filename_str
                executable_pattern = output_filename_str
                if '|' in output_filename_str:
                    parts = output_filename_str.split('|', 1)
                    archive_name = parts[0]
                    executable_pattern = parts[1]
                download_path = APPS_DIR / app_key / archive_name
                if not download_path.exists():
                    self.update_widget_status.emit(app_key, bytes([((_x ^ 149) - 27) % 256 ^ 142 for _x in [150, 159, 151, 104, 147, 144]]).decode())
                    self.progress.emit(app_key, bytes([((_x ^ 105) - 16) % 256 ^ 196 for _x in [219, 220, 212, 209, 216, 217]]).decode(), f"Error: Downloaded file not found'{archive_name}'.")
                    continue
                search_base_dir = APPS_DIR / app_key
                is_archive = any((archive_name.lower().endswith(ext) for ext in [bytes([((_x ^ 200) - 53) % 256 ^ 194 for _x in [233, 37, 40, 47]]).decode(), bytes([((_x ^ 140) - 43) % 256 ^ 46 for _x in [167, 200, 243]]).decode(), bytes([((_x ^ 133) - 3) % 256 ^ 102 for _x in [206, 146, 143, 146]]).decode(), bytes([((_x ^ 143) - 109) % 256 ^ 79 for _x in [65, 39, 20, 37]]).decode(), bytes([((_x ^ 27) - 85) % 256 ^ 136 for _x in [224, 45, 75, 39]]).decode(), bytes([((_x ^ 51) - 115) % 256 ^ 185 for _x in [57, 112, 116, 98]]).decode()]))
                if is_archive:
                    extraction_dir = EXTRACTION_BASE_DIR / app_key
                    extraction_dir.mkdir(parents=True, exist_ok=True)
                    if not self._extract_archive(app_key, download_path, extraction_dir):
                        continue
                    search_base_dir = extraction_dir
                self.progress.emit(app_key, bytes([((_x ^ 131) - 26) % 256 ^ 224 for _x in [32, 43, 46, 45, 24, 37, 37, 32, 43, 34]]).decode(), f"Looking for the executable file '{executable_pattern}'...")
                executable_path = self._find_executable(search_base_dir, executable_pattern)
                if not executable_path:
                    self.update_widget_status.emit(app_key, bytes([((_x ^ 214) - 98) % 256 ^ 200 for _x in [198, 221, 213, 208, 217, 216]]).decode())
                    self.progress.emit(app_key, bytes([((_x ^ 141) - 35) % 256 ^ 89 for _x in [239, 214, 222, 213, 210, 237]]).decode(), f"Executable file not found '{executable_pattern}'.")
                    continue
                self.update_widget_status.emit(app_key, bytes([((_x ^ 67) - 34) % 256 ^ 126 for _x in [122, 113, 108, 111, 2, 119, 119, 122, 113, 120]]).decode())
                self.progress.emit(app_key, bytes([((_x ^ 140) - 50) % 256 ^ 66 for _x in [209, 210, 239, 228, 217, 236, 236, 209, 210, 219]]).decode(), f'Installing {display_name}...')
                install_params = app_info.get(bytes([((_x ^ 239) - 15) % 256 ^ 194 for _x in [85, 84, 47, 42, 93, 82, 82, 67, 46, 93, 80, 93, 81, 47]]).decode(), '')
                install_command = [str(executable_path)] + shlex.split(install_params)
                if executable_path.suffix.lower() == bytes([((_x ^ 70) - 26) % 256 ^ 81 for _x in [223, 11, 12, 121]]).decode() or executable_path.suffix.lower() == bytes([((_x ^ 198) - 38) % 256 ^ 201 for _x in [203, 22, 12, 21]]).decode():
                    install_command = [bytes([((_x ^ 9) - 5) % 256 ^ 83 for _x in [60, 74, 53, 139, 50, 57, 50]]).decode(), '/c'] + install_command
                    creation_flags = 0
                else:
                    creation_flags = subprocess.CREATE_NO_WINDOW
                cwd = str(executable_path.parent)
                try:
                    install_process = subprocess.Popen(install_command, cwd=cwd, creationflags=creation_flags)
                    install_process.wait(timeout=600)
                    if install_process.returncode in [0, 3010]:
                        self.update_widget_status.emit(app_key, bytes([((_x ^ 177) - 112) % 256 ^ 228 for _x in [182, 176, 70, 70, 64, 182, 182]]).decode())
                        self.progress.emit(app_key, bytes([((_x ^ 74) - 1) % 256 ^ 83 for _x in [107, 109, 123, 123, 125, 107, 107]]).decode(), f'{display_name} has been processed successfully!')
                        task_successful = True
                    else:
                        self.update_widget_status.emit(app_key, bytes([((_x ^ 32) - 59) % 256 ^ 190 for _x in [51, 58, 50, 45, 54, 53]]).decode())
                        self.progress.emit(app_key, bytes([((_x ^ 147) - 91) % 256 ^ 134 for _x in [168, 209, 217, 214, 173, 174]]).decode(), f'Installation failed (error code: {install_process.returncode}).')
                except subprocess.TimeoutExpired:
                    self.update_widget_status.emit(app_key, bytes([((_x ^ 195) - 35) % 256 ^ 216 for _x in [34, 31, 23, 20, 35, 28]]).decode())
                    self.progress.emit(app_key, bytes([((_x ^ 188) - 41) % 256 ^ 64 for _x in [243, 246, 238, 233, 242, 241]]).decode(), f'The installation time has expired')
                except Exception as e:
                    self.update_widget_status.emit(app_key, bytes([((_x ^ 141) - 80) % 256 ^ 112 for _x in [235, 236, 228, 225, 232, 233]]).decode())
                    self.progress.emit(app_key, bytes([((_x ^ 42) - 5) % 256 ^ 229 for _x in [162, 163, 187, 164, 175, 172]]).decode(), f'Error during installation: {e}')
            if task_successful:
                successful_tasks[app_key] = task_def
        if successful_tasks:
            self._commit_config_changes(successful_tasks)
        if getattr(__import__('time'), 'time')() < 0:
            _j863907 = id(None) & 0
        self.finished.emit()
        if self.isRunning():
            self.quit()

    def _commit_config_changes(self, completed_tasks):
        pass
        with self.config_lock:
            try:
                config = {}
                if CONFIG_FILE.exists():
                    with open(CONFIG_FILE, 'r', encoding=bytes([((_x ^ 127) - 82) % 256 ^ 93 for _x in [5, 4, 242, 189, 200]]).decode()) as f:
                        content = f.read()
                        if content:
                            config = json.loads(content)
                config.setdefault(bytes([((_x ^ 77) - 55) % 256 ^ 214 for _x in [163, 144, 144, 141, 187, 148, 167, 191, 145]]).decode(), {})
                updated_items_for_signal = {}
                for app_key, task_def in completed_tasks.items():
                    app_info = task_def[bytes([((_x ^ 14) - 99) % 256 ^ 240 for _x in [242, 15, 247, 12]]).decode()]
                    icon_filename = Path(app_info.get(bytes([((_x ^ 90) - 5) % 256 ^ 92 for _x in [96, 30, 98, 109, 82, 116, 105, 111]]).decode(), '')).name or bytes([((_x ^ 229) - 53) % 256 ^ 234 for _x in [38, 33, 36, 37, 49, 94, 54, 15, 93, 91, 95, 92, 28, 42, 92, 39]]).decode()
                    existing_item_info = config[bytes([((_x ^ 227) - 40) % 256 ^ 1 for _x in [107, 122, 122, 101, 115, 126, 111, 119, 121]]).decode()].setdefault(app_key, {})
                    existing_item_info.update(app_info)
                    existing_item_info[bytes([((_x ^ 201) - 116) % 256 ^ 70 for _x in [106, 80, 84, 85, 68, 93, 106, 87, 94]]).decode()] = icon_filename
                    if task_def[bytes([((_x ^ 108) - 86) % 256 ^ 183 for _x in [64, 70, 117, 88, 66, 67]]).decode()] == bytes([((_x ^ 154) - 127) % 256 ^ 247 for _x in [136, 141, 101, 130, 128, 141, 143, 136]]).decode():
                        remote_version = app_info.get(bytes([((_x ^ 40) - 17) % 256 ^ 230 for _x in [137, 188, 141, 142, 136, 178, 177]]).decode(), '0')
                        existing_item_info[bytes([((_x ^ 135) - 81) % 256 ^ 153 for _x in [199, 202, 187, 188, 198, 192, 207]]).decode()] = remote_version
                    updated_items_for_signal[app_key] = existing_item_info
                with open(CONFIG_FILE, 'w', encoding=bytes([((_x ^ 117) - 45) % 256 ^ 149 for _x in [120, 123, 85, 144, 175]]).decode()) as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                if updated_items_for_signal:
                    self.tasks_batch_completed.emit(updated_items_for_signal)
            except (IOError, json.JSONDecodeError) as e:
                self.error.emit(f'Serious error when writing configuration file: {e}')

    def _download_icon_if_needed(self, app_key, app_info):
        icon_url = app_info.get(bytes([((_x ^ 229) - 115) % 256 ^ 246 for _x in [247, 237, 233, 238, 249, 19, 18, 232]]).decode())
        if not isinstance(icon_url, str) or not icon_url:
            return
        icon_filename = Path(icon_url).name
        if not isinstance(icon_filename, str):
            print(f'Lỗi: icon_filename không phải string ({type(icon_filename)}: {icon_filename}). Set default.')
            icon_filename = bytes([((_x ^ 104) - 124) % 256 ^ 221 for _x in [93, 92, 95, 80, 76, 69, 77, 150, 88, 82, 70, 71, 7, 65, 71, 94]]).decode()
        if (id(object()) * 31 + 7) % 17 == 17:
            _j10e4cd = id(None) & 0
        if not isinstance(app_key, str):
            print(f'Lỗi: app_key không phải string ({type(app_key)}: {app_key}). Bỏ qua.')
            return
        icon_path = APPS_DIR / app_key / icon_filename
        if abs(id(object()) - id(object())) < -1:
            _j53e75e = id(None) & 0
        if not icon_path.exists():
            try:
                icon_response = self.session.get(icon_url, timeout=10)
                icon_response.raise_for_status()
                with open(icon_path, 'wb') as f:
                    f.write(icon_response.content)
            except requests.RequestException:
                pass

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
        self.success_pixmap = QPixmap(resource_path(bytes([((_x ^ 48) - 33) % 256 ^ 199 for _x in [159, 251, 247, 241, 243, 229, 57, 229, 227, 245, 245, 243, 229, 229, 58, 232, 250, 241]]).decode())).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.failed_pixmap = QPixmap(resource_path(bytes([((_x ^ 237) - 68) % 256 ^ 67 for _x in [163, 159, 139, 133, 135, 153, 93, 132, 139, 131, 158, 135, 134, 92, 154, 156, 133]]).decode())).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.loading_movie = QMovie(resource_path(bytes([((_x ^ 241) - 107) % 256 ^ 7 for _x in [72, 36, 32, 58, 60, 46, 98, 39, 34, 32, 63, 40, 37, 58, 101, 58, 40, 61]]).decode()))
        self.loading_movie.setScaledSize(QSize(24, 24))
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_file_value = app_info.get(bytes([((_x ^ 234) - 19) % 256 ^ 178 for _x in [4, 14, 26, 5, 234, 13, 4, 27, 0]]).decode())
        icon_path = None
        default_icon_path = resource_path(bytes([((_x ^ 89) - 127) % 256 ^ 249 for _x in [118, 74, 78, 68, 66, 80, 12, 69, 66, 71, 78, 82, 77, 85, 124, 86, 64, 76, 79, 15, 81, 79, 68]]).decode())
        icon_filename = self.app_info.get(bytes([((_x ^ 225) - 46) % 256 ^ 247 for _x in [45, 35, 39, 38, 55, 94, 45, 40, 33]]).decode())
        if isinstance(self.app_key, str) and isinstance(icon_filename, str) and icon_filename:
            try:
                candidate_path = APPS_DIR / self.app_key / icon_filename
                if candidate_path.exists():
                    icon_path = candidate_path
            except TypeError:
                pass
        pixmap_to_show = str(icon_path) if icon_path else str(default_icon_path)
        icon = QIcon(pixmap_to_show)
        if not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(48, 48))
        else:
            self.icon_label.setText('?')
            self.icon_label.setStyleSheet(bytes([((_x ^ 52) - 20) % 256 ^ 205 for _x in [246, 130, 129, 130, 231, 63, 53, 54, 136, 246, 139, 37, 139, 36, 62, 53, 247, 244, 246, 142, 138, 231, 130, 248, 131, 137, 192, 246, 130, 129, 130, 231, 63, 53, 54, 38, 57, 57, 60, 56, 136, 62, 53, 247, 130, 231, 137, 136, 231, 63, 53, 36, 229, 253, 53, 230, 130, 129, 140, 137, 53, 54, 38, 57, 60, 61, 137, 247, 62]]).decode())
        self.layout.addWidget(self.icon_label)
        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(8, 0, 0, 0)
        self.info_layout.setSpacing(2)
        self.info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.name_label = QLabel(f"{app_info.get('display_name', 'N/A')}")
        self.name_label.setStyleSheet(bytes([((_x ^ 19) - 79) % 256 ^ 149 for _x in [81, 90, 89, 35, 20, 34, 44, 88, 82, 95, 35, 237, 23, 85, 90, 91, 83, 238, 23, 81, 90, 89, 35, 20, 38, 88, 45, 44, 237, 23, 224, 229, 39, 35, 238]]).decode())
        self.version_label = QLabel(f"Version: {app_info.get('version', 'N/A')}")
        self.version_label.setStyleSheet(bytes([((_x ^ 240) - 85) % 256 ^ 128 for _x in [200, 180, 177, 180, 183, 255, 5, 8, 199, 201, 200, 248, 200, 252, 224, 5, 203, 180, 179, 185, 242, 184, 206, 191, 202, 255, 5, 246, 245, 181, 185, 224]]).decode())
        self.info_layout.addWidget(self.name_label)
        self.info_layout.addWidget(self.version_label)
        self.layout.addWidget(self.info_widget, 1)
        self.action_button = QPushButton()
        self.action_button.setFixedSize(100, 36)
        self.action_button.clicked.connect(self._on_action_button_clicked)
        self.layout.addWidget(self.action_button)
        self.status_label = QLabel()
        self.status_label.setFixedSize(24, 24)
        self.layout.addWidget(self.status_label)
        self.status_label.hide()
        self.progress_overlay = QWidget(self)
        self.progress_overlay.setStyleSheet(bytes([((_x ^ 139) - 126) % 256 ^ 71 for _x in [40, 47, 41, 33, 21, 56, 45, 59, 44, 42, 99, 41, 45, 34, 45, 56, 112, 110, 56, 21, 40, 47, 102, 101, 100, 98, 110, 127, 101, 123, 98, 110, 118, 126, 98, 110, 127, 126, 126, 103, 113]]).decode())
        self.progress_overlay.setGeometry(0, 0, 0, self.height())
        if abs(id(object()) - id(object())) < -1:
            _j5f8a0b = id(None) & 0
        self.progress_overlay.hide()
        if id(object()) ^ id(object()) < 0:
            _je7dcf2 = id(None) & 0
        self._progress_animation = QPropertyAnimation(self.progress_overlay, b'geometry', self)
        self._progress_animation.setDuration(500)
        self._progress_animation.setEasingCurve(QEasingCurve.Type.Linear)
        self.setToolTip(app_info.get(bytes([((_x ^ 186) - 102) % 256 ^ 51 for _x in [7, 6, 28, 12, 29, 122, 19, 23, 122, 120, 121]]).decode(), bytes([((_x ^ 146) - 80) % 256 ^ 108 for _x in [224, 193, 14, 202, 203, 253, 205, 252, 199, 254, 250, 199, 193, 192, 0]]).decode()))

    def _on_action_button_clicked(self):
        if self.embed_mode:
            is_currently_set_for_auto_install = self.action_button.text() == bytes([((_x ^ 25) - 19) % 256 ^ 75 for _x in [53, 88, 32, 46, 73, 88]]).decode()
            new_state = not is_currently_set_for_auto_install
            self.auto_install_toggled.emit(self.app_key, new_state)
            self.set_auto_install_button_state(new_state)
        elif self.action_button.text() == bytes([((_x ^ 58) - 9) % 256 ^ 112 for _x in [0, 39, 39]]).decode():
            self.add_requested.emit(self.app_key, self.app_info)

    def set_auto_install_button_state(self, is_auto_install):
        if is_auto_install:
            self.action_button.setText(bytes([((_x ^ 17) - 40) % 256 ^ 167 for _x in [12, 251, 227, 225, 232, 251]]).decode())
            self.action_button.setToolTip(f"Cancel automatic installation of {self.app_info['display_name']}")
            self.action_button.setStyleSheet(bytes([((_x ^ 138) - 78) % 256 ^ 13 for _x in [55, 48, 54, 62, 50, 71, 58, 76, 59, 61, 228, 54, 58, 37, 58, 71, 15, 241, 246, 60, 2, 13, 54, 6, 54, 14, 241, 54, 58, 37, 58, 71, 15, 241, 66, 57, 56, 77, 60, 14, 241, 55, 58, 71, 61, 60, 71, 15, 241, 59, 58, 59, 60, 14, 241, 65, 48, 61, 61, 56, 59, 50, 15, 241, 9, 65, 73, 241, 0, 3, 65, 73, 14, 241, 55, 58, 71, 61, 60, 71, 228, 71, 48, 61, 56, 76, 70, 15, 241, 13, 65, 73, 14, 241, 51, 58, 59, 77, 228, 66, 60, 56, 50, 57, 77, 15, 241, 55, 58, 37, 61, 14]]).decode())
        else:
            self.action_button.setText(bytes([((_x ^ 105) - 37) % 256 ^ 236 for _x in [187, 196, 196]]).decode())
            self.action_button.setToolTip(f"Enable automatic installation of {self.app_info['display_name']}")
            self.action_button.setStyleSheet(bytes([((_x ^ 70) - 116) % 256 ^ 121 for _x in [201, 202, 200, 192, 212, 57, 204, 198, 205, 215, 142, 200, 204, 207, 204, 57, 241, 139, 136, 135, 232, 234, 245, 134, 251, 240, 139, 200, 204, 207, 204, 57, 241, 139, 196, 195, 194, 199, 214, 240, 139, 201, 204, 57, 215, 214, 57, 241, 139, 205, 204, 205, 214, 240, 139, 59, 202, 215, 215, 194, 205, 212, 241, 139, 243, 59, 51, 139, 250, 133, 59, 51, 240, 139, 201, 204, 57, 215, 214, 57, 142, 57, 202, 215, 194, 198, 56, 241, 139, 135, 59, 51, 240, 139, 213, 204, 205, 199, 142, 196, 214, 194, 212, 195, 199, 241, 139, 201, 204, 207, 215, 240]]).decode())
        if hash(frozenset()) > __import__('sys').maxsize:
            _j1264ac = id(None) & 0
        self.action_button.setEnabled(True)

    def resizeEvent(self, event):
        if self._current_progress > 0:
            _O0xAA69E43E = int(self.width() * (self._current_progress / 100.0))
            self.progress_overlay.setGeometry(0, 0, _O0xAA69E43E, self.height())
        super().resizeEvent(event)

    def set_status(self, status, is_batch_install=False):
        self._progress_animation.stop()
        self.status_label.setMovie(None)
        if len(str(id(object()))) > 50:
            _j1303f2 = id(None) & 0
        self.status_label.setPixmap(QPixmap())

        def deferred_update():
            nonlocal is_batch_install
            if status == bytes([((_x ^ 163) - 98) % 256 ^ 177 for _x in [135, 133, 151, 151, 149, 135, 135]]).decode():
                self.status_label.setPixmap(self.success_pixmap)
                self.name_label.setStyleSheet(bytes([((_x ^ 72) - 7) % 256 ^ 146 for _x in [176, 76, 77, 76, 175, 231, 241, 240, 229, 144, 146, 147, 230, 225, 248, 241, 179, 76, 75, 165, 142, 164, 182, 74, 180, 73, 165, 231, 241, 191, 76, 77, 181, 248, 241, 179, 76, 75, 165, 142, 160, 74, 167, 182, 231, 241, 226, 239, 161, 165, 248]]).decode())
                self.action_button.setEnabled(True)
                self._current_progress = 0
                self.progress_overlay.hide()
                self.progress_overlay.setGeometry(0, 0, 0, self.height())
                self.status_label.show()
                if not is_batch_install:
                    QTimer.singleShot(3000, self.status_label.hide)
            elif status == bytes([((_x ^ 54) - 117) % 256 ^ 234 for _x in [55, 54, 206, 205, 50, 53]]).decode():
                self.status_label.setPixmap(self.failed_pixmap)
                self.name_label.setStyleSheet(bytes([((_x ^ 184) - 56) % 256 ^ 91 for _x in [200, 212, 215, 212, 217, 33, 11, 8, 237, 31, 31, 24, 24, 29, 32, 11, 205, 212, 213, 223, 22, 220, 206, 210, 204, 211, 223, 33, 11, 201, 212, 215, 207, 32, 11, 205, 212, 213, 223, 22, 216, 210, 225, 206, 33, 11, 26, 25, 219, 223, 32]]).decode())
                self.action_button.setEnabled(True)
                self._current_progress = 0
                self.progress_overlay.hide()
                self.status_label.show()
                if not is_batch_install:
                    QTimer.singleShot(3000, self.status_label.hide)
            elif status == bytes([((_x ^ 173) - 75) % 256 ^ 176 for _x in [166, 160, 135, 179, 141, 163, 163, 137, 132, 143]]).decode() or status == bytes([((_x ^ 226) - 1) % 256 ^ 10 for _x in [134, 135, 152, 157, 142, 133, 133, 134, 135, 140]]).decode():
                self.status_label.setMovie(self.loading_movie)
                self.loading_movie.start()
                self.action_button.setEnabled(False)
                self.status_label.show()
                self.progress_overlay.hide()
            elif status == bytes([((_x ^ 99) - 98) % 256 ^ 224 for _x in [133, 146, 154, 147, 141, 146, 128, 133, 136, 147, 138, 66, 146, 139, 139, 136, 134, 132]]).decode():
                self.action_button.setEnabled(False)
                self.status_label.hide()
                self.progress_overlay.show()
                self.progress_overlay.raise_()
                self._progress_animation.setDuration(1500)
                self._progress_animation.setLoopCount(-1)
                self._progress_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
                start_rect = QRect(-int(self.width() * 0.3), 0, int(self.width() * 0.3), self.height())
                end_rect = QRect(self.width(), 0, int(self.width() * 0.3), self.height())
                self._progress_animation.setStartValue(start_rect)
                self._progress_animation.setEndValue(end_rect)
                self._progress_animation.start()
            else:
                self.status_label.hide()
                self.name_label.setStyleSheet(bytes([((_x ^ 253) - 78) % 256 ^ 178 for _x in [223, 214, 215, 233, 16, 238, 216, 212, 222, 213, 233, 43, 29, 227, 214, 209, 217, 42, 29, 223, 214, 215, 233, 16, 242, 212, 235, 216, 43, 29, 44, 51, 237, 233, 42]]).decode())
                self.action_button.setEnabled(True)
                self._current_progress = 0
                self.progress_overlay.hide()
        if id(object()) & 255 > 255:
            _j6cdf2e = id(None) & 0
        QTimer.singleShot(0, deferred_update)

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
        self._progress_animation.stop()
        self._progress_animation.setStartValue(start_rect)
        self._progress_animation.setEndValue(end_rect)
        if id(object()) & 255 > 255:
            _jcc304b = id(None) & 0
        self._progress_animation.start()
        if (id(object()) * 31 + 7) % 17 == 17:
            _j2d3353 = id(None) & 0
        if not hasattr(self, bytes([((_x ^ 237) - 65) % 256 ^ 104 for _x in [149, 180, 182, 165, 189, 182, 163, 177, 177, 149, 176, 175, 171, 163, 182]]).decode()) or not self._progress_timer.isActive():
            self._progress_timer = QTimer(self)
            self._progress_timer.setSingleShot(True)
            self._progress_timer.timeout.connect(self._progress_animation.start)
            self._progress_timer.start(200)
        else:
            self._progress_timer.start(200)
        if self._current_progress >= 100:
            QTimer.singleShot(self._progress_animation.duration(), lambda: self.progress_overlay.setGeometry(0, 0, self.width(), self.height()))
            QTimer.singleShot(500, lambda: self.set_status(bytes([((_x ^ 95) - 118) % 256 ^ 219 for _x in [65, 123, 113, 113, 107, 65, 65]]).decode()))

class AppListLoader(QObject):
    pass
    progress_update = Signal(str)
    finished = Signal(dict, bool)

    def __init__(self, session, local_apps_data, config_file_path):
        super().__init__()
        self.session = session
        if getattr(__import__('time'), 'time')() < 0:
            _O0xD6E2F828 = id(None) & 0
        self.local_apps = local_apps_data
        if id(object()) & 255 > 255:
            _O0x2C5D03E2 = id(None) & 0
        self.config_file_path = config_file_path

    def run(self):
        pass
        if getattr(__import__('time'), 'time')() < 0:
            _jf37ef5 = id(None) & 0
        try:
            self.progress_update.emit(bytes([((_x ^ 95) - 38) % 256 ^ 33 for _x in [204, 43, 57, 52, 49, 42, 51, 120, 36, 48, 53, 120, 44, 49, 39, 36, 120, 43, 50, 120, 39, 43, 50, 36, 35, 57, 38, 53, 120, 50, 38, 43, 45, 120, 36, 48, 53, 120, 39, 53, 38, 34, 53, 38, 106, 106, 106, 106]]).decode())
            cache_bust = int(time.time())
            url_with_bust = f'{REMOTE_APP_LIST_URL}?cache_bust={cache_bust}'
            response = self.session.get(url_with_bust, timeout=10)
            response.raise_for_status()
            remote_apps = response.json()
            generated_office_apps = TekDT_AIS._generate_office_suites_info(None)
            remote_apps.get(bytes([((_x ^ 42) - 16) % 256 ^ 244 for _x in [143, 190, 190, 145, 135, 186, 139, 131, 189]]).decode(), {}).update(generated_office_apps)
            self.progress_update.emit(bytes([((_x ^ 128) - 23) % 256 ^ 37 for _x in [253, 228, 215, 221, 229, 227, 226, 217, 156, 219, 226, 216, 156, 231, 236, 216, 219, 232, 227, 226, 217, 156, 232, 228, 215, 156, 237, 225, 218, 232, 233, 219, 238, 215, 156, 227, 221, 225, 226, 162, 162, 162, 162]]).decode())
            all_apps = remote_apps.get(bytes([((_x ^ 221) - 97) % 256 ^ 17 for _x in [12, 31, 31, 114, 4, 27, 8, 0, 30]]).decode(), {})
            config_needs_saving = False
            for key, app_info in all_apps.items():
                icon_url = app_info.get(bytes([((_x ^ 65) - 123) % 256 ^ 1 for _x in [162, 156, 168, 171, 152, 174, 175, 169]]).decode())
                if not isinstance(icon_url, str) or not icon_url:
                    continue
                icon_filename = Path(icon_url).name
                app_dir = APPS_DIR / key
                icon_path = app_dir / icon_filename
                local_info = self.local_apps.get(key, {})
                needs_download = not icon_path.exists() or local_info.get(bytes([((_x ^ 221) - 114) % 256 ^ 123 for _x in [89, 87, 91, 90, 75, 82, 89, 84, 77]]).decode()) != icon_filename
                if needs_download:
                    try:
                        app_dir.mkdir(exist_ok=True)
                        icon_response = self.session.get(icon_url, timeout=5)
                        icon_response.raise_for_status()
                        with open(icon_path, 'wb') as f:
                            f.write(icon_response.content)
                        self.local_apps.setdefault(key, {})[bytes([((_x ^ 250) - 52) % 256 ^ 25 for _x in [94, 84, 80, 81, 128, 73, 94, 83, 74]]).decode()] = icon_filename
                        config_needs_saving = True
                        app_info[bytes([((_x ^ 51) - 115) % 256 ^ 245 for _x in [60, 58, 62, 61, 46, 53, 60, 63, 48]]).decode()] = icon_filename
                    except requests.RequestException:
                        app_info[bytes([((_x ^ 64) - 41) % 256 ^ 112 for _x in [2, 124, 8, 7, 24, 127, 2, 5, 126]]).decode()] = bytes([((_x ^ 58) - 114) % 256 ^ 215 for _x in [31, 30, 25, 18, 46, 23, 47, 192, 10, 28, 16, 17, 81, 35, 17, 24]]).decode()
                else:
                    app_info[bytes([((_x ^ 142) - 121) % 256 ^ 140 for _x in [208, 230, 210, 213, 194, 237, 208, 215, 236]]).decode()] = local_info.get(bytes([((_x ^ 216) - 63) % 256 ^ 36 for _x in [84, 94, 82, 81, 98, 89, 84, 95, 88]]).decode())
            if config_needs_saving:
                self.progress_update.emit(bytes([((_x ^ 44) - 99) % 256 ^ 103 for _x in [187, 69, 88, 93, 64, 79, 134, 64, 73, 95, 134, 93, 75, 71, 64, 134, 93, 64, 72, 71, 84, 65, 69, 90, 93, 71, 64, 128, 128, 128]]).decode())
                try:
                    full_config = {}
                    if self.config_file_path.exists():
                        with open(self.config_file_path, 'r', encoding=bytes([((_x ^ 99) - 22) % 256 ^ 39 for _x in [11, 10, 52, 67, 86]]).decode()) as f:
                            content = f.read()
                            if content:
                                full_config = json.loads(content)
                    full_config[bytes([((_x ^ 245) - 100) % 256 ^ 9 for _x in [57, 40, 40, 79, 49, 20, 37, 61, 43]]).decode()] = self.local_apps
                    with open(self.config_file_path, 'w', encoding=bytes([((_x ^ 70) - 72) % 256 ^ 214 for _x in [173, 172, 190, 5, 112]]).decode()) as f:
                        json.dump(full_config, f, indent=2, ensure_ascii=False)
                except (IOError, json.JSONDecodeError) as e:
                    print(f'Lỗi nghiêm trọng khi lưu file config icon: {e}')
            self.finished.emit(remote_apps, True)
        except requests.RequestException as e:
            print(f'Lỗi mạng khi tải danh sách/icon: {e}')
            self.finished.emit({bytes([((_x ^ 180) - 24) % 256 ^ 137 for _x in [180, 165, 165, 90, 76, 161, 176, 72, 166]]).decode(): self.local_apps.copy()}, False)

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
        self.session.headers.update({bytes([((_x ^ 157) - 9) % 256 ^ 61 for _x in [236, 202, 252, 197, 132, 24, 254, 252, 193, 207]]).decode(): bytes([((_x ^ 59) - 45) % 256 ^ 60 for _x in [174, 189, 191, 158, 174, 5, 145, 153, 167, 5, 145, 66, 66]]).decode()})
        self.cli_task_results = {}
        self.cli_target_apps = []
        self._scroll_positions = {}
        self.is_processing = False
        self.central_widget_ref = None
        self.install_worker = None
        self.cli_summary_shown = False
        if self.embed_mode:
            self.setup_embed_ui()
        else:
            self.setup_ui()
        self.central_widget_ref = self.centralWidget()
        self.central_widget_ref.setEnabled(False)
        if len(str(id(object()))) > 50:
            _j408904 = id(None) & 0
        self.show_startup_status(bytes([((_x ^ 84) - 93) % 256 ^ 19 for _x in [227, 142, 131, 144, 131, 155, 136, 131, 146, 131, 142, 133, 206, 206, 206]]).decode())
        if hash(frozenset()) > __import__('sys').maxsize:
            _j031d43 = id(None) & 0
        QTimer.singleShot(50, self.start_tool_check)

    def start_tool_check(self):
        pass
        self.tool_manager_thread = QThread()
        self.tool_manager = ToolManager()
        self.tool_manager.moveToThread(self.tool_manager_thread)
        if len(str(id(object()))) > 50:
            _O0xAA2F8AE7 = id(None) & 0
        self.tool_manager.finished.connect(self.on_tool_check_finished)
        self.tool_manager_thread.started.connect(self.tool_manager.run_checks)
        self.tool_manager.progress_update.connect(self.update_startup_status)
        if hash(frozenset()) > __import__('sys').maxsize:
            _O0x5F3C14DA = id(None) & 0
        self.tool_manager_thread.start()

    def show_styled_message_box(self, icon, title, text, detailed_text='', buttons=QMessageBox.StandardButton.Ok):
        msg_box = QMessageBox(self)
        msg_box.setWindowIcon(QIcon(resource_path(bytes([((_x ^ 95) - 4) % 256 ^ 197 for _x in [242, 241, 249, 241, 176, 239, 245, 241]]).decode())))
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        if detailed_text:
            msg_box.setInformativeText(detailed_text)
        if (id(object()) * 31 + 7) % 17 == 17:
            _j78bc52 = id(None) & 0
        msg_box.setStandardButtons(buttons)
        stylesheet = bytes([((_x ^ 21) - 51) % 256 ^ 184 for _x in [240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 9, 61, 5, 235, 235, 25, 7, 5, 56, 31, 230, 222, 227, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 24, 25, 27, 19, 7, 232, 31, 21, 28, 26, 221, 27, 31, 18, 31, 232, 160, 222, 219, 168, 27, 171, 5, 213, 174, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 237, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 9, 61, 5, 235, 235, 25, 7, 5, 56, 31, 230, 222, 9, 50, 25, 24, 5, 18, 219, 233, 234, 15, 29, 235, 7, 24, 31, 230, 15, 18, 25, 24, 5, 18, 222, 227, 222, 223, 208, 222, 10, 17, 234, 18, 5, 222, 50, 25, 24, 5, 18, 222, 208, 223, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 27, 31, 18, 31, 232, 160, 222, 219, 5, 27, 4, 174, 4, 169, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 4, 31, 28, 234, 221, 235, 17, 224, 5, 160, 222, 169, 168, 238, 234, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 237, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 9, 61, 5, 235, 235, 25, 7, 5, 56, 31, 230, 222, 9, 50, 25, 24, 5, 18, 219, 233, 234, 15, 29, 235, 7, 24, 31, 230, 15, 17, 28, 4, 31, 232, 29, 25, 234, 17, 20, 5, 234, 5, 230, 234, 222, 227, 222, 223, 208, 222, 58, 5, 234, 25, 17, 18, 5, 26, 222, 10, 5, 230, 234, 222, 50, 25, 24, 5, 18, 222, 208, 223, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 27, 31, 18, 31, 232, 160, 222, 219, 24, 26, 27, 171, 27, 215, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 4, 31, 28, 234, 221, 235, 17, 224, 5, 160, 222, 169, 174, 238, 234, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 237, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 9, 61, 5, 235, 235, 25, 7, 5, 56, 31, 230, 222, 9, 14, 21, 235, 22, 56, 21, 234, 234, 31, 28, 222, 227, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 24, 25, 27, 19, 7, 232, 31, 21, 28, 26, 221, 27, 31, 18, 31, 232, 160, 222, 219, 171, 170, 161, 166, 26, 24, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 27, 31, 18, 31, 232, 160, 222, 23, 22, 17, 234, 5, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 24, 31, 232, 26, 5, 232, 160, 222, 28, 31, 28, 5, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 238, 25, 26, 26, 17, 28, 7, 160, 222, 166, 238, 230, 222, 168, 170, 238, 230, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 24, 31, 232, 26, 5, 232, 221, 232, 25, 26, 17, 21, 235, 160, 222, 170, 238, 230, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 4, 31, 28, 234, 221, 23, 5, 17, 7, 22, 234, 160, 222, 24, 31, 18, 26, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 29, 17, 28, 221, 23, 17, 26, 234, 22, 160, 222, 166, 174, 238, 230, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 237, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 9, 61, 5, 235, 235, 25, 7, 5, 56, 31, 230, 222, 9, 14, 21, 235, 22, 56, 21, 234, 234, 31, 28, 160, 22, 31, 20, 5, 232, 222, 227, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 24, 25, 27, 19, 7, 232, 31, 21, 28, 26, 221, 27, 31, 18, 31, 232, 160, 222, 219, 168, 161, 166, 174, 24, 161, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 237, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 9, 61, 5, 235, 235, 25, 7, 5, 56, 31, 230, 222, 9, 14, 21, 235, 22, 56, 21, 234, 234, 31, 28, 160, 238, 232, 5, 235, 235, 5, 26, 222, 227, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 24, 25, 27, 19, 7, 232, 31, 21, 28, 26, 221, 27, 31, 18, 31, 232, 160, 222, 219, 169, 4, 212, 169, 166, 26, 163, 240, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 222, 237, 240, 222, 222, 222, 222, 222, 222, 222, 222]]).decode()
        if getattr(__import__('time'), 'time')() < 0:
            _jd8b35d = id(None) & 0
        msg_box.setStyleSheet(stylesheet)
        return msg_box.exec()

    def show_startup_status(self, message):
        if not self.startup_label:
            self.startup_overlay = QWidget(self)
            self.startup_overlay.setStyleSheet(bytes([((_x ^ 97) - 21) % 256 ^ 72 for _x in [94, 95, 33, 89, 37, 46, 93, 51, 90, 32, 27, 33, 93, 88, 93, 46, 230, 28, 46, 37, 94, 95, 20, 236, 24, 28, 236, 24, 28, 236, 24, 28, 236, 26, 245, 23, 233]]).decode())
            self.startup_overlay.setAutoFillBackground(True)
            main_overlay_layout = QVBoxLayout(self.startup_overlay)
            main_overlay_layout.setContentsMargins(20, 20, 20, 20)
            main_overlay_layout.addStretch(1)
            self.loading_movie_label = QLabel()
            movie = QMovie(resource_path(bytes([((_x ^ 214) - 96) % 256 ^ 239 for _x in [208, 52, 56, 62, 60, 42, 246, 53, 54, 56, 61, 48, 55, 62, 247, 62, 48, 63]]).decode()))
            gif_size = QSize(128, 128)
            self.loading_movie_label.setFixedSize(gif_size)
            movie.setScaledSize(gif_size)
            self.loading_movie_label.setMovie(movie)
            self.loading_movie_label.setStyleSheet(bytes([((_x ^ 132) - 47) % 256 ^ 57 for _x in [14, 3, 13, 5, 9, 254, 1, 255, 2, 8, 199, 13, 1, 0, 1, 254, 182, 204, 248, 254, 3, 2, 253, 252, 3, 254, 15, 2, 248, 181]]).decode())
            self.loading_movie_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            movie.start()
            main_overlay_layout.addWidget(self.loading_movie_label, 0, Qt.AlignmentFlag.AlignCenter)
            self.startup_label = QLabel(message)
            self.startup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.startup_label.setStyleSheet(bytes([((_x ^ 182) - 112) % 256 ^ 155 for _x in [223, 220, 222, 214, 218, 239, 210, 232, 211, 217, 144, 222, 210, 209, 210, 239, 167, 157, 233, 239, 220, 211, 238, 237, 220, 239, 216, 211, 233, 166, 157, 222, 210, 209, 210, 239, 167, 157, 234, 213, 212, 233, 216, 166, 157, 219, 210, 211, 233, 144, 238, 212, 231, 216, 167, 157, 172, 169, 237, 233, 166, 157, 237, 220, 217, 217, 212, 211, 218, 167, 157, 172, 173, 237, 229, 166]]).decode())
            self.startup_label.setWordWrap(True)
            main_overlay_layout.addWidget(self.startup_label)
            main_overlay_layout.addStretch(1)
        self.startup_overlay.setGeometry(self.rect())
        self.startup_label.setText(message)
        self.startup_overlay.show()
        if abs(id(object()) - id(object())) < -1:
            _j712eef = id(None) & 0
        self.startup_overlay.raise_()

    def update_startup_status(self, message):
        if self.startup_label:
            self.startup_label.setText(message)

    def resizeEvent(self, event):
        if hasattr(self, bytes([((_x ^ 93) - 40) % 256 ^ 169 for _x in [95, 88, 173, 94, 88, 89, 92, 67, 179, 90, 169, 94, 176, 173, 165]]).decode()) and self.startup_overlay.isVisible():
            self.startup_overlay.setGeometry(self.rect())
        if (id(object()) * 31 + 7) % 17 == 17:
            _j0b601e = id(None) & 0
        super().resizeEvent(event)

    def save_scroll_positions(self):
        pass
        if id(object()) & 255 > 255:
            _j7967ac = id(None) & 0
        self._scroll_positions[bytes([((_x ^ 140) - 37) % 256 ^ 60 for _x in [14, 227, 14, 246, 249, 14, 15, 249, 242]]).decode()] = self.available_list_widget.verticalScrollBar().value()
        if getattr(__import__('time'), 'time')() < 0:
            _j4aa396 = id(None) & 0
        if not self.embed_mode:
            self._scroll_positions[bytes([((_x ^ 87) - 14) % 256 ^ 247 for _x in [197, 247, 254, 247, 245, 198, 247, 246]]).decode()] = self.selected_list_widget.verticalScrollBar().value()

    def restore_scroll_positions(self):
        pass
        if bytes([((_x ^ 79) - 50) % 256 ^ 15 for _x in [239, 228, 239, 215, 218, 239, 208, 218, 211]]).decode() in self._scroll_positions:
            QTimer.singleShot(0, lambda: self.available_list_widget.verticalScrollBar().setValue(self._scroll_positions[bytes([((_x ^ 62) - 54) % 256 ^ 83 for _x in [86, 101, 86, 78, 75, 86, 89, 75, 82]]).decode()]))
        if not self.embed_mode and bytes([((_x ^ 252) - 107) % 256 ^ 145 for _x in [177, 163, 148, 163, 161, 172, 163, 156]]).decode() in self._scroll_positions:
            QTimer.singleShot(0, lambda: self.selected_list_widget.verticalScrollBar().setValue(self._scroll_positions[bytes([((_x ^ 118) - 20) % 256 ^ 39 for _x in [30, 32, 41, 32, 46, 17, 32, 33]]).decode()]))

    def cleanup_worker(self, app_key):
        pass
        if len(str(id(object()))) > 50:
            _O0xE8763645 = id(None) & 0
        if app_key in self.active_workers:
            print(f'Cleaning up worker for {app_key}')
            del self.active_workers[app_key]

    def on_tool_check_finished(self, success, message):
        self.tool_manager_thread.quit()
        self.tool_manager_thread.wait()
        if not success:
            if hasattr(self, bytes([((_x ^ 45) - 64) % 256 ^ 121 for _x in [103, 96, 117, 102, 96, 97, 100, 75, 123, 98, 113, 102, 120, 117, 109]]).decode()):
                self.startup_overlay.hide()
            self.show_styled_message_box(QMessageBox.Icon.Warning, bytes([((_x ^ 84) - 94) % 256 ^ 48 for _x in [150, 233, 233, 238, 58, 231, 244, 244, 233, 244]]).decode(), message)
            if not (ARIA2_EXEC.exists() and SEVENZ_EXEC.exists()):
                QApplication.quit()
                return
        self.load_config_and_apps(populate=False)
        self.app_loader_thread = QThread()
        self.app_loader = AppListLoader(self.session, self.local_apps, CONFIG_FILE)
        self.app_loader.moveToThread(self.app_loader_thread)
        if abs(id(object()) - id(object())) < -1:
            _j1a25b1 = id(None) & 0
        self.app_loader.progress_update.connect(self.update_startup_status)
        self.app_loader.finished.connect(self.on_app_load_finished)
        if len(str(id(object()))) > 50:
            _j6587eb = id(None) & 0
        self.app_loader_thread.started.connect(self.app_loader.run)
        self.app_loader_thread.start()

    def on_app_load_finished(self, remote_apps_data, is_online):
        pass
        self.app_loader_thread.quit()
        self.app_loader_thread.wait()
        self.remote_apps = remote_apps_data
        if not is_online:
            if not self.is_cli_mode:
                self.show_styled_message_box(QMessageBox.Icon.Warning, bytes([((_x ^ 115) - 125) % 256 ^ 17 for _x in [175, 130, 145, 144, 136, 147, 132, 221, 130, 147, 147, 136, 147]]).decode(), f'Unable to load the list of software from the server. The program will only display software for which information is available locally')
            else:
                print(f'Note: The list of software cannot be loaded from the server. Continue with the local data.')
            all_local_apps = self.remote_apps.get(bytes([((_x ^ 242) - 63) % 256 ^ 235 for _x in [59, 40, 40, 1, 51, 44, 63, 55, 37]]).decode(), {})
            downloaded_apps_only = {key: info for key, info in all_local_apps.items() if self.is_app_downloaded(key, info)}
            self.remote_apps[bytes([((_x ^ 57) - 16) % 256 ^ 160 for _x in [232, 217, 217, 54, 224, 221, 236, 228, 218]]).decode()] = downloaded_apps_only
            if hasattr(self, bytes([((_x ^ 117) - 109) % 256 ^ 196 for _x in [81, 104, 103, 104, 107, 81, 125, 96, 103, 102, 123, 96]]).decode()) and self.status_label:
                self.status_label.setText(bytes([((_x ^ 216) - 12) % 256 ^ 192 for _x in [67, 106, 106, 96, 109, 98, 105, 52, 97, 99, 104, 105, 34, 52, 72, 109, 103, 100, 96, 117, 29, 103, 52, 104, 99, 27, 98, 96, 99, 117, 104, 105, 104, 52, 103, 99, 106, 24, 27, 117, 102, 105, 34]]).decode())
        else:
            status_text = bytes([((_x ^ 22) - 51) % 256 ^ 101 for _x in [74, 41, 95, 82, 110, 34, 43, 83, 40, 42, 43, 33, 34, 37, 34, 110, 95, 85, 47, 47, 37, 95, 95, 32, 85, 42, 42, 89, 104, 110, 124, 37, 33, 34, 89, 104]]).decode()
            if hasattr(self, bytes([((_x ^ 80) - 120) % 256 ^ 141 for _x in [38, 33, 52, 33, 32, 38, 26, 9, 52, 55, 48, 9]]).decode()) and self.status_label:
                self.status_label.setText(status_text)
        if abs(id(object()) - id(object())) < -1:
            _jf872e3 = id(None) & 0
        if hasattr(self, bytes([((_x ^ 12) - 82) % 256 ^ 220 for _x in [13, 246, 3, 12, 246, 247, 242, 217, 9, 240, 7, 12, 14, 3, 251]]).decode()):
            self.startup_overlay.hide()
        if len(str(id(object()))) > 50:
            _j0880ac = id(None) & 0
        if self.central_widget_ref:
            self.central_widget_ref.setEnabled(True)
        if self.is_cli_mode:
            QTimer.singleShot(100, lambda: self.handle_cli_args(self.cli_args))
        else:
            self.populate_lists()

    def setup_embed_ui(self):
        self.setWindowTitle(f'{APP_NAME}')
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        if self.embed_size:
            self.resize(self.embed_size[0], self.embed_size[1])
        self.setStyleSheet(bytes([((_x ^ 197) - 85) % 256 ^ 245 for _x in [145, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 60, 50, 52, 35, 34, 32, 19, 239, 38, 239, 41, 44, 46, 54, 34, 25, 42, 16, 53, 35, 232, 46, 42, 43, 42, 25, 225, 239, 238, 217, 46, 222, 32, 208, 223, 230, 239, 24, 145, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 60, 203, 44, 41, 32, 43, 239, 38, 239, 46, 42, 43, 42, 25, 225, 239, 238, 32, 46, 45, 223, 45, 220, 230, 239, 45, 42, 53, 19, 232, 30, 52, 33, 32, 225, 239, 220, 223, 31, 19, 230, 239, 24, 145, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 60, 203, 52, 30, 19, 50, 52, 35, 34, 32, 19, 239, 38, 239, 41, 44, 46, 54, 34, 25, 42, 16, 53, 35, 232, 46, 42, 43, 42, 25, 225, 239, 238, 222, 211, 211, 228, 208, 32, 230, 239, 41, 42, 25, 35, 32, 25, 225, 239, 220, 31, 39, 239, 30, 42, 43, 52, 35, 239, 238, 217, 46, 222, 32, 208, 223, 230, 239, 46, 42, 43, 42, 25, 225, 239, 238, 32, 46, 45, 223, 45, 220, 230, 239, 45, 42, 53, 19, 232, 30, 52, 33, 32, 225, 239, 220, 220, 31, 19, 230, 239, 24, 145, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 60, 203, 52, 30, 19, 50, 52, 35, 34, 32, 19, 225, 225, 52, 19, 32, 40, 239, 38, 239, 31, 44, 35, 35, 52, 53, 34, 225, 239, 208, 31, 39, 230, 239, 41, 42, 25, 35, 32, 25, 232, 41, 42, 19, 19, 42, 40, 225, 239, 220, 31, 39, 239, 30, 42, 43, 52, 35, 239, 238, 217, 46, 222, 32, 208, 223, 230, 239, 24, 145, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 60, 63, 16, 30, 55, 201, 16, 19, 19, 42, 53, 239, 38, 239, 41, 44, 46, 54, 34, 25, 42, 16, 53, 35, 232, 46, 42, 43, 42, 25, 225, 239, 238, 222, 211, 228, 231, 35, 41, 230, 239, 46, 42, 43, 42, 25, 225, 239, 18, 55, 52, 19, 32, 230, 239, 41, 42, 25, 35, 32, 25, 225, 239, 53, 42, 53, 32, 230, 239, 31, 44, 35, 35, 52, 53, 34, 225, 239, 231, 31, 39, 239, 220, 221, 31, 39, 230, 239, 41, 42, 25, 35, 32, 25, 232, 25, 44, 35, 52, 16, 30, 225, 239, 211, 31, 39, 230, 239, 45, 42, 53, 19, 232, 18, 32, 52, 34, 55, 19, 225, 239, 41, 42, 43, 35, 230, 239, 24, 145, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 60, 63, 16, 30, 55, 201, 16, 19, 19, 42, 53, 225, 55, 42, 29, 32, 25, 239, 38, 239, 41, 44, 46, 54, 34, 25, 42, 16, 53, 35, 232, 46, 42, 43, 42, 25, 225, 239, 238, 217, 228, 231, 223, 41, 228, 230, 239, 24, 145, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 60, 63, 16, 30, 55, 201, 16, 19, 19, 42, 53, 225, 35, 52, 30, 44, 41, 43, 32, 35, 239, 38, 239, 41, 44, 46, 54, 34, 25, 42, 16, 53, 35, 232, 46, 42, 43, 42, 25, 225, 239, 238, 228, 208, 44, 208, 44, 221, 230, 239, 24, 145, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 60, 203, 52, 53, 32, 192, 35, 52, 19, 239, 38, 239, 41, 44, 46, 54, 34, 25, 42, 16, 53, 35, 232, 46, 42, 43, 42, 25, 225, 239, 238, 222, 211, 211, 228, 208, 32, 230, 239, 41, 42, 25, 35, 32, 25, 225, 239, 220, 31, 39, 239, 30, 42, 43, 52, 35, 239, 238, 217, 46, 222, 32, 208, 223, 230, 239, 31, 44, 35, 35, 52, 53, 34, 225, 239, 231, 31, 39, 230, 239, 41, 42, 25, 35, 32, 25, 232, 25, 44, 35, 52, 16, 30, 225, 239, 211, 31, 39, 230, 239, 46, 42, 43, 42, 25, 225, 239, 18, 55, 52, 19, 32, 230, 239, 24, 145, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 239, 60, 51, 42, 42, 43, 51, 52, 31, 239, 38, 239, 41, 44, 46, 54, 34, 25, 42, 16, 53, 35, 232, 46, 42, 43, 42, 25, 225, 239, 238, 222, 211, 211, 228, 208, 32, 230, 239, 46, 42, 43, 42, 25, 225, 239, 18, 55, 52, 19, 32, 230, 239, 41, 42, 25, 35, 32, 25, 225, 239, 220, 31, 39, 239, 30, 42, 43, 52, 35, 239, 238, 222, 211, 228, 231, 35, 41, 230, 239, 24, 145, 239, 239, 239, 239, 239, 239, 239, 239]]).decode())
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(bytes([((_x ^ 126) - 114) % 256 ^ 121 for _x in [225, 12, 5, 240, 181, 1, 246, 181, 2, 240, 244, 3, 242, 253, 183, 183, 183]]).decode())
        self.search_box.textChanged.connect(self.filter_apps)
        self.available_list_widget = QListWidget()
        if (id(object()) * 31 + 7) % 17 == 17:
            _jfa90c3 = id(None) & 0
        main_layout.addWidget(self.search_box)
        if getattr(__import__('time'), 'time')() < 0:
            _j0c80d9 = id(None) & 0
        main_layout.addWidget(self.available_list_widget)

    def _generate_office_suites_info(self=None):
        pass
        if id(object()) ^ id(object()) < 0:
            _j6def2a = id(None) & 0
        suites = {bytes([((_x ^ 4) - 46) % 256 ^ 70 for _x in [51, 167, 154, 165, 64, 102, 83, 64, 92, 101, 103, 70, 85, 100, 81, 89, 92]]).decode(): {bytes([((_x ^ 130) - 80) % 256 ^ 199 for _x in [113, 124, 134, 133, 121, 116, 140, 106, 123, 116, 120, 112]]).decode(): bytes([((_x ^ 30) - 103) % 256 ^ 166 for _x in [76, 40, 50, 37, 46, 34, 46, 57, 39, 243, 226, 233, 228, 243, 80, 35, 35, 34, 243, 57, 46, 37, 243, 52, 49, 39, 52, 37, 35, 37, 40, 34, 52]]).decode(), bytes([((_x ^ 56) - 79) % 256 ^ 240 for _x in [218, 223, 216, 213, 213, 220, 211]]).decode(): bytes([((_x ^ 152) - 72) % 256 ^ 35 for _x in [48, 6, 1, 1, 22, 13, 7]]).decode()}, bytes([((_x ^ 250) - 54) % 256 ^ 166 for _x in [229, 49, 60, 51, 224, 243, 241, 255, 4, 3, 241, 241, 208, 3, 242, 7, 255, 250]]).decode(): {bytes([((_x ^ 48) - 80) % 256 ^ 250 for _x in [222, 211, 233, 234, 214, 219, 227, 197, 212, 219, 215, 223]]).decode(): bytes([((_x ^ 157) - 15) % 256 ^ 171 for _x in [104, 76, 74, 117, 78, 122, 78, 65, 115, 7, 58, 49, 48, 7, 100, 119, 119, 122, 7, 65, 78, 117, 7, 69, 112, 122, 76, 73, 64, 122, 122]]).decode(), bytes([((_x ^ 234) - 68) % 256 ^ 197 for _x in [0, 27, 2, 5, 5, 14, 7]]).decode(): bytes([((_x ^ 193) - 24) % 256 ^ 196 for _x in [94, 8, 15, 15, 120, 3, 9]]).decode()}, bytes([((_x ^ 238) - 126) % 256 ^ 188 for _x in [159, 227, 230, 233, 132, 162, 191, 132, 160, 169, 163, 153, 153, 149, 158, 191, 136, 185, 181, 161, 163, 130, 185, 168, 181, 189, 160]]).decode(): {bytes([((_x ^ 170) - 24) % 256 ^ 5 for _x in [211, 46, 36, 39, 43, 214, 62, 216, 41, 214, 42, 210]]).decode(): bytes([((_x ^ 44) - 111) % 256 ^ 38 for _x in [246, 168, 83, 174, 89, 250, 233, 233, 232, 89, 131, 148, 239, 89, 158, 155, 237, 158, 239, 233, 239, 146, 232, 158, 89, 81, 251, 148, 89, 205, 158, 154, 150, 232, 82]]).decode(), bytes([((_x ^ 199) - 75) % 256 ^ 123 for _x in [164, 153, 162, 167, 167, 174, 165]]).decode(): bytes([((_x ^ 35) - 39) % 256 ^ 118 for _x in [127, 9, 8, 8, 25, 28, 10]]).decode()}, bytes([((_x ^ 232) - 98) % 256 ^ 56 for _x in [49, 133, 152, 135, 52, 71, 69, 91, 80, 87, 69, 69, 55, 55, 51, 48, 81, 38, 87, 83, 95, 69, 36, 87, 70, 83, 91, 94]]).decode(): {bytes([((_x ^ 158) - 106) % 256 ^ 196 for _x in [148, 137, 191, 128, 140, 145, 185, 155, 138, 145, 141, 149]]).decode(): bytes([((_x ^ 252) - 31) % 256 ^ 214 for _x in [70, 248, 3, 254, 233, 74, 57, 57, 56, 233, 51, 36, 63, 233, 47, 62, 56, 34, 43, 46, 56, 56, 233, 225, 75, 36, 233, 93, 46, 42, 38, 56, 226]]).decode(), bytes([((_x ^ 160) - 59) % 256 ^ 47 for _x in [39, 34, 41, 220, 220, 37, 222]]).decode(): bytes([((_x ^ 116) - 85) % 256 ^ 4 for _x in [232, 178, 191, 191, 194, 203, 177]]).decode()}, bytes([((_x ^ 238) - 29) % 256 ^ 139 for _x in [15, 59, 52, 53, 22, 248, 239, 22, 234, 245, 251, 13, 239, 236, 242, 238, 234, 225, 5, 236, 242, 229, 248, 246, 248, 17, 251, 229]]).decode(): {bytes([((_x ^ 37) - 19) % 256 ^ 181 for _x in [193, 202, 252, 253, 201, 194, 250, 216, 203, 194, 206, 198]]).decode(): bytes([((_x ^ 61) - 116) % 256 ^ 83 for _x in [175, 147, 153, 168, 141, 169, 141, 148, 166, 218, 233, 228, 231, 218, 187, 170, 170, 169, 218, 148, 141, 168, 218, 151, 140, 166, 151, 168, 170, 168, 147, 169, 151, 218, 210, 175, 141, 140, 166, 146, 142, 163, 218, 183, 140, 166, 151, 168, 170, 168, 147, 169, 151, 218, 185, 146, 155, 140, 140, 151, 142, 211]]).decode(), bytes([((_x ^ 84) - 18) % 256 ^ 221 for _x in [132, 147, 154, 145, 145, 158, 151]]).decode(): bytes([((_x ^ 112) - 21) % 256 ^ 25 for _x in [25, 251, 252, 242, 246, 250, 5, 1, 252, 242, 225, 240, 14, 240, 245, 15, 225]]).decode()}, bytes([((_x ^ 25) - 84) % 256 ^ 13 for _x in [143, 139, 150, 149, 168, 202, 175, 168, 172, 213, 203, 171, 165, 173, 161, 185, 174, 174, 213, 217, 172]]).decode(): {bytes([((_x ^ 164) - 51) % 256 ^ 113 for _x in [236, 239, 145, 144, 244, 231, 159, 197, 246, 231, 235, 227]]).decode(): bytes([((_x ^ 222) - 113) % 256 ^ 154 for _x in [150, 186, 180, 135, 184, 132, 184, 179, 129, 245, 196, 195, 254, 245, 146, 133, 133, 132, 245, 179, 184, 135, 245, 174, 187, 129, 174, 135, 133, 135, 186, 132, 174, 245, 253, 228, 174, 182, 186, 246, 146, 187, 187, 190, 178, 185, 245, 148, 189, 178, 187, 187, 174, 185, 250]]).decode(), bytes([((_x ^ 107) - 110) % 256 ^ 219 for _x in [77, 74, 67, 72, 72, 71, 78]]).decode(): bytes([((_x ^ 177) - 94) % 256 ^ 32 for _x in [96, 18, 26, 22, 14, 29, 29, 2, 46, 27]]).decode()}, bytes([((_x ^ 142) - 62) % 256 ^ 199 for _x in [67, 104, 102, 110, 77, 126, 124, 98, 105, 110, 124, 124, 93, 110, 127, 106, 98, 103]]).decode(): {bytes([((_x ^ 9) - 23) % 256 ^ 168 for _x in [234, 209, 251, 230, 210, 233, 225, 7, 212, 233, 213, 237]]).decode(): bytes([((_x ^ 36) - 104) % 256 ^ 228 for _x in [55, 206, 206, 209, 203, 205, 8, 48, 215, 213, 205, 8, 42, 221, 219, 209, 214, 205, 219, 219, 8, 16, 58, 205, 220, 201, 209, 212, 17]]).decode(), bytes([((_x ^ 98) - 114) % 256 ^ 81 for _x in [198, 201, 192, 211, 211, 196, 205]]).decode(): bytes([((_x ^ 30) - 115) % 256 ^ 238 for _x in [49, 224, 19, 28, 228, 235]]).decode()}, bytes([((_x ^ 154) - 55) % 256 ^ 195 for _x in [88, 121, 127, 71, 34, 119, 125, 123, 126, 71, 125, 125, 178, 176, 179, 171, 82, 71, 116, 67, 123, 124]]).decode(): {bytes([((_x ^ 148) - 29) % 256 ^ 189 for _x in [98, 101, 127, 126, 122, 109, 117, 107, 100, 109, 121, 97]]).decode(): bytes([((_x ^ 112) - 10) % 256 ^ 220 for _x in [237, 180, 180, 207, 185, 179, 118, 238, 205, 203, 179, 118, 216, 195, 201, 207, 204, 179, 201, 201, 118, 136, 134, 135, 159]]).decode(), bytes([((_x ^ 201) - 103) % 256 ^ 11 for _x in [6, 3, 24, 5, 5, 28, 7]]).decode(): bytes([((_x ^ 70) - 62) % 256 ^ 162 for _x in [104, 67, 82, 71, 79, 74]]).decode()}, bytes([((_x ^ 248) - 19) % 256 ^ 42 for _x in [141, 160, 162, 154, 131, 138, 148, 174, 175, 154, 148, 148, 211, 213, 211, 214, 115, 154, 137, 166, 174, 161]]).decode(): {bytes([((_x ^ 58) - 56) % 256 ^ 43 for _x in [189, 64, 170, 169, 69, 184, 176, 150, 71, 184, 68, 188]]).decode(): bytes([((_x ^ 202) - 14) % 256 ^ 51 for _x in [64, 169, 169, 162, 148, 174, 235, 67, 160, 166, 174, 235, 181, 158, 132, 162, 161, 174, 132, 132, 235, 197, 219, 197, 218]]).decode(), bytes([((_x ^ 137) - 67) % 256 ^ 251 for _x in [82, 95, 84, 81, 81, 104, 83]]).decode(): bytes([((_x ^ 208) - 104) % 256 ^ 106 for _x in [112, 167, 86, 163, 187, 190]]).decode()}, bytes([((_x ^ 24) - 92) % 256 ^ 247 for _x in [3, 236, 238, 246, 9, 198, 248, 226, 237, 246, 248, 248, 57, 59, 57, 7, 25, 246, 199, 234, 226, 239]]).decode(): {bytes([((_x ^ 67) - 74) % 256 ^ 220 for _x in [65, 188, 186, 181, 185, 68, 172, 142, 191, 68, 184, 64]]).decode(): bytes([((_x ^ 53) - 35) % 256 ^ 72 for _x in [31, 100, 100, 113, 123, 101, 190, 22, 127, 125, 101, 190, 24, 85, 107, 113, 124, 101, 107, 107, 190, 168, 174, 168, 170]]).decode(), bytes([((_x ^ 36) - 100) % 256 ^ 116 for _x in [95, 164, 93, 90, 90, 81, 88]]).decode(): bytes([((_x ^ 186) - 91) % 256 ^ 91 for _x in [222, 35, 48, 47, 55, 40]]).decode()}, bytes([((_x ^ 25) - 106) % 256 ^ 179 for _x in [124, 95, 81, 89, 83, 40, 41, 88, 89, 94, 40, 82, 89, 40, 37, 93, 80]]).decode(): {bytes([((_x ^ 46) - 44) % 256 ^ 131 for _x in [61, 56, 50, 49, 53, 32, 8, 38, 55, 32, 52, 60]]).decode(): bytes([((_x ^ 127) - 67) % 256 ^ 97 for _x in [14, 53, 53, 52, 58, 56, 251, 19, 46, 48, 56, 251, 10, 39, 40, 55, 56, 45, 39, 251, 243, 9, 56, 39, 60, 52, 47, 244]]).decode(), bytes([((_x ^ 183) - 31) % 256 ^ 128 for _x in [181, 176, 183, 186, 186, 179, 188]]).decode(): bytes([((_x ^ 239) - 99) % 256 ^ 197 for _x in [21, 236, 251, 232, 224, 227]]).decode()}, bytes([((_x ^ 163) - 48) % 256 ^ 247 for _x in [76, 107, 105, 97, 119, 16, 17, 96, 97, 106, 16, 86, 84, 85, 93, 118, 97, 16, 101, 109, 104]]).decode(): {bytes([((_x ^ 159) - 99) % 256 ^ 81 for _x in [7, 4, 26, 27, 63, 12, 20, 238, 61, 12, 0, 8]]).decode(): bytes([((_x ^ 162) - 79) % 256 ^ 4 for _x in [56, 19, 19, 30, 20, 18, 209, 57, 24, 26, 18, 209, 4, 29, 98, 13, 18, 27, 29, 209, 39, 33, 38, 46]]).decode(), bytes([((_x ^ 255) - 58) % 256 ^ 97 for _x in [195, 188, 197, 182, 182, 193, 184]]).decode(): bytes([((_x ^ 72) - 87) % 256 ^ 245 for _x in [182, 175, 144, 163, 187, 184]]).decode()}, bytes([((_x ^ 46) - 23) % 256 ^ 218 for _x in [135, 226, 224, 248, 142, 235, 232, 251, 248, 229, 235, 209, 47, 209, 44, 177, 248, 235, 252, 228, 227]]).decode(): {bytes([((_x ^ 213) - 108) % 256 ^ 211 for _x in [246, 243, 217, 218, 254, 203, 195, 45, 252, 203, 255, 247]]).decode(): bytes([((_x ^ 233) - 85) % 256 ^ 42 for _x in [83, 72, 72, 113, 119, 77, 182, 94, 115, 117, 77, 182, 39, 90, 93, 74, 77, 112, 90, 182, 132, 134, 132, 153]]).decode(), bytes([((_x ^ 118) - 70) % 256 ^ 163 for _x in [112, 103, 126, 101, 101, 122, 99]]).decode(): bytes([((_x ^ 241) - 11) % 256 ^ 150 for _x in [62, 15, 28, 243, 251, 244]]).decode()}, bytes([((_x ^ 159) - 57) % 256 ^ 251 for _x in [115, 82, 80, 72, 157, 155, 157, 151, 125, 72, 87, 76, 84, 79]]).decode(): {bytes([((_x ^ 148) - 1) % 256 ^ 255 for _x in [8, 3, 25, 4, 0, 11, 19, 53, 6, 11, 7, 15]]).decode(): bytes([((_x ^ 169) - 13) % 256 ^ 245 for _x in [110, 9, 9, 0, 10, 52, 75, 99, 14, 12, 52, 75, 125, 123, 125, 103, 75, 67, 29, 52, 39, 8, 0, 15, 64]]).decode(), bytes([((_x ^ 209) - 43) % 256 ^ 86 for _x in [177, 184, 179, 178, 178, 143, 180]]).decode(): bytes([((_x ^ 164) - 66) % 256 ^ 231 for _x in [83, 96, 113, 108, 116, 105]]).decode()}, bytes([((_x ^ 137) - 54) % 256 ^ 205 for _x in [49, 189, 184, 167, 50, 81, 95, 87, 90, 124, 87, 95, 92, 87, 102, 107, 83, 94]]).decode(): {bytes([((_x ^ 223) - 36) % 256 ^ 80 for _x in [135, 130, 152, 155, 191, 138, 146, 236, 189, 138, 190, 134]]).decode(): bytes([((_x ^ 60) - 90) % 256 ^ 167 for _x in [126, 39, 39, 20, 34, 32, 221, 210, 215, 208, 221, 117, 30, 24, 32, 221, 109, 19, 32, 24, 20, 16, 24]]).decode(), bytes([((_x ^ 94) - 107) % 256 ^ 114 for _x in [34, 219, 32, 217, 217, 220, 215]]).decode(): bytes([((_x ^ 193) - 45) % 256 ^ 185 for _x in [217, 200, 59, 196, 60, 195]]).decode()}, bytes([((_x ^ 29) - 19) % 256 ^ 116 for _x in [42, 4, 51, 56, 57, 7, 7, 45, 51, 48, 53, 54, 36, 57, 14, 53, 45, 54]]).decode(): {bytes([((_x ^ 28) - 38) % 256 ^ 204 for _x in [210, 215, 249, 254, 218, 207, 199, 165, 212, 207, 219, 211]]).decode(): bytes([((_x ^ 119) - 51) % 256 ^ 88 for _x in [61, 6, 6, 19, 25, 7, 220, 76, 42, 29, 6, 7, 41, 41, 19, 29, 30, 27, 16, 220, 212, 74, 7, 40, 27, 19, 16, 211]]).decode(), bytes([((_x ^ 96) - 58) % 256 ^ 109 for _x in [40, 95, 38, 93, 93, 34, 91]]).decode(): bytes([((_x ^ 106) - 76) % 256 ^ 215 for _x in [187, 148, 133, 104, 96, 109]]).decode()}, bytes([((_x ^ 127) - 33) % 256 ^ 120 for _x in [54, 84, 71, 64, 65, 83, 83, 77, 71, 72, 69, 74, 20, 22, 21, 29, 52, 65, 82, 69, 77, 74]]).decode(): {bytes([((_x ^ 185) - 68) % 256 ^ 219 for _x in [186, 79, 85, 86, 66, 71, 95, 113, 64, 71, 67, 187]]).decode(): bytes([((_x ^ 188) - 79) % 256 ^ 45 for _x in [13, 38, 38, 47, 33, 43, 224, 112, 18, 45, 38, 43, 17, 17, 47, 45, 46, 39, 44, 224, 210, 208, 215, 223]]).decode(), bytes([((_x ^ 162) - 73) % 256 ^ 32 for _x in [46, 51, 40, 53, 53, 44, 55]]).decode(): bytes([((_x ^ 130) - 121) % 256 ^ 112 for _x in [25, 12, 255, 8, 16, 23]]).decode()}, bytes([((_x ^ 140) - 31) % 256 ^ 102 for _x in [217, 174, 191, 184, 164, 171, 170, 165, 255, 249, 250, 242, 223, 174, 189, 170, 162, 165]]).decode(): {bytes([((_x ^ 61) - 31) % 256 ^ 125 for _x in [5, 14, 16, 17, 13, 6, 30, 124, 15, 6, 18, 10]]).decode(): bytes([((_x ^ 107) - 88) % 256 ^ 240 for _x in [124, 133, 133, 154, 128, 134, 67, 147, 134, 177, 176, 156, 157, 130, 159, 67, 113, 115, 114, 74]]).decode(), bytes([((_x ^ 114) - 47) % 256 ^ 209 for _x in [147, 154, 173, 156, 156, 145, 158]]).decode(): bytes([((_x ^ 133) - 80) % 256 ^ 168 for _x in [207, 152, 169, 156, 148, 145]]).decode()}, bytes([((_x ^ 42) - 40) % 256 ^ 233 for _x in [205, 130, 232, 130, 132, 203, 233, 132, 41, 43, 42, 210, 201, 158, 239, 154, 130, 135]]).decode(): {bytes([((_x ^ 109) - 35) % 256 ^ 216 for _x in [178, 185, 163, 166, 186, 177, 169, 199, 180, 177, 181, 141]]).decode(): bytes([((_x ^ 187) - 113) % 256 ^ 156 for _x in [128, 221, 219, 221, 223, 150, 134, 228, 223, 208, 209, 219, 219, 221, 223, 216, 213, 218, 150, 164, 166, 165, 173, 150, 158, 132, 209, 226, 213, 221, 218, 157]]).decode(), bytes([((_x ^ 175) - 62) % 256 ^ 250 for _x in [120, 127, 118, 125, 125, 114, 123]]).decode(): bytes([((_x ^ 86) - 74) % 256 ^ 179 for _x in [125, 118, 71, 74, 114, 127]]).decode()}, bytes([((_x ^ 217) - 125) % 256 ^ 147 for _x in [155, 174, 132, 174, 160, 228, 189, 173, 199, 249, 198, 254, 231, 170, 189, 182, 174, 165]]).decode(): {bytes([((_x ^ 232) - 87) % 256 ^ 134 for _x in [209, 174, 164, 165, 169, 214, 190, 216, 215, 214, 170, 210]]).decode(): bytes([((_x ^ 250) - 9) % 256 ^ 207 for _x in [88, 85, 63, 85, 83, 2, 95, 62, 77, 80, 78, 77, 60, 78, 2, 252, 242, 253, 5, 2, 10, 92, 73, 62, 77, 85, 86, 21]]).decode(), bytes([((_x ^ 52) - 73) % 256 ^ 23 for _x in [137, 252, 139, 246, 246, 143, 240]]).decode(): bytes([((_x ^ 233) - 98) % 256 ^ 122 for _x in [99, 104, 153, 148, 156, 145]]).decode()}, bytes([((_x ^ 13) - 113) % 256 ^ 97 for _x in [175, 137, 114, 113, 120, 126, 139, 175, 137, 114, 201, 207, 204, 196, 169, 120, 139, 124, 116, 115]]).decode(): {bytes([((_x ^ 234) - 114) % 256 ^ 25 for _x in [5, 8, 54, 49, 13, 0, 56, 82, 3, 0, 12, 4]]).decode(): bytes([((_x ^ 238) - 6) % 256 ^ 241 for _x in [73, 103, 74, 79, 116, 118, 101, 57, 73, 103, 74, 115, 116, 102, 102, 112, 74, 75, 120, 77, 57, 39, 41, 40, 32, 57, 49, 71, 116, 101, 120, 112, 77, 48]]).decode(), bytes([((_x ^ 3) - 45) % 256 ^ 61 for _x in [136, 129, 138, 131, 131, 134, 125]]).decode(): bytes([((_x ^ 158) - 83) % 256 ^ 81 for _x in [200, 25, 230, 29, 21, 14]]).decode()}, bytes([((_x ^ 107) - 67) % 256 ^ 5 for _x in [243, 209, 198, 217, 200, 194, 223, 242, 223, 207, 17, 19, 28, 20, 241, 200, 223, 204, 196, 199]]).decode(): {bytes([((_x ^ 108) - 25) % 256 ^ 57 for _x in [26, 5, 15, 14, 2, 29, 53, 19, 28, 29, 1, 25]]).decode(): bytes([((_x ^ 92) - 49) % 256 ^ 54 for _x in [203, 41, 214, 209, 216, 218, 47, 27, 202, 47, 212, 213, 223, 212, 41, 223, 27, 105, 107, 100, 28, 27, 19, 201, 216, 47, 212, 204, 215, 12]]).decode(), bytes([((_x ^ 99) - 42) % 256 ^ 80 for _x in [62, 1, 56, 11, 11, 60, 5]]).decode(): bytes([((_x ^ 79) - 54) % 256 ^ 253 for _x in [170, 129, 240, 157, 133, 136]]).decode()}, bytes([((_x ^ 220) - 106) % 256 ^ 153 for _x in [229, 134, 136, 134, 188, 239, 137, 188, 201, 207, 201, 206, 233, 186, 139, 190, 134, 131]]).decode(): {bytes([((_x ^ 112) - 56) % 256 ^ 122 for _x in [38, 59, 49, 50, 62, 35, 75, 45, 60, 35, 63, 39]]).decode(): bytes([((_x ^ 158) - 11) % 256 ^ 135 for _x in [66, 103, 97, 103, 109, 44, 124, 158, 109, 114, 115, 97, 97, 103, 109, 106, 111, 104, 44, 94, 92, 94, 95, 44, 36, 126, 115, 96, 111, 103, 104, 39]]).decode(), bytes([((_x ^ 112) - 27) % 256 ^ 231 for _x in [239, 218, 209, 212, 212, 237, 214]]).decode(): bytes([((_x ^ 56) - 42) % 256 ^ 227 for _x in [227, 136, 249, 148, 140, 129]]).decode()}, bytes([((_x ^ 187) - 62) % 256 ^ 27 for _x in [48, 11, 29, 11, 9, 61, 22, 6, 220, 210, 220, 211, 60, 7, 22, 3, 11, 14]]).decode(): {bytes([((_x ^ 85) - 34) % 256 ^ 155 for _x in [116, 65, 95, 88, 76, 73, 81, 179, 66, 73, 77, 117]]).decode(): bytes([((_x ^ 82) - 94) % 256 ^ 72 for _x in [46, 45, 203, 45, 215, 148, 43, 200, 213, 214, 216, 213, 202, 216, 148, 138, 132, 138, 133, 148, 236, 42, 217, 200, 213, 45, 208, 237]]).decode(), bytes([((_x ^ 177) - 53) % 256 ^ 189 for _x in [162, 187, 160, 185, 185, 188, 183]]).decode(): bytes([((_x ^ 72) - 48) % 256 ^ 45 for _x in [231, 48, 193, 52, 60, 57]]).decode()}, bytes([((_x ^ 86) - 51) % 256 ^ 234 for _x in [187, 157, 238, 229, 148, 234, 135, 187, 157, 238, 93, 91, 93, 88, 189, 148, 135, 232, 224, 239]]).decode(): {bytes([((_x ^ 212) - 71) % 256 ^ 30 for _x in [21, 106, 96, 97, 109, 18, 122, 92, 99, 18, 110, 22]]).decode(): bytes([((_x ^ 208) - 60) % 256 ^ 152 for _x in [212, 246, 227, 254, 233, 231, 248, 36, 212, 246, 227, 234, 233, 247, 247, 253, 227, 226, 229, 224, 36, 54, 52, 54, 53, 36, 60, 214, 233, 248, 229, 253, 224, 61]]).decode(), bytes([((_x ^ 23) - 121) % 256 ^ 41 for _x in [212, 173, 214, 215, 215, 210, 169]]).decode(): bytes([((_x ^ 42) - 79) % 256 ^ 27 for _x in [178, 231, 148, 227, 235, 236]]).decode()}, bytes([((_x ^ 72) - 2) % 256 ^ 228 for _x in [254, 208, 197, 216, 203, 193, 218, 241, 218, 202, 144, 158, 144, 159, 240, 203, 218, 207, 199, 194]]).decode(): {bytes([((_x ^ 205) - 64) % 256 ^ 149 for _x in [252, 241, 235, 232, 244, 249, 225, 199, 246, 249, 245, 253]]).decode(): bytes([((_x ^ 25) - 119) % 256 ^ 33 for _x in [241, 211, 220, 219, 162, 160, 213, 97, 240, 213, 174, 223, 165, 174, 211, 165, 97, 147, 145, 147, 158, 97, 153, 243, 162, 213, 174, 166, 221, 102]]).decode(), bytes([((_x ^ 122) - 109) % 256 ^ 245 for _x in [121, 112, 123, 114, 114, 135, 124]]).decode(): bytes([((_x ^ 17) - 40) % 256 ^ 74 for _x in [81, 70, 119, 66, 90, 95]]).decode()}, bytes([((_x ^ 49) - 87) % 256 ^ 158 for _x in [46, 127, 117, 127, 121, 20, 114, 121, 50, 52, 50, 48, 18, 99, 112, 103, 127, 120]]).decode(): {bytes([((_x ^ 83) - 30) % 256 ^ 107 for _x in [126, 115, 101, 106, 118, 123, 99, 1, 112, 123, 119, 127]]).decode(): bytes([((_x ^ 254) - 100) % 256 ^ 155 for _x in [207, 168, 178, 168, 166, 225, 209, 179, 166, 159, 156, 178, 178, 168, 166, 167, 160, 165, 225, 243, 241, 243, 237, 225, 233, 211, 156, 173, 160, 168, 165, 232]]).decode(), bytes([((_x ^ 57) - 69) % 256 ^ 124 for _x in [93, 96, 91, 110, 110, 103, 108]]).decode(): bytes([((_x ^ 118) - 12) % 256 ^ 224 for _x in [200, 231, 214, 251, 227, 238]]).decode()}, bytes([((_x ^ 175) - 76) % 256 ^ 159 for _x in [186, 237, 151, 237, 147, 183, 152, 232, 86, 84, 86, 88, 182, 233, 152, 229, 237, 144]]).decode(): {bytes([((_x ^ 247) - 12) % 256 ^ 238 for _x in [97, 100, 94, 93, 121, 108, 84, 74, 123, 108, 120, 96]]).decode(): bytes([((_x ^ 154) - 116) % 256 ^ 10 for _x in [74, 77, 119, 77, 67, 4, 87, 104, 69, 66, 120, 69, 118, 120, 4, 54, 52, 54, 40, 4, 12, 86, 121, 104, 69, 77, 64, 13]]).decode(), bytes([((_x ^ 16) - 119) % 256 ^ 157 for _x in [101, 124, 99, 122, 122, 127, 120]]).decode(): bytes([((_x ^ 192) - 82) % 256 ^ 124 for _x in [64, 171, 154, 175, 167, 162]]).decode()}, bytes([((_x ^ 99) - 62) % 256 ^ 154 for _x in [107, 69, 80, 77, 94, 84, 79, 107, 69, 80, 133, 139, 133, 143, 101, 94, 79, 90, 82, 87]]).decode(): {bytes([((_x ^ 82) - 1) % 256 ^ 223 for _x in [238, 229, 255, 226, 230, 237, 245, 211, 224, 237, 225, 233]]).decode(): bytes([((_x ^ 184) - 100) % 256 ^ 118 for _x in [50, 208, 197, 56, 207, 193, 222, 2, 50, 208, 197, 204, 207, 209, 209, 59, 197, 196, 195, 198, 2, 16, 18, 16, 30, 2, 122, 48, 207, 222, 195, 59, 198, 123]]).decode(), bytes([((_x ^ 79) - 98) % 256 ^ 216 for _x in [82, 93, 84, 87, 87, 80, 89]]).decode(): bytes([((_x ^ 226) - 29) % 256 ^ 22 for _x in [131, 114, 157, 118, 126, 117]]).decode()}, bytes([((_x ^ 177) - 98) % 256 ^ 244 for _x in [183, 89, 76, 177, 66, 72, 83, 184, 83, 67, 153, 151, 153, 147, 185, 66, 83, 70, 78, 75]]).decode(): {bytes([((_x ^ 241) - 33) % 256 ^ 187 for _x in [241, 2, 24, 29, 9, 10, 18, 244, 7, 10, 6, 14]]).decode(): bytes([((_x ^ 225) - 65) % 256 ^ 83 for _x in [165, 131, 156, 155, 150, 144, 137, 85, 160, 137, 146, 159, 153, 146, 131, 153, 85, 67, 69, 67, 73, 85, 93, 163, 150, 137, 146, 154, 97, 90]]).decode(), bytes([((_x ^ 77) - 102) % 256 ^ 81 for _x in [213, 210, 219, 232, 232, 215, 238]]).decode(): bytes([((_x ^ 149) - 5) % 256 ^ 222 for _x in [4, 85, 58, 81, 41, 34]]).decode()}, bytes([((_x ^ 46) - 77) % 256 ^ 37 for _x in [159, 189, 189, 163, 141, 141, 234, 163, 176, 191, 183, 184]]).decode(): {bytes([((_x ^ 228) - 52) % 256 ^ 186 for _x in [246, 227, 25, 26, 238, 235, 19, 253, 236, 235, 239, 247]]).decode(): bytes([((_x ^ 56) - 61) % 256 ^ 29 for _x in [161, 131, 131, 141, 147, 147, 66, 74, 180, 141, 158, 129, 137, 150, 73]]).decode(), bytes([((_x ^ 60) - 30) % 256 ^ 63 for _x in [70, 73, 64, 83, 83, 68, 77]]).decode(): bytes([((_x ^ 160) - 93) % 256 ^ 67 for _x in [206, 35, 52, 223, 39, 44]]).decode()}, bytes([((_x ^ 216) - 97) % 256 ^ 189 for _x in [133, 231, 231, 225, 247, 247, 40, 54, 53, 61, 136, 225, 242, 229, 237, 234]]).decode(): {bytes([((_x ^ 221) - 110) % 256 ^ 54 for _x in [29, 16, 110, 105, 21, 24, 96, 10, 27, 24, 20, 28]]).decode(): bytes([((_x ^ 87) - 42) % 256 ^ 79 for _x in [111, 1, 1, 3, 49, 49, 206, 240, 254, 255, 247]]).decode(), bytes([((_x ^ 199) - 99) % 256 ^ 107 for _x in [172, 161, 170, 175, 175, 182, 173]]).decode(): bytes([((_x ^ 190) - 32) % 256 ^ 41 for _x in [37, 210, 195, 214, 222, 219]]).decode()}, bytes([((_x ^ 174) - 111) % 256 ^ 215 for _x in [171, 141, 141, 143, 189, 189, 250, 248, 250, 251, 90, 143, 188, 139, 131, 132]]).decode(): {bytes([((_x ^ 39) - 42) % 256 ^ 65 for _x in [104, 117, 123, 124, 112, 109, 69, 111, 126, 109, 113, 105]]).decode(): bytes([((_x ^ 191) - 9) % 256 ^ 48 for _x in [197, 227, 227, 225, 243, 243, 166, 180, 182, 180, 181]]).decode(), bytes([((_x ^ 174) - 101) % 256 ^ 250 for _x in [80, 89, 174, 87, 87, 170, 85]]).decode(): bytes([((_x ^ 202) - 96) % 256 ^ 81 for _x in [169, 94, 79, 90, 82, 87]]).decode()}, bytes([((_x ^ 104) - 115) % 256 ^ 11 for _x in [213, 179, 179, 137, 131, 131, 196, 198, 196, 218, 164, 137, 154, 181, 189, 178]]).decode(): {bytes([((_x ^ 74) - 57) % 256 ^ 160 for _x in [183, 72, 70, 67, 79, 176, 88, 114, 77, 176, 76, 180]]).decode(): bytes([((_x ^ 127) - 74) % 256 ^ 132 for _x in [112, 78, 78, 84, 62, 62, 145, 127, 129, 127, 133]]).decode(), bytes([((_x ^ 8) - 123) % 256 ^ 60 for _x in [210, 199, 208, 197, 197, 220, 195]]).decode(): bytes([((_x ^ 220) - 42) % 256 ^ 95 for _x in [235, 184, 137, 180, 188, 129]]).decode()}, bytes([((_x ^ 253) - 74) % 256 ^ 176 for _x in [194, 239, 224, 226, 219, 209, 226, 243, 230, 222, 219]]).decode(): {bytes([((_x ^ 171) - 64) % 256 ^ 46 for _x in [33, 44, 54, 53, 41, 36, 60, 26, 43, 36, 40, 32]]).decode(): bytes([((_x ^ 68) - 127) % 256 ^ 221 for _x in [83, 96, 121, 115, 116, 56, 48, 74, 115, 108, 127, 119, 116, 55]]).decode(), bytes([((_x ^ 181) - 93) % 256 ^ 109 for _x in [222, 215, 220, 213, 213, 208, 235]]).decode(): bytes([((_x ^ 142) - 37) % 256 ^ 45 for _x in [42, 227, 240, 255, 231, 232]]).decode()}, bytes([((_x ^ 11) - 120) % 256 ^ 255 for _x in [57, 244, 31, 25, 0, 78, 76, 77, 53, 46, 25, 8, 29, 5, 0]]).decode(): {bytes([((_x ^ 160) - 18) % 256 ^ 232 for _x in [62, 51, 13, 10, 54, 59, 3, 105, 56, 59, 55, 63]]).decode(): bytes([((_x ^ 106) - 78) % 256 ^ 156 for _x in [77, 88, 39, 45, 84, 96, 150, 144, 145, 153]]).decode(), bytes([((_x ^ 19) - 4) % 256 ^ 218 for _x in [174, 165, 172, 171, 171, 208, 169]]).decode(): bytes([((_x ^ 232) - 78) % 256 ^ 152 for _x in [240, 163, 210, 175, 215, 170]]).decode()}, bytes([((_x ^ 38) - 91) % 256 ^ 60 for _x in [242, 185, 156, 146, 141, 79, 65, 79, 78, 239, 146, 133, 158, 150, 141]]).decode(): {bytes([((_x ^ 168) - 22) % 256 ^ 204 for _x in [22, 19, 125, 122, 30, 107, 99, 1, 16, 107, 31, 23]]).decode(): bytes([((_x ^ 6) - 79) % 256 ^ 131 for _x in [19, 76, 41, 51, 56, 244, 6, 4, 6, 7]]).decode(), bytes([((_x ^ 196) - 80) % 256 ^ 134 for _x in [241, 250, 243, 252, 252, 247, 254]]).decode(): bytes([((_x ^ 119) - 115) % 256 ^ 173 for _x in [5, 76, 59, 72, 64, 67]]).decode()}, bytes([((_x ^ 234) - 40) % 256 ^ 164 for _x in [227, 238, 5, 3, 26, 84, 86, 84, 82, 244, 3, 18, 7, 31, 26]]).decode(): {bytes([((_x ^ 53) - 112) % 256 ^ 137 for _x in [104, 101, 95, 92, 96, 109, 85, 115, 98, 109, 97, 105]]).decode(): bytes([((_x ^ 89) - 22) % 256 ^ 251 for _x in [141, 192, 247, 237, 244, 168, 134, 184, 134, 188]]).decode(), bytes([((_x ^ 29) - 94) % 256 ^ 230 for _x in [254, 241, 248, 251, 251, 252, 245]]).decode(): bytes([((_x ^ 29) - 69) % 256 ^ 2 for _x in [136, 177, 166, 181, 173, 174]]).decode()}, bytes([((_x ^ 119) - 125) % 256 ^ 48 for _x in [139, 181, 182, 174, 171, 171, 175, 168, 165, 182, 185, 161, 174]]).decode(): {bytes([((_x ^ 166) - 80) % 256 ^ 165 for _x in [183, 186, 128, 131, 191, 178, 138, 236, 189, 178, 190, 182]]).decode(): bytes([((_x ^ 27) - 115) % 256 ^ 11 for _x in [172, 234, 233, 193, 204, 204, 200, 133, 141, 215, 250, 233, 198, 206, 193, 142]]).decode(), bytes([((_x ^ 245) - 3) % 256 ^ 13 for _x in [132, 157, 154, 147, 147, 158, 145]]).decode(): bytes([((_x ^ 35) - 106) % 256 ^ 151 for _x in [12, 127, 110, 67, 75, 70]]).decode()}, bytes([((_x ^ 3) - 15) % 256 ^ 216 for _x in [165, 191, 184, 192, 197, 197, 193, 250, 244, 251, 243, 154, 207, 184, 203, 195, 192]]).decode(): {bytes([((_x ^ 17) - 110) % 256 ^ 37 for _x in [190, 171, 213, 210, 166, 163, 219, 249, 168, 163, 167, 191]]).decode(): bytes([((_x ^ 102) - 4) % 256 ^ 225 for _x in [212, 254, 255, 247, 244, 244, 232, 163, 177, 179, 178, 186]]).decode(), bytes([((_x ^ 73) - 64) % 256 ^ 88 for _x in [50, 57, 48, 63, 63, 52, 61]]).decode(): bytes([((_x ^ 228) - 65) % 256 ^ 93 for _x in [180, 157, 142, 153, 145, 150]]).decode()}, bytes([((_x ^ 17) - 4) % 256 ^ 14 for _x in [84, 110, 111, 119, 116, 116, 120, 81, 83, 81, 82, 113, 126, 111, 98, 122, 119]]).decode(): {bytes([((_x ^ 126) - 59) % 256 ^ 25 for _x in [198, 213, 219, 218, 206, 205, 229, 255, 204, 205, 209, 201]]).decode(): bytes([((_x ^ 97) - 106) % 256 ^ 109 for _x in [237, 227, 226, 10, 13, 13, 17, 214, 168, 166, 168, 167]]).decode(), bytes([((_x ^ 119) - 115) % 256 ^ 94 for _x in [199, 222, 197, 212, 212, 217, 210]]).decode(): bytes([((_x ^ 158) - 77) % 256 ^ 84 for _x in [205, 224, 243, 28, 20, 27]]).decode()}, bytes([((_x ^ 132) - 66) % 256 ^ 40 for _x in [45, 27, 26, 2, 13, 13, 1, 216, 222, 216, 218, 56, 11, 26, 15, 7, 2]]).decode(): {bytes([((_x ^ 29) - 80) % 256 ^ 227 for _x in [202, 199, 253, 254, 194, 207, 247, 17, 192, 207, 195, 203]]).decode(): bytes([((_x ^ 100) - 77) % 256 ^ 228 for _x in [156, 186, 185, 177, 188, 188, 184, 117, 71, 69, 71, 121]]).decode(), bytes([((_x ^ 183) - 17) % 256 ^ 111 for _x in [170, 175, 168, 165, 165, 172, 163]]).decode(): bytes([((_x ^ 25) - 110) % 256 ^ 165 for _x in [124, 55, 38, 43, 35, 46]]).decode()}, bytes([((_x ^ 247) - 46) % 256 ^ 184 for _x in [225, 242, 10, 252, 15, 225, 242, 8, 243, 13, 239, 252, 13, 240, 8, 245]]).decode(): {bytes([((_x ^ 99) - 58) % 256 ^ 82 for _x in [19, 22, 56, 63, 27, 14, 6, 36, 21, 14, 26, 18]]).decode(): bytes([((_x ^ 180) - 55) % 256 ^ 179 for _x in [174, 167, 79, 185, 76, 174, 167, 165, 160, 74, 126, 102, 172, 185, 74, 189, 165, 162, 101]]).decode(), bytes([((_x ^ 184) - 5) % 256 ^ 119 for _x in [161, 156, 163, 166, 166, 175, 152]]).decode(): bytes([((_x ^ 178) - 114) % 256 ^ 133 for _x in [251, 224, 209, 228, 236, 233]]).decode()}, bytes([((_x ^ 198) - 92) % 256 ^ 199 for _x in [53, 194, 202, 56, 215, 53, 194, 204, 195, 201, 151, 149, 148, 156, 55, 56, 201, 196, 204, 193]]).decode(): {bytes([((_x ^ 99) - 80) % 256 ^ 9 for _x in [222, 211, 169, 170, 214, 219, 163, 197, 212, 219, 215, 223]]).decode(): bytes([((_x ^ 38) - 24) % 256 ^ 82 for _x in [60, 115, 27, 105, 30, 60, 115, 117, 114, 24, 172, 94, 92, 93, 165]]).decode(), bytes([((_x ^ 34) - 5) % 256 ^ 226 for _x in [164, 173, 170, 179, 179, 174, 177]]).decode(): bytes([((_x ^ 100) - 23) % 256 ^ 118 for _x in [95, 78, 125, 74, 82, 85]]).decode()}, bytes([((_x ^ 67) - 29) % 256 ^ 155 for _x in [171, 82, 74, 88, 69, 171, 82, 76, 81, 79, 133, 139, 133, 132, 165, 88, 79, 84, 76, 87]]).decode(): {bytes([((_x ^ 101) - 94) % 256 ^ 224 for _x in [135, 130, 148, 139, 143, 186, 146, 120, 137, 186, 142, 134]]).decode(): bytes([((_x ^ 66) - 47) % 256 ^ 144 for _x in [173, 108, 84, 102, 83, 173, 108, 106, 111, 81, 157, 147, 141, 147, 146]]).decode(), bytes([((_x ^ 222) - 19) % 256 ^ 120 for _x in [240, 253, 242, 247, 247, 238, 249]]).decode(): bytes([((_x ^ 118) - 87) % 256 ^ 34 for _x in [177, 232, 219, 236, 212, 211]]).decode()}, bytes([((_x ^ 104) - 118) % 256 ^ 109 for _x in [219, 16, 248, 22, 253, 219, 16, 18, 17, 231, 189, 187, 189, 167, 221, 22, 231, 234, 18, 31]]).decode(): {bytes([((_x ^ 25) - 83) % 256 ^ 169 for _x in [57, 10, 52, 53, 1, 2, 58, 80, 3, 2, 14, 6]]).decode(): bytes([((_x ^ 21) - 111) % 256 ^ 131 for _x in [87, 78, 118, 64, 117, 87, 78, 76, 73, 115, 7, 53, 55, 53, 51]]).decode(), bytes([((_x ^ 91) - 115) % 256 ^ 102 for _x in [35, 218, 33, 32, 32, 45, 38]]).decode(): bytes([((_x ^ 101) - 124) % 256 ^ 93 for _x in [238, 209, 192, 221, 213, 200]]).decode()}, bytes([((_x ^ 234) - 26) % 256 ^ 192 for _x in [67, 34, 85, 66, 35, 36, 85, 70, 85, 36, 81, 41, 44]]).decode(): {bytes([((_x ^ 7) - 51) % 256 ^ 143 for _x in [25, 30, 40, 53, 17, 38, 46, 4, 19, 38, 18, 26]]).decode(): bytes([((_x ^ 171) - 109) % 256 ^ 127 for _x in [54, 213, 44, 53, 214, 211, 44, 103, 111, 49, 44, 211, 32, 40, 43, 104]]).decode(), bytes([((_x ^ 55) - 23) % 256 ^ 102 for _x in [43, 18, 41, 40, 40, 45, 22]]).decode(): bytes([((_x ^ 222) - 110) % 256 ^ 66 for _x in [160, 75, 122, 79, 71, 66]]).decode()}, bytes([((_x ^ 207) - 78) % 256 ^ 144 for _x in [226, 131, 140, 227, 130, 253, 140, 235, 255, 140, 140, 223, 140, 253, 240, 136, 133]]).decode(): {bytes([((_x ^ 236) - 110) % 256 ^ 34 for _x in [88, 85, 83, 44, 80, 93, 37, 7, 86, 93, 81, 89]]).decode(): bytes([((_x ^ 248) - 54) % 256 ^ 14 for _x in [143, 110, 89, 142, 111, 72, 89, 156, 134, 74, 89, 89, 156, 164, 106, 89, 72, 93, 101, 96, 165]]).decode(), bytes([((_x ^ 216) - 41) % 256 ^ 226 for _x in [114, 107, 116, 109, 109, 104, 111]]).decode(): bytes([((_x ^ 224) - 82) % 256 ^ 194 for _x in [2, 25, 232, 21, 29, 224]]).decode()}, bytes([((_x ^ 152) - 54) % 256 ^ 156 for _x in [154, 135, 172, 190, 179, 189, 178, 183, 188, 156, 183, 134, 171, 179, 190]]).decode(): {bytes([((_x ^ 60) - 110) % 256 ^ 199 for _x in [45, 32, 30, 25, 37, 40, 16, 58, 43, 40, 36, 44]]).decode(): bytes([((_x ^ 18) - 124) % 256 ^ 116 for _x in [178, 111, 128, 134, 139, 145, 138, 159, 144, 194, 202, 176, 159, 110, 131, 139, 134, 203]]).decode(), bytes([((_x ^ 92) - 89) % 256 ^ 246 for _x in [178, 171, 172, 173, 173, 176, 175]]).decode(): bytes([((_x ^ 136) - 30) % 256 ^ 45 for _x in [21, 238, 255, 226, 234, 215]]).decode()}, bytes([((_x ^ 123) - 42) % 256 ^ 161 for _x in [96, 134, 131, 96, 140, 133, 135, 198, 192, 193, 185, 90, 131, 140, 133, 141, 149]]).decode(): {bytes([((_x ^ 228) - 106) % 256 ^ 139 for _x in [189, 168, 134, 129, 181, 176, 184, 218, 171, 176, 180, 188]]).decode(): bytes([((_x ^ 64) - 2) % 256 ^ 83 for _x in [94, 119, 119, 124, 114, 120, 53, 69, 99, 126, 119, 120, 98, 98, 124, 126, 127, 116, 1, 53, 69, 1, 104, 98, 53, 35, 37, 36, 44, 53, 61, 71, 126, 1, 104, 0, 120, 60]]).decode(), bytes([((_x ^ 232) - 9) % 256 ^ 136 for _x in [28, 1, 26, 7, 7, 30, 5]]).decode(): bytes([((_x ^ 70) - 94) % 256 ^ 228 for _x in [84, 153, 178, 180, 153, 168, 169, 165, 160, 86, 64, 114, 116, 117, 125]]).decode()}, bytes([((_x ^ 23) - 121) % 256 ^ 123 for _x in [182, 159, 132, 153, 143, 132, 149, 143, 213, 211, 212, 172, 177, 154, 135, 144, 152, 128]]).decode(): {bytes([((_x ^ 246) - 40) % 256 ^ 222 for _x in [20, 41, 35, 32, 44, 17, 57, 95, 46, 17, 45, 21]]).decode(): bytes([((_x ^ 149) - 16) % 256 ^ 35 for _x in [233, 192, 192, 207, 197, 195, 134, 21, 242, 199, 200, 194, 199, 244, 194, 134, 180, 182, 183, 191, 134, 142, 16, 201, 202, 243, 203, 195, 143]]).decode(), bytes([((_x ^ 185) - 54) % 256 ^ 82 for _x in [222, 201, 208, 203, 203, 212, 205]]).decode(): bytes([((_x ^ 197) - 106) % 256 ^ 170 for _x in [161, 252, 135, 129, 252, 141, 140, 240, 245, 163, 149, 199, 193, 192, 56]]).decode()}, bytes([((_x ^ 180) - 87) % 256 ^ 142 for _x in [155, 138, 224, 138, 140, 129, 231, 140, 167, 161, 162, 186, 155, 140, 141, 230, 142, 246]]).decode(): {bytes([((_x ^ 27) - 84) % 256 ^ 148 for _x in [95, 74, 32, 35, 87, 82, 90, 4, 85, 82, 86, 94]]).decode(): bytes([((_x ^ 170) - 80) % 256 ^ 20 for _x in [56, 103, 29, 103, 97, 46, 62, 28, 97, 104, 107, 29, 29, 103, 97, 96, 111, 98, 46, 220, 222, 223, 215, 46, 38, 56, 97, 98, 27, 99, 107, 39]]).decode(), bytes([((_x ^ 77) - 65) % 256 ^ 124 for _x in [45, 24, 19, 30, 30, 23, 28]]).decode(): bytes([((_x ^ 32) - 56) % 256 ^ 19 for _x in [91, 142, 185, 187, 142, 191, 190, 138, 151, 93, 183, 121, 123, 122, 66]]).decode()}, bytes([((_x ^ 22) - 10) % 256 ^ 89 for _x in [15, 44, 34, 44, 86, 2, 33, 81, 99, 101, 100, 124, 15, 86, 41, 32, 40, 80]]).decode(): {bytes([((_x ^ 250) - 5) % 256 ^ 15 for _x in [138, 145, 123, 126, 146, 137, 129, 175, 156, 137, 157, 149]]).decode(): bytes([((_x ^ 172) - 64) % 256 ^ 95 for _x in [229, 218, 192, 218, 220, 19, 224, 199, 210, 221, 215, 210, 193, 215, 19, 1, 3, 2, 10, 19, 27, 229, 220, 223, 198, 222, 214, 26]]).decode(), bytes([((_x ^ 230) - 6) % 256 ^ 118 for _x in [253, 194, 251, 248, 248, 255, 198]]).decode(): bytes([((_x ^ 96) - 49) % 256 ^ 177 for _x in [114, 101, 148, 146, 101, 150, 149, 97, 110, 120, 78, 212, 210, 209, 217]]).decode()}, bytes([((_x ^ 87) - 55) % 256 ^ 178 for _x in [78, 160, 67, 88, 89, 95, 170, 78, 160, 67, 224, 238, 237, 149, 76, 67, 66, 169, 65, 89]]).decode(): {bytes([((_x ^ 166) - 44) % 256 ^ 116 for _x in [154, 239, 149, 150, 226, 231, 159, 241, 224, 231, 227, 155]]).decode(): bytes([((_x ^ 240) - 25) % 256 ^ 44 for _x in [101, 135, 172, 175, 146, 152, 129, 213, 101, 135, 172, 147, 146, 136, 136, 174, 172, 171, 150, 169, 213, 199, 197, 198, 222, 213, 237, 99, 172, 169, 130, 170, 146, 238]]).decode(), bytes([((_x ^ 168) - 86) % 256 ^ 181 for _x in [132, 155, 130, 153, 153, 142, 135]]).decode(): bytes([((_x ^ 72) - 110) % 256 ^ 107 for _x in [225, 52, 207, 193, 52, 197, 196, 48, 61, 227, 221, 143, 129, 128, 136]]).decode()}, bytes([((_x ^ 136) - 67) % 256 ^ 233 for _x in [116, 86, 65, 78, 71, 69, 104, 117, 104, 88, 150, 148, 147, 155, 138, 65, 64, 87, 79, 71]]).decode(): {bytes([((_x ^ 156) - 31) % 256 ^ 80 for _x in [207, 196, 222, 163, 199, 204, 212, 178, 193, 204, 192, 200]]).decode(): bytes([((_x ^ 5) - 72) % 256 ^ 211 for _x in [206, 236, 1, 4, 251, 253, 234, 62, 205, 234, 255, 0, 250, 255, 236, 250, 62, 44, 46, 47, 55, 62, 70, 200, 1, 2, 235, 3, 251, 71]]).decode(), bytes([((_x ^ 206) - 18) % 256 ^ 4 for _x in [183, 176, 185, 178, 178, 189, 180]]).decode(): bytes([((_x ^ 209) - 34) % 256 ^ 208 for _x in [115, 6, 21, 19, 6, 23, 22, 2, 15, 121, 111, 213, 211, 210, 218]]).decode()}, bytes([((_x ^ 90) - 22) % 256 ^ 155 for _x in [176, 73, 73, 82, 84, 78, 229, 155, 229, 154, 185, 80, 87, 94, 86, 78]]).decode(): {bytes([((_x ^ 41) - 67) % 256 ^ 128 for _x in [14, 5, 31, 26, 6, 13, 21, 11, 24, 13, 25, 1]]).decode(): bytes([((_x ^ 32) - 26) % 256 ^ 229 for _x in [228, 189, 189, 134, 128, 186, 255, 227, 235, 240, 224, 255, 239, 145, 132, 189, 186, 144, 144, 134, 132, 133, 190, 131, 255, 239, 131, 138, 144, 255, 209, 207, 209, 206]]).decode(), bytes([((_x ^ 177) - 101) % 256 ^ 133 for _x in [250, 227, 248, 225, 225, 244, 255]]).decode(): bytes([((_x ^ 149) - 13) % 256 ^ 46 for _x in [30, 205, 252, 254, 205, 242, 253, 201, 218, 16, 250, 188, 190, 188, 185]]).decode()}, bytes([((_x ^ 250) - 117) % 256 ^ 11 for _x in [55, 14, 37, 32, 30, 37, 20, 30, 84, 74, 84, 85, 40, 35, 38, 9, 33, 25]]).decode(): {bytes([((_x ^ 254) - 65) % 256 ^ 222 for _x in [5, 6, 16, 17, 13, 254, 22, 60, 15, 254, 10, 2]]).decode(): bytes([((_x ^ 27) - 61) % 256 ^ 211 for _x in [194, 233, 233, 236, 246, 232, 43, 166, 255, 244, 225, 239, 244, 197, 239, 43, 5, 59, 5, 4, 43, 35, 217, 226, 231, 248, 224, 232, 44]]).decode(), bytes([((_x ^ 8) - 9) % 256 ^ 130 for _x in [226, 251, 228, 253, 253, 248, 255]]).decode(): bytes([((_x ^ 226) - 109) % 256 ^ 239 for _x in [206, 21, 232, 238, 21, 234, 229, 25, 18, 196, 242, 168, 174, 168, 169]]).decode()}, bytes([((_x ^ 245) - 103) % 256 ^ 68 for _x in [140, 97, 107, 97, 103, 142, 104, 103, 40, 46, 40, 41, 140, 103, 122, 109, 101, 125]]).decode(): {bytes([((_x ^ 70) - 25) % 256 ^ 74 for _x in [1, 122, 20, 21, 121, 2, 10, 104, 123, 2, 6, 14]]).decode(): bytes([((_x ^ 9) - 64) % 256 ^ 79 for _x in [80, 111, 117, 111, 105, 166, 86, 116, 105, 96, 99, 117, 117, 111, 105, 104, 103, 106, 166, 180, 182, 180, 183, 166, 174, 80, 105, 106, 115, 107, 99, 175]]).decode(), bytes([((_x ^ 13) - 89) % 256 ^ 91 for _x in [156, 129, 158, 131, 131, 154, 157]]).decode(): bytes([((_x ^ 72) - 12) % 256 ^ 9 for _x in [45, 48, 207, 205, 48, 193, 192, 60, 57, 35, 25, 15, 13, 15, 12]]).decode()}, bytes([((_x ^ 138) - 55) % 256 ^ 254 for _x in [85, 68, 78, 68, 66, 110, 75, 91, 137, 143, 137, 140, 85, 66, 67, 72, 64, 88]]).decode(): {bytes([((_x ^ 64) - 113) % 256 ^ 37 for _x in [242, 253, 135, 134, 250, 245, 141, 171, 252, 245, 249, 241]]).decode(): bytes([((_x ^ 84) - 18) % 256 ^ 146 for _x in [130, 89, 167, 89, 91, 144, 135, 172, 81, 90, 92, 81, 166, 92, 144, 230, 224, 230, 225, 144, 152, 130, 91, 68, 173, 69, 93, 153]]).decode(), bytes([((_x ^ 185) - 108) % 256 ^ 95 for _x in [17, 26, 19, 36, 36, 31, 38]]).decode(): bytes([((_x ^ 27) - 4) % 256 ^ 168 for _x in [231, 202, 197, 199, 202, 251, 250, 214, 211, 25, 243, 133, 135, 133, 134]]).decode()}, bytes([((_x ^ 229) - 68) % 256 ^ 196 for _x in [61, 31, 10, 23, 0, 14, 17, 61, 31, 10, 223, 221, 223, 220, 51, 10, 9, 16, 8, 0]]).decode(): {bytes([((_x ^ 45) - 15) % 256 ^ 96 for _x in [62, 53, 15, 50, 54, 61, 5, 99, 48, 61, 49, 57]]).decode(): bytes([((_x ^ 18) - 95) % 256 ^ 119 for _x in [148, 118, 101, 110, 99, 97, 112, 164, 148, 118, 101, 98, 99, 113, 113, 111, 101, 106, 103, 104, 164, 182, 180, 182, 183, 164, 172, 146, 101, 104, 115, 107, 99, 175]]).decode(), bytes([((_x ^ 86) - 21) % 256 ^ 72 for _x in [22, 99, 104, 109, 109, 20, 111]]).decode(): bytes([((_x ^ 136) - 39) % 256 ^ 231 for _x in [86, 33, 52, 54, 33, 50, 49, 37, 58, 80, 90, 116, 118, 116, 117]]).decode()}, bytes([((_x ^ 158) - 86) % 256 ^ 254 for _x in [154, 124, 121, 116, 111, 109, 126, 157, 126, 110, 188, 186, 188, 187, 96, 121, 118, 127, 119, 111]]).decode(): {bytes([((_x ^ 50) - 126) % 256 ^ 100 for _x in [76, 185, 167, 160, 180, 177, 169, 139, 186, 177, 181, 77]]).decode(): bytes([((_x ^ 244) - 37) % 256 ^ 129 for _x in [2, 236, 231, 228, 253, 243, 238, 50, 3, 238, 241, 224, 254, 241, 236, 254, 50, 44, 34, 44, 33, 50, 58, 8, 231, 230, 237, 229, 253, 57]]).decode(), bytes([((_x ^ 145) - 119) % 256 ^ 235 for _x in [110, 107, 144, 109, 109, 148, 111]]).decode(): bytes([((_x ^ 30) - 76) % 256 ^ 143 for _x in [53, 40, 87, 85, 40, 89, 88, 36, 49, 59, 17, 23, 21, 23, 20]]).decode()}, bytes([((_x ^ 33) - 48) % 256 ^ 195 for _x in [226, 192, 253, 226, 254, 199, 193, 0, 2, 3, 4, 228, 253, 254, 199, 255, 247]]).decode(): {bytes([((_x ^ 197) - 63) % 256 ^ 218 for _x in [56, 55, 45, 44, 48, 63, 39, 1, 54, 63, 51, 59]]).decode(): bytes([((_x ^ 117) - 93) % 256 ^ 207 for _x in [168, 115, 115, 118, 124, 114, 57, 137, 111, 136, 115, 114, 108, 108, 118, 136, 139, 126, 117, 57, 137, 117, 98, 108, 57, 47, 41, 46, 35, 57, 49, 131, 136, 117, 98, 138, 114, 54]]).decode(), bytes([((_x ^ 33) - 25) % 256 ^ 160 for _x in [253, 192, 251, 198, 198, 255, 196]]).decode(): bytes([((_x ^ 54) - 106) % 256 ^ 241 for _x in [61, 200, 219, 221, 200, 217, 216, 204, 49, 39, 17, 27, 29, 28, 7]]).decode()}, bytes([((_x ^ 92) - 87) % 256 ^ 106 for _x in [204, 41, 62, 7, 57, 62, 51, 57, 243, 237, 238, 239, 207, 0, 1, 42, 2, 58]]).decode(): {bytes([((_x ^ 130) - 6) % 256 ^ 86 for _x in [186, 199, 169, 174, 194, 191, 183, 141, 188, 191, 195, 187]]).decode(): bytes([((_x ^ 172) - 40) % 256 ^ 9 for _x in [194, 59, 59, 36, 62, 56, 253, 46, 9, 60, 35, 57, 60, 15, 57, 253, 207, 205, 204, 203, 253, 229, 43, 34, 33, 8, 32, 56, 228]]).decode(), bytes([((_x ^ 49) - 17) % 256 ^ 47 for _x in [108, 105, 110, 99, 99, 106, 101]]).decode(): bytes([((_x ^ 192) - 117) % 256 ^ 177 for _x in [150, 137, 248, 246, 137, 250, 249, 133, 146, 156, 178, 56, 54, 53, 60]]).decode()}, bytes([((_x ^ 107) - 36) % 256 ^ 36 for _x in [253, 26, 16, 26, 4, 243, 17, 4, 81, 83, 82, 93, 253, 4, 7, 30, 6, 14]]).decode(): {bytes([((_x ^ 219) - 34) % 256 ^ 163 for _x in [50, 55, 41, 46, 42, 63, 39, 197, 52, 63, 43, 51]]).decode(): bytes([((_x ^ 72) - 58) % 256 ^ 28 for _x in [204, 231, 225, 231, 229, 62, 206, 224, 229, 252, 251, 225, 225, 231, 229, 228, 255, 226, 62, 32, 46, 47, 44, 62, 38, 204, 229, 226, 235, 227, 251, 39]]).decode(), bytes([((_x ^ 16) - 100) % 256 ^ 104 for _x in [127, 116, 125, 122, 122, 97, 120]]).decode(): bytes([((_x ^ 112) - 121) % 256 ^ 36 for _x in [157, 202, 191, 189, 202, 185, 186, 206, 177, 155, 145, 255, 253, 254, 251]]).decode()}, bytes([((_x ^ 220) - 13) % 256 ^ 227 for _x in [30, 75, 65, 75, 69, 97, 120, 72, 2, 60, 3, 62, 30, 69, 64, 127, 71, 79]]).decode(): {bytes([((_x ^ 227) - 74) % 256 ^ 88 for _x in [101, 152, 150, 145, 157, 96, 136, 178, 99, 96, 156, 100]]).decode(): bytes([((_x ^ 76) - 46) % 256 ^ 228 for _x in [172, 247, 137, 247, 245, 190, 169, 242, 255, 244, 226, 255, 136, 226, 190, 72, 78, 79, 76, 190, 182, 172, 245, 250, 243, 251, 227, 183]]).decode(), bytes([((_x ^ 125) - 4) % 256 ^ 104 for _x in [114, 121, 112, 119, 119, 108, 117]]).decode(): bytes([((_x ^ 93) - 110) % 256 ^ 97 for _x in [194, 47, 220, 34, 47, 222, 223, 51, 38, 248, 198, 156, 226, 227, 152]]).decode()}, bytes([((_x ^ 206) - 99) % 256 ^ 167 for _x in [148, 246, 229, 254, 235, 233, 248, 148, 246, 229, 54, 52, 55, 58, 154, 229, 224, 251, 227, 235]]).decode(): {bytes([((_x ^ 187) - 41) % 256 ^ 120 for _x in [254, 129, 143, 138, 134, 249, 145, 235, 132, 249, 133, 253]]).decode(): bytes([((_x ^ 12) - 117) % 256 ^ 139 for _x in [92, 98, 85, 90, 111, 81, 120, 44, 92, 98, 85, 110, 111, 97, 97, 91, 85, 86, 83, 80, 44, 34, 60, 35, 62, 44, 20, 94, 85, 80, 127, 87, 111, 27]]).decode(), bytes([((_x ^ 169) - 2) % 256 ^ 54 for _x in [254, 201, 240, 243, 243, 252, 245]]).decode(): bytes([((_x ^ 150) - 110) % 256 ^ 232 for _x in [176, 109, 158, 144, 109, 156, 157, 97, 100, 186, 132, 222, 208, 209, 218]]).decode()}, bytes([((_x ^ 48) - 2) % 256 ^ 83 for _x in [53, 19, 14, 11, 8, 2, 25, 50, 25, 9, 83, 85, 84, 87, 55, 14, 113, 24, 112, 8]]).decode(): {bytes([((_x ^ 9) - 117) % 256 ^ 231 for _x in [241, 10, 0, 5, 9, 242, 26, 36, 247, 242, 246, 254]]).decode(): bytes([((_x ^ 213) - 20) % 256 ^ 201 for _x in [120, 26, 111, 98, 21, 107, 4, 40, 123, 4, 105, 110, 20, 105, 26, 20, 40, 218, 216, 217, 198, 40, 32, 102, 111, 108, 5, 109, 21, 33]]).decode(), bytes([((_x ^ 79) - 70) % 256 ^ 137 for _x in [127, 104, 97, 98, 98, 125, 100]]).decode(): bytes([((_x ^ 192) - 3) % 256 ^ 110 for _x in [129, 206, 223, 225, 206, 221, 222, 210, 197, 251, 229, 159, 161, 162, 155]]).decode()}, bytes([((_x ^ 248) - 37) % 256 ^ 225 for _x in [46, 64, 75, 46, 74, 65, 79, 0, 14, 13, 15, 36, 75, 74, 65, 73, 81]]).decode(): {bytes([((_x ^ 153) - 24) % 256 ^ 83 for _x in [214, 203, 161, 162, 206, 211, 219, 189, 204, 211, 207, 215]]).decode(): bytes([((_x ^ 198) - 104) % 256 ^ 37 for _x in [20, 109, 109, 114, 104, 110, 171, 27, 121, 116, 109, 110, 120, 120, 114, 116, 117, 106, 119, 171, 27, 119, 126, 120, 171, 185, 187, 186, 184, 171, 179, 29, 116, 119, 126, 118, 110, 178]]).decode(), bytes([((_x ^ 120) - 126) % 256 ^ 248 for _x in [97, 118, 111, 108, 108, 99, 106]]).decode(): bytes([((_x ^ 129) - 103) % 256 ^ 160 for _x in [214, 173, 184, 182, 173, 186, 189, 169, 178, 220, 210, 120, 118, 121, 123]]).decode()}, bytes([((_x ^ 41) - 46) % 256 ^ 21 for _x in [93, 166, 139, 128, 182, 139, 188, 182, 124, 122, 123, 125, 88, 129, 142, 167, 143, 183]]).decode(): {bytes([((_x ^ 180) - 95) % 256 ^ 177 for _x in [128, 131, 149, 148, 136, 155, 147, 249, 138, 155, 143, 135]]).decode(): bytes([((_x ^ 216) - 67) % 256 ^ 167 for _x in [243, 220, 220, 201, 223, 221, 18, 239, 206, 209, 212, 222, 209, 192, 222, 18, 0, 2, 1, 15, 18, 10, 236, 211, 214, 205, 213, 221, 9]]).decode(), bytes([((_x ^ 228) - 8) % 256 ^ 208 for _x in [95, 36, 93, 34, 34, 89, 32]]).decode(): bytes([((_x ^ 216) - 82) % 256 ^ 217 for _x in [3, 214, 37, 35, 214, 39, 38, 210, 223, 57, 63, 229, 227, 226, 228]]).decode()}, bytes([((_x ^ 46) - 99) % 256 ^ 58 for _x in [225, 152, 130, 152, 150, 227, 133, 150, 69, 67, 64, 66, 225, 150, 151, 156, 148, 236]]).decode(): {bytes([((_x ^ 111) - 108) % 256 ^ 10 for _x in [181, 160, 138, 137, 189, 184, 176, 174, 191, 184, 188, 180]]).decode(): bytes([((_x ^ 41) - 68) % 256 ^ 227 for _x in [208, 231, 253, 231, 249, 46, 222, 252, 249, 224, 227, 253, 253, 231, 249, 248, 239, 250, 46, 60, 62, 63, 61, 46, 38, 208, 249, 250, 243, 251, 227, 39]]).decode(), bytes([((_x ^ 93) - 115) % 256 ^ 153 for _x in [48, 57, 54, 55, 55, 50, 53]]).decode(): bytes([((_x ^ 241) - 49) % 256 ^ 232 for _x in [24, 79, 58, 56, 79, 60, 63, 75, 68, 30, 36, 250, 248, 251, 253]]).decode()}, bytes([((_x ^ 239) - 108) % 256 ^ 169 for _x in [132, 195, 169, 195, 221, 137, 166, 214, 232, 234, 235, 233, 132, 221, 222, 167, 223, 215]]).decode(): {bytes([((_x ^ 230) - 108) % 256 ^ 50 for _x in [36, 33, 75, 72, 44, 89, 81, 63, 46, 89, 45, 37]]).decode(): bytes([((_x ^ 223) - 104) % 256 ^ 4 for _x in [101, 10, 0, 10, 12, 83, 96, 7, 18, 13, 23, 18, 1, 23, 83, 65, 67, 66, 64, 83, 75, 101, 12, 15, 6, 14, 22, 74]]).decode(), bytes([((_x ^ 137) - 124) % 256 ^ 36 for _x in [74, 65, 72, 79, 79, 52, 77]]).decode(): bytes([((_x ^ 39) - 99) % 256 ^ 3 for _x in [145, 238, 243, 241, 238, 253, 254, 226, 245, 159, 149, 179, 177, 178, 180]]).decode()}, bytes([((_x ^ 63) - 29) % 256 ^ 247 for _x in [251, 157, 138, 133, 144, 142, 159, 251, 157, 138, 221, 219, 220, 222, 129, 138, 135, 160, 136, 144]]).decode(): {bytes([((_x ^ 51) - 117) % 256 ^ 194 for _x in [40, 19, 21, 20, 16, 43, 3, 33, 18, 43, 23, 47]]).decode(): bytes([((_x ^ 138) - 109) % 256 ^ 115 for _x in [26, 228, 3, 12, 9, 247, 254, 74, 26, 228, 3, 8, 9, 231, 231, 13, 3, 0, 245, 6, 74, 36, 58, 37, 39, 74, 66, 24, 3, 6, 249, 1, 9, 77]]).decode(), bytes([((_x ^ 248) - 112) % 256 ^ 186 for _x in [177, 186, 179, 188, 188, 183, 190]]).decode(): bytes([((_x ^ 70) - 59) % 256 ^ 213 for _x in [134, 173, 164, 166, 173, 154, 157, 169, 178, 248, 146, 100, 102, 89, 103]]).decode()}, bytes([((_x ^ 206) - 8) % 256 ^ 81 for _x in [199, 229, 136, 141, 242, 244, 227, 196, 227, 243, 165, 167, 166, 164, 193, 136, 139, 226, 138, 242]]).decode(): {bytes([((_x ^ 116) - 18) % 256 ^ 20 for _x in [246, 251, 13, 2, 254, 243, 11, 41, 248, 243, 255, 247]]).decode(): bytes([((_x ^ 167) - 71) % 256 ^ 212 for _x in [108, 74, 165, 162, 95, 89, 64, 156, 105, 64, 91, 166, 80, 91, 74, 80, 156, 138, 140, 139, 137, 156, 228, 110, 165, 88, 79, 167, 95, 227]]).decode(), bytes([((_x ^ 246) - 29) % 256 ^ 65 for _x in [201, 176, 203, 186, 186, 183, 188]]).decode(): bytes([((_x ^ 159) - 108) % 256 ^ 247 for _x in [140, 97, 110, 108, 97, 112, 113, 157, 152, 146, 184, 174, 172, 173, 175]]).decode()}, bytes([((_x ^ 241) - 49) % 256 ^ 200 for _x in [56, 26, 41, 41, 46, 35, 38, 17, 60, 41, 41, 36, 29]]).decode(): {bytes([((_x ^ 21) - 61) % 256 ^ 23 for _x in [165, 174, 180, 177, 173, 166, 190, 144, 163, 166, 162, 186]]).decode(): bytes([((_x ^ 22) - 85) % 256 ^ 60 for _x in [215, 181, 190, 190, 185, 188, 177, 166, 103, 171, 190, 190, 179, 178, 103, 127, 222, 185, 185, 188, 162, 184, 103, 117, 119, 116, 76, 124]]).decode(), bytes([((_x ^ 232) - 56) % 256 ^ 58 for _x in [121, 98, 123, 100, 100, 127, 102]]).decode(): bytes([((_x ^ 66) - 49) % 256 ^ 25 for _x in [62, 239, 220, 235, 227, 228]]).decode()}, bytes([((_x ^ 25) - 13) % 256 ^ 61 for _x in [99, 69, 70, 70, 113, 120, 121, 126, 111, 70, 70, 71, 66, 5, 3, 5, 0]]).decode(): {bytes([((_x ^ 93) - 77) % 256 ^ 162 for _x in [78, 69, 67, 66, 70, 77, 117, 23, 68, 77, 65, 73]]).decode(): bytes([((_x ^ 153) - 124) % 256 ^ 106 for _x in [47, 13, 24, 24, 17, 230, 25, 16, 95, 35, 24, 24, 27, 12, 95, 39, 56, 17, 17, 230, 28, 18, 95, 77, 79, 77, 78, 38]]).decode(), bytes([((_x ^ 178) - 53) % 256 ^ 8 for _x in [18, 39, 44, 41, 41, 16, 43]]).decode(): bytes([((_x ^ 213) - 114) % 256 ^ 223 for _x in [42, 249, 200, 229, 253, 240]]).decode()}, bytes([((_x ^ 140) - 7) % 256 ^ 252 for _x in [63, 25, 22, 22, 45, 16, 21, 46, 35, 22, 22, 27, 26, 89, 95, 89, 67]]).decode(): {bytes([((_x ^ 121) - 92) % 256 ^ 27 for _x in [162, 183, 189, 190, 170, 175, 199, 217, 168, 175, 171, 163]]).decode(): bytes([((_x ^ 113) - 3) % 256 ^ 9 for _x in [45, 15, 24, 24, 3, 18, 27, 0, 93, 17, 24, 24, 25, 12, 93, 85, 56, 3, 3, 18, 28, 30, 93, 79, 77, 79, 49, 82]]).decode(), bytes([((_x ^ 20) - 38) % 256 ^ 164 for _x in [249, 230, 255, 228, 228, 243, 250]]).decode(): bytes([((_x ^ 53) - 45) % 256 ^ 165 for _x in [17, 216, 203, 196, 204, 195]]).decode()}, bytes([((_x ^ 45) - 28) % 256 ^ 197 for _x in [156, 254, 235, 156, 232, 225, 255, 62, 60, 62, 32, 130, 235, 232, 225, 233, 145]]).decode(): {bytes([((_x ^ 183) - 127) % 256 ^ 10 for _x in [90, 85, 79, 78, 82, 93, 69, 99, 84, 93, 81, 89]]).decode(): bytes([((_x ^ 76) - 45) % 256 ^ 18 for _x in [198, 237, 237, 228, 210, 232, 19, 35, 193, 230, 237, 232, 194, 194, 228, 230, 229, 236, 231, 19, 35, 231, 216, 194, 19, 1, 3, 1, 31, 19, 43, 61, 230, 231, 216, 224, 232, 36]]).decode(), bytes([((_x ^ 129) - 16) % 256 ^ 97 for _x in [147, 152, 145, 158, 158, 149, 156]]).decode(): bytes([((_x ^ 130) - 27) % 256 ^ 184 for _x in [129, 122, 103, 97, 122, 101, 106, 118, 109, 139, 141, 39, 33, 39, 37]]).decode()}, bytes([((_x ^ 19) - 87) % 256 ^ 179 for _x in [36, 13, 58, 39, 61, 58, 11, 61, 203, 201, 203, 205, 47, 32, 37, 14, 38, 62]]).decode(): {bytes([((_x ^ 18) - 8) % 256 ^ 26 for _x in [148, 105, 99, 96, 108, 145, 121, 95, 110, 145, 109, 149]]).decode(): bytes([((_x ^ 102) - 94) % 256 ^ 77 for _x in [6, 239, 239, 228, 234, 224, 173, 26, 241, 236, 231, 225, 236, 251, 225, 173, 187, 189, 187, 177, 173, 165, 31, 230, 25, 240, 24, 224, 164]]).decode(), bytes([((_x ^ 190) - 114) % 256 ^ 75 for _x in [36, 43, 34, 41, 41, 30, 39]]).decode(): bytes([((_x ^ 155) - 97) % 256 ^ 47 for _x in [123, 48, 37, 91, 48, 39, 32, 52, 63, 65, 95, 229, 27, 229, 231]]).decode()}, bytes([((_x ^ 189) - 83) % 256 ^ 168 for _x in [236, 169, 147, 169, 167, 246, 144, 167, 80, 86, 80, 82, 236, 167, 170, 141, 165, 157]]).decode(): {bytes([((_x ^ 156) - 52) % 256 ^ 99 for _x in [167, 162, 216, 219, 223, 170, 210, 236, 221, 170, 222, 166]]).decode(): bytes([((_x ^ 104) - 69) % 256 ^ 208 for _x in [163, 150, 128, 150, 108, 93, 173, 143, 108, 147, 146, 128, 128, 150, 108, 107, 158, 105, 93, 79, 77, 79, 65, 93, 85, 163, 108, 105, 130, 106, 146, 86]]).decode(), bytes([((_x ^ 242) - 44) % 256 ^ 87 for _x in [146, 153, 144, 151, 151, 172, 149]]).decode(): bytes([((_x ^ 182) - 14) % 256 ^ 74 for _x in [158, 139, 240, 254, 139, 250, 251, 143, 130, 156, 162, 48, 62, 48, 58]]).decode()}, bytes([((_x ^ 241) - 53) % 256 ^ 176 for _x in [234, 255, 9, 255, 229, 233, 8, 248, 70, 68, 70, 72, 234, 229, 224, 11, 227, 251]]).decode(): {bytes([((_x ^ 99) - 15) % 256 ^ 77 for _x in [91, 80, 46, 47, 83, 88, 32, 66, 81, 88, 76, 84]]).decode(): bytes([((_x ^ 115) - 102) % 256 ^ 253 for _x in [98, 137, 135, 137, 139, 48, 103, 156, 113, 138, 140, 113, 134, 140, 48, 70, 64, 70, 92, 48, 72, 98, 139, 132, 157, 133, 141, 73]]).decode(), bytes([((_x ^ 48) - 15) % 256 ^ 95 for _x in [123, 118, 125, 112, 112, 121, 114]]).decode(): bytes([((_x ^ 204) - 43) % 256 ^ 117 for _x in [156, 247, 254, 252, 247, 224, 231, 243, 136, 130, 168, 190, 188, 190, 160]]).decode()}, bytes([((_x ^ 78) - 48) % 256 ^ 199 for _x in [137, 171, 150, 147, 156, 154, 173, 137, 171, 150, 107, 105, 107, 109, 143, 150, 149, 172, 148, 156]]).decode(): {bytes([((_x ^ 154) - 50) % 256 ^ 189 for _x in [145, 156, 154, 101, 153, 148, 108, 142, 159, 148, 152, 144]]).decode(): bytes([((_x ^ 179) - 101) % 256 ^ 41 for _x in [109, 115, 24, 27, 2, 28, 113, 221, 109, 115, 24, 7, 2, 12, 12, 22, 24, 31, 30, 25, 221, 51, 205, 51, 49, 221, 213, 87, 24, 25, 114, 26, 2, 214]]).decode(), bytes([((_x ^ 30) - 21) % 256 ^ 153 for _x in [17, 24, 19, 18, 18, 15, 20]]).decode(): bytes([((_x ^ 250) - 117) % 256 ^ 120 for _x in [103, 104, 133, 135, 104, 123, 120, 116, 115, 89, 83, 69, 71, 69, 59]]).decode()}, bytes([((_x ^ 84) - 35) % 256 ^ 223 for _x in [230, 132, 135, 140, 137, 139, 154, 251, 154, 138, 68, 70, 68, 90, 248, 135, 130, 153, 129, 137]]).decode(): {bytes([((_x ^ 99) - 78) % 256 ^ 146 for _x in [39, 42, 76, 83, 47, 34, 90, 120, 41, 34, 46, 38]]).decode(): bytes([((_x ^ 110) - 125) % 256 ^ 233 for _x in [88, 118, 109, 110, 103, 105, 116, 40, 89, 116, 107, 106, 100, 107, 118, 100, 40, 54, 56, 54, 52, 40, 80, 82, 109, 108, 119, 111, 103, 83]]).decode(), bytes([((_x ^ 126) - 58) % 256 ^ 185 for _x in [106, 117, 108, 111, 111, 104, 113]]).decode(): bytes([((_x ^ 105) - 26) % 256 ^ 89 for _x in [74, 63, 44, 42, 63, 46, 47, 59, 38, 64, 70, 236, 234, 236, 238]]).decode()}}
        office_apps = {}
        for product_id, info in suites.items():
            for arch in ['64', '32']:
                app_key = f'{product_id}_{arch}bit'
                display_name_with_arch = f"{info['display_name']} (x{arch})"
                office_apps[app_key] = {bytes([((_x ^ 58) - 57) % 256 ^ 243 for _x in [234, 233, 131, 134, 226, 241, 249, 223, 236, 241, 237, 245]]).decode(): display_name_with_arch, bytes([((_x ^ 56) - 49) % 256 ^ 2 for _x in [157, 160, 153, 154, 164, 166, 165]]).decode(): bytes([((_x ^ 42) - 42) % 256 ^ 87 for _x in [186, 137, 187, 137, 187, 137, 187]]).decode(), bytes([((_x ^ 99) - 48) % 256 ^ 152 for _x in [79, 78, 120, 72, 121, 66, 123, 127, 66, 68, 69]]).decode(): f'Installer {display_name_with_arch} via Office Deployment Tool.', bytes([((_x ^ 8) - 86) % 256 ^ 248 for _x in [249, 231, 234, 251, 253, 229, 232, 223]]).decode(): bytes([((_x ^ 126) - 20) % 256 ^ 52 for _x in [241, 24, 24, 15, 21, 27]]).decode(), bytes([((_x ^ 23) - 95) % 256 ^ 57 for _x in [187, 136, 191, 172]]).decode(): bytes([((_x ^ 129) - 15) % 256 ^ 122 for _x in [165, 170, 170, 163, 169, 175, 181, 153, 159, 163, 156, 175]]).decode(), bytes([((_x ^ 120) - 103) % 256 ^ 82 for _x in [218, 224, 220, 219, 12, 246, 255, 221]]).decode(): bytes([((_x ^ 66) - 55) % 256 ^ 155 for _x in [104, 100, 100, 96, 93, 154, 169, 169, 107, 111, 113, 174, 107, 109, 105, 110, 93, 152, 174, 109, 105, 111, 169, 109, 105, 108, 105, 98, 169, 155, 166, 169, 111, 107, 109, 98, 105, 93, 105, 118, 100, 175, 105, 118, 118, 107, 109, 119, 175, 162, 160, 163, 155, 174, 96, 110, 113]]).decode(), bytes([((_x ^ 92) - 71) % 256 ^ 166 for _x in [65, 71, 76, 85, 70, 80, 69, 28, 74, 85]]).decode(): product_id, bytes([((_x ^ 136) - 124) % 256 ^ 32 for _x in [53, 70, 55, 76, 77, 88, 73, 55, 88, 89, 70, 73]]).decode(): f'x{arch}', bytes([((_x ^ 217) - 35) % 256 ^ 74 for _x in [149, 156, 151, 158, 158, 139, 144]]).decode(): info[bytes([((_x ^ 234) - 120) % 256 ^ 84 for _x in [69, 94, 71, 88, 88, 67, 90]]).decode()]}
        return office_apps

    def update_download_progress_anywhere(self, app_key, percentage):
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if hasattr(widget, bytes([((_x ^ 65) - 113) % 256 ^ 182 for _x in [9, 118, 118, 27, 15, 5, 1]]).decode()) and widget.app_key == app_key:
                widget.update_download_progress(app_key, percentage)
                return
        if (id(object()) * 31 + 7) % 17 == 17:
            _j42acb4 = id(None) & 0
        if not self.embed_mode:
            for i in range(self.selected_list_widget.count()):
                item = self.selected_list_widget.item(i)
                widget = self.selected_list_widget.itemWidget(item)
                if hasattr(widget, bytes([((_x ^ 105) - 63) % 256 ^ 6 for _x in [207, 220, 220, 241, 197, 203, 215]]).decode()) and widget.app_key == app_key:
                    widget.update_download_progress(app_key, percentage)
                    return

    def on_tasks_batch_completed(self, completed_items):
        for app_key, item_info in completed_items.items():
            self.local_apps[app_key] = item_info
            self.remote_apps.setdefault(bytes([((_x ^ 119) - 37) % 256 ^ 49 for _x in [2, 17, 17, 228, 10, 29, 14, 246, 16]]).decode(), {})[app_key] = item_info
        self.load_config_and_apps(populate=False)
        if abs(id(object()) - id(object())) < -1:
            _j18ac00 = id(None) & 0
        if self.is_processing:
            for app_key in completed_items.keys():
                self.update_single_app_widget(app_key)
            return
        if (id(object()) * 31 + 7) % 17 == 17:
            _j9f8ae0 = id(None) & 0
        for app_key in completed_items.keys():
            self.update_single_app_widget(app_key)
            if app_key in self.selected_for_install:
                for i in range(self.selected_list_widget.count() - 1, -1, -1):
                    item = self.selected_list_widget.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == app_key:
                        self.selected_list_widget.takeItem(i)
                        break
                app_info = self.local_apps.get(app_key, {})
                if app_info:
                    self.move_app_to_selection(app_key, app_info)

    def is_app_downloaded(self, app_key, app_info):
        pass
        if app_info.get(bytes([((_x ^ 145) - 2) % 256 ^ 207 for _x in [44, 41, 80, 61]]).decode()) == bytes([((_x ^ 66) - 61) % 256 ^ 127 for _x in [15, 20, 20, 17, 27, 21, 31, 11, 5, 17, 10, 21]]).decode():
            marker_file = APPS_DIR / app_key / bytes([((_x ^ 44) - 59) % 256 ^ 193 for _x in [245, 204, 197, 221, 198, 196, 197, 247, 204, 245, 241, 197, 203, 192, 196, 243, 220, 243, 204, 6, 203, 247, 194, 201, 243, 194]]).decode()
            return marker_file.exists()
        download_url = app_info.get(bytes([((_x ^ 46) - 96) % 256 ^ 197 for _x in [47, 36, 60, 37, 39, 36, 42, 47, 212, 62, 57, 39]]).decode(), '')
        if not download_url:
            return False
        output_filename_str = app_info.get(bytes([((_x ^ 138) - 32) % 256 ^ 201 for _x in [76, 86, 87, 83, 86, 87, 60, 69, 74, 79, 70, 77, 66, 78, 70]]).decode(), Path(app_info.get(bytes([((_x ^ 138) - 125) % 256 ^ 246 for _x in [133, 156, 116, 159, 157, 156, 158, 133, 172, 138, 139, 157]]).decode(), '')).name)
        file_name = output_filename_str.split('|', 1)[0] if '|' in output_filename_str else output_filename_str
        download_path = APPS_DIR / app_key / file_name
        if len(str(id(object()))) > 50:
            _j38323e = id(None) & 0
        aria2_control_file = download_path.with_suffix(download_path.suffix + bytes([((_x ^ 214) - 35) % 256 ^ 48 for _x in [151, 162, 179, 170, 162, 243]]).decode())
        if len(str(id(object()))) > 50:
            _jfb951d = id(None) & 0
        return download_path.exists() and (not aria2_control_file.exists())

    def handle_cli_args(self, args):
        self.load_config_and_apps(populate=False)
        if not self.remote_apps.get(bytes([((_x ^ 87) - 93) % 256 ^ 196 for _x in [85, 70, 70, 175, 93, 90, 169, 81, 67]]).decode()):
            self.show_styled_message_box(QMessageBox.Icon.Critical, bytes([((_x ^ 137) - 99) % 256 ^ 139 for _x in [184, 213, 213, 206, 213]]).decode(), bytes([((_x ^ 13) - 105) % 256 ^ 120 for _x in [155, 114, 143, 142, 112, 139, 204, 120, 141, 204, 112, 141, 143, 136, 204, 120, 116, 139, 204, 112, 119, 121, 120, 204, 141, 138, 204, 121, 141, 138, 120, 117, 143, 126, 139, 178, 204, 169, 143, 114, 114, 141, 120, 204, 137, 141, 114, 120, 119, 114, 123, 139, 178, 178]]).decode())
            QApplication.quit()
            return
        is_install_action = bytes([((_x ^ 139) - 15) % 256 ^ 51 for _x in [160, 226, 231, 196, 221, 234, 229, 229]]).decode() in args
        is_update_action = bytes([((_x ^ 78) - 65) % 256 ^ 63 for _x in [31, 197, 222, 210, 209, 194, 213]]).decode() in args
        target_keys = set()
        app_names_str = ''
        for arg in args:
            if not arg.startswith('/'):
                app_names_str = arg.strip('\'"')
                break
        if app_names_str:
            target_keys = set(app_names_str.split('|'))
        elif is_install_action and (not app_names_str):
            for key, info in self.local_apps.items():
                if info.get(bytes([((_x ^ 219) - 19) % 256 ^ 14 for _x in [89, 85, 86, 175, 191, 161, 168, 75, 86, 89, 174, 174]]).decode(), False):
                    target_keys.add(key)
        elif is_update_action and (not is_install_action) and (not app_names_str):
            for key in self.local_apps:
                target_keys.add(key)
        self.cli_target_apps = list(target_keys)
        worker_tasks = {}
        self.cli_task_results = {}
        report = {bytes([((_x ^ 146) - 60) % 256 ^ 209 for _x in [114, 79, 99, 126, 115, 98]]).decode(): {bytes([((_x ^ 254) - 35) % 256 ^ 210 for _x in [58, 52, 42, 42, 36, 58, 58]]).decode(): 0, bytes([((_x ^ 61) - 12) % 256 ^ 188 for _x in [219, 212, 220, 225]]).decode(): 0, bytes([((_x ^ 108) - 90) % 256 ^ 201 for _x in [120, 144, 150, 127, 127, 106, 107]]).decode(): []}, bytes([((_x ^ 48) - 30) % 256 ^ 56 for _x in [95, 68, 89, 90, 71, 66, 66]]).decode(): {bytes([((_x ^ 169) - 97) % 256 ^ 97 for _x in [218, 220, 202, 202, 204, 218, 218]]).decode(): 0, bytes([((_x ^ 45) - 33) % 256 ^ 158 for _x in [52, 13, 53, 62]]).decode(): 0, bytes([((_x ^ 157) - 42) % 256 ^ 113 for _x in [177, 217, 223, 182, 182, 163, 162]]).decode(): []}}
        for key in target_keys:
            remote_info = self.remote_apps.get(bytes([((_x ^ 121) - 72) % 256 ^ 228 for _x in [180, 165, 165, 122, 172, 161, 176, 168, 166]]).decode(), {}).get(key)
            local_info = self.local_apps.get(key, {})
            if not remote_info:
                report[bytes([((_x ^ 238) - 13) % 256 ^ 146 for _x in [26, 1, 237, 238, 29, 234]]).decode()][bytes([((_x ^ 237) - 5) % 256 ^ 221 for _x in [94, 86, 84, 95, 95, 80, 83]]).decode()].append(key)
                report[bytes([((_x ^ 175) - 89) % 256 ^ 63 for _x in [0, 5, 10, 11, 24, 3, 3]]).decode()][bytes([((_x ^ 221) - 15) % 256 ^ 73 for _x in [148, 236, 242, 149, 149, 230, 225]]).decode()].append(key)
                continue
            if not self.is_app_downloaded(key, remote_info):
                report[bytes([((_x ^ 15) - 90) % 256 ^ 208 for _x in [240, 245, 1, 4, 241, 0]]).decode()][bytes([((_x ^ 47) - 30) % 256 ^ 174 for _x in [212, 204, 202, 211, 211, 198, 199]]).decode()].append(key)
                report[bytes([((_x ^ 28) - 70) % 256 ^ 142 for _x in [49, 58, 95, 92, 41, 52, 52]]).decode()][bytes([((_x ^ 178) - 116) % 256 ^ 57 for _x in [12, 116, 118, 15, 15, 98, 99]]).decode()].append(key)
                continue
            needs_update = False
            if is_update_action:
                local_version = local_info.get(bytes([((_x ^ 249) - 42) % 256 ^ 192 for _x in [25, 54, 37, 36, 42, 32, 33]]).decode(), '0')
                remote_version = remote_info.get(bytes([((_x ^ 55) - 44) % 256 ^ 44 for _x in [177, 66, 189, 188, 70, 88, 89]]).decode(), '0')
                if parse_version(remote_version) > parse_version(local_version):
                    needs_update = True
            if needs_update:
                worker_tasks[key] = {bytes([((_x ^ 215) - 62) % 256 ^ 143 for _x in [243, 200, 240, 201]]).decode(): remote_info, bytes([((_x ^ 221) - 78) % 256 ^ 51 for _x in [125, 67, 72, 117, 119, 118]]).decode(): bytes([((_x ^ 110) - 108) % 256 ^ 173 for _x in [42, 39, 91, 86, 43, 90]]).decode()}
            elif is_install_action:
                worker_tasks[key] = {bytes([((_x ^ 152) - 50) % 256 ^ 58 for _x in [29, 30, 22, 31]]).decode(): remote_info, bytes([((_x ^ 154) - 49) % 256 ^ 85 for _x in [255, 253, 200, 247, 241, 246]]).decode(): bytes([((_x ^ 251) - 119) % 256 ^ 53 for _x in [40, 41, 70, 67, 48, 43, 43]]).decode()}
        if not worker_tasks:
            self.show_styled_message_box(QMessageBox.Icon.Information, bytes([((_x ^ 174) - 76) % 256 ^ 18 for _x in [6, 103, 28, 105, 110, 105, 19, 17, 28, 105, 103, 102]]).decode(), bytes([((_x ^ 78) - 100) % 256 ^ 121 for _x in [213, 52, 243, 63, 50, 32, 56, 32, 243, 53, 206, 206, 207, 243, 63, 52, 243, 49, 206, 243, 35, 206, 33, 205, 52, 33, 54, 206, 207, 243, 251, 63, 59, 206, 243, 32, 52, 205, 63, 60, 50, 33, 206, 243, 207, 52, 206, 32, 243, 53, 52, 63, 243, 206, 43, 58, 32, 63, 247, 243, 59, 50, 32, 243, 53, 52, 63, 243, 49, 206, 206, 53, 243, 207, 52, 60, 53, 55, 52, 50, 207, 206, 207, 247, 243, 52, 33, 243, 58, 32, 243, 50, 55, 33, 206, 50, 207, 42, 243, 63, 59, 206, 243, 55, 50, 63, 206, 32, 63, 243, 61, 206, 33, 32, 58, 52, 53, 250, 245]]).decode())
            QApplication.quit()
            return
        self.show()
        if len(str(id(object()))) > 50:
            _jfb00f1 = id(None) & 0
        self.populate_lists()
        self.set_ui_interactive(False)
        self.start_button.hide()
        self.is_processing = True
        self.install_worker = InstallWorker(worker_tasks)

        def on_cli_finished():
            if getattr(self, bytes([((_x ^ 230) - 44) % 256 ^ 30 for _x in [79, 120, 69, 139, 127, 113, 121, 121, 77, 126, 117, 139, 127, 68, 123, 115, 122]]).decode(), False):
                return
            self.cli_summary_shown = True
            final_report = {bytes([((_x ^ 107) - 122) % 256 ^ 45 for _x in [185, 188, 168, 173, 184, 169]]).decode(): {bytes([((_x ^ 250) - 77) % 256 ^ 40 for _x in [82, 80, 98, 98, 96, 82, 82]]).decode(): 0, bytes([((_x ^ 177) - 62) % 256 ^ 167 for _x in [78, 181, 189, 184]]).decode(): 0}, bytes([((_x ^ 209) - 31) % 256 ^ 166 for _x in [63, 54, 37, 32, 55, 56, 56]]).decode(): {bytes([((_x ^ 211) - 28) % 256 ^ 121 for _x in [245, 251, 229, 229, 235, 245, 245]]).decode(): 0, bytes([((_x ^ 204) - 110) % 256 ^ 129 for _x in [153, 130, 154, 151]]).decode(): 0}}
            for key, result in self.cli_task_results.items():
                action = result.get(bytes([((_x ^ 69) - 53) % 256 ^ 207 for _x in [166, 164, 181, 158, 144, 147]]).decode())
                status = result.get(bytes([((_x ^ 211) - 33) % 256 ^ 106 for _x in [233, 236, 255, 236, 147, 233]]).decode())
                if status not in [bytes([((_x ^ 59) - 106) % 256 ^ 114 for _x in [80, 74, 64, 64, 186, 80, 80]]).decode(), bytes([((_x ^ 69) - 3) % 256 ^ 224 for _x in [204, 193, 201, 202, 205, 194]]).decode()]:
                    continue
                if action == bytes([((_x ^ 186) - 106) % 256 ^ 43 for _x in [114, 127, 3, 14, 115, 2]]).decode():
                    if status == bytes([((_x ^ 170) - 1) % 256 ^ 68 for _x in [146, 152, 130, 130, 136, 146, 146]]).decode():
                        final_report[bytes([((_x ^ 50) - 56) % 256 ^ 22 for _x in [169, 172, 152, 157, 168, 153]]).decode()][bytes([((_x ^ 86) - 62) % 256 ^ 139 for _x in [96, 106, 112, 112, 122, 96, 96]]).decode()] += 1
                    else:
                        final_report[bytes([((_x ^ 234) - 42) % 256 ^ 209 for _x in [36, 33, 53, 48, 37, 52]]).decode()][bytes([((_x ^ 228) - 32) % 256 ^ 217 for _x in [59, 60, 52, 49]]).decode()] += 1
                elif action == bytes([((_x ^ 22) - 27) % 256 ^ 166 for _x in [252, 245, 230, 251, 244, 243, 243]]).decode():
                    if status == bytes([((_x ^ 185) - 9) % 256 ^ 164 for _x in [89, 99, 105, 105, 115, 89, 89]]).decode():
                        final_report[bytes([((_x ^ 171) - 41) % 256 ^ 136 for _x in [161, 164, 143, 142, 185, 166, 166]]).decode()][bytes([((_x ^ 210) - 82) % 256 ^ 77 for _x in [66, 88, 82, 82, 168, 66, 66]]).decode()] += 1
                    else:
                        final_report[bytes([((_x ^ 199) - 43) % 256 ^ 127 for _x in [134, 251, 240, 241, 142, 249, 249]]).decode()][bytes([((_x ^ 123) - 103) % 256 ^ 71 for _x in [243, 246, 238, 233]]).decode()] += 1
            summary_lines = []
            if is_update_action:
                s = final_report[bytes([((_x ^ 85) - 45) % 256 ^ 52 for _x in [59, 36, 40, 215, 56, 43]]).decode()][bytes([((_x ^ 160) - 41) % 256 ^ 172 for _x in [168, 162, 88, 88, 82, 168, 168]]).decode()]
                f = final_report[bytes([((_x ^ 16) - 62) % 256 ^ 93 for _x in [118, 123, 103, 106, 119, 102]]).decode()][bytes([((_x ^ 44) - 21) % 256 ^ 185 for _x in [216, 193, 201, 198]]).decode()]
                skip = len(report[bytes([((_x ^ 5) - 89) % 256 ^ 39 for _x in [174, 181, 153, 154, 169, 158]]).decode()].get(bytes([((_x ^ 99) - 9) % 256 ^ 110 for _x in [69, 109, 115, 68, 68, 119, 112]]).decode(), []))
                summary_lines.append(f'--- Update ---\nSuccess: {s} | Failed: {f} | Skipped: {skip}')
            if is_install_action:
                s = final_report[bytes([((_x ^ 51) - 46) % 256 ^ 242 for _x in [250, 249, 156, 135, 242, 255, 255]]).decode()][bytes([((_x ^ 168) - 12) % 256 ^ 142 for _x in [161, 175, 81, 81, 95, 161, 161]]).decode()]
                f = final_report[bytes([((_x ^ 157) - 66) % 256 ^ 97 for _x in [215, 204, 201, 202, 223, 210, 210]]).decode()][bytes([((_x ^ 129) - 4) % 256 ^ 180 for _x in [87, 88, 96, 93]]).decode()]
                skip = len(report[bytes([((_x ^ 184) - 8) % 256 ^ 193 for _x in [8, 15, 2, 5, 16, 13, 13]]).decode()].get(bytes([((_x ^ 224) - 55) % 256 ^ 85 for _x in [189, 149, 147, 188, 188, 135, 136]]).decode(), []))
                summary_lines.append(f'--- Install ---\nSuccess: {s} | Failed: {f} | Skipped: {skip}')
            final_message = '\n\n'.join(summary_lines) if summary_lines else bytes([((_x ^ 253) - 4) % 256 ^ 157 for _x in [42, 11, 60, 16, 253, 15, 7, 15, 60, 19, 1, 14, 1, 60, 12, 1, 14, 2, 11, 14, 9, 1, 0, 74]]).decode()
            self.is_processing = False
            self.install_worker = None
            if len(str(id(object()))) > 50:
                _j53c25e = id(None) & 0
            self.show_styled_message_box(QMessageBox.Icon.Information, bytes([((_x ^ 203) - 65) % 256 ^ 63 for _x in [118, 90, 88, 91, 95, 80, 71, 80, 171, 71, 83, 80, 171, 86, 90, 88, 88, 84, 89, 87, 152, 95, 92, 89, 80, 171, 71, 84, 70, 94]]).decode(), final_message)
            if id(object()) & 255 > 255:
                _j5d6f29 = id(None) & 0
            QApplication.quit()
        try:
            self.install_worker.tasks_batch_completed.disconnect()
            self.install_worker.finished.disconnect()
        except Exception:
            pass
        if id(object()) ^ id(object()) < 0:
            _j10dc3a = id(None) & 0
        self.install_worker.progress.connect(self.update_and_record_progress, Qt.ConnectionType.QueuedConnection)
        self.install_worker.progress_percentage.connect(self.update_download_progress_anywhere, Qt.ConnectionType.QueuedConnection)
        self.install_worker.tasks_batch_completed.connect(self.on_tasks_batch_completed, Qt.ConnectionType.QueuedConnection)
        self.install_worker.finished.connect(on_cli_finished, Qt.ConnectionType.QueuedConnection)
        self.install_worker.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, bytes([((_x ^ 33) - 16) % 256 ^ 93 for _x in [9, 30, 30, 99, 30, 172, 59, 99, 30, 103, 105, 30]]).decode(), str(e)), Qt.ConnectionType.QueuedConnection)
        self.install_worker.update_widget_status.connect(self.update_widget_status, Qt.ConnectionType.QueuedConnection)
        self.install_worker.start()

    def update_and_record_progress(self, app_key, status, message):
        pass
        if getattr(__import__('time'), 'time')() < 0:
            _jb8cce3 = id(None) & 0
        self.update_install_progress(app_key, status, message)
        if len(str(id(object()))) > 50:
            _j4a4124 = id(None) & 0
        if self.is_cli_mode and status in [bytes([((_x ^ 94) - 54) % 256 ^ 211 for _x in [136, 130, 184, 184, 178, 136, 136]]).decode(), bytes([((_x ^ 128) - 125) % 256 ^ 30 for _x in [117, 124, 116, 111, 120, 119]]).decode(), bytes([((_x ^ 12) - 100) % 256 ^ 76 for _x in [175, 144, 139, 172, 172, 129, 128]]).decode()]:
            if self.install_worker and app_key in self.install_worker.worker_tasks:
                original_action = self.install_worker.worker_tasks[app_key][bytes([((_x ^ 148) - 114) % 256 ^ 232 for _x in [111, 105, 154, 103, 109, 108]]).decode()]
                if original_action == bytes([((_x ^ 167) - 95) % 256 ^ 47 for _x in [30, 25, 13, 10, 29, 14]]).decode():
                    if status == bytes([((_x ^ 45) - 74) % 256 ^ 24 for _x in [229, 238, 150, 147, 234, 235]]).decode() and message == bytes([((_x ^ 23) - 110) % 256 ^ 97 for _x in [132, 107, 147, 106, 108, 107, 121, 100, 101, 100, 184, 98, 121, 97, 108, 101, 100]]).decode():
                        self.cli_task_results[app_key] = {bytes([((_x ^ 98) - 61) % 256 ^ 101 for _x in [49, 44, 35, 44, 47, 49]]).decode(): bytes([((_x ^ 107) - 93) % 256 ^ 34 for _x in [202, 203, 195, 192, 207, 200]]).decode(), bytes([((_x ^ 134) - 84) % 256 ^ 230 for _x in [93, 95, 96, 101, 91, 90]]).decode(): bytes([((_x ^ 114) - 3) % 256 ^ 244 for _x in [246, 245, 225, 234, 241, 230]]).decode()}
                    elif status == bytes([((_x ^ 239) - 27) % 256 ^ 145 for _x in [253, 228, 252, 247, 224, 255]]).decode():
                        self.cli_task_results[app_key] = {bytes([((_x ^ 139) - 126) % 256 ^ 9 for _x in [115, 112, 109, 112, 113, 115]]).decode(): bytes([((_x ^ 5) - 79) % 256 ^ 102 for _x in [74, 83, 91, 92, 87, 84]]).decode(), bytes([((_x ^ 15) - 60) % 256 ^ 202 for _x in [232, 234, 245, 208, 238, 239]]).decode(): bytes([((_x ^ 240) - 77) % 256 ^ 168 for _x in [254, 227, 216, 217, 230, 225, 225]]).decode()}
                    elif status == bytes([((_x ^ 221) - 32) % 256 ^ 43 for _x in [165, 163, 181, 181, 179, 165, 165]]).decode():
                        is_install_requested = bytes([((_x ^ 118) - 101) % 256 ^ 134 for _x in [120, 34, 59, 44, 33, 58, 57, 57]]).decode() in self.cli_args
                        self.cli_task_results[f'{app_key}_update'] = {bytes([((_x ^ 105) - 109) % 256 ^ 126 for _x in [19, 30, 229, 30, 17, 19]]).decode(): bytes([((_x ^ 40) - 93) % 256 ^ 34 for _x in [134, 156, 182, 182, 140, 134, 134]]).decode(), bytes([((_x ^ 215) - 91) % 256 ^ 194 for _x in [41, 43, 198, 209, 223, 208]]).decode(): bytes([((_x ^ 113) - 119) % 256 ^ 35 for _x in [188, 187, 207, 200, 191, 204]]).decode()}
                        if is_install_requested:
                            self.cli_task_results[f'{app_key}_install'] = {bytes([((_x ^ 254) - 101) % 256 ^ 230 for _x in [4, 9, 18, 9, 6, 4]]).decode(): bytes([((_x ^ 99) - 122) % 256 ^ 185 for _x in [39, 37, 55, 55, 53, 39, 39]]).decode(), bytes([((_x ^ 89) - 56) % 256 ^ 144 for _x in [112, 114, 69, 104, 110, 111]]).decode(): bytes([((_x ^ 75) - 8) % 256 ^ 238 for _x in [196, 195, 238, 233, 220, 193, 193]]).decode()}
                elif original_action == bytes([((_x ^ 165) - 95) % 256 ^ 143 for _x in [224, 229, 254, 255, 232, 231, 231]]).decode():
                    self.cli_task_results[app_key] = {bytes([((_x ^ 95) - 71) % 256 ^ 159 for _x in [108, 109, 26, 109, 110, 108]]).decode(): status, bytes([((_x ^ 155) - 1) % 256 ^ 197 for _x in [62, 60, 41, 54, 48, 55]]).decode(): bytes([((_x ^ 87) - 59) % 256 ^ 158 for _x in [101, 124, 127, 114, 109, 122, 122]]).decode()}

    def setup_ui(self):
        self.setWindowTitle(f'{APP_NAME} - v{APP_VERSION}')
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet('\n            QMainWindow { background-color: #2c3e50; }\n            QLabel { color: #ecf0f1; font-size: 10pt; }\n            QListWidget { background-color: #34495e; border: 1px solid #2c3e50; color: #ecf0f1; font-size: 11pt; }\n            QListWidget::item { padding: 5px; border-bottom: 1px solid #2c3e50; }\n            QListWidget::item:hover { background-color: #4a627a; }\n            QPushButton { background-color: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }\n            QPushButton:hover { background-color: #2980b9; }\n            QPushButton:disabled { background-color: #95a5a6; }\n            QLineEdit { background-color: #34495e; border: 1px solid #2c3e50; padding: 8px; border-radius: 4px; color: white; }\n            QComboBox { background-color: #34495e; border: 1px solid #2c3e50; padding: 5px; border-radius: 4px; color: white; min-width: 150px; }\n            QComboBox::drop-down { border: none; }\n            QComboBox QAbstractItemView { background-color: #34495e; color: white; selection-background-color: #4a627a; }\n            QToolTip { background-color: #34495e; color: white; border: 1px solid #3498db; }\n        ')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        panels_layout = QHBoxLayout()
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(5)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(bytes([((_x ^ 201) - 49) % 256 ^ 214 for _x in [127, 45, 33, 28, 47, 38, 238, 230, 0, 33, 37, 45, 226, 238, 10, 45, 31, 47, 28, 57, 30, 26, 57, 35, 32, 249, 224, 224, 224]]).decode())
        self.category_filter = CheckableComboBox()
        self.category_filter.setToolTip(bytes([((_x ^ 32) - 37) % 256 ^ 170 for _x in [62, 212, 203, 212, 206, 35, 143, 206, 208, 35, 212, 210, 202, 221, 200, 212, 222, 143, 35, 202, 143, 209, 200, 203, 35, 212, 221, 143, 205, 216]]).decode())
        self.clear_search_button = QPushButton('X')
        button_height = self.search_box.sizeHint().height()
        self.clear_search_button.setFixedSize(button_height, button_height)
        self.clear_search_button.setStyleSheet(bytes([((_x ^ 142) - 3) % 256 ^ 204 for _x in [71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 46, 17, 50, 76, 41, 31, 50, 53, 53, 40, 43, 97, 52, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 49, 62, 37, 37, 38, 43, 32, 119, 97, 113, 49, 57, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 42, 62, 79, 32, 38, 43, 119, 97, 113, 49, 57, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 35, 40, 43, 53, 106, 48, 34, 38, 32, 41, 53, 119, 97, 63, 40, 45, 37, 116, 97, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 35, 40, 43, 53, 106, 76, 38, 55, 34, 119, 97, 142, 113, 49, 53, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 60, 40, 45, 40, 79, 119, 97, 48, 41, 38, 53, 34, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 63, 62, 60, 36, 32, 79, 40, 50, 43, 37, 106, 60, 40, 45, 40, 79, 119, 97, 124, 140, 117, 117, 118, 114, 34, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 63, 40, 79, 37, 34, 79, 119, 97, 142, 49, 57, 97, 76, 40, 45, 38, 37, 97, 124, 143, 60, 140, 34, 114, 113, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 63, 40, 79, 37, 34, 79, 106, 45, 34, 35, 53, 119, 97, 142, 49, 57, 97, 76, 40, 45, 38, 37, 97, 124, 117, 62, 115, 143, 112, 62, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 104, 103, 97, 31, 40, 97, 53, 79, 156, 15, 43, 97, 32, 156, 12, 60, 97, 49, 41, 190, 247, 252, 38, 97, 133, 238, 190, 244, 220, 97, 36, 41, 190, 244, 212, 49, 97, 51, 190, 244, 212, 38, 97, 156, 245, 97, 76, 34, 62, 79, 60, 41, 97, 103, 104, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 63, 40, 79, 37, 34, 79, 106, 53, 40, 49, 106, 45, 34, 35, 53, 106, 79, 62, 37, 38, 50, 76, 119, 97, 113, 49, 57, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 63, 40, 79, 37, 34, 79, 106, 63, 40, 53, 53, 40, 42, 106, 45, 34, 35, 53, 106, 79, 62, 37, 38, 50, 76, 119, 97, 113, 49, 57, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 63, 40, 79, 37, 34, 79, 106, 53, 40, 49, 106, 79, 38, 32, 41, 53, 106, 79, 62, 37, 38, 50, 76, 119, 97, 117, 49, 57, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 63, 40, 79, 37, 34, 79, 106, 63, 40, 53, 53, 40, 42, 106, 79, 38, 32, 41, 53, 106, 79, 62, 37, 38, 50, 76, 119, 97, 117, 49, 57, 116, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 58, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 46, 17, 50, 76, 41, 31, 50, 53, 53, 40, 43, 119, 41, 40, 51, 34, 79, 97, 52, 97, 63, 62, 60, 36, 32, 79, 40, 50, 43, 37, 106, 60, 40, 45, 40, 79, 119, 97, 124, 60, 113, 140, 118, 143, 63, 116, 97, 58, 71, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 97, 46, 17, 50, 76, 41, 31, 50, 53, 53, 40, 43, 119, 49, 79, 34, 76, 76, 34, 37, 97, 52, 97, 63, 62, 60, 36, 32, 79, 40, 50, 43, 37, 106, 60, 40, 45, 40, 79, 119, 97, 124, 34, 112, 117, 60, 140, 60, 116, 97, 58, 71, 97, 97, 97, 97, 97, 97, 97, 97]]).decode())
        self.clear_search_button.hide()
        search_layout.addWidget(self.search_box, 1)
        search_layout.addWidget(self.category_filter)
        search_layout.addWidget(self.clear_search_button)
        self.search_box.textChanged.connect(self.filter_apps)
        self.search_box.textChanged.connect(lambda text: self.clear_search_button.setVisible(bool(text)))
        self.clear_search_button.clicked.connect(self.search_box.clear)
        self.category_filter.checkedItemsChanged.connect(lambda: self.filter_apps(self.search_box.text()))
        left_layout.addLayout(search_layout)
        self.available_count_label = QLabel(bytes([((_x ^ 183) - 106) % 256 ^ 44 for _x in [85, 26, 117, 0, 29, 193, 27, 116, 28, 15, 4, 127, 193, 26, 3, 193, 126, 26, 3, 117, 114, 0, 127, 4, 193, 113, 127, 26, 2, 127, 0, 28, 126, 55, 193, 49]]).decode())
        self.available_list_widget = QListWidget()
        left_layout.addWidget(self.available_count_label)
        left_layout.addWidget(self.available_list_widget)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.selected_count_label = QLabel(bytes([((_x ^ 38) - 65) % 256 ^ 91 for _x in [111, 89, 94, 89, 95, 86, 89, 166, 132, 154, 138]]).decode())
        self.selected_list_widget = QListWidget()
        right_layout.addWidget(self.selected_count_label)
        right_layout.addWidget(self.selected_list_widget)
        panels_layout.addWidget(left_panel)
        panels_layout.addWidget(right_panel)
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.start_button = QPushButton(bytes([((_x ^ 46) - 98) % 256 ^ 136 for _x in [19, 16, 5, 18, 16, 36, 13, 6, 19, 16, 5, 8, 8, 5, 16, 13, 7, 6]]).decode())
        self.start_button.clicked.connect(self.start_installation)
        self.start_button.setMinimumHeight(40)
        self.status_label = QLabel(bytes([((_x ^ 252) - 28) % 256 ^ 49 for _x in [130, 157, 144, 157, 156, 162, 219, 209, 131, 140, 144, 141, 152]]).decode())
        bottom_layout.addWidget(self.status_label, 1)
        bottom_layout.addWidget(self.start_button)
        if id(object()) ^ id(object()) < 0:
            _j97fe47 = id(None) & 0
        main_layout.addLayout(panels_layout)
        if hash(frozenset()) > __import__('sys').maxsize:
            _j0f381d = id(None) & 0
        main_layout.addWidget(bottom_panel)

    def set_ui_interactive(self, enabled):
        self.search_box.setEnabled(enabled)
        if id(object()) & 255 > 255:
            _jc3f254 = id(None) & 0
        self.available_list_widget.setEnabled(enabled)
        if len(str(id(object()))) > 50:
            _jb0bd61 = id(None) & 0
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            widget = self.selected_list_widget.itemWidget(item)
            if hasattr(widget, bytes([((_x ^ 237) - 110) % 256 ^ 170 for _x in [212, 218, 161, 220, 222, 223, 142, 219, 160, 161, 161, 222, 223]]).decode()):
                if not enabled:
                    widget.action_button.hide()
                    widget.set_status(bytes([((_x ^ 224) - 4) % 256 ^ 195 for _x in [87, 85, 80, 68, 74, 84, 84, 78, 81, 72]]).decode())
                else:
                    widget.action_button.show()
                    widget.set_status('')
        if not enabled:
            self.start_button.setText(bytes([((_x ^ 35) - 49) % 256 ^ 215 for _x in [150, 151, 234, 155]]).decode())
            self.start_button.setEnabled(True)
            self.start_button.setStyleSheet(bytes([((_x ^ 75) - 81) % 256 ^ 177 for _x in [111, 106, 104, 96, 108, 95, 100, 94, 123, 109, 166, 104, 100, 101, 100, 95, 151, 169, 168, 110, 156, 157, 104, 152, 104, 144, 169, 104, 100, 101, 100, 95, 151, 169, 92, 97, 98, 93, 110, 144]]).decode())
        else:
            self.start_button.setText(bytes([((_x ^ 237) - 58) % 256 ^ 138 for _x in [254, 245, 232, 255, 245, 9, 16, 19, 254, 245, 232, 237, 237, 232, 245, 16, 18, 19]]).decode())
            self.start_button.setStyleSheet(bytes([((_x ^ 192) - 80) % 256 ^ 183 for _x in [229, 230, 228, 236, 224, 213, 232, 210, 233, 227, 42, 228, 232, 235, 232, 213, 29, 39, 36, 20, 19, 30, 31, 227, 229, 28, 39, 228, 232, 235, 232, 213, 29, 39, 208, 239, 238, 211, 226, 28]]).decode())

    def load_config_and_apps(self, populate=True):
        pass
        if len(str(id(object()))) > 50:
            _j2e9518 = id(None) & 0
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding=bytes([((_x ^ 141) - 21) % 256 ^ 199 for _x in [74, 69, 59, 114, 153]]).decode()) as f:
                    content = f.read()
                    self.config = json.loads(content) if content else {}
            except json.JSONDecodeError:
                self.config = {}
        else:
            self.config = {bytes([((_x ^ 83) - 29) % 256 ^ 63 for _x in [58, 36, 59, 59, 32, 61, 38, 58]]).decode(): {}, bytes([((_x ^ 237) - 9) % 256 ^ 189 for _x in [8, 59, 59, 6, 48, 63, 12, 52, 58]]).decode(): {}}
            with open(CONFIG_FILE, 'w', encoding=bytes([((_x ^ 55) - 23) % 256 ^ 77 for _x in [120, 103, 117, 64, 187]]).decode()) as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        self.config.setdefault(bytes([((_x ^ 7) - 76) % 256 ^ 168 for _x in [32, 30, 47, 47, 10, 21, 28, 32]]).decode(), {})
        self.config.setdefault(bytes([((_x ^ 184) - 15) % 256 ^ 206 for _x in [6, 117, 117, 24, 14, 113, 2, 10, 116]]).decode(), {})
        self.local_apps = self.config.get(bytes([((_x ^ 4) - 52) % 256 ^ 230 for _x in [191, 206, 206, 233, 199, 194, 179, 187, 205]]).decode(), {})
        if id(object()) ^ id(object()) < 0:
            _j5907d8 = id(None) & 0
        if not self.embed_mode:
            self.selected_for_install = self.config.get(bytes([((_x ^ 1) - 51) % 256 ^ 91 for _x in [90, 112, 99, 99, 100, 105, 110, 90]]).decode(), {}).get(bytes([((_x ^ 148) - 122) % 256 ^ 56 for _x in [81, 67, 90, 67, 65, 82, 67, 66, 117, 76, 69, 80, 117, 95, 68, 81, 82, 71, 90, 90]]).decode(), [])
            if not isinstance(self.selected_for_install, list):
                self.selected_for_install = []

    def update_single_app_widget(self, app_key):
        pass
        widget = self.find_widget_by_key(app_key)
        if not widget:
            print(f'Không tìm thấy widget cho {app_key} để cập nhật.')
            return
        app_info = self.remote_apps.get(bytes([((_x ^ 246) - 62) % 256 ^ 235 for _x in [62, 47, 47, 4, 54, 43, 58, 50, 32]]).decode(), {}).get(app_key, {})
        local_info = self.local_apps.get(app_key, {})
        app_info.update(local_info)
        widget.app_info = app_info
        is_downloaded = self.is_app_downloaded(app_key, app_info)
        local_ver_str = local_info.get(bytes([((_x ^ 201) - 44) % 256 ^ 220 for _x in [31, 44, 19, 18, 40, 22, 23]]).decode(), '0')
        remote_ver_str = self.remote_apps.get(bytes([((_x ^ 75) - 43) % 256 ^ 46 for _x in [49, 194, 194, 215, 57, 206, 61, 37, 195]]).decode(), {}).get(app_key, {}).get(bytes([((_x ^ 96) - 76) % 256 ^ 57 for _x in [251, 200, 247, 246, 252, 194, 195]]).decode(), '0')
        is_update_available = is_downloaded and parse_version(remote_ver_str) > parse_version(local_ver_str)
        if id(object()) * 3 % 19 == 19:
            _j7c123c = id(None) & 0
        widget.version_label.setText(f"Version: {app_info.get('version', 'N/A')}")
        if id(object()) * 3 % 19 == 19:
            _j4b5574 = id(None) & 0
        widget.version_label.setStyleSheet(bytes([((_x ^ 110) - 14) % 256 ^ 221 for _x in [162, 174, 209, 174, 211, 155, 101, 98, 163, 169, 162, 146, 162, 150, 154, 101, 167, 174, 175, 217, 144, 210, 172, 219, 168, 155, 101, 148, 149, 213, 217, 154]]).decode())
        if is_update_available:
            widget.version_label.setText(f'Update: {local_ver_str} -> {remote_ver_str}')
            widget.version_label.setStyleSheet(bytes([((_x ^ 171) - 78) % 256 ^ 85 for _x in [47, 35, 44, 35, 222, 22, 104, 111, 30, 213, 47, 47, 27, 25, 23, 104, 42, 35, 34, 196, 109, 219, 213, 33, 43, 32, 196, 22, 104, 46, 35, 44, 212, 23]]).decode())
        try:
            widget.action_button.clicked.disconnect()
        except (TypeError, RuntimeError):
            pass
        if self.embed_mode:
            is_auto = self.local_apps.get(app_key, {}).get(bytes([((_x ^ 68) - 76) % 256 ^ 127 for _x in [46, 18, 19, 24, 40, 38, 25, 28, 19, 46, 27, 27]]).decode(), False)
            if is_auto:
                widget.set_auto_install_button_state(True)
                widget.action_button.clicked.connect(lambda: self.on_auto_install_toggled(app_key, False))
            else:
                widget.set_auto_install_button_state(False)
                on_add_action = lambda: self.on_auto_install_toggled(app_key, True)
                if is_update_available:
                    widget.action_button.clicked.connect(lambda _, k=app_key, i=app_info, w=widget, lv=local_ver_str, rv=remote_ver_str, cb=on_add_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
                else:
                    widget.action_button.clicked.connect(on_add_action)
        elif app_info.get(bytes([((_x ^ 156) - 99) % 256 ^ 163 for _x in [166, 161, 170, 181]]).decode(), '').lower() == bytes([((_x ^ 251) - 116) % 256 ^ 62 for _x in [57, 62, 59, 69, 40, 43, 61, 52]]).decode():
            widget.action_button.setText(bytes([((_x ^ 115) - 49) % 256 ^ 151 for _x in [133, 96, 89]]).decode())
            widget.action_button.setToolTip(f"Run {app_info['display_name']} direct")
            widget.action_button.setStyleSheet(bytes([((_x ^ 95) - 11) % 256 ^ 233 for _x in [201, 204, 202, 210, 198, 249, 206, 248, 205, 199, 144, 202, 206, 207, 206, 249, 129, 139, 138, 186, 183, 132, 131, 199, 201, 130, 139, 202, 206, 207, 206, 249, 129, 139, 246, 211, 212, 247, 200, 130]]).decode())
            on_run_action = lambda: self.run_portable_app(app_key, app_info)
            if is_update_available:
                widget.action_button.clicked.connect(lambda _, k=app_key, i=app_info, w=widget, lv=local_ver_str, rv=remote_ver_str, cb=on_run_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
            else:
                widget.action_button.clicked.connect(on_run_action)
        else:
            widget.action_button.setText(bytes([((_x ^ 196) - 47) % 256 ^ 66 for _x in [246, 145, 145]]).decode())
            widget.action_button.setToolTip(f"Add {app_info['display_name']} to the list")
            widget.action_button.setStyleSheet(bytes([((_x ^ 173) - 115) % 256 ^ 144 for _x in [200, 201, 203, 195, 199, 248, 223, 245, 220, 202, 157, 203, 223, 194, 223, 248, 176, 142, 139, 186, 235, 233, 228, 181, 190, 179, 142, 203, 223, 194, 223, 248, 176, 142, 247, 198, 193, 250, 197, 179]]).decode())
            on_complete_action = lambda: self.move_app_to_selection(app_key, app_info)
            if is_update_available:
                widget.action_button.clicked.connect(lambda _, k=app_key, i=app_info, w=widget, lv=local_ver_str, rv=remote_ver_str, cb=on_complete_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
            else:
                widget.action_button.clicked.connect(on_complete_action)

    def populate_lists(self):
        if hasattr(self, bytes([((_x ^ 135) - 54) % 256 ^ 44 for _x in [46, 21, 254, 21, 8, 241, 4, 9, 248, 46, 9, 252, 240, 248, 19]]).decode()):
            self._populate_timer.stop()
        if self.is_processing:
            return
        self.save_scroll_positions()
        self.available_list_widget.clear()
        if not self.embed_mode:
            self.selected_list_widget.clear()
        if hasattr(self, bytes([((_x ^ 136) - 24) % 256 ^ 243 for _x in [32, 34, 23, 38, 36, 60, 17, 42, 76, 37, 58, 63, 23, 38, 17]]).decode()):
            self.category_filter.clear_items()
        all_apps = self.remote_apps.get(bytes([((_x ^ 244) - 85) % 256 ^ 116 for _x in [158, 173, 173, 116, 134, 161, 146, 154, 168]]).decode(), {})
        compatible_apps = {}
        if self.system_arch == bytes([((_x ^ 24) - 30) % 256 ^ 32 for _x in [44, 42, 120, 127, 106]]).decode():
            compatible_apps = all_apps.copy()
        else:
            for key, app_info in all_apps.items():
                compatible_os_arch = app_info.get(bytes([((_x ^ 152) - 108) % 256 ^ 75 for _x in [12, 8, 10, 63, 14, 51, 22, 13, 11, 2, 24, 8, 60, 24, 14, 61, 12, 23]]).decode(), bytes([((_x ^ 147) - 53) % 256 ^ 72 for _x in [204, 207, 226, 198]]).decode())
                if compatible_os_arch in [bytes([((_x ^ 13) - 112) % 256 ^ 214 for _x in [88, 89, 41, 34, 31]]).decode(), bytes([((_x ^ 195) - 25) % 256 ^ 8 for _x in [64, 67, 86, 186]]).decode()]:
                    compatible_apps[key] = app_info.copy()
        for key, local_info in self.local_apps.items():
            if key in compatible_apps:
                compatible_apps[key].update(local_info)
        categories = sorted(list(set((app.get(bytes([((_x ^ 232) - 105) % 256 ^ 29 for _x in [15, 13, 58, 9, 11, 51, 48, 37]]).decode(), bytes([((_x ^ 203) - 113) % 256 ^ 71 for _x in [72, 81, 94, 92, 111, 88, 90, 82, 109, 84, 101, 88, 95]]).decode()) for app in compatible_apps.values()))))
        if hasattr(self, bytes([((_x ^ 172) - 81) % 256 ^ 26 for _x in [102, 96, 19, 124, 98, 106, 21, 24, 58, 97, 104, 107, 19, 124, 21]]).decode()):
            for category in categories:
                self.category_filter.add_item(category)
        if len(str(id(object()))) > 50:
            _j03ae7b = id(None) & 0
        for category in categories:
            cat_item = QListWidgetItem(category.upper())
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            font = QFont()
            font.setBold(True)
            cat_item.setFont(font)
            cat_item.setForeground(QColor(bytes([((_x ^ 98) - 55) % 256 ^ 28 for _x in [20, 4, 61, 62, 57, 205, 215]]).decode()))
            self.available_list_widget.addItem(cat_item)
            for key, info in sorted(compatible_apps.items(), key=lambda item: item[1].get(bytes([((_x ^ 232) - 28) % 256 ^ 175 for _x in [15, 10, 16, 19, 55, 2, 26, 228, 53, 2, 54, 14]]).decode(), '')):
                if info.get(bytes([((_x ^ 220) - 6) % 256 ^ 5 for _x in [176, 182, 171, 186, 180, 172, 161, 94]]).decode(), bytes([((_x ^ 105) - 64) % 256 ^ 182 for _x in [74, 113, 124, 126, 107, 122, 120, 112, 109, 118, 101, 122, 123]]).decode()) == category:
                    self.add_app_to_list(self.available_list_widget, key, info)
        if not self.embed_mode:
            valid_selected = []
            if self.is_cli_mode:
                valid_selected = [key for key in self.cli_target_apps if key in compatible_apps]
            else:
                valid_selected = [key for key in self.selected_for_install if key in compatible_apps]
            self.selected_for_install = valid_selected
            for key in valid_selected:
                app_info_to_move = compatible_apps.get(key)
                if app_info_to_move:
                    self.move_app_to_selection(key, app_info_to_move)
        self.update_counts()
        self.restore_scroll_positions()
        if id(object()) ^ id(object()) < 0:
            _ja4d281 = id(None) & 0
        self.filter_apps(self.search_box.text())

    def add_app_to_list(self, list_widget, key, info):
        item_widget = AppItemWidget(key, info, embed_mode=self.embed_mode)
        is_downloaded = self.is_app_downloaded(key, info)
        local_ver_str = self.local_apps.get(key, {}).get(bytes([((_x ^ 26) - 33) % 256 ^ 225 for _x in [162, 191, 174, 169, 179, 181, 170]]).decode(), '0')
        remote_ver_str = self.remote_apps.get(bytes([((_x ^ 66) - 2) % 256 ^ 193 for _x in [224, 241, 241, 226, 232, 245, 228, 236, 246]]).decode(), {}).get(key, {}).get(bytes([((_x ^ 71) - 2) % 256 ^ 249 for _x in [214, 217, 202, 203, 213, 223, 222]]).decode(), '0')
        is_update_available = False
        if info.get(bytes([((_x ^ 194) - 87) % 256 ^ 212 for _x in [53, 198, 57, 202]]).decode()) != bytes([((_x ^ 46) - 89) % 256 ^ 154 for _x in [96, 123, 123, 98, 124, 118, 48, 108, 102, 98, 105, 118]]).decode():
            is_update_available = is_downloaded and parse_version(remote_ver_str) > parse_version(local_ver_str)
        if is_update_available:
            item_widget.version_label.setText(f'Update: {local_ver_str} -> {remote_ver_str}')
            item_widget.version_label.setStyleSheet(bytes([((_x ^ 70) - 68) % 256 ^ 35 for _x in [194, 214, 213, 214, 211, 27, 1, 2, 19, 204, 194, 194, 30, 16, 26, 1, 207, 214, 215, 221, 20, 222, 204, 200, 206, 201, 221, 27, 1, 195, 214, 213, 205, 26]]).decode())
        item_widget.action_button.clicked.disconnect()
        if not is_downloaded:
            item_widget.action_button.setText(bytes([((_x ^ 127) - 43) % 256 ^ 71 for _x in [81, 44, 36, 43, 41, 44, 46, 49]]).decode())
            item_widget.action_button.setToolTip(f"Download {info['display_name']}")
            item_widget.action_button.setStyleSheet(bytes([((_x ^ 152) - 103) % 256 ^ 242 for _x in [111, 98, 96, 152, 100, 127, 156, 118, 155, 101, 222, 96, 156, 157, 156, 127, 183, 161, 160, 99, 176, 170, 96, 178, 191, 168, 161, 96, 156, 157, 156, 127, 183, 161, 116, 153, 154, 117, 102, 168]]).decode())
            item_widget.action_button.clicked.connect(lambda _, k=key, i=info, w=item_widget: self.confirm_download(k, i, w))
        elif self.embed_mode:
            is_auto = self.local_apps.get(key, {}).get(bytes([((_x ^ 1) - 99) % 256 ^ 90 for _x in [159, 147, 144, 153, 105, 151, 150, 141, 144, 159, 152, 152]]).decode(), False)
            if is_auto:
                item_widget.set_auto_install_button_state(True)
                item_widget.action_button.clicked.connect(lambda _, w=item_widget, k=key: (w.auto_install_toggled.emit(k, False), w.set_auto_install_button_state(False)))
            else:
                item_widget.set_auto_install_button_state(False)
                on_complete_action = lambda: item_widget.auto_install_toggled.emit(key, True)
                if is_update_available:
                    item_widget.action_button.clicked.connect(lambda _, k=key, i=info, w=item_widget, lv=local_ver_str, rv=remote_ver_str, cb=on_complete_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
                else:
                    item_widget.action_button.clicked.connect(lambda _, w=item_widget, k=key: (w.auto_install_toggled.emit(k, True), w.set_auto_install_button_state(True)))
            item_widget.auto_install_toggled.connect(self.on_auto_install_toggled)
        elif info.get(bytes([((_x ^ 184) - 48) % 256 ^ 95 for _x in [227, 238, 231, 210]]).decode(), '').lower() == bytes([((_x ^ 22) - 25) % 256 ^ 86 for _x in [41, 68, 43, 45, 70, 91, 69, 90]]).decode():
            item_widget.action_button.setText(bytes([((_x ^ 188) - 97) % 256 ^ 17 for _x in [24, 121, 92]]).decode())
            item_widget.action_button.setToolTip(f"Run {info['display_name']} direct")
            item_widget.action_button.setStyleSheet(bytes([((_x ^ 254) - 6) % 256 ^ 55 for _x in [165, 162, 164, 156, 168, 181, 160, 182, 161, 167, 222, 164, 160, 159, 160, 181, 237, 227, 228, 244, 247, 234, 235, 167, 165, 236, 227, 164, 160, 159, 160, 181, 237, 227, 184, 155, 154, 183, 166, 236]]).decode())
            on_run_action = lambda: self.run_portable_app(key, info)
            if is_update_available:
                item_widget.action_button.clicked.connect(lambda _, k=key, i=info, w=item_widget, lv=local_ver_str, rv=remote_ver_str, cb=on_run_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
            else:
                item_widget.action_button.clicked.connect(on_run_action)
        else:
            item_widget.action_button.setText(bytes([((_x ^ 54) - 34) % 256 ^ 139 for _x in [218, 39, 39]]).decode())
            item_widget.action_button.setToolTip(f"Add {info['display_name']} to the list")
            item_widget.action_button.setStyleSheet(bytes([((_x ^ 48) - 22) % 256 ^ 43 for _x in [111, 80, 110, 102, 82, 95, 106, 68, 107, 85, 44, 110, 106, 109, 106, 95, 23, 17, 46, 5, 78, 176, 179, 4, 1, 22, 17, 110, 106, 109, 106, 95, 23, 17, 66, 105, 104, 69, 84, 22]]).decode())
            on_complete_action = lambda: self.move_app_to_selection(key, info)
            if is_update_available:
                item_widget.action_button.clicked.connect(lambda _, k=key, i=info, w=item_widget, lv=local_ver_str, rv=remote_ver_str, cb=on_complete_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
            else:
                item_widget.action_button.clicked.connect(on_complete_action)
        list_item = QListWidgetItem()
        if getattr(__import__('time'), 'time')() < 0:
            _j0dc088 = id(None) & 0
        list_item.setSizeHint(QSize(0, 70))
        if abs(id(object()) - id(object())) < -1:
            _je39b31 = id(None) & 0
        list_item.setData(Qt.ItemDataRole.UserRole, key)
        list_widget.addItem(list_item)
        list_widget.setItemWidget(list_item, item_widget)
        if not self.embed_mode and key in self.selected_for_install:
            self.update_available_item_state(key, is_selected=True)

    def on_auto_install_toggled(self, key, state):
        pass
        if (id(object()) * 31 + 7) % 17 == 17:
            _jfc93b8 = id(None) & 0
        self.config.setdefault(bytes([((_x ^ 78) - 127) % 256 ^ 6 for _x in [168, 187, 187, 150, 160, 191, 172, 164, 186]]).decode(), {}).setdefault(key, {})
        self.config[bytes([((_x ^ 67) - 29) % 256 ^ 113 for _x in [110, 93, 93, 8, 118, 97, 114, 122, 92]]).decode()][key][bytes([((_x ^ 61) - 93) % 256 ^ 49 for _x in [144, 156, 159, 134, 246, 136, 129, 162, 159, 144, 135, 135]]).decode()] = state
        self.save_config()
        if self.embed_mode:
            self.update_single_app_widget(key)

    def find_widget_by_key(self, app_key):
        pass
        for _O0x56573B7D in range(self.available_list_widget.count()):
            _O0x021A0A84 = self.available_list_widget.item(_O0x56573B7D)
            if _O0x021A0A84.data(Qt.ItemDataRole.UserRole) == app_key:
                return self.available_list_widget.itemWidget(_O0x021A0A84)
        if hash(frozenset()) > __import__('sys').maxsize:
            _O0x9584D921 = id(None) & 0
        if not self.embed_mode:
            for _O0x56573B7D in range(self.selected_list_widget.count()):
                _O0x021A0A84 = self.selected_list_widget.item(_O0x56573B7D)
                if _O0x021A0A84.data(Qt.ItemDataRole.UserRole) == app_key:
                    return self.selected_list_widget.itemWidget(_O0x021A0A84)
        if hash(frozenset()) > __import__('sys').maxsize:
            _O0x0AC55B52 = id(None) & 0
        return None

    def update_widget_status(self, app_key, status):
        pass
        _O0x99689E8D = None
        if self.is_processing and (not self.embed_mode):
            _O0x99689E8D = self.find_widget_by_key(app_key, list_widget=self.selected_list_widget)
        else:
            _O0x99689E8D = self.find_widget_by_key(app_key, list_widget=self.available_list_widget)
        if _O0x99689E8D and _O0x99689E8D.parent():
            _O0x99689E8D.set_status(status, is_batch_install=self.is_processing)

    def confirm_download(self, key, info, widget):
        reply = self.show_styled_message_box(QMessageBox.Icon.Question, bytes([((_x ^ 230) - 90) % 256 ^ 232 for _x in [224, 7, 31, 6, 56, 7, 5, 0, 196, 16, 60, 1, 196, 19, 7, 14, 16, 31, 5, 18, 1]]).decode(), f"Do you want to download {info['display_name']}?", buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            worker = InstallWorker({key: {bytes([((_x ^ 228) - 80) % 256 ^ 114 for _x in [143, 136, 128, 137]]).decode(): info, bytes([((_x ^ 170) - 102) % 256 ^ 210 for _x in [179, 189, 166, 139, 137, 136]]).decode(): bytes([((_x ^ 124) - 16) % 256 ^ 152 for _x in [112, 123, 131, 122, 120, 123, 117, 112]]).decode()}}, parent=self)
            worker.tasks_batch_completed.connect(self.on_worker_finished)
            worker.progress.connect(self.update_install_progress)
            worker.progress_percentage.connect(self.update_download_progress_anywhere)
            worker.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, bytes([((_x ^ 220) - 110) % 256 ^ 140 for _x in [235, 176, 176, 141, 176, 198, 149, 141, 176, 137, 139, 176]]).decode(), str(e)))
            worker.update_widget_status.connect(self.update_widget_status)
            worker.finished.connect(worker.deleteLater)
            self.active_workers[key] = worker
            worker.start()

    def confirm_update(self, key, info, widget, local_ver, remote_ver, on_complete):
        reply = self.show_styled_message_box(QMessageBox.Icon.Question, bytes([((_x ^ 79) - 25) % 256 ^ 69 for _x in [102, 1, 117, 114, 5, 118, 49, 5, 9, 118, 49, 0, 12, 115, 5, 4, 114, 31, 118]]).decode(), f"A newer version of {info['display_name']} ({remote_ver}) is now available Current version: {local_ver}.\n\nDo you want to update?", buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if len(str(id(object()))) > 50:
            _j62dc69 = id(None) & 0
        if reply == QMessageBox.StandardButton.No:
            if on_complete:
                on_complete()
            return
        if id(object()) * 3 % 19 == 19:
            _j30ff08 = id(None) & 0
        if reply == QMessageBox.StandardButton.Yes:
            worker = InstallWorker({key: {bytes([((_x ^ 75) - 123) % 256 ^ 71 for _x in [226, 239, 215, 232]]).decode(): info, bytes([((_x ^ 53) - 8) % 256 ^ 58 for _x in [86, 84, 99, 110, 104, 105]]).decode(): bytes([((_x ^ 233) - 43) % 256 ^ 223 for _x in [60, 51, 15, 0, 63, 12]]).decode()}}, parent=self)

            def on_update_and_action(completed_items):
                self.on_worker_finished(completed_items)
                if on_complete:
                    QTimer.singleShot(50, on_complete)
            worker.progress.connect(self.update_install_progress)
            worker.progress_percentage.connect(self.update_download_progress_anywhere)
            worker.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, bytes([((_x ^ 10) - 69) % 256 ^ 64 for _x in [64, 125, 125, 126, 125, 175, 86, 126, 125, 122, 96, 125]]).decode(), str(e)))
            worker.update_widget_status.connect(self.update_widget_status)
            worker.tasks_batch_completed.connect(on_update_and_action)
            worker.finished.connect(worker.deleteLater)
            self.active_workers[key] = worker
            worker.start()

    def _update_office_selection_state(self):
        pass
        if abs(id(object()) - id(object())) < -1:
            _j752681 = id(None) & 0
        is_office_selected = any((self.remote_apps.get(bytes([((_x ^ 218) - 96) % 256 ^ 179 for _x in [232, 249, 249, 150, 224, 253, 236, 228, 250]]).decode(), {}).get(key, {}).get(bytes([((_x ^ 61) - 6) % 256 ^ 188 for _x in [243, 246, 239, 226]]).decode()) == bytes([((_x ^ 62) - 36) % 256 ^ 87 for _x in [98, 107, 107, 92, 102, 104, 18, 118, 120, 92, 121, 104]]).decode() for key in self.selected_for_install))
        if id(object()) ^ id(object()) < 0:
            _j0cf3de = id(None) & 0
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if hasattr(widget, bytes([((_x ^ 213) - 7) % 256 ^ 160 for _x in [29, 2, 2, 211, 5, 0, 24, 3]]).decode()) and widget.app_info.get(bytes([((_x ^ 191) - 66) % 256 ^ 138 for _x in [255, 138, 131, 142]]).decode()) == bytes([((_x ^ 221) - 107) % 256 ^ 136 for _x in [143, 132, 132, 145, 139, 133, 159, 187, 181, 145, 186, 133]]).decode():
                if is_office_selected and widget.app_key not in self.selected_for_install:
                    widget.action_button.setDisabled(True)
                    widget.action_button.setToolTip(bytes([((_x ^ 106) - 45) % 256 ^ 113 for _x in [1, 38, 32, 95, 20, 33, 38, 43, 20, 94, 43, 90, 69, 47, 33, 38, 20, 33, 46, 20, 1, 46, 46, 47, 85, 43, 20, 85, 87, 38, 20, 42, 43, 20, 69, 43, 32, 43, 85, 88, 43, 40, 20, 46, 33, 90, 20, 47, 38, 69, 88, 87, 32, 32, 87, 88, 47, 33, 38]]).decode())
                elif not is_office_selected:
                    widget.action_button.setDisabled(False)
                    is_downloaded = self.is_app_downloaded(widget.app_key, widget.app_info)
                    if is_downloaded:
                        widget.action_button.setText(bytes([((_x ^ 200) - 66) % 256 ^ 187 for _x in [244, 233, 233]]).decode())
                        widget.action_button.setToolTip(f"Add {widget.app_info['display_name']} to the list")
                        widget.action_button.setStyleSheet(bytes([((_x ^ 207) - 52) % 256 ^ 142 for _x in [239, 236, 238, 214, 210, 255, 218, 224, 219, 209, 24, 238, 218, 217, 218, 255, 39, 45, 46, 33, 206, 204, 51, 32, 61, 38, 45, 238, 218, 217, 218, 255, 39, 45, 226, 213, 212, 225, 208, 38]]).decode())
                    else:
                        widget.action_button.setText(bytes([((_x ^ 65) - 75) % 256 ^ 155 for _x in [107, 126, 118, 1, 3, 126, 4, 11]]).decode())
                        widget.action_button.setToolTip(f"Download {widget.app_info['display_name']}")
                        widget.action_button.setStyleSheet(bytes([((_x ^ 226) - 92) % 256 ^ 43 for _x in [71, 68, 70, 126, 74, 87, 66, 88, 67, 73, 128, 70, 66, 65, 66, 87, 143, 133, 134, 75, 150, 140, 70, 148, 151, 142, 133, 70, 66, 65, 66, 87, 143, 133, 90, 125, 124, 89, 72, 142]]).decode())

    def move_app_to_selection(self, key, info):
        if not isinstance(key, str) or not key:
            print(f'Lỗi: key không hợp lệ (không phải string hoặc rỗng): {key}. Bỏ qua di chuyển.')
            return
        app_info_latest = {}
        if isinstance(info, dict):
            app_info_latest.update(info)
        local_info = self.local_apps.get(key)
        if isinstance(local_info, dict):
            app_info_latest.update(local_info)
        if not app_info_latest:
            app_info_latest = self.remote_apps.get(bytes([((_x ^ 22) - 109) % 256 ^ 167 for _x in [37, 82, 82, 115, 45, 86, 57, 33, 87]]).decode(), {}).get(key, {})
            if not app_info_latest:
                print(f"Lỗi: Không tìm thấy thông tin cho '{key}' ở cả local và remote.")
                return
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            widget = self.selected_list_widget.itemWidget(item)
            if widget and getattr(widget, bytes([((_x ^ 46) - 79) % 256 ^ 6 for _x in [152, 235, 235, 134, 146, 156, 224]]).decode(), None) == key:
                return
        item_widget = AppItemWidget(key, app_info_latest)
        item_widget.action_button.setText(bytes([((_x ^ 157) - 78) % 256 ^ 37 for _x in [88, 19, 11, 5, 60, 19]]).decode())
        item_widget.action_button.setToolTip(f"Remove {app_info_latest.get('display_name', key)} from the list")
        item_widget.action_button.setStyleSheet(bytes([((_x ^ 1) - 74) % 256 ^ 45 for _x in [152, 151, 153, 145, 149, 168, 141, 163, 140, 146, 75, 153, 141, 138, 141, 168, 96, 86, 89, 147, 101, 98, 153, 105, 153, 97, 86, 153, 141, 138, 141, 168, 96, 86, 165, 142, 143, 162, 147, 97, 86, 152, 141, 168, 146, 147, 168, 96, 86, 140, 141, 140, 147, 97, 86, 166, 151, 146, 146, 143, 140, 149, 96, 86, 94, 166, 158, 86, 103, 100, 166, 158, 97, 86, 152, 141, 168, 146, 147, 168, 75, 168, 151, 146, 143, 163, 169, 96, 86, 98, 166, 158, 97, 86, 148, 141, 140, 162, 75, 165, 147, 143, 149, 142, 162, 96, 86, 152, 141, 138, 146, 97]]).decode())
        try:
            item_widget.action_button.clicked.disconnect()
        except Exception:
            pass
        item_widget.action_button.clicked.connect(lambda checked, k=key, i=app_info_latest: self.remove_app_from_selection(k, i))
        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(0, 70))
        list_item.setData(Qt.ItemDataRole.UserRole, key)
        self.selected_list_widget.addItem(list_item)
        self.selected_list_widget.setItemWidget(list_item, item_widget)
        if key not in self.selected_for_install:
            self.selected_for_install.append(key)
        self.save_config()
        if id(object()) * 3 % 19 == 19:
            _j425204 = id(None) & 0
        self.update_counts()
        self.update_available_item_state(key, is_selected=True)
        if id(object()) * 3 % 19 == 19:
            _j92c1f6 = id(None) & 0
        self._update_office_selection_state()

    def remove_app_from_selection(self, key, info):
        for _O0x8B2AFD93 in range(self.selected_list_widget.count() - 1, -1, -1):
            _O0x7533ACBE = self.selected_list_widget.item(_O0x8B2AFD93)
            if _O0x7533ACBE.data(Qt.ItemDataRole.UserRole) == key:
                self.selected_list_widget.takeItem(_O0x8B2AFD93)
                break
        if key in self.selected_for_install:
            self.selected_for_install.remove(key)
        self.save_config()
        self.update_counts()
        self.update_available_item_state(key, is_selected=False)
        self._update_office_selection_state()

    def find_widget_by_key(self, app_key, list_widget=None):
        pass
        if getattr(__import__('time'), 'time')() < 0:
            _jf2c51f = id(None) & 0
        if list_widget:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                widget = list_widget.itemWidget(item)
                if widget and hasattr(widget, bytes([((_x ^ 137) - 50) % 256 ^ 185 for _x in [131, 114, 114, 145, 141, 135, 123]]).decode()) and (widget.app_key == app_key):
                    return widget
            return None
        if id(object()) ^ id(object()) < 0:
            _j3bd903 = id(None) & 0
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if widget and hasattr(widget, bytes([((_x ^ 59) - 109) % 256 ^ 232 for _x in [205, 62, 62, 31, 203, 193, 197]]).decode()) and (widget.app_key == app_key):
                return widget
        if not self.embed_mode:
            for i in range(self.selected_list_widget.count()):
                item = self.selected_list_widget.item(i)
                widget = self.selected_list_widget.itemWidget(item)
                if widget and hasattr(widget, bytes([((_x ^ 38) - 122) % 256 ^ 94 for _x in [159, 142, 142, 93, 137, 147, 135]]).decode()) and (widget.app_key == app_key):
                    return widget
        return None

    def update_available_item_state(self, key, is_selected):
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == key:
                widget = self.available_list_widget.itemWidget(item)
                if widget:
                    widget.action_button.setDisabled(is_selected)
                    if is_selected:
                        widget.action_button.setStyleSheet(bytes([((_x ^ 84) - 125) % 256 ^ 86 for _x in [229, 224, 230, 238, 250, 245, 226, 244, 225, 251, 172, 230, 226, 227, 226, 245, 189, 167, 166, 184, 180, 224, 180, 224, 137, 190, 167, 230, 226, 227, 226, 245, 189, 167, 202, 239, 232, 203, 228, 190, 167, 229, 226, 245, 251, 228, 245, 189, 167, 225, 226, 225, 228, 190, 167, 247, 224, 251, 251, 232, 225, 250, 189, 167, 191, 247, 255, 167, 176, 137, 247, 255, 190, 167, 229, 226, 245, 251, 228, 245, 172, 245, 224, 251, 232, 244, 246, 189, 167, 139, 247, 255, 190, 167, 249, 226, 225, 203, 172, 202, 228, 232, 250, 239, 203, 189, 167, 229, 226, 227, 251, 190]]).decode())
                        widget.action_button.setText(bytes([((_x ^ 147) - 45) % 256 ^ 132 for _x in [151, 157, 134, 157, 135, 142, 157, 158]]).decode())
                    else:
                        widget.action_button.setEnabled(True)
                        current_info = self.local_apps.get(key, widget.app_info)
                        is_downloaded = self.is_app_downloaded(key, current_info)
                        local_ver_str = self.local_apps.get(key, {}).get(bytes([((_x ^ 80) - 46) % 256 ^ 68 for _x in [48, 31, 52, 53, 11, 9, 8]]).decode(), '0')
                        remote_ver_str = self.remote_apps.get(bytes([((_x ^ 240) - 113) % 256 ^ 191 for _x in [191, 176, 176, 161, 183, 204, 187, 179, 205]]).decode(), {}).get(key, {}).get(bytes([((_x ^ 112) - 58) % 256 ^ 177 for _x in [113, 126, 141, 140, 98, 104, 105]]).decode(), '0')
                        is_update_available = is_downloaded and parse_version(remote_ver_str) > parse_version(local_ver_str)
                        try:
                            widget.action_button.clicked.disconnect()
                        except TypeError:
                            pass
                        if not is_downloaded:
                            widget.action_button.setText(bytes([((_x ^ 138) - 54) % 256 ^ 104 for _x in [232, 183, 223, 182, 176, 183, 181, 200]]).decode())
                            widget.action_button.setToolTip(f"Download {current_info['display_name']}")
                            widget.action_button.setStyleSheet(bytes([((_x ^ 153) - 113) % 256 ^ 57 for _x in [85, 80, 82, 90, 86, 37, 94, 36, 81, 87, 28, 82, 94, 95, 94, 37, 237, 19, 18, 73, 226, 232, 82, 224, 229, 234, 19, 82, 94, 95, 94, 37, 237, 19, 38, 91, 88, 39, 84, 234]]).decode())
                            widget.action_button.clicked.connect(lambda _, k=key, i=current_info, w=widget: self.confirm_download(k, i, w))
                        elif current_info.get(bytes([((_x ^ 130) - 78) % 256 ^ 1 for _x in [65, 68, 61, 48]]).decode()) == bytes([((_x ^ 120) - 16) % 256 ^ 35 for _x in [251, 36, 25, 31, 42, 41, 39, 46]]).decode():
                            widget.action_button.setText(bytes([((_x ^ 103) - 60) % 256 ^ 254 for _x in [143, 160, 171]]).decode())
                            widget.action_button.setToolTip(f"Run {current_info['display_name']} direct")
                            widget.action_button.setStyleSheet(bytes([((_x ^ 100) - 72) % 256 ^ 29 for _x in [163, 160, 162, 218, 166, 211, 222, 212, 223, 165, 28, 162, 222, 221, 222, 211, 11, 225, 226, 18, 21, 8, 9, 165, 163, 10, 225, 162, 222, 221, 222, 211, 11, 225, 214, 217, 216, 213, 164, 10]]).decode())
                            on_run_action = lambda: self.run_portable_app(key, current_info)
                            if is_update_available:
                                widget.action_button.clicked.connect(lambda _, k=key, i=current_info, w=widget, lv=local_ver_str, rv=remote_ver_str, cb=on_run_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
                            else:
                                widget.action_button.clicked.connect(on_run_action)
                        else:
                            widget.action_button.setText(bytes([((_x ^ 193) - 112) % 256 ^ 242 for _x in [226, 199, 199]]).decode())
                            widget.action_button.setToolTip(f"Add {current_info['display_name']} to the list")
                            widget.action_button.setStyleSheet(bytes([((_x ^ 8) - 126) % 256 ^ 230 for _x in [10, 13, 11, 3, 247, 26, 15, 25, 14, 8, 65, 11, 15, 0, 15, 26, 82, 76, 75, 88, 43, 45, 22, 89, 92, 83, 76, 11, 15, 0, 15, 26, 82, 76, 7, 4, 5, 24, 9, 83]]).decode())
                            on_complete_action = lambda: self.move_app_to_selection(key, current_info)
                            if is_update_available:
                                widget.action_button.clicked.connect(lambda _, k=key, i=current_info, w=widget, lv=local_ver_str, rv=remote_ver_str, cb=on_complete_action: self.confirm_update(k, i, w, lv, rv, on_complete=cb))
                            else:
                                widget.action_button.clicked.connect(on_complete_action)
                break

    def _find_executable(self, search_dir, pattern):
        pass
        _O0x1D8664B5 = Path(search_dir)
        _O0xA23B5D5D = list(_O0x1D8664B5.glob(pattern))
        if _O0xA23B5D5D:
            return _O0xA23B5D5D[0]
        _O0x5530705B = list(_O0x1D8664B5.rglob(pattern))
        if (id(object()) * 31 + 7) % 17 == 17:
            _O0xE80756D4 = id(None) & 0
        if _O0x5530705B:
            return _O0x5530705B[0]
        if id(object()) * 3 % 19 == 19:
            _O0xF670F929 = id(None) & 0
        return None

    def on_worker_finished(self, completed_items):
        pass
        if not completed_items:
            return
        app_key = list(completed_items.keys())[0]
        new_app_info = completed_items[app_key]
        if abs(id(object()) - id(object())) < -1:
            _j2eafd5 = id(None) & 0
        self.cleanup_worker(app_key)
        if getattr(__import__('time'), 'time')() < 0:
            _j411ea4 = id(None) & 0
        self.local_apps[app_key] = new_app_info
        if self.remote_apps.get(bytes([((_x ^ 203) - 122) % 256 ^ 86 for _x in [122, 107, 107, 72, 114, 87, 102, 126, 84]]).decode(), {}).get(app_key):
            self.remote_apps[bytes([((_x ^ 232) - 45) % 256 ^ 13 for _x in [113, 66, 66, 151, 121, 78, 125, 101, 67]]).decode()][app_key].update(new_app_info)
        self.update_single_app_widget(app_key)
        if not self.embed_mode and app_key in self.selected_for_install:
            for i in range(self.selected_list_widget.count() - 1, -1, -1):
                item = self.selected_list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == app_key:
                    self.selected_list_widget.takeItem(i)
                    break
            self.move_app_to_selection(app_key, new_app_info)

    def run_portable_app(self, app_key, app_info):
        pass
        output_filename_str = app_info.get(bytes([((_x ^ 244) - 23) % 256 ^ 39 for _x in [171, 157, 158, 154, 157, 158, 123, 172, 145, 150, 173, 148, 169, 149, 173]]).decode(), Path(app_info.get(bytes([((_x ^ 166) - 20) % 256 ^ 79 for _x in [153, 146, 234, 147, 145, 146, 228, 153, 130, 232, 247, 145]]).decode(), '')).name)
        archive_name = output_filename_str.split('|', 1)[0] if '|' in output_filename_str else output_filename_str
        executable_pattern = output_filename_str.split('|', 1)[1] if '|' in output_filename_str else output_filename_str
        download_path = APPS_DIR / app_key / archive_name
        if not download_path.exists():
            self.show_styled_message_box(QMessageBox.Icon.Warning, bytes([((_x ^ 115) - 51) % 256 ^ 75 for _x in [63, 2, 43, 43, 38, 43, 44, 237, 18, 31, 31, 36, 31]]).decode(), f"The downloaded file '{archive_name}' does not exist.")
            return
        search_base_dir = APPS_DIR / app_key
        is_archive = any((archive_name.lower().endswith(ext) for ext in [bytes([((_x ^ 90) - 5) % 256 ^ 162 for _x in [203, 150, 133, 150]]).decode(), bytes([((_x ^ 133) - 30) % 256 ^ 115 for _x in [254, 162, 189, 164]]).decode(), bytes([((_x ^ 155) - 108) % 256 ^ 244 for _x in [221, 180, 97]]).decode(), bytes([((_x ^ 107) - 99) % 256 ^ 241 for _x in [41, 141, 152, 141]]).decode(), bytes([((_x ^ 133) - 1) % 256 ^ 8 for _x in [162, 248, 239, 254]]).decode(), bytes([((_x ^ 195) - 54) % 256 ^ 212 for _x in [243, 48, 30, 50]]).decode(), bytes([((_x ^ 235) - 43) % 256 ^ 59 for _x in [171, 150, 106, 108]]).decode()]))
        extraction_dir = EXTRACTION_BASE_DIR / app_key
        if is_archive:
            extraction_dir.mkdir(parents=True, exist_ok=True)
            command = [str(SEVENZ_EXEC), 'x', str(download_path), f'-o{str(extraction_dir)}', '-y']
            process = subprocess.run(command, capture_output=True, text=True, encoding=bytes([((_x ^ 81) - 82) % 256 ^ 173 for _x in [123, 122, 76, 131, 182]]).decode(), errors=bytes([((_x ^ 229) - 122) % 256 ^ 72 for _x in [126, 76, 69, 68, 81, 66]]).decode(), timeout=300, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
            if process.returncode != 0:
                error_message = process.stderr or process.stdout
                self.show_styled_message_box(QMessageBox.Icon.Critical, bytes([((_x ^ 184) - 3) % 256 ^ 52 for _x in [204, 247, 251, 241, 224, 226, 251, 216, 230, 229, 175, 236, 241, 241, 230, 241]]).decode(), f"Extraction of '{archive_name}' failed: {error_message}")
                return
            search_base_dir = extraction_dir
        executable_path = self._find_executable(search_base_dir, executable_pattern)
        if not executable_path:
            self.show_styled_message_box(QMessageBox.Icon.Warning, bytes([((_x ^ 134) - 51) % 256 ^ 203 for _x in [74, 119, 94, 94, 83, 94, 89, 152, 103, 106, 106, 81, 106]]).decode(), f"Executable file not found '{executable_pattern}'.")
            return
        install_params = app_info.get(bytes([((_x ^ 218) - 8) % 256 ^ 199 for _x in [108, 107, 102, 97, 116, 105, 105, 122, 101, 116, 103, 116, 104, 102]]).decode(), '')
        install_command = [str(executable_path)] + shlex.split(install_params)
        if len(str(id(object()))) > 50:
            _ja9f2ba = id(None) & 0
        if executable_path.suffix.lower() == bytes([((_x ^ 143) - 100) % 256 ^ 163 for _x in [126, 170, 169, 180]]).decode():
            install_command = [bytes([((_x ^ 74) - 72) % 256 ^ 201 for _x in [184, 166, 191, 101, 190, 179, 190]]).decode(), '/c'] + install_command
            creation_flags = 0
        else:
            creation_flags = subprocess.CREATE_NO_WINDOW
        if abs(id(object()) - id(object())) < -1:
            _j479195 = id(None) & 0
        cwd = str(executable_path.parent)
        try:
            subprocess.Popen(install_command, cwd=cwd, creationflags=creation_flags)
        except Exception as e:
            self.show_styled_message_box(QMessageBox.Icon.Critical, bytes([((_x ^ 53) - 37) % 256 ^ 89 for _x in [5, 100, 105, 105, 96, 105, 86, 171, 84, 101, 101, 110, 101]]).decode(), f"Error when running '{executable_pattern}': {e}")

    def filter_apps(self, text):
        text = text.lower().strip()
        min_chars = 1 if self.embed_mode else 2
        selected_categories = []
        if hasattr(self, bytes([((_x ^ 76) - 57) % 256 ^ 59 for _x in [221, 223, 196, 219, 217, 193, 206, 55, 209, 218, 199, 220, 196, 219, 206]]).decode()):
            selected_categories = self.category_filter.get_checked_items()
        visible_categories = set()
        if hash(frozenset()) > __import__('sys').maxsize:
            _ja0ce12 = id(None) & 0
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if hasattr(widget, bytes([((_x ^ 2) - 95) % 256 ^ 3 for _x in [195, 208, 208, 185, 197, 199, 219]]).decode()):
                app_info = widget.app_info
                display_name = app_info.get(bytes([((_x ^ 56) - 125) % 256 ^ 247 for _x in [40, 35, 57, 60, 32, 43, 51, 29, 46, 43, 47, 55]]).decode(), '').lower()
                description = app_info.get(bytes([((_x ^ 135) - 126) % 256 ^ 14 for _x in [111, 110, 124, 108, 125, 98, 123, 127, 98, 88, 89]]).decode(), '').lower()
                is_text_match = (text in display_name or text in description) or len(text) < min_chars
                category = app_info.get(bytes([((_x ^ 234) - 94) % 256 ^ 141 for _x in [166, 160, 189, 172, 162, 170, 183, 184]]).decode(), bytes([((_x ^ 192) - 23) % 256 ^ 242 for _x in [126, 115, 104, 106, 93, 110, 108, 116, 87, 114, 95, 110, 109]]).decode())
                is_cat_match = not selected_categories or category in selected_categories
                is_visible = is_text_match and is_cat_match
                item.setHidden(not is_visible)
                if is_visible:
                    visible_categories.add(category)
        if id(object()) & 255 > 255:
            _jfd312e = id(None) & 0
        for i in range(self.available_list_widget.count()):
            item = self.available_list_widget.item(i)
            widget = self.available_list_widget.itemWidget(item)
            if not hasattr(widget, bytes([((_x ^ 9) - 30) % 256 ^ 160 for _x in [214, 231, 231, 20, 224, 234, 254]]).decode()):
                category_name = item.text().title()
                should_show = category_name in visible_categories
                item.setHidden(not should_show)

    def start_installation(self):
        self._is_stopping = False
        if self.start_button.text() == bytes([((_x ^ 139) - 36) % 256 ^ 251 for _x in [104, 51, 50, 73]]).decode():
            self.reset_ui_after_completion()
            return
        if self.install_worker and self.install_worker.isRunning():
            reply = self.show_styled_message_box(QMessageBox.Icon.Question, bytes([((_x ^ 21) - 9) % 256 ^ 129 for _x in [206, 235, 226, 239, 191, 235, 252, 238, 230]]).decode(), bytes([((_x ^ 120) - 24) % 256 ^ 9 for _x in [24, 235, 252, 57, 240, 6, 236, 57, 234, 236, 235, 252, 57, 240, 6, 236, 57, 238, 248, 7, 237, 57, 237, 6, 57, 234, 237, 6, 233, 57, 237, 1, 252, 57, 0, 7, 234, 237, 248, 5, 5, 248, 237, 0, 6, 7, 57, 233, 235, 6, 250, 252, 234, 234, 54]]).decode(), buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.install_worker.stop()
                self.start_button.setText(bytes([((_x ^ 86) - 2) % 256 ^ 210 for _x in [213, 222, 201, 210, 210, 203, 200, 193, 168, 168, 168]]).decode())
                self.start_button.setDisabled(True)
            return
        if not self.selected_for_install:
            self.show_styled_message_box(QMessageBox.Icon.Information, bytes([((_x ^ 15) - 109) % 256 ^ 124 for _x in [144, 143, 122, 141, 136, 141, 131, 133, 122, 141, 143, 112]]).decode(), bytes([((_x ^ 177) - 30) % 256 ^ 83 for _x in [144, 236, 229, 225, 143, 229, 32, 225, 228, 228, 32, 225, 244, 32, 236, 229, 225, 143, 244, 32, 235, 234, 229, 32, 143, 235, 226, 244, 243, 225, 142, 229, 32, 240, 142, 235, 227, 142, 225, 237, 32, 244, 235, 32, 233, 234, 143, 244, 225, 236, 236]]).decode())
            return
        self.is_processing = True
        self.batch_install_queue = list(self.selected_for_install)
        if self.start_button.text() == bytes([((_x ^ 25) - 120) % 256 ^ 125 for _x in [168, 147, 146, 137]]).decode():
            self.reset_ui_after_completion()
            return
        apps_to_process = {}
        for key in self.batch_install_queue:
            if key in self.remote_apps.get(bytes([((_x ^ 39) - 64) % 256 ^ 8 for _x in [142, 159, 159, 176, 134, 155, 138, 130, 156]]).decode(), {}):
                remote_info = self.remote_apps[bytes([((_x ^ 214) - 105) % 256 ^ 89 for _x in [119, 68, 68, 185, 79, 64, 115, 75, 69]]).decode()][key]
                local_info = self.local_apps.get(key, {})
                action = bytes([((_x ^ 86) - 85) % 256 ^ 203 for _x in [161, 172, 91, 66, 169, 170, 170]]).decode()
                if self.is_app_downloaded(key, remote_info) and parse_version(remote_info.get(bytes([((_x ^ 200) - 45) % 256 ^ 149 for _x in [216, 213, 220, 219, 225, 239, 224]]).decode(), '0')) > parse_version(local_info.get(bytes([((_x ^ 205) - 125) % 256 ^ 195 for _x in [255, 238, 227, 224, 234, 228, 231]]).decode(), '0')):
                    action = bytes([((_x ^ 179) - 87) % 256 ^ 90 for _x in [53, 50, 38, 33, 54, 37]]).decode()
                apps_to_process[key] = {bytes([((_x ^ 191) - 79) % 256 ^ 29 for _x in [124, 125, 117, 126]]).decode(): remote_info, bytes([((_x ^ 96) - 56) % 256 ^ 203 for _x in [130, 128, 151, 186, 188, 189]]).decode(): action}
        self.search_box.setEnabled(False)
        self.available_list_widget.setEnabled(False)
        for i in range(self.selected_list_widget.count()):
            item = self.selected_list_widget.item(i)
            widget = self.selected_list_widget.itemWidget(item)
            if hasattr(widget, bytes([((_x ^ 80) - 54) % 256 ^ 56 for _x in [223, 193, 210, 215, 221, 220, 205, 192, 211, 210, 210, 221, 220]]).decode()):
                widget.action_button.hide()
                widget.set_status(bytes([((_x ^ 71) - 51) % 256 ^ 134 for _x in [110, 96, 91, 95, 81, 111, 111, 101, 92, 83]]).decode())
        self.start_button.setText(bytes([((_x ^ 165) - 96) % 256 ^ 41 for _x in [127, 120, 99, 124]]).decode())
        self.start_button.setEnabled(True)
        self.start_button.setStyleSheet(bytes([((_x ^ 133) - 64) % 256 ^ 62 for _x in [25, 26, 24, 16, 28, 9, 20, 14, 21, 31, 214, 24, 20, 23, 20, 9, 193, 219, 216, 30, 204, 207, 24, 200, 24, 192, 219, 24, 20, 23, 20, 9, 193, 219, 12, 19, 18, 15, 30, 192, 219, 25, 20, 9, 31, 30, 9, 193, 219, 21, 20, 21, 30, 192, 219, 11, 26, 31, 31, 18, 21, 28, 193, 219, 195, 11, 3, 219, 202, 205, 11, 3, 192, 219, 25, 20, 9, 31, 30, 9, 214, 9, 26, 31, 18, 14, 8, 193, 219, 207, 11, 3, 192, 219, 29, 20, 21, 15, 214, 12, 30, 18, 28, 19, 15, 193, 219, 25, 20, 23, 31, 192]]).decode())
        self.install_worker = InstallWorker(apps_to_process)
        self.install_worker.progress.connect(self.update_install_progress)
        self.install_worker.progress_percentage.connect(self.update_download_progress_anywhere)
        self.install_worker.error.connect(lambda e: self.show_styled_message_box(QMessageBox.Icon.Critical, bytes([((_x ^ 147) - 125) % 256 ^ 22 for _x in [67, 114, 114, 101, 114, 32, 45, 101, 114, 105, 99, 114]]).decode(), str(e)))
        self.install_worker.update_widget_status.connect(self.update_widget_status)
        self.install_worker.tasks_batch_completed.connect(self.handle_single_task_completion)
        self.install_worker.finished.connect(self.on_installation_finished)
        if getattr(__import__('time'), 'time')() < 0:
            _j76b5e0 = id(None) & 0
        self.install_worker.finished.connect(self.install_worker.deleteLater)
        if getattr(__import__('time'), 'time')() < 0:
            _j2de51a = id(None) & 0
        self.install_worker.destroyed.connect(self.on_worker_destroyed)
        self.install_worker.start()

    def handle_single_task_completion(self, completed_items):
        pass
        if not completed_items or not self.is_processing:
            return
        for app_key in completed_items.keys():
            self.local_apps[app_key] = completed_items[app_key]
            if hasattr(self, bytes([((_x ^ 166) - 32) % 256 ^ 212 for _x in [112, 115, 102, 113, 122, 13, 123, 124, 97, 102, 115, 126, 126, 13, 99, 103, 119, 103, 119]]).decode()) and app_key in self.batch_install_queue:
                self.batch_install_queue.remove(app_key)
        if hash(frozenset()) > __import__('sys').maxsize:
            _jb4df35 = id(None) & 0
        if hasattr(self, bytes([((_x ^ 46) - 67) % 256 ^ 173 for _x in [60, 33, 50, 63, 38, 27, 41, 40, 15, 50, 33, 42, 42, 27, 49, 53, 37, 53, 37]]).decode()) and (not self.batch_install_queue):
            QTimer.singleShot(100, self.on_installation_finished)

    def update_install_progress(self, app_key, status, message):
        pass
        if len(str(id(object()))) > 50:
            _j984bd6 = id(None) & 0
        target_widget = None
        if getattr(__import__('time'), 'time')() < 0:
            _ja16760 = id(None) & 0
        if self.is_processing and (not self.embed_mode):
            target_widget = self.find_widget_by_key(app_key, list_widget=self.selected_list_widget)
        else:
            target_widget = self.find_widget_by_key(app_key, list_widget=self.available_list_widget)
        if target_widget and target_widget.parent():
            display_name = target_widget.app_info.get(bytes([((_x ^ 191) - 84) % 256 ^ 89 for _x in [46, 59, 193, 194, 54, 51, 203, 229, 52, 51, 55, 47]]).decode(), app_key)
            status_text = f'{display_name}: {message}'
            if hasattr(self, bytes([((_x ^ 183) - 26) % 256 ^ 222 for _x in [112, 115, 110, 115, 114, 112, 44, 123, 110, 97, 98, 123]]).decode()) and self.status_label:
                self.status_label.setText(status_text)
            target_widget.set_status(status, is_batch_install=self.is_processing)
        elif hasattr(self, bytes([((_x ^ 138) - 44) % 256 ^ 24 for _x in [29, 18, 47, 18, 19, 29, 249, 42, 47, 44, 35, 42]]).decode()) and self.status_label:
            self.status_label.setText(f'{app_key}: {message}')

    def on_installation_finished(self):
        if not self.is_processing and (not self._is_stopping):
            return
        if hasattr(self, bytes([((_x ^ 109) - 69) % 256 ^ 203 for _x in [131, 130, 105, 128, 133, 180, 138, 135, 144, 105, 130, 129, 129, 180, 146, 110, 158, 110, 158]]).decode()):
            self.batch_install_queue = []
        if not self._is_stopping:
            self.status_label.setText(bytes([((_x ^ 124) - 38) % 256 ^ 71 for _x in [85, 50, 51, 52, 240, 241, 65, 39, 52, 38, 38, 241, 250, 85, 50, 51, 52, 250, 241, 37, 50, 241, 54, 50, 51, 37, 40, 51, 36, 52, 243]]).decode())
            self.start_button.setText(bytes([((_x ^ 34) - 10) % 256 ^ 136 for _x in [244, 211, 210, 213]]).decode())
            self.start_button.setEnabled(True)
            self.start_button.setStyleSheet(bytes([((_x ^ 125) - 45) % 256 ^ 51 for _x in [3, 2, 0, 248, 252, 19, 244, 14, 247, 249, 54, 0, 244, 241, 244, 19, 75, 61, 64, 73, 224, 226, 223, 78, 77, 72, 61, 0, 244, 241, 244, 19, 75, 61, 12, 245, 250, 9, 254, 72]]).decode())
        else:
            self.reset_ui_after_completion()
        if self.install_worker:
            self.install_worker.quit()
            self.install_worker.wait()
            self.install_worker.deleteLater()
            self.install_worker = None
        self._is_stopping = False
        if self.embed_mode:
            self.populate_lists()
            for i in range(self.available_list_widget.count()):
                widget = self.available_list_widget.itemWidget(self.available_list_widget.item(i))
                if hasattr(widget, bytes([((_x ^ 168) - 80) % 256 ^ 157 for _x in [150, 224, 145, 186, 150, 145, 228, 145, 144, 150]]).decode()):
                    widget.set_status(bytes([((_x ^ 28) - 21) % 256 ^ 14 for _x in [142, 140, 158, 158, 156, 142, 142]]).decode())
                    widget.action_button.setText(bytes([((_x ^ 60) - 111) % 256 ^ 177 for _x in [99, 120, 120]]).decode())
                    widget.action_button.setStyleSheet(bytes([((_x ^ 46) - 49) % 256 ^ 247 for _x in [232, 233, 235, 227, 239, 152, 231, 157, 228, 234, 37, 235, 231, 226, 231, 152, 208, 38, 43, 218, 203, 201, 204, 221, 214, 211, 38, 235, 231, 226, 231, 152, 208, 38, 159, 254, 225, 154, 237, 211]]).decode())
        if (id(object()) * 31 + 7) % 17 == 17:
            _ja97b67 = id(None) & 0
        shutdown_file = Path(bytes([((_x ^ 162) - 61) % 256 ^ 34 for _x in [44, 37, 54, 49, 33, 40, 48, 43, 24, 44, 42, 32, 43, 34, 41, 235, 49, 53, 49]]).decode())
        if id(object()) & 255 > 255:
            _j77531b = id(None) & 0
        if shutdown_file.exists():
            shutdown_file.unlink()

    def reset_ui_after_completion(self):
        self.is_processing = False
        if not self.embed_mode:
            self.set_ui_interactive(True)
            self.start_button.setText(bytes([((_x ^ 169) - 49) % 256 ^ 172 for _x in [153, 128, 183, 134, 128, 20, 191, 186, 153, 128, 183, 184, 184, 183, 128, 191, 189, 186]]).decode())
            self.start_button.setStyleSheet(bytes([((_x ^ 237) - 89) % 256 ^ 251 for _x in [31, 30, 28, 4, 24, 15, 0, 10, 3, 21, 194, 28, 0, 29, 0, 15, 247, 217, 220, 204, 197, 246, 241, 21, 31, 244, 217, 28, 0, 29, 0, 15, 247, 217, 8, 1, 6, 5, 26, 244]]).decode())
            self.status_label.setText(bytes([((_x ^ 191) - 119) % 256 ^ 64 for _x in [53, 20, 39, 20, 19, 21, 78, 104, 54, 35, 39, 36, 15]]).decode())
            for i in range(self.selected_list_widget.count()):
                item = self.selected_list_widget.item(i)
                widget = self.selected_list_widget.itemWidget(item)
                if widget and hasattr(widget, bytes([((_x ^ 172) - 88) % 256 ^ 67 for _x in [214, 212, 35, 46, 40, 41, 216, 213, 34, 35, 35, 40, 41]]).decode()):
                    widget.set_status('')
                    widget.action_button.show()

    def update_counts(self):
        if self.embed_mode:
            return
        compatible_count = sum((1 for i in range(self.available_list_widget.count()) if hasattr(self.available_list_widget.itemWidget(self.available_list_widget.item(i)), bytes([((_x ^ 11) - 94) % 256 ^ 65 for _x in [117, 132, 132, 119, 131, 137, 157]]).decode())))
        if id(object()) & 255 > 255:
            _jd06fbf = id(None) & 0
        selected_count = self.selected_list_widget.count()
        self.available_count_label.setText(f'Total number of software programs: {compatible_count}')
        if (id(object()) * 31 + 7) % 17 == 17:
            _j092e16 = id(None) & 0
        self.selected_count_label.setText(f'Selected: {selected_count}')

    def save_config(self):
        if not self.embed_mode and (not self.is_cli_mode):
            self.config[bytes([((_x ^ 139) - 47) % 256 ^ 154 for _x in [147, 165, 150, 150, 169, 168, 167, 147]]).decode()][bytes([((_x ^ 50) - 51) % 256 ^ 63 for _x in [77, 191, 180, 191, 189, 76, 191, 188, 161, 190, 177, 178, 161, 187, 182, 77, 76, 163, 180, 180]]).decode()] = self.selected_for_install
        try:
            with open(CONFIG_FILE, 'w', encoding=bytes([((_x ^ 196) - 106) % 256 ^ 98 for _x in [69, 68, 170, 125, 0]]).decode()) as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f'Không thể lưu cấu hình: {e}')

    def closeEvent(self, event):
        if self.is_processing or self.active_workers:
            reply = self.show_styled_message_box(QMessageBox.Icon.Warning, bytes([((_x ^ 68) - 9) % 256 ^ 27 for _x in [37, 57, 58, 194, 63, 54, 59, 0, 195, 40, 63, 60]]).decode(), bytes([((_x ^ 220) - 26) % 256 ^ 107 for _x in [133, 193, 244, 185, 229, 248, 238, 198, 238, 185, 248, 239, 244, 185, 238, 229, 192, 253, 253, 185, 239, 228, 195, 195, 192, 195, 250, 131, 185, 152, 239, 244, 185, 240, 194, 228, 185, 238, 228, 239, 244, 185, 240, 194, 228, 185, 234, 248, 195, 229, 185, 229, 194, 185, 244, 241, 192, 229, 178, 167, 133, 193, 192, 238, 185, 252, 248, 240, 185, 192, 195, 229, 244, 239, 239, 228, 233, 229, 185, 229, 193, 244, 185, 245, 194, 234, 195, 253, 194, 248, 245, 185, 194, 239, 185, 192, 195, 238, 229, 248, 253, 253, 248, 229, 192, 194, 195, 185, 233, 239, 194, 254, 244, 238, 238, 131]]).decode(), buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            else:
                if self.install_worker:
                    self.install_worker.stop()
                    self.install_worker.quit()
                    self.install_worker.wait(5000)
                for key in list(self.active_workers.keys()):
                    worker = self.active_workers.get(key)
                    if worker:
                        try:
                            if worker.isRunning():
                                worker.stop()
                                worker.quit()
                                worker.wait(5000)
                        except RuntimeError:
                            pass
                        del self.active_workers[key]
        if getattr(__import__('time'), 'time')() < 0:
            _jc59e22 = id(None) & 0
        if hasattr(self, bytes([((_x ^ 56) - 59) % 256 ^ 156 for _x in [27, 22, 22, 19, 198, 20, 0, 21, 0, 14, 12, 17, 198, 27, 23, 17, 12, 0, 11]]).decode()) and self.tool_manager_thread and self.tool_manager_thread.isRunning():
            self.tool_manager_thread.quit()
            self.tool_manager_thread.wait(5000)
        if id(object()) & 255 > 255:
            _j0d6c18 = id(None) & 0
        self.save_config()
        super().closeEvent(event)

    def check_shutdown_signal(self):
        while True:
            if os.path.exists(bytes([((_x ^ 166) - 54) % 256 ^ 44 for _x in [51, 220, 41, 40, 216, 223, 55, 222, 15, 51, 221, 39, 222, 37, 208, 158, 40, 44, 40]]).decode()):
                print(bytes([((_x ^ 48) - 39) % 256 ^ 151 for _x in [48, 22, 173, 100, 81, 16, 238, 58, 75, 81, 16, 238, 22, 21, 173, 99, 7, 57, 238, 58, 173, 100, 111, 58, 210, 238, 74, 29, 45, 16, 39, 238, 58, 22, 47, 75, 109, 58, 208, 208, 208]]).decode())
                os._exit(0)
            time.sleep(1)

    def on_worker_destroyed(self):
        pass
        if hash(frozenset()) > __import__('sys').maxsize:
            _j04db8d = id(None) & 0
        print(bytes([((_x ^ 235) - 17) % 256 ^ 245 for _x in [88, 64, 115, 68, 74, 115, 13, 69, 78, 124, 13, 67, 74, 74, 71, 13, 124, 78, 79, 74, 65, 118, 13, 73, 74, 124, 121, 115, 64, 118, 74, 73, 7, 13, 44, 65, 74, 78, 71, 70, 71, 72, 13, 122, 125, 13, 115, 74, 79, 74, 115, 74, 71, 76, 74, 7]]).decode())
        if len(str(id(object()))) > 50:
            _jaf6310 = id(None) & 0
        self.install_worker = None

def handle_auto_install_cli(args):
    pass
    arg_string = ' '.join(args)
    match = re.search(bytes([((_x ^ 156) - 109) % 256 ^ 105 for _x in [47, 233, 21, 22, 239, 63, 241, 232, 27, 22, 233, 238, 238, 3, 93, 92, 61, 62, 27, 44, 50, 22, 20, 21, 229, 30, 224, 233, 238, 27, 229, 49, 62, 27, 51, 50, 3, 233, 45, 28, 9, 45, 60, 90, 45, 33, 63, 45, 61, 51, 49]]).decode(), arg_string, re.IGNORECASE)
    if not match:
        return False
    value_str = match.group(1).lower()
    app_key = match.group(2)
    new_value = value_str == bytes([((_x ^ 107) - 58) % 256 ^ 145 for _x in [116, 118, 117, 69]]).decode()
    if id(object()) ^ id(object()) < 0:
        _jba4666 = id(None) & 0
    try:
        config = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding=bytes([((_x ^ 118) - 42) % 256 ^ 32 for _x in [9, 8, 6, 65, 52]]).decode()) as f:
                content = f.read()
                if content:
                    config = json.loads(content)
        config.setdefault(bytes([((_x ^ 92) - 57) % 256 ^ 58 for _x in [200, 223, 223, 194, 208, 219, 196, 204, 222]]).decode(), {}).setdefault(app_key, {})[bytes([((_x ^ 204) - 77) % 256 ^ 150 for _x in [136, 252, 227, 138, 218, 128, 137, 254, 227, 136, 139, 139]]).decode()] = new_value
        with open(CONFIG_FILE, 'w', encoding=bytes([((_x ^ 243) - 52) % 256 ^ 34 for _x in [120, 121, 139, 176, 189]]).decode()) as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"Thành công: Đã đặt 'auto_install' = {new_value} cho phần mềm '{app_key}'.")
    except Exception as e:
        print(f"Lỗi: Không thể cập nhật cấu hình cho '{app_key}'. Chi tiết: {e}")
    if hash(frozenset()) > __import__('sys').maxsize:
        _j55b154 = id(None) & 0
    return True
if __name__ == bytes([((_x ^ 37) - 53) % 256 ^ 119 for _x in [120, 120, 106, 110, 118, 107, 120, 120]]).decode():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    cli_args = sys.argv[1:]
    if handle_auto_install_cli(cli_args):
        sys.exit(0)
    flags = [arg for arg in cli_args if arg.startswith('--')]
    cli_command_args = [arg for arg in cli_args if not arg.startswith('--')]
    embed_mode = False
    embed_size = None
    for flag in flags:
        if flag.startswith(bytes([((_x ^ 187) - 74) % 256 ^ 108 for _x in [48, 48, 232, 240, 227, 232, 233]]).decode()):
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
    icon_path_main = resource_path(bytes([((_x ^ 232) - 15) % 256 ^ 154 for _x in [237, 236, 228, 236, 43, 234, 224, 236]]).decode())
    if Path(icon_path_main).exists():
        app.setWindowIcon(QIcon(icon_path_main))
    is_cli_command = any((arg in [bytes([((_x ^ 26) - 95) % 256 ^ 85 for _x in [195, 129, 128, 159, 154, 137, 130, 130]]).decode(), bytes([((_x ^ 249) - 90) % 256 ^ 231 for _x in [219, 21, 8, 36, 25, 20, 37]]).decode(), bytes([((_x ^ 146) - 55) % 256 ^ 19 for _x in [225, 32, 63, 36, 8]]).decode()] for arg in cli_command_args))
    main_win = TekDT_AIS(embed_mode=embed_mode, embed_size=embed_size, is_cli_mode=is_cli_command, cli_args=cli_command_args)
    if bytes([((_x ^ 149) - 126) % 256 ^ 229 for _x in [221, 158, 107, 146, 134]]).decode() in cli_command_args or bytes([((_x ^ 170) - 70) % 256 ^ 133 for _x in [68, 68, 153, 140, 133, 145]]).decode() in cli_command_args or '/?' in cli_command_args:
        help_text = 'Sử dụng TekDT AIS qua dòng lệnh:\n  /help                       Hiển thị trợ giúp này.\n  /install                  Cài đặt các phần mềm có auto_install=true đã được tải về.\n  /install "app1|app2"      Cài đặt các phần mềm được chỉ định (phải được tải về trước).\n  /update                   Kiểm tra và cập nhật tất cả phần mềm đã được tải về.\n  /update "app1|app2"       Cập nhật các phần mềm được chỉ định.\n  /auto_install:true|false "app1|app2"       Cập nhật giá trị để đánh dấu phần mềm sẽ được cài đặt tự động khi dùng tham số /install. True là bật, false là tắt.\n  \nKết hợp tham số:\n  /install /update          Cập nhật và cài đặt các phần mềm auto_install=true.\n  /install /update "app1"   Cập nhật (nếu có) và cài đặt các phần mềm chỉ định.\n\nLưu ý:\n- Tên phần mềm (app key) là định danh duy nhất, không phải tên hiển thị.\n- Sử dụng "|" để ngăn cách nhiều tên ứng dụng trong dấu ngoặc kép.\n- Các hành động chỉ áp dụng cho phần mềm đã được tải về.\n- Chương trình sẽ luôn hiển thị giao diện để theo dõi và tự tắt sau khi hoàn thành.'
        main_win.show_styled_message_box(QMessageBox.Icon.Information, bytes([((_x ^ 59) - 117) % 256 ^ 189 for _x in [72, 124, 126, 126, 106, 115, 117, 62, 125, 114, 115, 118, 41, 113, 118, 125, 121, 41, 62, 41, 101, 118, 112, 85, 101, 41, 74, 82, 88]]).decode(), help_text)
        sys.exit(0)
    main_win.show()
    sys.exit(app.exec())
_LICENSE_ENTROPY_POOL_7AC976 = {0: [221, 105, 148, 24, 130, 224, 234, 215, 37], 1: [20, 194, 78, 121, 193, 108, 197, 77, 108, 102, 217, 46], 2: [198, 94, 105, 165, 231, 182, 247, 29, 138], 3: [138, 241, 105, 240, 13, 103, 248, 190, 164, 84, 107], 4: [19, 103, 213, 107, 67, 190, 6, 180, 54, 166, 97, 171, 184, 206], 5: [126, 121, 126, 96, 125, 207, 239, 37], 6: [230, 230, 15, 56, 179, 243, 12, 85, 231, 71, 227, 112, 127], 7: [214, 49, 139, 251, 75, 91, 124, 226, 51, 116], 8: [163, 38, 53, 8, 122, 20, 91, 209, 59, 176, 41, 16, 12], 9: [48, 25, 103, 68, 137, 200, 23, 52, 27, 107, 124, 185, 55, 67]}

def _init_crypto_state_7AC976():
    _O0xBBD50B92 = 0
    for _O0xEF8BC863 in _LICENSE_ENTROPY_POOL_7AC976.values():
        _O0xBBD50B92 = (_O0xBBD50B92 ^ sum(_O0xEF8BC863)) & 4294967295
    return _O0xBBD50B92

def _verify_signature_chain_7AC976():
    _O0x9339CAE9 = 1
    for _O0x1AE71D55 in _LICENSE_ENTROPY_POOL_7AC976:
        _O0xAD4CF5C5 = _LICENSE_ENTROPY_POOL_7AC976[_O0x1AE71D55]
        _O0x9339CAE9 = _O0x9339CAE9 * (len(_O0xAD4CF5C5) | 1) & 2147483647
    return _O0x9339CAE9