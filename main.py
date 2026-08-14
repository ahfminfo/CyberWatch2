"""
سامانه کاربران تحت نظارت در فضای مجازی
نسخه 9.0 - نسخه حرفه‌ای با تحلیل هوشمند
با پشتیبانی از تعداد دنبال‌کننده و بک‌آپ خودکار
"""
import sys
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QTabWidget, QMessageBox, QFileDialog,
    QHeaderView, QFrame, QStackedWidget, QScrollArea,
    QGridLayout, QProgressBar, QDialog, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

from database import Database


# ═══════════════════════════════════════════════════════
# تنظیمات اصلی برنامه
# ═══════════════════════════════════════════════════════
APP_NAME = "سامانه کاربران تحت نظارت در فضای مجازی"
APP_SHORT_NAME = "سامانه نظارت"
APP_VERSION = "9.0"

YEARS_LIST = [""] + [str(y) for y in range(1399, 1416)]

DEFAULT_SUBJECTS = [
    "",
    "اراذل و اوباش",
    "اخلاقی",
    "سلاح",
    "تشویش اذهان عمومی",
    "سیاسی",
    "امنیتی",
    "سلطنت طلب",
    "تشکیل دسته یا جمعیت با هدف بر هم زدن امنیت کشور",
    "پانجیا",
    "رصد اولیه",
    "کنکور",
    "بلاگر",
]

SUBJECT_COLORS = {
    "اراذل و اوباش": "#EF4444",
    "اخلاقی": "#F59E0B",
    "سلاح": "#DC2626",
    "تشویش اذهان عمومی": "#8B5CF6",
    "سیاسی": "#3B82F6",
    "امنیتی": "#06B6D4",
    "سلطنت طلب": "#EC4899",
    "تشکیل دسته یا جمعیت با هدف بر هم زدن امنیت کشور": "#A855F7",
    "پانجیا": "#10B981",
    "رصد اولیه": "#14B8A6",
    "کنکور": "#F97316",
    "بلاگر": "#EAB308",
}


# ═══════════════════════════════════════════════════════
# توابع کمکی برای فالوور
# ═══════════════════════════════════════════════════════
def format_followers(n):
    """تبدیل عدد فالوور به فرمت خوانا"""
    if not n or n == 0:
        return "-"
    try:
        n = int(n)
        if n >= 1000000:
            return "{:.1f}M".format(n / 1000000)
        elif n >= 1000:
            return "{:.1f}K".format(n / 1000)
        else:
            return str(n)
    except Exception:
        return "-"


def get_follower_category(n):
    """دسته‌بندی فالوور با رنگ"""
    try:
        n = int(n) if n else 0
    except Exception:
        n = 0

    if n > 1000000:
        return ("مگا", "#EF4444", "🔴")
    elif n >= 100000:
        return ("ماکرو", "#F97316", "🟠")
    elif n >= 10000:
        return ("میدل", "#EAB308", "🟡")
    elif n >= 1000:
        return ("میکرو", "#10B981", "🟢")
    elif n > 0:
        return ("نانو", "#94A3B8", "⚪")
    else:
        return ("نامشخص", "#64748B", "⚫")


# ═══════════════════════════════════════════════════════
# استایل کامل (اصلاح شده - بدون تورفتگی)
# ═══════════════════════════════════════════════════════
STYLE = """
* {
    font-family: 'Segoe UI', 'Tahoma', 'Vazirmatn', sans-serif;
}

QMainWindow, QWidget {
    background-color: #0F172A;
    color: #F1F5F9;
    font-size: 14px;
}

/* ═══ سایدبار ═══ */
#sidebar {
    background-color: #1E293B;
    border-right: 2px solid #334155;
}

#sidebarLogo {
    color: #60A5FA;
    font-size: 22px;
    font-weight: 900;
    padding: 20px 15px 5px 15px;
    background-color: transparent;
}

#sidebarSubtitle {
    color: #94A3B8;
    font-size: 12px;
    padding: 5px 15px 20px 15px;
    background-color: transparent;
}

QPushButton#navButton {
    background-color: transparent;
    color: #E2E8F0;
    border: none;
    text-align: right;
    padding: 14px 20px;
    font-size: 14px;
    font-weight: 600;
    border-radius: 10px;
    margin: 3px 8px;
}

QPushButton#navButton:hover {
    background-color: #334155;
    color: #60A5FA;
}

QPushButton#navButton:checked {
    background-color: #2563EB;
    color: white;
    font-weight: 700;
}

/* ═══ هدر صفحه ═══ */
#pageHeader {
    background-color: #2563EB;
    border-radius: 12px;
    color: white;
}

#pageTitle {
    color: white;
    font-size: 22px;
    font-weight: 900;
    padding: 8px 20px 4px 20px;
    background-color: transparent;
}

#pageSubtitle {
    color: #DBEAFE;
    font-size: 12px;
    font-weight: 500;
    padding: 0 20px 8px 20px;
    background-color: transparent;
}

/* ═══ کارت‌ها ═══ */
#card {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px;
}

#statCard {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px;
}

/* ═══ دکمه‌ها ═══ */
QPushButton {
    background-color: #334155;
    color: #F1F5F9;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #475569;
    border-color: #60A5FA;
}

QPushButton:disabled {
    background-color: #1E293B;
    color: #64748B;
    border-color: #334155;
}

QPushButton#primaryButton {
    background-color: #2563EB;
    color: white;
    border: none;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background-color: #1D4ED8;
}

QPushButton#successButton {
    background-color: #16A34A;
    color: white;
    border: none;
    font-weight: 700;
}

QPushButton#successButton:hover {
    background-color: #15803D;
}

QPushButton#dangerButton {
    background-color: #DC2626;
    color: white;
    border: none;
    font-weight: 700;
}

QPushButton#dangerButton:hover {
    background-color: #B91C1C;
}

QPushButton#warningButton {
    background-color: #F59E0B;
    color: white;
    border: none;
    font-weight: 700;
}

QPushButton#warningButton:hover {
    background-color: #D97706;
}

/* ═══ ورودی‌ها ═══ */
QLineEdit, QTextEdit {
    background-color: #0F172A;
    color: #F1F5F9;
    border: 2px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    min-height: 20px;
    selection-background-color: #2563EB;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #60A5FA;
    background-color: #1E293B;
}

QLineEdit:disabled {
    background-color: #1E293B;
    color: #64748B;
}

/* ═══ کمبوباکس ═══ */
QComboBox {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 2px solid #3B82F6;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 600;
    min-height: 22px;
    selection-background-color: #2563EB;
}

QComboBox:hover {
    border-color: #60A5FA;
    background-color: #334155;
}

QComboBox:focus {
    border-color: #93C5FD;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top left;
    width: 30px;
    border-left: 2px solid #3B82F6;
    background-color: #2563EB;
    border-top-left-radius: 6px;
    border-bottom-left-radius: 6px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid white;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 2px solid #3B82F6;
    selection-background-color: #2563EB;
    padding: 5px;
    outline: 0;
    font-size: 13px;
}

QComboBox QAbstractItemView::item {
    padding: 8px 10px;
    min-height: 25px;
    border-radius: 4px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #334155;
    color: #60A5FA;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #2563EB;
    color: white;
    font-weight: 700;
}

/* ═══ جدول ═══ */
QTableWidget {
    background-color: #1E293B;
    color: #F1F5F9;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 10px;
    selection-background-color: #1E40AF;
    font-size: 12px;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #1E40AF;
    color: white;
}

QHeaderView::section {
    background-color: #334155;
    color: #60A5FA;
    padding: 10px 8px;
    border: none;
    font-weight: 700;
    font-size: 12px;
}

/* ═══ لیبل‌ها ═══ */
QLabel {
    color: #F1F5F9;
    font-size: 13px;
    background-color: transparent;
}

QLabel#formLabel {
    color: #94A3B8;
    font-size: 12px;
    font-weight: 700;
    padding: 2px 0;
}

QLabel#requiredLabel {
    color: #F59E0B;
    font-size: 12px;
    font-weight: 700;
    padding: 2px 0;
}

/* ═══ تب‌ها ═══ */
QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 10px;
    background-color: #1E293B;
    padding: 10px;
}

QTabBar::tab {
    background-color: #334155;
    color: #94A3B8;
    padding: 10px 20px;
    margin-right: 3px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    min-width: 100px;
}

QTabBar::tab:selected {
    background-color: #2563EB;
    color: white;
    font-weight: 700;
}

QTabBar::tab:hover:!selected {
    background-color: #475569;
}

/* ═══ اسکرول‌بار ═══ */
QScrollBar:vertical {
    background-color: #0F172A;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #475569;
    border-radius: 5px;
    min-height: 25px;
}

QScrollBar::handle:vertical:hover {
    background-color: #60A5FA;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #0F172A;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #475569;
    border-radius: 5px;
    min-width: 25px;
}

/* ═══ پراگرس ═══ */
QProgressBar {
    background-color: #334155;
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #2563EB;
    border-radius: 6px;
}

/* ═══ دیالوگ ═══ */
QDialog {
    background-color: #0F172A;
}

QMessageBox {
    background-color: #1E293B;
    color: #F1F5F9;
    font-size: 13px;
}

QMessageBox QPushButton {
    min-width: 90px;
    padding: 8px 15px;
}

/* ═══ SpinBox ═══ */
QSpinBox {
    background-color: #0F172A;
    color: #F1F5F9;
    border: 2px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    min-height: 20px;
}

QSpinBox:focus {
    border-color: #60A5FA;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #334155;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #475569;
}
"""


# ═══════════════════════════════════════════════════════
# صفحه Splash
# ═══════════════════════════════════════════════════════
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 420)
        self.setLayoutDirection(Qt.RightToLeft)

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 600) // 2
        y = (screen.height() - 420) // 2
        self.move(x, y)

        self.setup_ui()

    def setup_ui(self):
        container = QFrame(self)
        container.setGeometry(0, 0, 600, 420)
        container.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 3px solid #2563EB;
                border-radius: 22px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 35, 40, 35)
        layout.setSpacing(15)

        logo = QLabel("🛡️")
        logo.setStyleSheet(
            "font-size: 70px; padding: 0; background-color: transparent;"
        )
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel(APP_NAME)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: 900;
            color: #60A5FA;
            background-color: transparent;
            padding: 5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)

        subtitle = QLabel("سامانه هوشمند جستجو، ثبت و تحلیل کاربران")
        subtitle.setStyleSheet(
            "font-size: 13px; color: #94A3B8; "
            "background-color: transparent; padding: 5px;"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p%")
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #334155;
                border: 2px solid #475569;
                border-radius: 12px;
                height: 28px;
                text-align: center;
                color: white;
                font-weight: 900;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
                border-radius: 10px;
            }
        """)
        self.progress.setFixedHeight(32)
        layout.addWidget(self.progress)

        self.status_label = QLabel("در حال آماده‌سازی...")
        self.status_label.setStyleSheet(
            "color: #E2E8F0; font-size: 13px; font-weight: 600; "
            "background-color: transparent; padding: 5px;"
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        version = QLabel("نسخه " + APP_VERSION)
        version.setStyleSheet(
            "color: #64748B; font-size: 11px; "
            "background-color: transparent;"
        )
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

    def update_progress(self, value, status=""):
        self.progress.setValue(value)
        if status:
            self.status_label.setText(status)
        QApplication.processEvents()


# ═══════════════════════════════════════════════════════
# دیالوگ Setup اولیه
# ═══════════════════════════════════════════════════════
def show_setup_dialog_standalone(app, db):
    """دیالوگ نصب اولیه"""
    dialog = QDialog()
    dialog.setWindowTitle("راه‌اندازی اولیه")
    dialog.setLayoutDirection(Qt.RightToLeft)
    dialog.setMinimumWidth(600)
    dialog.setMinimumHeight(380)
    dialog.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
    dialog.setStyleSheet("QDialog { background-color: #0F172A; }")

    result = {'done': False}

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(35, 30, 35, 30)
    layout.setSpacing(18)

    title = QLabel("🛡️ " + APP_SHORT_NAME)
    title.setStyleSheet(
        "font-size: 26px; font-weight: 900; color: #60A5FA; padding: 10px;"
    )
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    subtitle = QLabel("برای شروع، فایل اکسل دیتابیس را انتخاب کنید")
    subtitle.setAlignment(Qt.AlignCenter)
    subtitle.setStyleSheet(
        "color: #94A3B8; font-size: 14px; padding: 5px;"
    )
    layout.addWidget(subtitle)

    progress = QProgressBar()
    progress.setMinimum(0)
    progress.setMaximum(0)
    progress.setFixedHeight(26)
    progress.setStyleSheet("""
        QProgressBar {
            background-color: #334155;
            border: 2px solid #475569;
            border-radius: 10px;
        }
        QProgressBar::chunk {
            background-color: #2563EB;
            border-radius: 8px;
        }
    """)
    progress.hide()
    layout.addWidget(progress)

    status_label = QLabel("")
    status_label.setAlignment(Qt.AlignCenter)
    status_label.setStyleSheet(
        "color: #10B981; font-size: 13px; font-weight: 700;"
    )
    status_label.hide()
    layout.addWidget(status_label)

    btn = QPushButton("📂  انتخاب فایل اکسل")
    btn.setMinimumHeight(52)
    btn.setStyleSheet("""
        QPushButton {
            background-color: #2563EB;
            color: white;
            border: none;
            font-weight: 700;
            font-size: 15px;
            border-radius: 10px;
        }
        QPushButton:hover { background-color: #1D4ED8; }
        QPushButton:disabled {
            background-color: #475569;
            color: #94A3B8;
        }
    """)
    layout.addWidget(btn)

    skip_btn = QPushButton("رد کردن (شروع با دیتابیس خالی)")
    skip_btn.setMinimumHeight(40)
    skip_btn.setStyleSheet("""
        QPushButton {
            background-color: #334155;
            color: #F1F5F9;
            border: 1px solid #475569;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
        }
        QPushButton:hover { background-color: #475569; }
    """)
    layout.addWidget(skip_btn)

    layout.addStretch()

    def load_excel():
        file_path, _ = QFileDialog.getOpenFileName(
            dialog, "انتخاب فایل اکسل", "",
            "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        btn.setEnabled(False)
        skip_btn.setEnabled(False)
        btn.setText("⏳  در حال بارگذاری...")
        progress.show()
        status_label.setText("در حال خواندن فایل...")
        status_label.setStyleSheet(
            "color: #60A5FA; font-size: 13px; font-weight: 700;"
        )
        status_label.show()
        app.processEvents()

        try:
            total = db.import_excel(file_path)
            progress.hide()
            status_label.setText(
                "✅ {:,} رکورد با موفقیت بارگذاری شد!".format(total)
            )
            status_label.setStyleSheet(
                "color: #10B981; font-size: 14px; font-weight: 700;"
            )
            app.processEvents()
            time.sleep(1.5)
            result['done'] = True
            dialog.accept()

        except Exception as e:
            progress.hide()
            btn.setEnabled(True)
            skip_btn.setEnabled(True)
            btn.setText("📂  انتخاب فایل اکسل")
            status_label.setText("❌ خطا: " + str(e))
            status_label.setStyleSheet(
                "color: #EF4444; font-size: 12px; font-weight: 700;"
            )
            status_label.show()
            app.processEvents()

    def skip_setup():
        db.create_tables()
        result['done'] = True
        dialog.accept()

    btn.clicked.connect(load_excel)
    skip_btn.clicked.connect(skip_setup)

    screen = app.primaryScreen().geometry()
    x = (screen.width() - dialog.width()) // 2
    y = (screen.height() - dialog.height()) // 2
    dialog.move(x, y)

    dialog.raise_()
    dialog.activateWindow()
    dialog.exec_()

    return result['done']
    # ═══════════════════════════════════════════════════════
# کلاس اصلی برنامه
# ═══════════════════════════════════════════════════════
class CyberWatchApp(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.edit_id = None

        self.setWindowTitle(APP_NAME + " - نسخه " + APP_VERSION)
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(1550, 920)
        self.setMinimumSize(1350, 780)

        self.setup_ui()
        self.show_dashboard()

    def closeEvent(self, event):
        """بک‌آپ خودکار هنگام بستن برنامه"""
        try:
            if self.db.is_ready():
                self.db.create_backup()
        except Exception:
            pass
        event.accept()

    # ═══════════════════════════════════════════════
    # توابع کمکی
    # ═══════════════════════════════════════════════
    def get_subjects_list(self):
        return DEFAULT_SUBJECTS

    def get_clean_subject_stats(self):
        """آمار موضوعات پاک (بدون ترکیب)"""
        if not self.db.is_ready():
            return []

        conn = self.db._conn()
        rows = conn.execute(
            "SELECT subject FROM users WHERE subject != ''"
        ).fetchall()
        conn.close()

        subject_counts = {s: 0 for s in DEFAULT_SUBJECTS if s}

        for row in rows:
            subj = row['subject']
            parts = [s.strip() for s in subj.split('|')]
            for part in parts:
                if part in subject_counts:
                    subject_counts[part] += 1

        result = [(s, c) for s, c in subject_counts.items() if c > 0]
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def get_user_all_subjects(self, instagram_id):
        if not self.db.is_ready():
            return []
        conn = self.db._conn()
        rows = conn.execute(
            "SELECT DISTINCT subject FROM users "
            "WHERE instagram_id=? AND subject!=''",
            (instagram_id,)
        ).fetchall()
        conn.close()
        subjects = []
        for r in rows:
            subj = r['subject']
            parts = [s.strip() for s in subj.split('|')]
            for p in parts:
                if p and p not in subjects:
                    subjects.append(p)
        return subjects

    # ═══════════════════════════════════════════════
    # ساخت UI اصلی
    # ═══════════════════════════════════════════════
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        self.dashboard_page = self.create_dashboard_page()
        self.search_page = self.create_search_page()
        self.advanced_page = self.create_advanced_page()
        self.form_page = self.create_form_page()
        self.list_page = self.create_list_page()
        self.analytics_page = self.create_analytics_page()
        self.settings_page = self.create_settings_page()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.advanced_page)
        self.stack.addWidget(self.form_page)
        self.stack.addWidget(self.list_page)
        self.stack.addWidget(self.analytics_page)
        self.stack.addWidget(self.settings_page)

    # ═══════════════════════════════════════════════
    # سایدبار
    # ═══════════════════════════════════════════════
    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel("🛡️ " + APP_SHORT_NAME)
        logo.setObjectName("sidebarLogo")
        logo.setAlignment(Qt.AlignCenter)
        logo.setWordWrap(True)
        layout.addWidget(logo)

        subtitle = QLabel("مدیریت هوشمند\nکاربران فضای مجازی")
        subtitle.setObjectName("sidebarSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        self.nav_buttons = []

        nav_items = [
            ("🏠   داشبورد", self.show_dashboard),
            ("🔍   جستجوی هوشمند", self.show_search),
            ("🔬   جستجوی پیشرفته", self.show_advanced),
            ("➕   ثبت کاربر جدید", self.show_form),
            ("📋   همه رکوردها", self.show_list),
            ("📊   تحلیل هوشمند", self.show_analytics),
            ("⚙️   تنظیمات", self.show_settings),
        ]

        for text, callback in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(callback)
            btn.setMinimumHeight(48)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        self.records_label = QLabel("کل رکوردها: 0")
        self.records_label.setStyleSheet(
            "color: #60A5FA; padding: 18px 10px; "
            "font-weight: 700; font-size: 14px;"
        )
        self.records_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.records_label)

        version = QLabel("نسخه " + APP_VERSION)
        version.setStyleSheet(
            "color: #475569; padding: 6px; font-size: 11px;"
        )
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        return sidebar

    def set_active_nav(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    # ═══════════════════════════════════════════════
    # هدر صفحه
    # ═══════════════════════════════════════════════
    def create_page_header(self, title, subtitle=""):
        header = QFrame()
        header.setObjectName("pageHeader")
        header.setFixedHeight(80)

        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("pageTitle")
        layout.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("pageSubtitle")
            layout.addWidget(sub_lbl)

        return header

    # ═══════════════════════════════════════════════
    # صفحه داشبورد
    # ═══════════════════════════════════════════════
    def create_dashboard_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        page.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18)

        layout.addWidget(self.create_page_header(
            "🏠 داشبورد",
            "نمای کلی از وضعیت دیتابیس و آمار سامانه"
        ))

        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(15)
        layout.addLayout(self.stats_grid)

        self.subjects_card = QFrame()
        self.subjects_card.setObjectName("card")
        layout.addWidget(self.subjects_card)

        self.years_card = QFrame()
        self.years_card.setObjectName("card")
        layout.addWidget(self.years_card)

        layout.addStretch()

        page.setWidget(content)
        return page

    def update_dashboard(self):
        stats = self.db.get_stats()
        clean_subjects = self.get_clean_subject_stats()

        self.records_label.setText(
            "کل رکوردها: {:,}".format(stats['total'])
        )

        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        active_years = len(stats['years'])
        ph_pct = int(
            (stats['filled'].get('phone', 0) / max(stats['total'], 1)) * 100
        )
        ig_pct = int(
            (stats['filled'].get('instagram_id', 0) /
             max(stats['total'], 1)) * 100
        )
        fl_pct = int(
            (stats['filled'].get('followers', 0) /
             max(stats['total'], 1)) * 100
        )

        cards = [
            ("📦", "{:,}".format(stats['total']),
             "کل رکوردها", "#60A5FA"),
            ("📅", str(active_years), "سال فعال", "#10B981"),
            ("📂", str(len(clean_subjects)), "موضوعات", "#F59E0B"),
            ("📱", "{}%".format(ph_pct), "شماره تماس", "#A855F7"),
            ("📸", "{}%".format(ig_pct), "ایدی اینستا", "#EF4444"),
            ("👥", "{}%".format(fl_pct), "دارای فالوور", "#EAB308"),
        ]

        for i, (icon, value, label, color) in enumerate(cards):
            card = QFrame()
            card.setObjectName("statCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 12, 15, 12)
            card_layout.setSpacing(6)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 36px;")
            icon_lbl.setAlignment(Qt.AlignCenter)

            value_lbl = QLabel(value)
            value_lbl.setStyleSheet(
                "font-size: 26px; font-weight: 900; color: " + color + ";"
            )
            value_lbl.setAlignment(Qt.AlignCenter)

            label_lbl = QLabel(label)
            label_lbl.setStyleSheet(
                "color: #94A3B8; font-size: 13px; font-weight: 600;"
            )
            label_lbl.setAlignment(Qt.AlignCenter)

            card_layout.addWidget(icon_lbl)
            card_layout.addWidget(value_lbl)
            card_layout.addWidget(label_lbl)

            self.stats_grid.addWidget(card, 0, i)

        self.update_subjects_card(clean_subjects)
        self.update_years_card(stats)

    def update_subjects_card(self, subjects_data):
        old_layout = self.subjects_card.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            old_layout = QVBoxLayout(self.subjects_card)
            old_layout.setContentsMargins(15, 15, 15, 15)
            old_layout.setSpacing(10)

        title = QLabel("📂 موضوعات ثبت شده")
        title.setStyleSheet(
            "font-size: 16px; font-weight: 700; "
            "color: #60A5FA; padding: 5px;"
        )
        old_layout.addWidget(title)

        if not subjects_data:
            no_data = QLabel("هیچ موضوعی ثبت نشده است")
            no_data.setStyleSheet(
                "color: #64748B; padding: 15px; font-size: 13px;"
            )
            no_data.setAlignment(Qt.AlignCenter)
            old_layout.addWidget(no_data)
            return

        max_cnt = max((c for _, c in subjects_data), default=1)

        for subj, cnt in subjects_data:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(8, 3, 8, 3)
            row.setSpacing(10)

            color = SUBJECT_COLORS.get(subj, "#60A5FA")

            name = QLabel("▸  " + subj)
            name.setStyleSheet(
                "padding: 4px; font-size: 13px; "
                "font-weight: 600; color: #F1F5F9;"
            )
            row.addWidget(name, 3)

            bar = QProgressBar()
            bar.setMaximum(max_cnt)
            bar.setValue(cnt)
            bar.setTextVisible(False)
            bar.setStyleSheet(
                "QProgressBar { background-color: #334155; "
                "border: none; border-radius: 6px; height: 12px; } "
                "QProgressBar::chunk { background-color: " + color +
                "; border-radius: 6px; }"
            )
            bar.setFixedHeight(12)
            row.addWidget(bar, 4)

            count = QLabel(str(cnt))
            count.setStyleSheet(
                "color: " + color + "; font-weight: 900; "
                "font-size: 15px; padding: 3px 10px;"
            )
            count.setMinimumWidth(60)
            count.setAlignment(Qt.AlignCenter)
            row.addWidget(count, 1)

            old_layout.addWidget(row_widget)

    def update_years_card(self, stats):
        old_layout = self.years_card.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            old_layout = QVBoxLayout(self.years_card)
            old_layout.setContentsMargins(15, 15, 15, 15)
            old_layout.setSpacing(10)

        title = QLabel("📅 توزیع سال‌های ثبت")
        title.setStyleSheet(
            "font-size: 16px; font-weight: 700; "
            "color: #60A5FA; padding: 5px;"
        )
        old_layout.addWidget(title)

        if not stats['years']:
            no_data = QLabel("داده‌ای موجود نیست")
            no_data.setStyleSheet(
                "color: #64748B; padding: 15px; font-size: 13px;"
            )
            no_data.setAlignment(Qt.AlignCenter)
            old_layout.addWidget(no_data)
            return

        max_cnt = max((c for _, c in stats['years']), default=1)

        year_colors = [
            "#3B82F6", "#10B981", "#F59E0B", "#EF4444",
            "#A855F7", "#EC4899", "#14B8A6"
        ]

        for i, (year, cnt) in enumerate(stats['years']):
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(8, 3, 8, 3)
            row.setSpacing(10)

            color = year_colors[i % len(year_colors)]

            name = QLabel("📅  " + str(year))
            name.setStyleSheet(
                "padding: 4px; font-size: 13px; "
                "font-weight: 700; color: #F1F5F9;"
            )
            name.setMinimumWidth(90)
            row.addWidget(name, 1)

            bar = QProgressBar()
            bar.setMaximum(max_cnt)
            bar.setValue(cnt)
            bar.setTextVisible(False)
            bar.setStyleSheet(
                "QProgressBar { background-color: #334155; "
                "border: none; border-radius: 6px; height: 12px; } "
                "QProgressBar::chunk { background-color: " + color +
                "; border-radius: 6px; }"
            )
            bar.setFixedHeight(12)
            row.addWidget(bar, 4)

            count = QLabel("{:,}".format(cnt))
            count.setStyleSheet(
                "color: " + color + "; font-weight: 900; "
                "font-size: 15px; padding: 3px 10px;"
            )
            count.setMinimumWidth(60)
            count.setAlignment(Qt.AlignCenter)
            row.addWidget(count, 1)

            old_layout.addWidget(row_widget)

    # ═══════════════════════════════════════════════
    # جدول نتایج مشترک (با ستون فالوور)
    # ═══════════════════════════════════════════════
    def create_results_table(self):
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "ID", "ایدی اینستاگرام", "نام", "نام خانوادگی",
            "شماره تماس", "شماره ملی", "موضوع", "فالوور", "سال"
        ])
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.verticalHeader().setDefaultSectionSize(36)
        table.verticalHeader().setVisible(False)

        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        table.setColumnWidth(0, 60)
        table.setColumnWidth(2, 100)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 110)
        table.setColumnWidth(5, 100)
        table.setColumnWidth(6, 130)
        table.setColumnWidth(7, 90)
        table.setColumnWidth(8, 80)

        return table

    def populate_table(self, table, results):
        table.setRowCount(len(results))
        for row_idx, rec in enumerate(results):
            table.setItem(row_idx, 0,
                QTableWidgetItem(str(rec.get('id', ''))))
            table.setItem(row_idx, 1,
                QTableWidgetItem(rec.get('instagram_id', '')))
            table.setItem(row_idx, 2,
                QTableWidgetItem(rec.get('first_name', '')))
            table.setItem(row_idx, 3,
                QTableWidgetItem(rec.get('last_name', '')))
            table.setItem(row_idx, 4,
                QTableWidgetItem(rec.get('phone', '')))
            table.setItem(row_idx, 5,
                QTableWidgetItem(rec.get('national_id', '')))
            table.setItem(row_idx, 6,
                QTableWidgetItem(rec.get('subject', '')))

            # فالوور با فرمت زیبا
            followers = rec.get('followers', 0)
            follower_item = QTableWidgetItem(format_followers(followers))
            cat, color, _ = get_follower_category(followers)
            from PyQt5.QtGui import QColor
            follower_item.setForeground(QColor(color))
            table.setItem(row_idx, 7, follower_item)

            table.setItem(row_idx, 8,
                QTableWidgetItem(rec.get('reg_year', '')))

    def get_selected_id(self, table):
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "توجه", "یک ردیف را انتخاب کنید")
            return None
        return int(table.item(row, 0).text())

    # ═══════════════════════════════════════════════
    # صفحه جستجوی هوشمند
    # ═══════════════════════════════════════════════
    def create_search_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        layout.addWidget(self.create_page_header(
            "🔍 جستجوی هوشمند",
            "جستجو در تمام فیلدها به صورت همزمان"
        ))

        search_card = QFrame()
        search_card.setObjectName("card")
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(15, 12, 15, 12)
        search_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "🔍  نام، شماره، ایدی، موضوع، آدرس ..."
        )
        self.search_input.setMinimumHeight(44)
        self.search_input.setStyleSheet(
            "font-size: 14px; padding: 8px 12px;"
        )
        self.search_input.returnPressed.connect(self.do_search)
        search_layout.addWidget(self.search_input, 5)

        search_btn = QPushButton("🔍 جستجو")
        search_btn.setObjectName("primaryButton")
        search_btn.setMinimumHeight(44)
        search_btn.setStyleSheet("font-size: 14px;")
        search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(search_btn, 1)

        clear_btn = QPushButton("🔄 پاک")
        clear_btn.setMinimumHeight(44)
        clear_btn.clicked.connect(lambda: [
            self.search_input.clear(),
            self.search_table.setRowCount(0),
            self.search_count.setText("")
        ])
        search_layout.addWidget(clear_btn, 1)

        layout.addWidget(search_card)

        self.search_count = QLabel("")
        self.search_count.setStyleSheet(
            "color: #10B981; font-weight: 700; "
            "padding: 5px; font-size: 14px;"
        )
        layout.addWidget(self.search_count)

        self.search_table = self.create_results_table()
        layout.addWidget(self.search_table, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        view_btn = QPushButton("👁️ مشاهده کامل")
        view_btn.setObjectName("primaryButton")
        view_btn.setMinimumHeight(40)
        view_btn.clicked.connect(lambda: self.view_record(self.search_table))
        btn_row.addWidget(view_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.setObjectName("warningButton")
        edit_btn.setMinimumHeight(40)
        edit_btn.clicked.connect(lambda: self.edit_record(self.search_table))
        btn_row.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(lambda: self.delete_record(self.search_table))
        btn_row.addWidget(delete_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        return page

    def do_search(self):
        query = self.search_input.text().strip()
        results = self.db.search(query)
        self.populate_table(self.search_table, results)
        self.search_count.setText(
            "✅ {} نتیجه یافت شد".format(len(results))
        )

    # ═══════════════════════════════════════════════
    # مشاهده کامل رکورد
    # ═══════════════════════════════════════════════
    def view_record(self, table):
        rec_id = self.get_selected_id(table)
        if rec_id is None:
            return
        rec = self.db.get_by_id(rec_id)
        if not rec:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("مشاهده کامل کاربر")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumSize(720, 650)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        name = "{} {}".format(
            rec.get('first_name', ''), rec.get('last_name', '')
        )
        title = QLabel("👤 " + name)
        title.setStyleSheet(
            "font-size: 22px; font-weight: 900; color: #60A5FA; "
            "padding: 12px; background-color: #1E293B; border-radius: 10px;"
        )
        layout.addWidget(title)

        # نمایش فالوور با دسته‌بندی
        followers = rec.get('followers', 0)
        if followers and followers > 0:
            cat, color, emoji = get_follower_category(followers)
            follower_frame = QFrame()
            follower_frame.setStyleSheet(
                "background-color: " + color + "22; "
                "border: 2px solid " + color + "; "
                "border-radius: 10px; padding: 10px;"
            )
            fl = QHBoxLayout(follower_frame)
            fl.setContentsMargins(10, 5, 10, 5)

            fl_icon = QLabel(emoji + " " + cat)
            fl_icon.setStyleSheet(
                "font-size: 15px; font-weight: 700; color: " + color + ";"
            )
            fl.addWidget(fl_icon)

            fl_count = QLabel(
                "{:,} دنبال‌کننده".format(int(followers))
            )
            fl_count.setStyleSheet(
                "font-size: 15px; font-weight: 700; "
                "color: white; padding-right: 15px;"
            )
            fl.addWidget(fl_count)
            fl.addStretch()

            layout.addWidget(follower_frame)

        # موضوعات
        instagram_id = rec.get('instagram_id', '')
        if instagram_id:
            all_subjects = self.get_user_all_subjects(instagram_id)
            if all_subjects:
                subjects_frame = QFrame()
                subjects_frame.setStyleSheet(
                    "background-color: #1E3A8A; "
                    "border-radius: 10px; padding: 12px;"
                )
                sf_layout = QVBoxLayout(subjects_frame)
                sf_layout.setSpacing(8)
                sf_layout.setContentsMargins(10, 10, 10, 10)

                lbl = QLabel("📂 همه موضوعات ثبت شده برای این کاربر:")
                lbl.setStyleSheet(
                    "color: #93C5FD; font-weight: 700; font-size: 14px;"
                )
                sf_layout.addWidget(lbl)

                subjects_row = QHBoxLayout()
                subjects_row.setSpacing(6)
                for subj in all_subjects:
                    color = SUBJECT_COLORS.get(subj, "#60A5FA")
                    badge = QLabel("● " + subj)
                    badge.setStyleSheet(
                        "background-color: " + color + "; color: white; "
                        "padding: 5px 10px; border-radius: 12px; "
                        "font-weight: 700; font-size: 11px;"
                    )
                    subjects_row.addWidget(badge)
                subjects_row.addStretch()

                subjects_widget = QWidget()
                subjects_widget.setLayout(subjects_row)
                sf_layout.addWidget(subjects_widget)

                layout.addWidget(subjects_frame)

        fa_map = {
            'instagram_id': 'ایدی اینستاگرام',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'father_name': 'نام پدر',
            'phone': 'شماره تماس',
            'national_id': 'شماره ملی',
            'subject': 'موضوع این ثبت',
            'tarnama_code': 'کد تارنما',
            'reg_date': 'تاریخ ثبت',
            'address': 'نشانی',
            'reg_year': 'سال ثبت',
        }

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(6)
        content_layout.setContentsMargins(5, 5, 5, 5)

        for key, fa in fa_map.items():
            val = rec.get(key, '')
            if val:
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                row.setContentsMargins(5, 3, 5, 3)
                row.setSpacing(10)

                lbl = QLabel(fa + ":")
                lbl.setStyleSheet(
                    "color: #94A3B8; font-weight: 700; "
                    "min-width: 150px; font-size: 13px;"
                )
                row.addWidget(lbl)

                val_lbl = QLabel(str(val))
                val_lbl.setStyleSheet(
                    "color: #F1F5F9; padding: 8px 12px; "
                    "background: #334155; border-radius: 8px; "
                    "font-size: 13px; font-weight: 500;"
                )
                val_lbl.setWordWrap(True)
                row.addWidget(val_lbl, 1)

                content_layout.addWidget(row_widget)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        close_btn = QPushButton("بستن")
        close_btn.setMinimumHeight(42)
        close_btn.setStyleSheet("font-size: 14px;")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    def edit_record(self, table):
        rec_id = self.get_selected_id(table)
        if rec_id is None:
            return
        self.edit_id = rec_id
        self.load_form_data(self.db.get_by_id(rec_id))
        self.show_form()

    def delete_record(self, table):
        rec_id = self.get_selected_id(table)
        if rec_id is None:
            return
        rec = self.db.get_by_id(rec_id)
        if not rec:
            return
        name = "{} {}".format(
            rec.get('first_name', ''), rec.get('last_name', '')
        )
        reply = QMessageBox.question(
            self, "تأیید حذف",
            "آیا از حذف «" + name + "» مطمئن هستید؟",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_user(rec_id)
            QMessageBox.information(self, "موفق", "✅ حذف شد!")
            if table == self.search_table:
                self.do_search()
            elif table == self.list_table:
                self.load_list()
        # ═══════════════════════════════════════════════
    # صفحه جستجوی پیشرفته
    # ═══════════════════════════════════════════════
    def create_advanced_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        layout.addWidget(self.create_page_header(
            "🔬 جستجوی پیشرفته",
            "فیلتر همزمان چند فیلد برای نتیجه دقیق‌تر"
        ))

        form_card = QFrame()
        form_card.setObjectName("card")
        form_layout = QGridLayout(form_card)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(12)

        self.adv_filters = {}

        text_fields = [
            'نام', 'نام خانوادگی', 'ایدی اینستاگرام',
            'شماره تماس', 'شماره ملی', 'نشانی',
            'نام پدر', 'کد تارنما'
        ]

        for i, field in enumerate(text_fields):
            row = i // 4
            col = i % 4

            wrapper = QWidget()
            container = QVBoxLayout(wrapper)
            container.setContentsMargins(0, 0, 0, 0)
            container.setSpacing(5)

            lbl = QLabel(field)
            lbl.setObjectName("formLabel")
            container.addWidget(lbl)

            inp = QLineEdit()
            inp.setPlaceholderText(field + "...")
            inp.setMinimumHeight(38)
            container.addWidget(inp)
            self.adv_filters[field] = inp

            form_layout.addWidget(wrapper, row, col)

        # موضوع
        subj_wrapper = QWidget()
        subj_container = QVBoxLayout(subj_wrapper)
        subj_container.setContentsMargins(0, 0, 0, 0)
        subj_container.setSpacing(5)
        subj_lbl = QLabel("📂 موضوع ثبت")
        subj_lbl.setObjectName("formLabel")
        subj_container.addWidget(subj_lbl)
        self.adv_subject = QComboBox()
        self.adv_subject.setMinimumHeight(40)
        self.adv_subject.addItems(self.get_subjects_list())
        subj_container.addWidget(self.adv_subject)
        form_layout.addWidget(subj_wrapper, 2, 0, 1, 2)

        # سال
        year_wrapper = QWidget()
        year_container = QVBoxLayout(year_wrapper)
        year_container.setContentsMargins(0, 0, 0, 0)
        year_container.setSpacing(5)
        year_lbl = QLabel("📅 سال ثبت")
        year_lbl.setObjectName("formLabel")
        year_container.addWidget(year_lbl)
        self.adv_year = QComboBox()
        self.adv_year.setMinimumHeight(40)
        self.adv_year.addItems(YEARS_LIST)
        year_container.addWidget(self.adv_year)
        form_layout.addWidget(year_wrapper, 2, 2, 1, 2)

        layout.addWidget(form_card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        search_btn = QPushButton("🔬 اعمال فیلترها")
        search_btn.setObjectName("primaryButton")
        search_btn.setMinimumHeight(42)
        search_btn.setStyleSheet("font-size: 14px; min-width: 180px;")
        search_btn.clicked.connect(self.do_advanced_search)
        btn_row.addWidget(search_btn)

        clear_btn = QPushButton("🔄 پاک کردن")
        clear_btn.setMinimumHeight(42)
        clear_btn.clicked.connect(self.clear_advanced)
        btn_row.addWidget(clear_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.adv_count = QLabel("")
        self.adv_count.setStyleSheet(
            "color: #10B981; font-weight: 700; padding: 5px; font-size: 14px;"
        )
        layout.addWidget(self.adv_count)

        self.adv_table = self.create_results_table()
        layout.addWidget(self.adv_table, 1)

        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(10)
        view_btn = QPushButton("👁️ مشاهده")
        view_btn.setObjectName("primaryButton")
        view_btn.setMinimumHeight(40)
        view_btn.clicked.connect(lambda: self.view_record(self.adv_table))
        btn_row2.addWidget(view_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.setObjectName("warningButton")
        edit_btn.setMinimumHeight(40)
        edit_btn.clicked.connect(lambda: self.edit_record(self.adv_table))
        btn_row2.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(lambda: self.delete_record(self.adv_table))
        btn_row2.addWidget(delete_btn)

        btn_row2.addStretch()
        layout.addLayout(btn_row2)

        return page

    def do_advanced_search(self):
        filters = {}
        for key, widget in self.adv_filters.items():
            val = widget.text().strip()
            if val:
                filters[key] = val

        subj = self.adv_subject.currentText()
        if subj:
            filters['موضوع ثبت'] = subj

        year = self.adv_year.currentText()
        if year:
            filters['سال ثبت'] = year

        results = self.db.advanced_search(filters) if filters else []
        self.populate_table(self.adv_table, results)
        self.adv_count.setText("✅ {} نتیجه یافت شد".format(len(results)))

    def clear_advanced(self):
        for widget in self.adv_filters.values():
            widget.clear()
        self.adv_subject.setCurrentIndex(0)
        self.adv_year.setCurrentIndex(0)
        self.adv_table.setRowCount(0)
        self.adv_count.setText("")

    # ═══════════════════════════════════════════════
    # صفحه فرم ثبت (با فیلد فالوور)
    # ═══════════════════════════════════════════════
    def create_form_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        page.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(18)

        self.form_header = self.create_page_header(
            "➕ ثبت کاربر جدید",
            "اطلاعات کاربر جدید را با دقت وارد کنید"
        )
        layout.addWidget(self.form_header)

        form_card = QFrame()
        form_card.setObjectName("card")
        form_layout = QGridLayout(form_card)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(15)

        # ردیف ۱: ایدی + نام
        lbl = QLabel("⭐ ایدی اینستاگرام *")
        lbl.setObjectName("requiredLabel")
        form_layout.addWidget(lbl, 0, 0)
        self.form_instagram = QLineEdit()
        self.form_instagram.setMinimumHeight(40)
        form_layout.addWidget(self.form_instagram, 0, 1)

        lbl2 = QLabel("نام")
        lbl2.setObjectName("formLabel")
        form_layout.addWidget(lbl2, 0, 2)
        self.form_first_name = QLineEdit()
        self.form_first_name.setMinimumHeight(40)
        form_layout.addWidget(self.form_first_name, 0, 3)

        # ردیف ۲
        lbl3 = QLabel("نام خانوادگی")
        lbl3.setObjectName("formLabel")
        form_layout.addWidget(lbl3, 1, 0)
        self.form_last_name = QLineEdit()
        self.form_last_name.setMinimumHeight(40)
        form_layout.addWidget(self.form_last_name, 1, 1)

        lbl4 = QLabel("نام پدر")
        lbl4.setObjectName("formLabel")
        form_layout.addWidget(lbl4, 1, 2)
        self.form_father_name = QLineEdit()
        self.form_father_name.setMinimumHeight(40)
        form_layout.addWidget(self.form_father_name, 1, 3)

        # ردیف ۳
        lbl5 = QLabel("شماره تماس")
        lbl5.setObjectName("formLabel")
        form_layout.addWidget(lbl5, 2, 0)
        self.form_phone = QLineEdit()
        self.form_phone.setMinimumHeight(40)
        form_layout.addWidget(self.form_phone, 2, 1)

        lbl6 = QLabel("شماره ملی")
        lbl6.setObjectName("formLabel")
        form_layout.addWidget(lbl6, 2, 2)
        self.form_national_id = QLineEdit()
        self.form_national_id.setMinimumHeight(40)
        form_layout.addWidget(self.form_national_id, 2, 3)

        # ردیف ۴: فالوور + سال
        lbl_fl = QLabel("👥 تعداد دنبال‌کننده")
        lbl_fl.setObjectName("formLabel")
        form_layout.addWidget(lbl_fl, 3, 0)
        self.form_followers = QLineEdit()
        self.form_followers.setMinimumHeight(40)
        self.form_followers.setPlaceholderText("مثال: 15000")
        self.form_followers.setValidator(QIntValidator(0, 999999999))
        form_layout.addWidget(self.form_followers, 3, 1)

        lbl8 = QLabel("📅 سال ثبت")
        lbl8.setObjectName("formLabel")
        form_layout.addWidget(lbl8, 3, 2)
        self.form_year = QComboBox()
        self.form_year.setMinimumHeight(40)
        self.form_year.addItems(YEARS_LIST)
        form_layout.addWidget(self.form_year, 3, 3)

        # ردیف ۵: موضوع
        lbl7 = QLabel("📂 موضوع ثبت *")
        lbl7.setObjectName("requiredLabel")
        form_layout.addWidget(lbl7, 4, 0)
        self.form_subject = QComboBox()
        self.form_subject.setMinimumHeight(40)
        self.form_subject.addItems(self.get_subjects_list())
        form_layout.addWidget(self.form_subject, 4, 1)

        lbl9 = QLabel("کد تارنما")
        lbl9.setObjectName("formLabel")
        form_layout.addWidget(lbl9, 4, 2)
        self.form_tarnama = QLineEdit()
        self.form_tarnama.setMinimumHeight(40)
        form_layout.addWidget(self.form_tarnama, 4, 3)

        # ردیف ۶: تاریخ
        lbl10 = QLabel("تاریخ ثبت")
        lbl10.setObjectName("formLabel")
        form_layout.addWidget(lbl10, 5, 0)
        self.form_reg_date = QLineEdit()
        self.form_reg_date.setMinimumHeight(40)
        self.form_reg_date.setPlaceholderText("مثال: 1403/05/15")
        form_layout.addWidget(self.form_reg_date, 5, 1)

        # ردیف ۷: نشانی
        lbl11 = QLabel("نشانی")
        lbl11.setObjectName("formLabel")
        form_layout.addWidget(lbl11, 6, 0)
        self.form_address = QTextEdit()
        self.form_address.setMaximumHeight(90)
        form_layout.addWidget(self.form_address, 6, 1, 1, 3)

        layout.addWidget(form_card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.save_btn = QPushButton("✅  ثبت کاربر")
        self.save_btn.setObjectName("successButton")
        self.save_btn.setMinimumHeight(48)
        self.save_btn.setStyleSheet("font-size: 15px; min-width: 200px;")
        self.save_btn.clicked.connect(self.save_form)
        btn_row.addWidget(self.save_btn)

        cancel_btn = QPushButton("❌  انصراف")
        cancel_btn.setMinimumHeight(48)
        cancel_btn.setStyleSheet("font-size: 14px; min-width: 150px;")
        cancel_btn.clicked.connect(self.cancel_form)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addStretch()

        page.setWidget(content)
        return page

    def load_form_data(self, rec):
        self.form_instagram.setText(rec.get('instagram_id', ''))
        self.form_first_name.setText(rec.get('first_name', ''))
        self.form_last_name.setText(rec.get('last_name', ''))
        self.form_father_name.setText(rec.get('father_name', ''))
        self.form_phone.setText(rec.get('phone', ''))
        self.form_national_id.setText(rec.get('national_id', ''))
        self.form_tarnama.setText(rec.get('tarnama_code', ''))
        self.form_reg_date.setText(rec.get('reg_date', ''))
        self.form_address.setPlainText(rec.get('address', ''))

        followers = rec.get('followers', 0)
        self.form_followers.setText(
            str(followers) if followers else ""
        )

        subj = rec.get('subject', '')
        if '|' in subj:
            subj = subj.split('|')[0].strip()
        idx = self.form_subject.findText(subj)
        self.form_subject.setCurrentIndex(idx if idx >= 0 else 0)

        year = rec.get('reg_year', '')
        if '|' in year:
            year = year.split('|')[0].strip()
        idx = self.form_year.findText(year)
        self.form_year.setCurrentIndex(idx if idx >= 0 else 0)

    def clear_form(self):
        self.form_instagram.clear()
        self.form_first_name.clear()
        self.form_last_name.clear()
        self.form_father_name.clear()
        self.form_phone.clear()
        self.form_national_id.clear()
        self.form_tarnama.clear()
        self.form_reg_date.clear()
        self.form_address.clear()
        self.form_followers.clear()
        self.form_subject.setCurrentIndex(0)
        self.form_year.setCurrentIndex(0)

    def save_form(self):
        instagram_id = self.form_instagram.text().strip()
        if not instagram_id:
            QMessageBox.warning(
                self, "خطا", "⭐ ایدی اینستاگرام الزامی است!"
            )
            return

        subject = self.form_subject.currentText().strip()
        if not subject:
            QMessageBox.warning(
                self, "خطا", "📂 موضوع ثبت الزامی است!"
            )
            return

        followers_text = self.form_followers.text().strip()
        try:
            followers = int(followers_text) if followers_text else 0
        except Exception:
            followers = 0

        data = {
            'instagram_id': instagram_id,
            'first_name': self.form_first_name.text().strip(),
            'last_name': self.form_last_name.text().strip(),
            'father_name': self.form_father_name.text().strip(),
            'phone': self.form_phone.text().strip(),
            'national_id': self.form_national_id.text().strip(),
            'subject': subject,
            'tarnama_code': self.form_tarnama.text().strip(),
            'reg_date': self.form_reg_date.text().strip(),
            'address': self.form_address.toPlainText().strip(),
            'reg_year': self.form_year.currentText().strip(),
            'followers': followers,
        }

        if self.edit_id:
            self.db.update_user(self.edit_id, data)
            QMessageBox.information(
                self, "موفق", "✅ اطلاعات با موفقیت ویرایش شد!"
            )
            self.edit_id = None
        else:
            self.db.add_user(data)
            QMessageBox.information(
                self, "موفق", "✅ کاربر جدید با موفقیت ثبت شد!"
            )

        self.clear_form()
        self.show_dashboard()

    def cancel_form(self):
        self.clear_form()
        self.edit_id = None
        self.show_dashboard()

    # ═══════════════════════════════════════════════
    # 🔬 صفحه تحلیل هوشمند
    # ═══════════════════════════════════════════════
    def create_analytics_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        layout.addWidget(self.create_page_header(
            "📊 تحلیل هوشمند",
            "تحلیل تخصصی موضوعات، فالوور و مقایسه‌های آماری"
        ))

        # تب‌های تحلیل
        self.analytics_tabs = QTabWidget()

        # تب ۱: تحلیل یک موضوع
        self.analytics_tabs.addTab(
            self.create_single_analysis_tab(),
            "🎯  تحلیل یک موضوع"
        )

        # تب ۲: مقایسه دو موضوع
        self.analytics_tabs.addTab(
            self.create_compare_analysis_tab(),
            "🔄  مقایسه دو موضوع"
        )

        # تب ۳: نمای کلی
        self.analytics_tabs.addTab(
            self.create_overview_analysis_tab(),
            "📊  نمای کلی همه موضوعات"
        )

        layout.addWidget(self.analytics_tabs)

        return page

    def create_single_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # کارت انتخاب
        select_card = QFrame()
        select_card.setObjectName("card")
        sc_layout = QHBoxLayout(select_card)
        sc_layout.setContentsMargins(15, 12, 15, 12)
        sc_layout.setSpacing(12)

        lbl = QLabel("📂 موضوع را انتخاب کنید:")
        lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #60A5FA;")
        sc_layout.addWidget(lbl)

        self.single_subject_combo = QComboBox()
        self.single_subject_combo.setMinimumHeight(42)
        self.single_subject_combo.setMinimumWidth(250)
        self.single_subject_combo.addItems(
            [s for s in DEFAULT_SUBJECTS if s]
        )
        sc_layout.addWidget(self.single_subject_combo, 1)

        analyze_btn = QPushButton("🔍 شروع تحلیل")
        analyze_btn.setObjectName("primaryButton")
        analyze_btn.setMinimumHeight(42)
        analyze_btn.setStyleSheet("font-size: 14px; min-width: 150px;")
        analyze_btn.clicked.connect(self.do_single_analysis)
        sc_layout.addWidget(analyze_btn)

        layout.addWidget(select_card)

        # ناحیه نتایج
        self.single_result_scroll = QScrollArea()
        self.single_result_scroll.setWidgetResizable(True)
        self.single_result_scroll.setStyleSheet(
            "QScrollArea { border: none; }"
        )

        self.single_result_widget = QWidget()
        self.single_result_layout = QVBoxLayout(self.single_result_widget)
        self.single_result_layout.setContentsMargins(0, 0, 0, 0)
        self.single_result_layout.setSpacing(12)

        placeholder = QLabel(
            "👆 یک موضوع انتخاب کنید و دکمه تحلیل را بزنید"
        )
        placeholder.setStyleSheet(
            "color: #64748B; font-size: 15px; padding: 40px;"
        )
        placeholder.setAlignment(Qt.AlignCenter)
        self.single_result_layout.addWidget(placeholder)

        self.single_result_scroll.setWidget(self.single_result_widget)
        layout.addWidget(self.single_result_scroll, 1)

        return tab

    def do_single_analysis(self):
        subject = self.single_subject_combo.currentText()
        if not subject:
            return

        analysis = self.db.get_subject_analysis(subject)

        # پاک کردن نتایج قبلی
        while self.single_result_layout.count():
            item = self.single_result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not analysis or analysis['total'] == 0:
            no_data = QLabel(
                "❌ هیچ رکوردی برای موضوع «" + subject + "» یافت نشد"
            )
            no_data.setStyleSheet(
                "color: #EF4444; font-size: 15px; padding: 40px; "
                "font-weight: 700;"
            )
            no_data.setAlignment(Qt.AlignCenter)
            self.single_result_layout.addWidget(no_data)
            return

        # عنوان
        color = SUBJECT_COLORS.get(subject, "#60A5FA")
        title = QLabel("📊 تحلیل کامل موضوع: " + subject)
        title.setStyleSheet(
            "font-size: 20px; font-weight: 900; color: white; "
            "background-color: " + color + "; padding: 15px; "
            "border-radius: 10px;"
        )
        title.setAlignment(Qt.AlignCenter)
        self.single_result_layout.addWidget(title)

        # کارت‌های آمار اصلی
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        stats_cards = [
            ("👥", "{:,}".format(analysis['total']),
             "تعداد کل", "#60A5FA"),
            ("📊", format_followers(analysis['total_followers']),
             "مجموع فالوور", "#10B981"),
            ("📈", format_followers(analysis['avg_followers']),
             "میانگین فالوور", "#F59E0B"),
            ("🏆", format_followers(analysis['max_followers']),
             "بیشترین فالوور", "#EF4444"),
            ("📉", format_followers(analysis['median_followers']),
             "میانه", "#A855F7"),
        ]

        for icon, value, label, c in stats_cards:
            card = QFrame()
            card.setObjectName("statCard")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(12, 10, 12, 10)
            cl.setSpacing(4)

            i_lbl = QLabel(icon)
            i_lbl.setStyleSheet("font-size: 28px;")
            i_lbl.setAlignment(Qt.AlignCenter)
            cl.addWidget(i_lbl)

            v_lbl = QLabel(value)
            v_lbl.setStyleSheet(
                "font-size: 20px; font-weight: 900; color: " + c + ";"
            )
            v_lbl.setAlignment(Qt.AlignCenter)
            cl.addWidget(v_lbl)

            l_lbl = QLabel(label)
            l_lbl.setStyleSheet(
                "color: #94A3B8; font-size: 12px; font-weight: 600;"
            )
            l_lbl.setAlignment(Qt.AlignCenter)
            cl.addWidget(l_lbl)

            stats_row.addWidget(card)

        stats_widget = QWidget()
        stats_widget.setLayout(stats_row)
        self.single_result_layout.addWidget(stats_widget)

        # کارت دسته‌بندی فالوور
        cat_card = QFrame()
        cat_card.setObjectName("card")
        cat_layout = QVBoxLayout(cat_card)
        cat_layout.setContentsMargins(15, 15, 15, 15)
        cat_layout.setSpacing(10)

        cat_title = QLabel("🎯 دسته‌بندی بر اساس تعداد فالوور")
        cat_title.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #60A5FA; padding: 5px;"
        )
        cat_layout.addWidget(cat_title)

        cats = analysis['categories']
        total_cat = sum(cats.values()) or 1

        cat_data = [
            ("🔴 مگا (بیش از 1M)", cats['mega'], "#EF4444"),
            ("🟠 ماکرو (100K - 1M)", cats['macro'], "#F97316"),
            ("🟡 میدل (10K - 100K)", cats['middle'], "#EAB308"),
            ("🟢 میکرو (1K - 10K)", cats['micro'], "#10B981"),
            ("⚪ نانو (کمتر از 1K)", cats['nano'], "#94A3B8"),
        ]

        max_cat = max(cats.values()) if cats.values() else 1

        for name, cnt, c in cat_data:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(8, 3, 8, 3)
            row.setSpacing(10)

            n_lbl = QLabel(name)
            n_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 600; color: #F1F5F9;"
            )
            n_lbl.setMinimumWidth(180)
            row.addWidget(n_lbl)

            bar = QProgressBar()
            bar.setMaximum(max_cat)
            bar.setValue(cnt)
            bar.setTextVisible(False)
            bar.setStyleSheet(
                "QProgressBar { background-color: #334155; "
                "border: none; border-radius: 6px; height: 14px; } "
                "QProgressBar::chunk { background-color: " + c +
                "; border-radius: 6px; }"
            )
            bar.setFixedHeight(14)
            row.addWidget(bar, 3)

            pct = int((cnt / total_cat) * 100) if total_cat else 0
            info = QLabel(
                str(cnt) + " نفر  (" + str(pct) + "%)"
            )
            info.setStyleSheet(
                "color: " + c + "; font-weight: 900; "
                "font-size: 13px; padding: 3px 10px;"
            )
            info.setMinimumWidth(120)
            row.addWidget(info)

            cat_layout.addWidget(row_widget)

        self.single_result_layout.addWidget(cat_card)

        # کارت Top 10
        if analysis['top_users']:
            top_card = QFrame()
            top_card.setObjectName("card")
            top_layout = QVBoxLayout(top_card)
            top_layout.setContentsMargins(15, 15, 15, 15)
            top_layout.setSpacing(8)

            top_title = QLabel(
                "🏆 Top 10 کاربران با بیشترین دنبال‌کننده"
            )
            top_title.setStyleSheet(
                "font-size: 15px; font-weight: 700; "
                "color: #60A5FA; padding: 5px;"
            )
            top_layout.addWidget(top_title)

            for i, user in enumerate(analysis['top_users'], 1):
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                row.setContentsMargins(8, 3, 8, 3)
                row.setSpacing(10)

                medals = ["🥇", "🥈", "🥉"]
                medal = medals[i-1] if i <= 3 else "  "

                rank = QLabel(medal + " " + str(i))
                rank.setStyleSheet(
                    "font-size: 14px; font-weight: 700; color: #F59E0B;"
                )
                rank.setMinimumWidth(50)
                row.addWidget(rank)

                name = QLabel(
                    "@" + user.get('instagram_id', '') + "   " +
                    user.get('first_name', '') + " " +
                    user.get('last_name', '')
                )
                name.setStyleSheet(
                    "font-size: 13px; font-weight: 600; color: #F1F5F9;"
                )
                row.addWidget(name, 1)

                fl_val = user.get('followers', 0)
                cat, c, _ = get_follower_category(fl_val)
                fl_lbl = QLabel(
                    format_followers(fl_val) + "  (" + cat + ")"
                )
                fl_lbl.setStyleSheet(
                    "color: " + c + "; font-weight: 900; "
                    "font-size: 13px; padding: 3px 10px;"
                )
                fl_lbl.setMinimumWidth(150)
                fl_lbl.setAlignment(Qt.AlignLeft)
                row.addWidget(fl_lbl)

                top_layout.addWidget(row_widget)

            self.single_result_layout.addWidget(top_card)

        # کارت توزیع سالانه
        if analysis['year_distribution']:
            year_card = QFrame()
            year_card.setObjectName("card")
            year_layout = QVBoxLayout(year_card)
            year_layout.setContentsMargins(15, 15, 15, 15)
            year_layout.setSpacing(8)

            y_title = QLabel("📅 توزیع سالانه ثبت")
            y_title.setStyleSheet(
                "font-size: 15px; font-weight: 700; "
                "color: #60A5FA; padding: 5px;"
            )
            year_layout.addWidget(y_title)

            max_y = max(c for _, c in analysis['year_distribution'])

            for year, cnt in analysis['year_distribution']:
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                row.setContentsMargins(8, 3, 8, 3)
                row.setSpacing(10)

                y_lbl = QLabel("📅 " + str(year))
                y_lbl.setStyleSheet(
                    "font-size: 13px; font-weight: 700; color: #F1F5F9;"
                )
                y_lbl.setMinimumWidth(90)
                row.addWidget(y_lbl)

                bar = QProgressBar()
                bar.setMaximum(max_y)
                bar.setValue(cnt)
                bar.setTextVisible(False)
                bar.setStyleSheet(
                    "QProgressBar { background-color: #334155; "
                    "border: none; border-radius: 6px; height: 12px; } "
                    "QProgressBar::chunk { background-color: #3B82F6; "
                    "border-radius: 6px; }"
                )
                bar.setFixedHeight(12)
                row.addWidget(bar, 3)

                pct = int((cnt / analysis['total']) * 100)
                info = QLabel(
                    "{:,}".format(cnt) + "  (" + str(pct) + "%)"
                )
                info.setStyleSheet(
                    "color: #60A5FA; font-weight: 900; "
                    "font-size: 13px; padding: 3px 10px;"
                )
                info.setMinimumWidth(100)
                row.addWidget(info)

                year_layout.addWidget(row_widget)

            self.single_result_layout.addWidget(year_card)

        # کارت موضوعات مرتبط
        if analysis['related_subjects']:
            rel_card = QFrame()
            rel_card.setObjectName("card")
            rel_layout = QVBoxLayout(rel_card)
            rel_layout.setContentsMargins(15, 15, 15, 15)
            rel_layout.setSpacing(8)

            r_title = QLabel(
                "🔗 موضوعات مرتبط (کاربران چند موضوعه)"
            )
            r_title.setStyleSheet(
                "font-size: 15px; font-weight: 700; "
                "color: #60A5FA; padding: 5px;"
            )
            rel_layout.addWidget(r_title)

            for related_subj, cnt in analysis['related_subjects']:
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                row.setContentsMargins(8, 3, 8, 3)
                row.setSpacing(10)

                c = SUBJECT_COLORS.get(related_subj, "#60A5FA")

                badge = QLabel(
                    subject + "  +  " + related_subj
                )
                badge.setStyleSheet(
                    "font-size: 13px; font-weight: 600; color: #F1F5F9;"
                )
                row.addWidget(badge, 1)

                info = QLabel(str(cnt) + " نفر")
                info.setStyleSheet(
                    "background-color: " + c + "; color: white; "
                    "padding: 4px 12px; border-radius: 12px; "
                    "font-weight: 700; font-size: 12px;"
                )
                info.setMinimumWidth(80)
                info.setAlignment(Qt.AlignCenter)
                row.addWidget(info)

                rel_layout.addWidget(row_widget)

            self.single_result_layout.addWidget(rel_card)

        # کارت کیفیت اطلاعات
        q_card = QFrame()
        q_card.setObjectName("card")
        q_layout = QVBoxLayout(q_card)
        q_layout.setContentsMargins(15, 15, 15, 15)
        q_layout.setSpacing(8)

        q_title = QLabel("📱 کیفیت اطلاعات ثبت شده")
        q_title.setStyleSheet(
            "font-size: 15px; font-weight: 700; "
            "color: #60A5FA; padding: 5px;"
        )
        q_layout.addWidget(q_title)

        quality = analysis['quality']
        total = analysis['total']

        q_data = [
            ("📱 دارای شماره تماس", quality['has_phone'], "#10B981"),
            ("🆔 دارای شماره ملی", quality['has_national_id'], "#3B82F6"),
            ("🏠 دارای نشانی", quality['has_address'], "#F59E0B"),
            ("👥 دارای فالوور", quality['has_followers'], "#EAB308"),
        ]

        for name, cnt, c in q_data:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(8, 3, 8, 3)
            row.setSpacing(10)

            n_lbl = QLabel(name)
            n_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 600; color: #F1F5F9;"
            )
            n_lbl.setMinimumWidth(180)
            row.addWidget(n_lbl)

            bar = QProgressBar()
            bar.setMaximum(total)
            bar.setValue(cnt)
            bar.setTextVisible(False)
            bar.setStyleSheet(
                "QProgressBar { background-color: #334155; "
                "border: none; border-radius: 6px; height: 12px; } "
                "QProgressBar::chunk { background-color: " + c +
                "; border-radius: 6px; }"
            )
            bar.setFixedHeight(12)
            row.addWidget(bar, 3)

            pct = int((cnt / total) * 100) if total else 0
            info = QLabel(
                str(cnt) + " (" + str(pct) + "%)"
            )
            info.setStyleSheet(
                "color: " + c + "; font-weight: 900; "
                "font-size: 13px; padding: 3px 10px;"
            )
            info.setMinimumWidth(100)
            row.addWidget(info)

            q_layout.addWidget(row_widget)

        self.single_result_layout.addWidget(q_card)

        self.single_result_layout.addStretch()
    # ═══════════════════════════════════════════════
    # تب ۲: مقایسه دو موضوع
    # ═══════════════════════════════════════════════
    def create_compare_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # کارت انتخاب
        select_card = QFrame()
        select_card.setObjectName("card")
        sc_layout = QGridLayout(select_card)
        sc_layout.setContentsMargins(15, 12, 15, 12)
        sc_layout.setSpacing(12)

        lbl1 = QLabel("📂 موضوع اول:")
        lbl1.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #60A5FA;"
        )
        sc_layout.addWidget(lbl1, 0, 0)

        self.compare_subject1 = QComboBox()
        self.compare_subject1.setMinimumHeight(40)
        self.compare_subject1.addItems(
            [s for s in DEFAULT_SUBJECTS if s]
        )
        sc_layout.addWidget(self.compare_subject1, 0, 1)

        lbl2 = QLabel("📂 موضوع دوم:")
        lbl2.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #60A5FA;"
        )
        sc_layout.addWidget(lbl2, 0, 2)

        self.compare_subject2 = QComboBox()
        self.compare_subject2.setMinimumHeight(40)
        self.compare_subject2.addItems(
            [s for s in DEFAULT_SUBJECTS if s]
        )
        if self.compare_subject2.count() > 1:
            self.compare_subject2.setCurrentIndex(1)
        sc_layout.addWidget(self.compare_subject2, 0, 3)

        compare_btn = QPushButton("🔄 مقایسه کن")
        compare_btn.setObjectName("primaryButton")
        compare_btn.setMinimumHeight(42)
        compare_btn.setStyleSheet("font-size: 14px;")
        compare_btn.clicked.connect(self.do_compare_analysis)
        sc_layout.addWidget(compare_btn, 1, 0, 1, 4)

        layout.addWidget(select_card)

        # ناحیه نتایج
        self.compare_result_scroll = QScrollArea()
        self.compare_result_scroll.setWidgetResizable(True)
        self.compare_result_scroll.setStyleSheet(
            "QScrollArea { border: none; }"
        )

        self.compare_result_widget = QWidget()
        self.compare_result_layout = QVBoxLayout(
            self.compare_result_widget
        )
        self.compare_result_layout.setContentsMargins(0, 0, 0, 0)
        self.compare_result_layout.setSpacing(12)

        placeholder = QLabel(
            "👆 دو موضوع را انتخاب کنید و مقایسه را شروع کنید"
        )
        placeholder.setStyleSheet(
            "color: #64748B; font-size: 15px; padding: 40px;"
        )
        placeholder.setAlignment(Qt.AlignCenter)
        self.compare_result_layout.addWidget(placeholder)

        self.compare_result_scroll.setWidget(self.compare_result_widget)
        layout.addWidget(self.compare_result_scroll, 1)

        return tab

    def do_compare_analysis(self):
        s1 = self.compare_subject1.currentText()
        s2 = self.compare_subject2.currentText()

        if s1 == s2:
            QMessageBox.warning(
                self, "توجه",
                "دو موضوع متفاوت انتخاب کنید"
            )
            return

        result = self.db.compare_two_subjects(s1, s2)

        # پاک کردن قبلی
        while self.compare_result_layout.count():
            item = self.compare_result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not result:
            no_data = QLabel(
                "❌ داده‌ای برای مقایسه یافت نشد"
            )
            no_data.setStyleSheet(
                "color: #EF4444; font-size: 15px; padding: 40px;"
            )
            no_data.setAlignment(Qt.AlignCenter)
            self.compare_result_layout.addWidget(no_data)
            return

        a1 = result['subject1']
        a2 = result['subject2']

        # عنوان
        c1 = SUBJECT_COLORS.get(s1, "#60A5FA")
        c2 = SUBJECT_COLORS.get(s2, "#F59E0B")

        title = QLabel("🔄 مقایسه: " + s1 + "  در برابر  " + s2)
        title.setStyleSheet(
            "font-size: 18px; font-weight: 900; color: white; "
            "background-color: #2563EB; padding: 15px; "
            "border-radius: 10px;"
        )
        title.setAlignment(Qt.AlignCenter)
        self.compare_result_layout.addWidget(title)

        # جدول مقایسه
        comp_card = QFrame()
        comp_card.setObjectName("card")
        comp_layout = QVBoxLayout(comp_card)
        comp_layout.setContentsMargins(15, 15, 15, 15)
        comp_layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(10)

        h1 = QLabel("📊 معیار")
        h1.setStyleSheet(
            "font-size: 13px; font-weight: 700; "
            "color: #94A3B8; padding: 8px;"
        )
        h1.setMinimumWidth(180)
        header.addWidget(h1)

        h2 = QLabel(s1)
        h2.setStyleSheet(
            "font-size: 13px; font-weight: 900; color: white; "
            "background-color: " + c1 + "; padding: 8px; "
            "border-radius: 6px;"
        )
        h2.setAlignment(Qt.AlignCenter)
        header.addWidget(h2, 1)

        h3 = QLabel(s2)
        h3.setStyleSheet(
            "font-size: 13px; font-weight: 900; color: white; "
            "background-color: " + c2 + "; padding: 8px; "
            "border-radius: 6px;"
        )
        h3.setAlignment(Qt.AlignCenter)
        header.addWidget(h3, 1)

        h4 = QLabel("🏆 برنده")
        h4.setStyleSheet(
            "font-size: 13px; font-weight: 700; "
            "color: #94A3B8; padding: 8px;"
        )
        h4.setMinimumWidth(100)
        h4.setAlignment(Qt.AlignCenter)
        header.addWidget(h4)

        header_widget = QWidget()
        header_widget.setLayout(header)
        comp_layout.addWidget(header_widget)

        # ردیف‌های مقایسه
        rows_data = [
            ("👥 تعداد کاربران",
             "{:,}".format(a1['total']),
             "{:,}".format(a2['total']),
             a1['total'], a2['total']),
            ("📊 مجموع فالوور",
             format_followers(a1['total_followers']),
             format_followers(a2['total_followers']),
             a1['total_followers'], a2['total_followers']),
            ("📈 میانگین فالوور",
             format_followers(a1['avg_followers']),
             format_followers(a2['avg_followers']),
             a1['avg_followers'], a2['avg_followers']),
            ("🏆 بیشترین فالوور",
             format_followers(a1['max_followers']),
             format_followers(a2['max_followers']),
             a1['max_followers'], a2['max_followers']),
            ("📉 میانه فالوور",
             format_followers(a1['median_followers']),
             format_followers(a2['median_followers']),
             a1['median_followers'], a2['median_followers']),
            ("👥 دارای فالوور",
             "{:,}".format(a1['count_with_followers']),
             "{:,}".format(a2['count_with_followers']),
             a1['count_with_followers'], a2['count_with_followers']),
        ]

        for label, v1, v2, n1, n2 in rows_data:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(8, 3, 8, 3)
            row.setSpacing(10)

            l = QLabel(label)
            l.setStyleSheet(
                "font-size: 13px; font-weight: 600; "
                "color: #F1F5F9; padding: 8px;"
            )
            l.setMinimumWidth(180)
            row.addWidget(l)

            v1_lbl = QLabel(v1)
            v1_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: " + c1 + "; "
                "background-color: " + c1 + "22; padding: 8px; "
                "border-radius: 6px;"
            )
            v1_lbl.setAlignment(Qt.AlignCenter)
            row.addWidget(v1_lbl, 1)

            v2_lbl = QLabel(v2)
            v2_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: " + c2 + "; "
                "background-color: " + c2 + "22; padding: 8px; "
                "border-radius: 6px;"
            )
            v2_lbl.setAlignment(Qt.AlignCenter)
            row.addWidget(v2_lbl, 1)

            if n1 > n2:
                winner_text = "◀ " + s1
                winner_color = c1
            elif n2 > n1:
                winner_text = s2 + " ▶"
                winner_color = c2
            else:
                winner_text = "برابر"
                winner_color = "#94A3B8"

            w = QLabel(winner_text)
            w.setStyleSheet(
                "font-size: 12px; font-weight: 700; color: " + winner_color + ";"
            )
            w.setMinimumWidth(100)
            w.setAlignment(Qt.AlignCenter)
            row.addWidget(w)

            comp_layout.addWidget(row_widget)

        self.compare_result_layout.addWidget(comp_card)

        # کاربران مشترک
        both_card = QFrame()
        both_card.setObjectName("card")
        both_layout = QVBoxLayout(both_card)
        both_layout.setContentsMargins(15, 15, 15, 15)
        both_layout.setSpacing(10)

        both_title = QLabel(
            "🔗 کاربران مشترک (هم " + s1 + " هستند و هم " + s2 + ")"
        )
        both_title.setStyleSheet(
            "font-size: 15px; font-weight: 700; "
            "color: #60A5FA; padding: 5px;"
        )
        both_layout.addWidget(both_title)

        count_lbl = QLabel(
            "📊 تعداد کل: " + str(result['both_count']) + " نفر"
        )
        count_lbl.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #10B981; "
            "padding: 10px; background-color: #10B98122; "
            "border-radius: 8px;"
        )
        both_layout.addWidget(count_lbl)

        if result['both_users']:
            for user in result['both_users']:
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                row.setContentsMargins(8, 3, 8, 3)
                row.setSpacing(10)

                name = QLabel(
                    "@" + user.get('instagram_id', '') + "   " +
                    user.get('first_name', '') + " " +
                    user.get('last_name', '')
                )
                name.setStyleSheet(
                    "font-size: 13px; font-weight: 600; color: #F1F5F9;"
                )
                row.addWidget(name, 1)

                fl = user.get('followers', 0)
                if fl > 0:
                    _, c, _ = get_follower_category(fl)
                    fl_lbl = QLabel(format_followers(fl))
                    fl_lbl.setStyleSheet(
                        "color: " + c + "; font-weight: 900; "
                        "font-size: 13px; padding: 3px 10px;"
                    )
                    fl_lbl.setMinimumWidth(100)
                    fl_lbl.setAlignment(Qt.AlignCenter)
                    row.addWidget(fl_lbl)

                both_layout.addWidget(row_widget)

        self.compare_result_layout.addWidget(both_card)
        self.compare_result_layout.addStretch()

    # ═══════════════════════════════════════════════
    # تب ۳: نمای کلی همه موضوعات
    # ═══════════════════════════════════════════════
    def create_overview_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        header_card = QFrame()
        header_card.setObjectName("card")
        hc_layout = QHBoxLayout(header_card)
        hc_layout.setContentsMargins(15, 12, 15, 12)

        info = QLabel(
            "📊 مقایسه آماری همه موضوعات با یکدیگر"
        )
        info.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #60A5FA;"
        )
        hc_layout.addWidget(info, 1)

        refresh_btn = QPushButton("🔄 بارگذاری تحلیل")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.setMinimumHeight(42)
        refresh_btn.setStyleSheet("font-size: 14px; min-width: 180px;")
        refresh_btn.clicked.connect(self.do_overview_analysis)
        hc_layout.addWidget(refresh_btn)

        layout.addWidget(header_card)

        # ناحیه نتایج
        self.overview_scroll = QScrollArea()
        self.overview_scroll.setWidgetResizable(True)
        self.overview_scroll.setStyleSheet(
            "QScrollArea { border: none; }"
        )

        self.overview_widget = QWidget()
        self.overview_layout = QVBoxLayout(self.overview_widget)
        self.overview_layout.setContentsMargins(0, 0, 0, 0)
        self.overview_layout.setSpacing(12)

        placeholder = QLabel(
            "👆 برای مشاهده تحلیل کلی، دکمه بارگذاری را بزنید"
        )
        placeholder.setStyleSheet(
            "color: #64748B; font-size: 15px; padding: 40px;"
        )
        placeholder.setAlignment(Qt.AlignCenter)
        self.overview_layout.addWidget(placeholder)

        self.overview_scroll.setWidget(self.overview_widget)
        layout.addWidget(self.overview_scroll, 1)

        return tab

    def do_overview_analysis(self):
        subjects = [s for s in DEFAULT_SUBJECTS if s]
        results = self.db.get_all_subjects_comparison(subjects)

        while self.overview_layout.count():
            item = self.overview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not results:
            no_data = QLabel("❌ داده‌ای برای تحلیل موجود نیست")
            no_data.setStyleSheet(
                "color: #EF4444; font-size: 15px; padding: 40px;"
            )
            no_data.setAlignment(Qt.AlignCenter)
            self.overview_layout.addWidget(no_data)
            return

        title = QLabel("📊 نمای کلی همه موضوعات (رتبه‌بندی)")
        title.setStyleSheet(
            "font-size: 18px; font-weight: 900; color: white; "
            "background-color: #2563EB; padding: 15px; "
            "border-radius: 10px;"
        )
        title.setAlignment(Qt.AlignCenter)
        self.overview_layout.addWidget(title)

        # جدول رتبه‌بندی
        table_card = QFrame()
        table_card.setObjectName("card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(15, 15, 15, 15)
        table_layout.setSpacing(0)

        # هدر
        header = QHBoxLayout()
        header.setSpacing(8)

        headers = [
            ("#", 50),
            ("موضوع", 200),
            ("تعداد", 100),
            ("مجموع فالوور", 130),
            ("میانگین", 110),
            ("حداکثر", 110),
            ("با فالوور", 100),
        ]

        for h_text, w in headers:
            h_lbl = QLabel(h_text)
            h_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: #60A5FA; "
                "padding: 10px 5px; background-color: #334155; "
                "border-radius: 4px;"
            )
            h_lbl.setAlignment(Qt.AlignCenter)
            h_lbl.setMinimumWidth(w)
            header.addWidget(h_lbl)

        header_w = QWidget()
        header_w.setLayout(header)
        table_layout.addWidget(header_w)

        # ردیف‌ها
        for i, item in enumerate(results, 1):
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(8)

            bg = "#1E293B" if i % 2 == 0 else "#0F172A"
            c = SUBJECT_COLORS.get(item['subject'], "#60A5FA")

            # رتبه
            rank_lbl = QLabel(str(i))
            rank_lbl.setStyleSheet(
                "font-size: 14px; font-weight: 900; color: #F59E0B; "
                "background-color: " + bg + "; padding: 10px 5px;"
            )
            rank_lbl.setAlignment(Qt.AlignCenter)
            rank_lbl.setMinimumWidth(50)
            row.addWidget(rank_lbl)

            # موضوع
            subj_lbl = QLabel("● " + item['subject'])
            subj_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: " + c + "; "
                "background-color: " + bg + "; padding: 10px 5px;"
            )
            subj_lbl.setMinimumWidth(200)
            row.addWidget(subj_lbl)

            # تعداد
            cnt_lbl = QLabel("{:,}".format(item['total']))
            cnt_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: #F1F5F9; "
                "background-color: " + bg + "; padding: 10px 5px;"
            )
            cnt_lbl.setAlignment(Qt.AlignCenter)
            cnt_lbl.setMinimumWidth(100)
            row.addWidget(cnt_lbl)

            # مجموع فالوور
            tf_lbl = QLabel(format_followers(item['total_followers']))
            tf_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: #10B981; "
                "background-color: " + bg + "; padding: 10px 5px;"
            )
            tf_lbl.setAlignment(Qt.AlignCenter)
            tf_lbl.setMinimumWidth(130)
            row.addWidget(tf_lbl)

            # میانگین
            avg_lbl = QLabel(format_followers(item['avg_followers']))
            avg_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: #F59E0B; "
                "background-color: " + bg + "; padding: 10px 5px;"
            )
            avg_lbl.setAlignment(Qt.AlignCenter)
            avg_lbl.setMinimumWidth(110)
            row.addWidget(avg_lbl)

            # حداکثر
            max_lbl = QLabel(format_followers(item['max_followers']))
            max_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: #EF4444; "
                "background-color: " + bg + "; padding: 10px 5px;"
            )
            max_lbl.setAlignment(Qt.AlignCenter)
            max_lbl.setMinimumWidth(110)
            row.addWidget(max_lbl)

            # با فالوور
            wf_lbl = QLabel("{:,}".format(item['count_with_followers']))
            wf_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: #A855F7; "
                "background-color: " + bg + "; padding: 10px 5px;"
            )
            wf_lbl.setAlignment(Qt.AlignCenter)
            wf_lbl.setMinimumWidth(100)
            row.addWidget(wf_lbl)

            table_layout.addWidget(row_widget)

        self.overview_layout.addWidget(table_card)

        # نمودار نسبتی
        chart_card = QFrame()
        chart_card.setObjectName("card")
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(15, 15, 15, 15)
        chart_layout.setSpacing(8)

        ct = QLabel("📊 نمودار توزیع کاربران بین موضوعات")
        ct.setStyleSheet(
            "font-size: 15px; font-weight: 700; "
            "color: #60A5FA; padding: 5px;"
        )
        chart_layout.addWidget(ct)

        max_total = max(r['total'] for r in results) if results else 1

        for item in results:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(8, 3, 8, 3)
            row.setSpacing(10)

            c = SUBJECT_COLORS.get(item['subject'], "#60A5FA")

            n_lbl = QLabel("● " + item['subject'])
            n_lbl.setStyleSheet(
                "font-size: 13px; font-weight: 600; color: " + c + ";"
            )
            n_lbl.setMinimumWidth(200)
            row.addWidget(n_lbl)

            bar = QProgressBar()
            bar.setMaximum(max_total)
            bar.setValue(item['total'])
            bar.setTextVisible(False)
            bar.setStyleSheet(
                "QProgressBar { background-color: #334155; "
                "border: none; border-radius: 6px; height: 14px; } "
                "QProgressBar::chunk { background-color: " + c +
                "; border-radius: 6px; }"
            )
            bar.setFixedHeight(14)
            row.addWidget(bar, 3)

            info = QLabel("{:,}".format(item['total']))
            info.setStyleSheet(
                "color: " + c + "; font-weight: 900; "
                "font-size: 13px; padding: 3px 10px;"
            )
            info.setMinimumWidth(80)
            info.setAlignment(Qt.AlignCenter)
            row.addWidget(info)

            chart_layout.addWidget(row_widget)

        self.overview_layout.addWidget(chart_card)
        self.overview_layout.addStretch()

    # ═══════════════════════════════════════════════
    # صفحه لیست همه رکوردها
    # ═══════════════════════════════════════════════
    def create_list_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        layout.addWidget(self.create_page_header(
            "📋 همه رکوردها",
            "نمایش تمام رکوردهای ثبت شده در دیتابیس"
        ))

        self.list_count = QLabel("")
        self.list_count.setStyleSheet(
            "color: #60A5FA; font-weight: 700; padding: 5px; font-size: 14px;"
        )
        layout.addWidget(self.list_count)

        self.list_table = self.create_results_table()
        layout.addWidget(self.list_table, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        view_btn = QPushButton("👁️ مشاهده")
        view_btn.setObjectName("primaryButton")
        view_btn.setMinimumHeight(40)
        view_btn.clicked.connect(lambda: self.view_record(self.list_table))
        btn_row.addWidget(view_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.setObjectName("warningButton")
        edit_btn.setMinimumHeight(40)
        edit_btn.clicked.connect(lambda: self.edit_record(self.list_table))
        btn_row.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(lambda: self.delete_record(self.list_table))
        btn_row.addWidget(delete_btn)

        export_btn = QPushButton("📥 خروجی اکسل")
        export_btn.setMinimumHeight(40)
        export_btn.clicked.connect(self.export_excel)
        btn_row.addWidget(export_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        return page

    def load_list(self):
        all_data = self.db.get_all(limit=1000)
        self.populate_table(self.list_table, all_data)
        self.list_count.setText("📦 {} رکورد".format(len(all_data)))

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره فایل اکسل",
            "سامانه_نظارت_خروجی.xlsx",
            "Excel Files (*.xlsx)"
        )
        if path:
            n = self.db.export_excel(path)
            QMessageBox.information(
                self, "موفق",
                "✅ {} رکورد ذخیره شد در:\n{}".format(n, path)
            )

    # ═══════════════════════════════════════════════
    # صفحه تنظیمات
    # ═══════════════════════════════════════════════
    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        layout.addWidget(self.create_page_header(
            "⚙️ تنظیمات",
            "مدیریت دیتابیس، بک‌آپ و اطلاعات سامانه"
        ))

        tabs = QTabWidget()

        # تب ۱: بارگذاری مجدد
        reload_tab = QWidget()
        reload_layout = QVBoxLayout(reload_tab)
        reload_layout.setContentsMargins(20, 20, 20, 20)
        reload_layout.setSpacing(15)

        warn = QLabel(
            "⚠️  توجه: بارگذاری مجدد، تمام داده‌های فعلی را جایگزین می‌کند "
            "(بک‌آپ خودکار قبل از عملیات گرفته می‌شود)"
        )
        warn.setStyleSheet(
            "color: #F59E0B; padding: 15px; font-size: 13px; "
            "font-weight: 600; background-color: #78350F; border-radius: 8px;"
        )
        warn.setWordWrap(True)
        reload_layout.addWidget(warn)

        reload_btn = QPushButton("📂  انتخاب و بارگذاری فایل اکسل")
        reload_btn.setObjectName("primaryButton")
        reload_btn.setMinimumHeight(48)
        reload_btn.setStyleSheet("font-size: 14px;")
        reload_btn.clicked.connect(self.reload_excel_from_settings)
        reload_layout.addWidget(reload_btn)

        reload_layout.addStretch()
        tabs.addTab(reload_tab, "📂  بارگذاری مجدد")

        # تب ۲: بک‌آپ
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        backup_layout.setContentsMargins(20, 20, 20, 20)
        backup_layout.setSpacing(12)

        info = QLabel(
            "💾 مدیریت بک‌آپ‌ها\n"
            "بک‌آپ به صورت خودکار قبل از بارگذاری مجدد و "
            "هنگام بستن برنامه گرفته می‌شود."
        )
        info.setStyleSheet(
            "color: #60A5FA; padding: 12px; font-size: 13px; "
            "background-color: #1E293B; border-radius: 8px;"
        )
        info.setWordWrap(True)
        backup_layout.addWidget(info)

        backup_now_btn = QPushButton("💾  گرفتن بک‌آپ همین الان")
        backup_now_btn.setObjectName("successButton")
        backup_now_btn.setMinimumHeight(44)
        backup_now_btn.clicked.connect(self.manual_backup)
        backup_layout.addWidget(backup_now_btn)

        list_lbl = QLabel("📋 بک‌آپ‌های موجود:")
        list_lbl.setStyleSheet(
            "font-size: 14px; font-weight: 700; "
            "color: #60A5FA; padding: 5px;"
        )
        backup_layout.addWidget(list_lbl)

        self.backup_list_widget = QTextEdit()
        self.backup_list_widget.setReadOnly(True)
        self.backup_list_widget.setStyleSheet(
            "font-family: monospace; font-size: 12px;"
        )
        backup_layout.addWidget(self.backup_list_widget, 1)

        refresh_btn = QPushButton("🔄  بروزرسانی لیست")
        refresh_btn.setMinimumHeight(38)
        refresh_btn.clicked.connect(self.refresh_backup_list)
        backup_layout.addWidget(refresh_btn)

        tabs.addTab(backup_tab, "💾  بک‌آپ")

        # تب ۳: درباره
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(20, 20, 20, 20)

        subjects_html = ""
        for s in DEFAULT_SUBJECTS:
            if s:
                color = SUBJECT_COLORS.get(s, "#60A5FA")
                subjects_html += (
                    "<span style='background-color:" + color +
                    "; color:white; padding:4px 10px; border-radius:10px; "
                    "margin:2px; display:inline-block; font-weight:600; "
                    "font-size:11px;'>● " + s + "</span> "
                )

        about_text = QLabel(
            "<div style='line-height: 1.8;'>"
            "<h1 style='color: #60A5FA;'>🛡️ " + APP_NAME + "</h1>"
            "<p style='font-size:15px;'><b>نسخه " + APP_VERSION + "</b></p>"
            "<hr style='border-color:#334155;'>"
            "<h3 style='color:#10B981;'>✨ ویژگی‌ها:</h3>"
            "<ul style='font-size:13px;'>"
            "<li>✅ جستجوی هوشمند در تمام فیلدها</li>"
            "<li>✅ جستجوی پیشرفته با فیلترهای همزمان</li>"
            "<li>✅ ثبت و مدیریت تعداد دنبال‌کننده</li>"
            "<li>✅ تحلیل هوشمند موضوعات</li>"
            "<li>✅ مقایسه دو موضوع به صورت آماری</li>"
            "<li>✅ نمای کلی و رتبه‌بندی همه موضوعات</li>"
            "<li>✅ بک‌آپ خودکار دیتابیس</li>"
            "<li>✅ خروجی اکسل حرفه‌ای</li>"
            "</ul>"
            "<hr style='border-color:#334155;'>"
            "<h3 style='color:#F59E0B;'>📂 موضوعات قابل انتخاب:</h3>"
            "<div style='padding: 8px;'>" + subjects_html + "</div>"
            "<hr style='border-color:#334155;'>"
            "<h3 style='color:#A855F7;'>👥 دسته‌بندی فالوور:</h3>"
            "<ul style='font-size:13px;'>"
            "<li>🔴 <b>مگا</b>: بیش از 1 میلیون</li>"
            "<li>🟠 <b>ماکرو</b>: 100 هزار تا 1 میلیون</li>"
            "<li>🟡 <b>میدل</b>: 10 هزار تا 100 هزار</li>"
            "<li>🟢 <b>میکرو</b>: 1 هزار تا 10 هزار</li>"
            "<li>⚪ <b>نانو</b>: کمتر از 1 هزار</li>"
            "</ul>"
            "<hr style='border-color:#334155;'>"
            "<p style='color:#94A3B8;'><b>مسیر دیتابیس:</b><br>"
            "<code style='color: #60A5FA; background-color:#1E293B; "
            "padding:4px;'>" + self.db.db_path + "</code></p>"
            "<p style='color:#94A3B8;'><b>مسیر بک‌آپ‌ها:</b><br>"
            "<code style='color: #60A5FA; background-color:#1E293B; "
            "padding:4px;'>" + self.db.backup_dir + "</code></p>"
            "</div>"
        )
        about_text.setWordWrap(True)
        about_text.setStyleSheet("font-size: 13px;")

        scroll_about = QScrollArea()
        scroll_about.setWidgetResizable(True)
        scroll_about.setStyleSheet("QScrollArea { border: none; }")
        scroll_about.setWidget(about_text)
        about_layout.addWidget(scroll_about)

        tabs.addTab(about_tab, "ℹ️  درباره")

        layout.addWidget(tabs)

        return page

    def manual_backup(self):
        try:
            path = self.db.create_backup()
            if path:
                QMessageBox.information(
                    self, "موفق",
                    "✅ بک‌آپ با موفقیت گرفته شد!\n\n" + path
                )
                self.refresh_backup_list()
            else:
                QMessageBox.warning(
                    self, "خطا", "نتوانستم بک‌آپ بگیرم"
                )
        except Exception as e:
            QMessageBox.critical(self, "خطا", str(e))

    def refresh_backup_list(self):
        backups = self.db.get_backups_list()
        if not backups:
            self.backup_list_widget.setPlainText("هیچ بک‌آپی موجود نیست")
            return

        text = "📁 " + str(len(backups)) + " بک‌آپ موجود:\n\n"
        for i, b in enumerate(backups, 1):
            text += "  " + str(i) + ". " + b + "\n"
        self.backup_list_widget.setPlainText(text)

    def reload_excel_from_settings(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل اکسل", "",
            "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        loading = QDialog(self)
        loading.setWindowTitle("در حال بارگذاری...")
        loading.setLayoutDirection(Qt.RightToLeft)
        loading.setFixedSize(400, 170)
        loading.setWindowFlags(
            Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        )
        loading.setStyleSheet("""
            QDialog {
                background-color: #1E293B;
                border: 2px solid #2563EB;
                border-radius: 15px;
            }
        """)

        ll = QVBoxLayout(loading)
        ll.setContentsMargins(30, 30, 30, 30)
        ll.setSpacing(15)

        lbl = QLabel("⏳  در حال بارگذاری فایل اکسل...")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #F1F5F9;"
        )
        ll.addWidget(lbl)

        prog = QProgressBar()
        prog.setMinimum(0)
        prog.setMaximum(0)
        prog.setFixedHeight(22)
        prog.setStyleSheet("""
            QProgressBar {
                background-color: #334155;
                border: none;
                border-radius: 10px;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
                border-radius: 10px;
            }
        """)
        ll.addWidget(prog)

        loading.move(
            self.x() + (self.width() - 400) // 2,
            self.y() + (self.height() - 170) // 2
        )

        loading.show()
        QApplication.processEvents()

        try:
            total = self.db.import_excel(file_path)
            loading.close()
            loading.deleteLater()

            QMessageBox.information(
                self, "موفق",
                "✅ {:,} رکورد با موفقیت بارگذاری شد!".format(total)
            )
            self.show_dashboard()

        except Exception as e:
            loading.close()
            loading.deleteLater()

            QMessageBox.critical(
                self, "خطا",
                "❌ خطا در بارگذاری:\n" + str(e)
            )

    # ═══════════════════════════════════════════════
    # ناوبری بین صفحات
    # ═══════════════════════════════════════════════
    def show_dashboard(self):
        self.set_active_nav(0)
        self.stack.setCurrentIndex(0)
        self.update_dashboard()

    def show_search(self):
        self.set_active_nav(1)
        self.stack.setCurrentIndex(1)

    def show_advanced(self):
        self.set_active_nav(2)
        self.stack.setCurrentIndex(2)

    def show_form(self):
        self.set_active_nav(3)
        self.stack.setCurrentIndex(3)

    def show_list(self):
        self.set_active_nav(4)
        self.stack.setCurrentIndex(4)
        self.load_list()

    def show_analytics(self):
        self.set_active_nav(5)
        self.stack.setCurrentIndex(5)

    def show_settings(self):
        self.set_active_nav(6)
        self.stack.setCurrentIndex(6)
        self.refresh_backup_list()


# ═══════════════════════════════════════════════════════
# نقطه شروع برنامه
# ═══════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(STYLE)

    # مرحله ۱: Splash Screen
    splash = SplashScreen()
    splash.show()
    QApplication.processEvents()

    steps = [
        (20, "در حال بارگذاری کتابخانه‌ها..."),
        (50, "در حال راه‌اندازی رابط کاربری..."),
        (80, "در حال اتصال به دیتابیس..."),
        (100, "✅ آماده!"),
    ]
    for value, status in steps:
        splash.update_progress(value, status)
        time.sleep(0.3)

    # مرحله ۲: بستن Splash
    splash.close()
    splash.deleteLater()
    QApplication.processEvents()

    # مرحله ۳: Setup اولیه اگر لازم بود
    db = Database()
    if not db.is_ready():
        setup_done = show_setup_dialog_standalone(app, db)
        if not setup_done:
            sys.exit(0)

    # مرحله ۴: پنجره اصلی
    window = CyberWatchApp(db)
    window.show()
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
