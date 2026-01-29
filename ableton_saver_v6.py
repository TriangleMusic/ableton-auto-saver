import sys
import time
import re
import os
import subprocess
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QGraphicsDropShadowEffect,
    QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QCursor

# --- DESIGN SYSTEM ---
COLOR_ACCENT = "#D4FF00"
COLOR_DANGER = "#FF5F56"
COLOR_YELLOW = "#FFBD2E"
COLOR_GREEN = "#27C93F"
COLOR_BG = "#0d0d0d"
COLOR_BG_SECONDARY = "#151515"
COLOR_BORDER = "#2a2a2a"
COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#E0E0E0"
COLOR_TEXT_DIM = "#A0A0A0"

WINDOW_WIDTH = 420
WINDOW_HEIGHT = 850
CORNER_RADIUS = 20

# Social Links
TRIANGLE_DISCORD_URL = "https://discord.gg/94qDRJT4sW"
TRIANGLE_WHATSAPP_URL = "https://chat.whatsapp.com/Bxkdz1ZzA7l3Trdz1x9far"
INSTA_IDO_URL = "https://www.instagram.com/ido_triangle/"
INSTA_AMIT_URL = "https://www.instagram.com/amit.triangle/"

# Sound
TIMER_SOUND_FILE = "/System/Library/Sounds/Glass.aiff"


def play_notification_sound():
    try:
        subprocess.Popen(['afplay', TIMER_SOUND_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass


class GlassContainer(QWidget):
    """Rounded glass container widget"""
    def __init__(self, parent=None, radius=20):
        super().__init__(parent)
        self.radius = radius
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rounded rectangle background
        painter.setBrush(QBrush(QColor(13, 13, 13, 245)))
        painter.setPen(QPen(QColor(42, 42, 42), 1))
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)


class CircleButton(QPushButton):
    """macOS style circle button"""
    def __init__(self, color, hover_color, parent=None):
        super().__init__(parent)
        self.color = color
        self.hover_color = hover_color
        self.setFixedSize(14, 14)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 7px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)


class StyledButton(QPushButton):
    """Styled button with rounded corners"""
    def __init__(self, text, bg_color, text_color, hover_color, parent=None, border=False, border_color=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        border_style = f"border: 2px solid {border_color};" if border else "border: none;"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                {border_style}
                border-radius: 18px;
                padding: 10px 20px;
                font-family: 'Helvetica Neue';
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)


class IntervalButton(QPushButton):
    """Interval selection button"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(65, 30)
        self.selected = False
        self.update_style()

    def update_style(self):
        if self.selected:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT};
                    color: black;
                    border: none;
                    border-radius: 15px;
                    font-family: 'Helvetica Neue';
                    font-size: 12px;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_TEXT_DIM};
                    border: 1px solid #444444;
                    border-radius: 15px;
                    font-family: 'Helvetica Neue';
                    font-size: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #1a1a1a;
                }}
            """)

    def set_selected(self, selected):
        self.selected = selected
        self.update_style()


class TriangleSaver(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window setup - frameless transparent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - WINDOW_WIDTH) // 2
        y = (screen.height() - WINDOW_HEIGHT) // 2
        self.move(x, y)

        # Variables
        self.is_running = False
        self.interval_seconds = 300
        self.next_save_time = 0
        self.is_pro_mode = False
        self.drag_position = None
        self.is_timer_mode = False
        self.main_widgets = []  # Store widgets to hide in timer mode

        # Build UI
        self.build_ui()

        # Sync startup toggle with actual plist state
        self.sync_startup_toggle()

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_loop)
        self.timer.start(100)

    def build_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)

        # Glass container
        self.container = GlassContainer(radius=CORNER_RADIUS)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 15, 20, 15)
        container_layout.setSpacing(5)

        # --- Title Bar ---
        title_bar = QHBoxLayout()
        title_bar.setSpacing(8)

        self.btn_close = CircleButton(COLOR_DANGER, "#FF7B75")
        self.btn_close.clicked.connect(self.close_app)

        self.btn_minimize = CircleButton(COLOR_YELLOW, "#FFD062")
        self.btn_minimize.clicked.connect(self.showMinimized)

        self.btn_timer_mode = CircleButton(COLOR_GREEN, "#4AE567")
        self.btn_timer_mode.clicked.connect(self.toggle_timer_mode)

        title_bar.addWidget(self.btn_close)
        title_bar.addWidget(self.btn_minimize)
        title_bar.addWidget(self.btn_timer_mode)
        title_bar.addStretch()

        container_layout.addLayout(title_bar)

        # --- Header ---
        self.lbl_brand = QLabel("TRIANGLE")
        self.lbl_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_brand.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Helvetica Neue'; font-size: 48px; font-weight: bold;")
        container_layout.addWidget(self.lbl_brand)

        self.lbl_subtitle = QLabel("Ableton Auto Saver")
        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_subtitle.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Helvetica Neue'; font-size: 18px;")
        container_layout.addWidget(self.lbl_subtitle)

        self.lbl_desc = QLabel("Professional Auto-Save Tool\nfor Ableton Live.")
        self.lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_desc.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-family: 'Helvetica Neue'; font-size: 13px;")
        container_layout.addWidget(self.lbl_desc)

        container_layout.addSpacing(10)

        # --- Timer ---
        self.lbl_timer = QLabel("05:00")
        self.lbl_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_timer.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-family: 'Helvetica Neue'; font-size: 48px; font-weight: bold;")
        container_layout.addWidget(self.lbl_timer)

        self.lbl_timer_desc = QLabel("NEXT SAVE CYCLE")
        self.lbl_timer_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_timer_desc.setStyleSheet(f"color: {COLOR_ACCENT}; font-family: 'Helvetica Neue'; font-size: 10px;")
        container_layout.addWidget(self.lbl_timer_desc)

        self.lbl_last_saved = QLabel("Waiting to start...")
        self.lbl_last_saved.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_last_saved.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-family: 'Helvetica Neue'; font-size: 10px;")
        container_layout.addWidget(self.lbl_last_saved)

        container_layout.addSpacing(10)

        # --- Interval Buttons ---
        interval_layout = QHBoxLayout()
        interval_layout.setSpacing(8)
        interval_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.interval_buttons = []
        intervals = [("1m", 60), ("5m", 300), ("10m", 600), ("15m", 900)]

        for text, seconds in intervals:
            btn = IntervalButton(text)
            btn.clicked.connect(lambda checked, s=seconds, b=btn: self.set_interval(s, b))
            self.interval_buttons.append((btn, seconds))
            interval_layout.addWidget(btn)

        # Select 5m by default
        self.interval_buttons[1][0].set_selected(True)

        container_layout.addLayout(interval_layout)

        container_layout.addSpacing(10)

        # --- Custom Interval ---
        self.lbl_custom = QLabel("CUSTOM INTERVAL")
        self.lbl_custom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_custom.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-family: 'Helvetica Neue'; font-size: 10px;")
        container_layout.addWidget(self.lbl_custom)

        custom_frame = QFrame()
        custom_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_SECONDARY};
                border: 1px solid #333333;
                border-radius: 18px;
            }}
        """)
        custom_layout = QHBoxLayout(custom_frame)
        custom_layout.setContentsMargins(15, 10, 15, 10)

        self.entry_custom = QLineEdit()
        self.entry_custom.setPlaceholderText("00")
        self.entry_custom.setFixedSize(55, 32)
        self.entry_custom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entry_custom.setStyleSheet(f"""
            QLineEdit {{
                background-color: #0a0a0a;
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid #333333;
                border-radius: 16px;
                padding: 5px;
                font-family: 'Helvetica Neue';
                font-weight: bold;
                font-size: 12px;
            }}
        """)

        self.btn_sec = QPushButton("SEC")
        self.btn_min = QPushButton("MIN")
        self.time_unit = "MIN"

        for btn in [self.btn_sec, self.btn_min]:
            btn.setFixedSize(50, 30)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.btn_sec.clicked.connect(lambda: self.set_time_unit("SEC"))
        self.btn_min.clicked.connect(lambda: self.set_time_unit("MIN"))
        self.update_time_unit_buttons()

        self.btn_set = QPushButton("SET")
        self.btn_set.setFixedSize(60, 30)
        self.btn_set.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_set.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: black;
                border: none;
                border-radius: 15px;
                font-family: 'Helvetica Neue';
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #E2FF4D;
            }}
        """)
        self.btn_set.clicked.connect(self.set_custom_interval)

        custom_layout.addWidget(self.entry_custom)
        custom_layout.addSpacing(5)
        custom_layout.addWidget(self.btn_sec)
        custom_layout.addWidget(self.btn_min)
        custom_layout.addStretch()
        custom_layout.addWidget(self.btn_set)

        container_layout.addWidget(custom_frame)

        container_layout.addSpacing(15)

        # --- Main Action Button ---
        self.btn_toggle = StyledButton("START AUTO-SAVE", COLOR_ACCENT, "black", "#E2FF4D")
        self.btn_toggle.setFixedHeight(45)
        self.btn_toggle.clicked.connect(self.toggle_running)
        container_layout.addWidget(self.btn_toggle)

        container_layout.addSpacing(10)

        # --- Timer Mode Button ---
        self.btn_timer_only = StyledButton("TIMER MODE", "transparent", COLOR_ACCENT, "#1a1a1a", border=True, border_color=COLOR_ACCENT)
        self.btn_timer_only.setFixedWidth(140)
        self.btn_timer_only.clicked.connect(self.toggle_timer_mode)
        timer_btn_layout = QHBoxLayout()
        timer_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_btn_layout.addWidget(self.btn_timer_only)
        container_layout.addLayout(timer_btn_layout)

        # --- Back to Main Button (hidden initially) ---
        self.btn_back_main = StyledButton("← BACK TO MAIN", "transparent", COLOR_ACCENT, "#1a1a1a", border=True, border_color=COLOR_ACCENT)
        self.btn_back_main.setFixedWidth(160)
        self.btn_back_main.clicked.connect(self.toggle_timer_mode)
        self.btn_back_main.hide()
        back_btn_layout = QHBoxLayout()
        back_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        back_btn_layout.addWidget(self.btn_back_main)
        container_layout.addLayout(back_btn_layout)

        container_layout.addSpacing(10)

        # --- Switches/Settings ---
        self.switches = {}
        settings = [
            ("Incremental Save [PRO]", "pro", False),
            ("Always on Top", "top", True),
            ("Launch on Startup", "startup", False)
        ]

        for text, key, default_on in settings:
            row = QHBoxLayout()
            row.setSpacing(10)

            # Toggle switch container
            switch_container = QWidget()
            switch_container.setFixedSize(50, 26)
            switch_layout = QHBoxLayout(switch_container)
            switch_layout.setContentsMargins(0, 0, 0, 0)

            switch = QPushButton()
            switch.setCheckable(True)
            switch.setChecked(default_on)
            switch.setFixedSize(50, 26)
            switch.setProperty("key", key)
            switch.clicked.connect(lambda checked, s=switch, k=key: self.toggle_setting(s, k))
            self.update_switch_style(switch)
            self.switches[key] = switch

            switch_layout.addWidget(switch)

            label = QLabel(text)
            label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-family: 'Helvetica Neue'; font-size: 12px;")

            row.addWidget(switch_container)
            row.addWidget(label)
            row.addStretch()
            container_layout.addLayout(row)

        container_layout.addSpacing(10)

        # --- Separator ---
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: #222222;")
        container_layout.addWidget(separator)

        container_layout.addSpacing(10)

        # --- Social Links ---
        social_layout = QHBoxLayout()
        social_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        social_layout.setSpacing(10)

        btn_discord = StyledButton("Join Discord", "#5865F2", "white", "#7289da")
        btn_discord.setFixedSize(125, 32)
        btn_discord.clicked.connect(lambda: webbrowser.open(TRIANGLE_DISCORD_URL))

        btn_whatsapp = StyledButton("Join WhatsApp", "#25D366", "white", "#4CE77F")
        btn_whatsapp.setFixedSize(125, 32)
        btn_whatsapp.clicked.connect(lambda: webbrowser.open(TRIANGLE_WHATSAPP_URL))

        social_layout.addWidget(btn_discord)
        social_layout.addWidget(btn_whatsapp)
        container_layout.addLayout(social_layout)

        # --- Instagram Links ---
        insta_layout = QHBoxLayout()
        insta_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        insta_layout.setSpacing(10)

        btn_ido = QPushButton("@ido_triangle")
        btn_ido.setFixedSize(120, 30)
        btn_ido.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_ido.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_ACCENT};
                border: 2px solid {COLOR_ACCENT};
                border-radius: 15px;
                font-family: 'Helvetica Neue';
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(212, 255, 0, 0.1);
            }}
        """)
        btn_ido.clicked.connect(lambda: webbrowser.open(INSTA_IDO_URL))

        btn_amit = QPushButton("@amit.triangle")
        btn_amit.setFixedSize(120, 30)
        btn_amit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_amit.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_ACCENT};
                border: 2px solid {COLOR_ACCENT};
                border-radius: 15px;
                font-family: 'Helvetica Neue';
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(212, 255, 0, 0.1);
            }}
        """)
        btn_amit.clicked.connect(lambda: webbrowser.open(INSTA_AMIT_URL))

        insta_layout.addWidget(btn_ido)
        insta_layout.addWidget(btn_amit)
        container_layout.addLayout(insta_layout)

        container_layout.addStretch()

        # --- Footer ---
        self.lbl_footer = QLabel("V6.0 Official")
        self.lbl_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_footer.setStyleSheet(f"color: #444444; font-family: 'Helvetica Neue'; font-size: 10px;")
        container_layout.addWidget(self.lbl_footer)

        layout.addWidget(self.container)

    def update_switch_style(self, switch):
        if switch.isChecked():
            # ON state - accent color with circle on right
            switch.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT};
                    border: none;
                    border-radius: 13px;
                    text-align: right;
                    padding-right: 3px;
                }}
                QPushButton::before {{
                    content: '';
                }}
            """)
            switch.setText("  ●")
        else:
            # OFF state - gray with circle on left
            switch.setStyleSheet(f"""
                QPushButton {{
                    background-color: #333333;
                    border: none;
                    border-radius: 13px;
                    text-align: left;
                    padding-left: 3px;
                    color: white;
                }}
            """)
            switch.setText("●  ")

    def sync_startup_toggle(self):
        """Sync the startup toggle to match whether the plist actually exists."""
        if "startup" in self.switches:
            switch = self.switches["startup"]
            actual_state = self.is_startup_enabled()
            switch.setChecked(actual_state)
            self.update_switch_style(switch)

    # --- Launch on Startup ---
    def get_plist_path(self):
        return os.path.expanduser("~/Library/LaunchAgents/com.triangle.abletonsaver.plist")

    def is_startup_enabled(self):
        """Check if the launch agent plist exists."""
        return os.path.exists(self.get_plist_path())

    def enable_launch_on_startup(self):
        """Create a macOS Launch Agent plist so the app runs at login."""
        plist_path = self.get_plist_path()
        python_path = sys.executable  # Use the Python that's running this script
        script_path = os.path.abspath(__file__)

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.triangle.abletonsaver</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ableton_saver.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ableton_saver_error.log</string>
</dict>
</plist>
"""
        try:
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)
            with open(plist_path, "w") as f:
                f.write(plist_content)
            subprocess.run(["launchctl", "load", plist_path], check=True)
        except Exception as e:
            print(f"Failed to enable startup: {e}")

    def disable_launch_on_startup(self):
        """Remove the macOS Launch Agent plist to stop running at login."""
        plist_path = self.get_plist_path()
        try:
            if os.path.exists(plist_path):
                subprocess.run(["launchctl", "unload", plist_path], stderr=subprocess.DEVNULL)
                os.remove(plist_path)
        except Exception as e:
            print(f"Failed to disable startup: {e}")

    def toggle_setting(self, switch, key):
        checked = switch.isChecked()
        self.update_switch_style(switch)

        if key == "top":
            if checked:
                self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.show()
        elif key == "pro":
            self.is_pro_mode = checked
        elif key == "startup":
            if checked:
                self.enable_launch_on_startup()
            else:
                self.disable_launch_on_startup()

    def toggle_timer_mode(self):
        self.is_timer_mode = not self.is_timer_mode

        # Widgets to hide in timer mode
        widgets_to_hide = [
            self.lbl_brand, self.lbl_subtitle, self.lbl_desc,
            self.lbl_custom, self.btn_timer_only, self.lbl_footer
        ]

        # Find the custom frame and interval buttons container
        # Hide/show frames
        for widget in self.findChildren(QFrame):
            if widget != self.container:
                widget.setVisible(not self.is_timer_mode)

        if self.is_timer_mode:
            # Enter timer mode - compact view
            for w in widgets_to_hide:
                w.hide()

            # Hide interval buttons
            for btn, _ in self.interval_buttons:
                btn.hide()

            # Hide settings rows
            for key, switch in self.switches.items():
                switch.parentWidget().hide()

            # Hide social buttons - find by traversing
            for btn in self.findChildren(QPushButton):
                text = btn.text()
                if text in ["Join Discord", "Join WhatsApp", "@ido_triangle", "@amit.triangle"]:
                    btn.hide()

            # Show back button
            self.btn_back_main.show()

            # Resize window to compact
            self.setFixedSize(WINDOW_WIDTH, 320)
            self.container.setFixedSize(WINDOW_WIDTH - 20, 300)

        else:
            # Exit timer mode - full view
            for w in widgets_to_hide:
                w.show()

            # Show interval buttons
            for btn, _ in self.interval_buttons:
                btn.show()

            # Show settings rows
            for key, switch in self.switches.items():
                switch.parentWidget().show()

            # Show social buttons
            for btn in self.findChildren(QPushButton):
                text = btn.text()
                if text in ["Join Discord", "Join WhatsApp", "@ido_triangle", "@amit.triangle"]:
                    btn.show()

            # Hide back button
            self.btn_back_main.hide()

            # Restore window size
            self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
            self.container.setFixedSize(WINDOW_WIDTH - 20, WINDOW_HEIGHT - 20)

    def set_time_unit(self, unit):
        self.time_unit = unit
        self.update_time_unit_buttons()

    def update_time_unit_buttons(self):
        for btn, unit in [(self.btn_sec, "SEC"), (self.btn_min, "MIN")]:
            if self.time_unit == unit:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_ACCENT};
                        color: black;
                        border: none;
                        border-radius: 8px;
                        font-family: 'Helvetica Neue';
                        font-size: 10px;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #222222;
                        color: {COLOR_TEXT_DIM};
                        border: none;
                        border-radius: 8px;
                        font-family: 'Helvetica Neue';
                        font-size: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: #333333;
                    }}
                """)

    def set_interval(self, seconds, clicked_btn):
        self.interval_seconds = seconds
        for btn, _ in self.interval_buttons:
            btn.set_selected(btn == clicked_btn)
        self.update_timer_display(seconds)

    def set_custom_interval(self):
        try:
            val = float(self.entry_custom.text())
            seconds = int(val * 60) if self.time_unit == "MIN" else int(val)
            self.interval_seconds = seconds
            for btn, _ in self.interval_buttons:
                btn.set_selected(False)
            self.update_timer_display(seconds)
        except:
            pass

    def update_timer_display(self, seconds):
        mins, secs = divmod(seconds, 60)
        self.lbl_timer.setText(f"{mins:02d}:{secs:02d}")

    def toggle_running(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_DANGER};
                    color: white;
                    border: none;
                    border-radius: 18px;
                    padding: 10px 20px;
                    font-family: 'Helvetica Neue';
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #FF7B75;
                }}
            """)
            self.btn_toggle.setText("STOP AUTO-SAVE")
            self.next_save_time = time.time() + self.interval_seconds
            self.lbl_timer_desc.setText("MONITORING ABLETON...")
        else:
            self.btn_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ACCENT};
                    color: black;
                    border: none;
                    border-radius: 18px;
                    padding: 10px 20px;
                    font-family: 'Helvetica Neue';
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #E2FF4D;
                }}
            """)
            self.btn_toggle.setText("START AUTO-SAVE")
            self.lbl_timer_desc.setText("NEXT SAVE CYCLE")
            self.update_timer_display(self.interval_seconds)

    def timer_loop(self):
        if self.is_running:
            remaining = int(self.next_save_time - time.time())
            if remaining <= 0:
                if self.is_ableton_frontmost():
                    self.perform_save()
                    self.next_save_time = time.time() + self.interval_seconds
                    play_notification_sound()
                else:
                    self.lbl_timer.setText("PAUSED")
                    self.lbl_timer_desc.setText("Focus Ableton to resume")
            else:
                self.update_timer_display(remaining)

    def is_ableton_frontmost(self):
        try:
            from AppKit import NSWorkspace
            active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            if active_app:
                app_name = active_app.localizedName()
                return "Live" in app_name or "Ableton" in app_name
        except:
            pass
        return False

    def run_applescript(self, script):
        try:
            p = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.communicate()
            return p.returncode == 0
        except:
            return False

    def perform_save(self):
        script_save = '''
        tell application "System Events"
            key code 1 using {command down}
        end tell
        '''
        self.run_applescript(script_save)
        self.lbl_last_saved.setText(f"Saved @ {time.strftime('%H:%M:%S')}")
        self.lbl_last_saved.setStyleSheet(f"color: {COLOR_ACCENT}; font-family: 'Helvetica Neue'; font-size: 10px;")

    def close_app(self):
        self.close()

    # --- Mouse events for dragging ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close_app()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TriangleSaver()
    window.show()
    sys.exit(app.exec())
