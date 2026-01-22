import sys
import os
import json
from PyQt6.QtCore import Qt, QFileInfo
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QLabel, QScrollArea, QFileIconProvider, 
                             QFileDialog)
from win32mica import ApplyMica, MicaTheme, MicaStyle

CONFIG_FILE = "config.json"

class DesktopMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedWidth(480) 
        self.setFixedHeight(155) 
        self.setWindowTitle("Desktop Menu")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        ApplyMica(HWND=self.winId(), Theme=MicaTheme.LIGHT, Style=MicaStyle.ALT)

        self.apps_list = self.load_config() 
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 5)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:horizontal {
                border: none;
                background: rgba(0, 0, 0, 0.03);
                height: 8px;
                margin: 0px 10px 2px 10px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(255, 255, 255, 0.5);
                min-width: 30px;
                border-radius: 4px;
                border: 1px solid rgba(0, 0, 0, 0.05);
            }
            QScrollBar::handle:horizontal:hover { background: rgba(255, 255, 255, 0.8); }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }
        """)
        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.h_layout = QHBoxLayout(self.container)
        self.h_layout.setSpacing(12)
        self.h_layout.setContentsMargins(5, 5, 5, 10)
        self.h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        self.refresh_grid()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        else:
            self.save_to_json([])
            return []

    def save_to_json(self, data):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def refresh_grid(self):
        while self.h_layout.count():
            child = self.h_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        icon_provider = QFileIconProvider()

        for index, app_data in enumerate(self.apps_list):
            name, path = app_data
            btn = self.create_app_button(name, path, index, icon_provider)
            self.h_layout.addWidget(btn)

        if len(self.apps_list) < 30:
            add_btn = QPushButton("+")
            add_btn.setFixedSize(75, 75)
            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.05);
                    border: 2px dashed rgba(0, 0, 0, 0.15);
                    border-radius: 12px;
                    font-size: 26px; color: rgba(0, 0, 0, 0.3);
                }
                QPushButton:hover { background-color: rgba(0, 0, 0, 0.08); }
            """)
            add_btn.clicked.connect(self.add_application)
            self.h_layout.addWidget(add_btn)

    def create_app_button(self, name, path, index, provider):
        btn = QPushButton()
        btn.setFixedSize(75, 75)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        btn.customContextMenuRequested.connect(lambda: self.delete_app(index))
        
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 12px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.7); }
        """)
        
        l = QVBoxLayout(btn)
        l.setContentsMargins(5, 5, 5, 5)
        
        icon_label = QLabel()
        if os.path.exists(path):
            icon_label.setPixmap(provider.icon(QFileInfo(path)).pixmap(28, 28))
        else:
            icon_label.setText("❓")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        display_name = (name[:8] + '..') if len(name) > 9 else name
        name_label = QLabel(display_name)
        name_label.setStyleSheet("font-size: 10px; color: #111; font-weight: 600; background: transparent;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        l.addWidget(icon_label)
        l.addWidget(name_label)
        
        btn.clicked.connect(lambda: os.startfile(path))
        return btn

    def delete_app(self, index):
        if 0 <= index < len(self.apps_list):
            self.apps_list.pop(index)
            self.save_to_json(self.apps_list)
            self.refresh_grid()

    def add_application(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Program", "", "Exe Files (*.exe)")
        if file_path:
            name = QFileInfo(file_path).baseName()
            self.apps_list.append([name, file_path])
            self.save_to_json(self.apps_list)
            self.refresh_grid()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DesktopMenu()
    window.show()
    sys.exit(app.exec())