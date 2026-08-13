"""
CyberWatch Desktop v8.0 - نسخه نهایی حرفه‌ای
سامانه هوشمند جستجو و ثبت کاربران فضای مجازی
طراحی: مایکروسافت/گوگل استایل
تمام مشکلات پنجره‌ها اصلاح شده
"""
import sys
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QTabWidget, QMessageBox, QFileDialog,
    QHeaderView, QFrame, QStackedWidget, QScrollArea,
    QGridLayout, QProgressBar, QDialog
)
from PyQt5.QtCore import Qt

from database import Database


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
}


STYLE = """
* {
    font-family: 'Segoe UI', 'Tahoma', 'Vazirmatn', sans-serif;
}

QMainWindow, QWidget {
    background-color: #0F172A;
    color: #F1F5F9;
    font-size: 14px;
}

#sidebar {
    background-color: #1E293B;
    border-right: 2px solid #334155;
}

#sidebarLogo {
    color: #60A5FA;
    font-size: 26px;
    font-weight: 900;
    padding: 25px;
}

#sidebarSubtitle {
    color: #94A3B8;
    font-size: 13px;
    padding-bottom: 25px;
}

QPushButton#navButton {
    background-color: transparent;
    color: #E2E8F0;
    border: none;
    text-align: right;
    padding: 15px 25px;
    font-size: 15px;
    font-weight: 600;
    border-radius: 10px;
    margin: 4px 10px;
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

#pageHeader {
    background-color: #2563EB;
    border-radius: 14px;
    padding: 18px 28px;
    color: white;
    min-height: 75px;
    max-height: 95px;
}

#pageTitle {
    color: white;
    font-size: 24px;
    font-weight: 900;
    padding: 3px 0;
    background-color: transparent;
}

#pageSubtitle {
    color: #DBEAFE;
    font-size: 13px;
    font-weight: 500;
    padding: 3px 0;
    background-color: transparent;
}

#card {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px;
}

#statCard {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px;
}

QPushButton {
    background-color: #334155;
    color: #F1F5F9;
    border: 1px solid #475569;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    min-height: 22px;
}

QPushButton:hover {
    background-color: #475569;
    border-color: #60A5FA;
}

QPushButton#primaryButton {
    background-color: #2563EB;
    color: white;
    border: none;
    font-weight: 700;
    font-size: 14px;
}

QPushButton#primaryButton:hover {
    background-color: #1D4ED8;
}

QPushButton#successButton {
    background-color: #16A34A;
    color: white;
    border: none;
    font-weight: 700;
    font-size: 15px;
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

QLineEdit, QTextEdit {
    background-color: #0F172A;
    color: #F1F5F9;
    border: 2px solid #334155;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 14px;
    min-height: 22px;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #60A5FA;
    background-color: #1E293B;
}

QComboBox {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 2px solid #3B82F6;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 14px;
    font-weight: 600;
    min-height: 26px;
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
    width: 32px;
    border-left: 2px solid #3B82F6;
    background-color: #2563EB;
    border-top-left-radius: 6px;
    border-bottom-left-radius: 6px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 7px solid white;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 2px solid #3B82F6;
    selection-background-color: #2563EB;
    padding: 6px;
    outline: 0;
    font-size: 14px;
}

QComboBox QAbstractItemView::item {
    padding: 10px;
    min-height: 28px;
    border-bottom: 1px solid #334155;
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

QTableWidget {
    background-color: #1E293B;
    color: #F1F5F9;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 10px;
    selection-background-color: #1E40AF;
    font-size: 13px;
}

QTableWidget::item {
    padding: 10px;
    font-size: 13px;
}

QTableWidget::item:selected {
    background-color: #1E40AF;
    color: white;
}

QHeaderView::section {
    background-color: #334155;
    color: #60A5FA;
    padding: 12px;
    border: none;
    font-weight: 700;
    font-size: 13px;
}

QLabel {
    color: #F1F5F9;
    font-size: 14px;
}

QLabel#formLabel {
    color: #94A3B8;
    font-size: 13px;
    font-weight: 700;
    padding: 4px 0;
}

QLabel#requiredLabel {
    color: #F59E0B;
    font-size: 13px;
    font-weight: 700;
    padding: 4px 0;
}

QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 10px;
    background-color: #1E293B;
}

QTabBar::tab {
    background-color: #334155;
    color: #94A3B8;
    padding: 12px 24px;
    margin-right: 3px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 14px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #2563EB;
    color: white;
    font-weight: 700;
}

QScrollBar:vertical {
    background-color: #0F172A;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #475569;
    border-radius: 6px;
    min-height: 25px;
}

QScrollBar::handle:vertical:hover {
    background-color: #60A5FA;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

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

QDialog {
    background-color: #0F172A;
}

QMessageBox {
    background-color: #1E293B;
    color: #F1F5F9;
    font-size: 14px;
}

QMessageBox QPushButton {
    min-width: 100px;
    padding: 8px 16px;
}
"""


# ═══════════════════════════════════════════════════════
# صفحه Splash (بدون تغییر)
# ═══════════════════════════════════════════════════════
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(550, 400)
        self.setLayoutDirection(Qt.RightToLeft)

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 550) // 2
        y = (screen.height() - 400) // 2
        self.move(x, y)

        self.setup_ui()

    def setup_ui(self):
        container = QFrame(self)
        container.setGeometry(0, 0, 550, 400)
        container.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 3px solid #2563EB;
                border-radius: 22px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(18)

        logo = QLabel("🔍")
        logo.setStyleSheet("font-size: 72px; padding: 5px; background-color: transparent;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("CyberWatch")
        title.setStyleSheet("""
            font-size: 38px;
            font-weight: 900;
            color: #60A5FA;
            background-color: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("سامانه هوشمند جستجو و ثبت کاربران فضای مجازی")
        subtitle.setStyleSheet("font-size: 14px; color: #94A3B8; background-color: transparent;")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(25)

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
                font-size: 13px;
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
            "color: #E2E8F0; font-size: 14px; font-weight: 600; background-color: transparent;"
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        version = QLabel("نسخه ۸.۰")
        version.setStyleSheet("color: #64748B; font-size: 12px; background-color: transparent;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

    def update_progress(self, value, status=""):
        self.progress.setValue(value)
        if status:
            self.status_label.setText(status)
        QApplication.processEvents()


# ═══════════════════════════════════════════════════════
# دیالوگ Setup مستقل (اصلاح شده - پشت هیچ پنجره‌ای نمیره)
# ═══════════════════════════════════════════════════════
def show_setup_dialog_standalone(app, db):
    """
    دیالوگ نصب مستقل
    splash قبلاً بسته شده پس پشت چیزی نمیره
    بعد از بارگذاری خودش بسته میشه
    """
    dialog = QDialog()
    dialog.setWindowTitle("راه‌اندازی اولیه - CyberWatch")
    dialog.setLayoutDirection(Qt.RightToLeft)
    dialog.setMinimumWidth(580)
    dialog.setMinimumHeight(350)
    dialog.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
    dialog.setStyleSheet("""
        QDialog {
            background-color: #0F172A;
        }
    """)

    result = {'done': False}

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(35, 35, 35, 35)
    layout.setSpacing(22)

    # هدر
    title = QLabel("🔍 CyberWatch")
    title.setStyleSheet("""
        font-size: 30px;
        font-weight: 900;
        color: #60A5FA;
        padding: 15px;
    """)
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    subtitle = QLabel("برای شروع، فایل اکسل دیتابیس را انتخاب کنید")
    subtitle.setAlignment(Qt.AlignCenter)
    subtitle.setStyleSheet("color: #94A3B8; font-size: 15px; padding: 8px;")
    layout.addWidget(subtitle)

    # پراگرس بار (مخفی)
    progress = QProgressBar()
    progress.setMinimum(0)
    progress.setMaximum(0)
    progress.setFixedHeight(28)
    progress.setStyleSheet("""
        QProgressBar {
            background-color: #334155;
            border: 2px solid #475569;
            border-radius: 12px;
            height: 28px;
        }
        QProgressBar::chunk {
            background-color: #2563EB;
            border-radius: 10px;
        }
    """)
    progress.hide()
    layout.addWidget(progress)

    # لیبل وضعیت (مخفی)
    status_label = QLabel("")
    status_label.setAlignment(Qt.AlignCenter)
    status_label.setStyleSheet("color: #10B981; font-size: 14px; font-weight: 700;")
    status_label.hide()
    layout.addWidget(status_label)

    # دکمه انتخاب فایل
    btn = QPushButton("📂  انتخاب فایل اکسل")
    btn.setObjectName("primaryButton")
    btn.setMinimumHeight(55)
    btn.setStyleSheet("""
        QPushButton {
            background-color: #2563EB;
            color: white;
            border: none;
            font-weight: 700;
            font-size: 16px;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #1D4ED8;
        }
        QPushButton:disabled {
            background-color: #475569;
            color: #94A3B8;
        }
    """)
    layout.addWidget(btn)

    # دکمه رد کردن
    skip_btn = QPushButton("رد کردن (شروع با دیتابیس خالی)")
    skip_btn.setMinimumHeight(42)
    skip_btn.setStyleSheet("""
        QPushButton {
            background-color: #334155;
            color: #F1F5F9;
            border: 1px solid #475569;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #475569;
        }
        QPushButton:disabled {
            background-color: #1E293B;
            color: #64748B;
        }
    """)
    layout.addWidget(skip_btn)

    layout.addStretch()

    # منطق بارگذاری
    def load_excel():
        file_path, _ = QFileDialog.getOpenFileName(
            dialog, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        btn.setEnabled(False)
        skip_btn.setEnabled(False)
        btn.setText("⏳  در حال بارگذاری...")
        progress.show()
        status_label.setText("در حال خواندن فایل...")
        status_label.setStyleSheet("color: #60A5FA; font-size: 14px; font-weight: 700;")
        status_label.show()
        app.processEvents()

        try:
            total = db.import_excel(file_path)
            progress.hide()
            status_label.setText("✅ {:,} رکورد با موفقیت بارگذاری شد!".format(total))
            status_label.setStyleSheet("color: #10B981; font-size: 15px; font-weight: 700;")
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
            status_label.setStyleSheet("color: #EF4444; font-size: 13px; font-weight: 700;")
            status_label.show()
            app.processEvents()

    def skip_setup():
        db.create_tables()
        result['done'] = True
        dialog.accept()

    btn.clicked.connect(load_excel)
    skip_btn.clicked.connect(skip_setup)

    # وسط صفحه
    screen = app.primaryScreen().geometry()
    x = (screen.width() - dialog.width()) // 2
    y = (screen.height() - dialog.height()) // 2
    dialog.move(x, y)

    dialog.raise_()
    dialog.activateWindow()
    dialog.exec_()

    return result['done']


# ═══════════════════════════════════════════════════════
# کلاس اصلی برنامه (اصلاح شده)
# ═══════════════════════════════════════════════════════
class CyberWatchApp(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.edit_id = None

        self.setWindowTitle("CyberWatch v8.0 - سامانه هوشمند")
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(1500, 900)
        self.setMinimumSize(1300, 750)

        self.setup_ui()
        self.show_dashboard()

    def get_subjects_list(self):
        return DEFAULT_SUBJECTS

    def get_clean_subject_stats(self):
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
            "SELECT DISTINCT subject FROM users WHERE instagram_id=? AND subject!=''",
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
        self.settings_page = self.create_settings_page()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.advanced_page)
        self.stack.addWidget(self.form_page)
        self.stack.addWidget(self.list_page)
        self.stack.addWidget(self.settings_page)

    def create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel("🔍 CyberWatch")
        logo.setObjectName("sidebarLogo")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        subtitle = QLabel("سامانه هوشمند\nفضای مجازی")
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
            ("⚙️   تنظیمات", self.show_settings),
        ]

        for text, callback in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(callback)
            btn.setMinimumHeight(52)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        self.records_label = QLabel("کل رکوردها: 0")
        self.records_label.setStyleSheet(
            "color: #60A5FA; padding: 20px; font-weight: 700; font-size: 15px;"
        )
        self.records_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.records_label)

        version = QLabel("v8.0")
        version.setStyleSheet("color: #475569; padding: 8px; font-size: 12px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        return sidebar

    def set_active_nav(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def create_page_header(self, title, subtitle=""):
        header = QFrame()
        header.setObjectName("pageHeader")
        header.setFixedHeight(90)

        layout = QVBoxLayout(header)
        layout.setContentsMargins(25, 12, 25, 12)
        layout.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("pageTitle")
        layout.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("pageSubtitle")
            layout.addWidget(sub_lbl)

        return header

    def create_dashboard_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

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

        self.records_label.setText("کل رکوردها: {:,}".format(stats['total']))

        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        active_years = len(stats['years'])
        ph_pct = int((stats['filled'].get('phone', 0) / max(stats['total'], 1)) * 100)
        ig_pct = int((stats['filled'].get('instagram_id', 0) / max(stats['total'], 1)) * 100)

        cards = [
            ("📦", "{:,}".format(stats['total']), "کل رکوردها", "#60A5FA"),
            ("📅", str(active_years), "سال فعال", "#10B981"),
            ("📂", str(len(clean_subjects)), "موضوعات", "#F59E0B"),
            ("📱", "{}%".format(ph_pct), "شماره تماس", "#A855F7"),
            ("📸", "{}%".format(ig_pct), "ایدی اینستا", "#EF4444"),
        ]

        for i, (icon, value, label, color) in enumerate(cards):
            card = QFrame()
            card.setObjectName("statCard")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(8)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 40px;")
            icon_lbl.setAlignment(Qt.AlignCenter)

            value_lbl = QLabel(value)
            value_lbl.setStyleSheet(
                "font-size: 32px; font-weight: 900; color: " + color + ";"
            )
            value_lbl.setAlignment(Qt.AlignCenter)

            label_lbl = QLabel(label)
            label_lbl.setStyleSheet("color: #94A3B8; font-size: 14px; font-weight: 600;")
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
            old_layout.setSpacing(12)

        title = QLabel("📂 موضوعات ثبت شده (بر اساس دسته‌بندی اصلی)")
        title.setStyleSheet("font-size: 17px; font-weight: 700; color: #60A5FA; padding: 8px;")
        old_layout.addWidget(title)

        if not subjects_data:
            no_data = QLabel("هیچ موضوعی ثبت نشده است")
            no_data.setStyleSheet("color: #64748B; padding: 20px; font-size: 14px;")
            no_data.setAlignment(Qt.AlignCenter)
            old_layout.addWidget(no_data)
            return

        max_cnt = max((c for _, c in subjects_data), default=1)

        for subj, cnt in subjects_data:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(10, 5, 10, 5)

            color = SUBJECT_COLORS.get(subj, "#60A5FA")

            name = QLabel("▸  " + subj)
            name.setStyleSheet("padding: 6px; font-size: 14px; font-weight: 600; color: #F1F5F9;")
            row.addWidget(name, 3)

            bar = QProgressBar()
            bar.setMaximum(max_cnt)
            bar.setValue(cnt)
            bar.setTextVisible(False)
            bar.setStyleSheet(
                "QProgressBar { background-color: #334155; border: none; "
                "border-radius: 6px; height: 14px; } "
                "QProgressBar::chunk { background-color: " + color +
                "; border-radius: 6px; }"
            )
            bar.setFixedHeight(14)
            row.addWidget(bar, 4)

            count = QLabel(str(cnt))
            count.setStyleSheet(
                "color: " + color + "; font-weight: 900; font-size: 16px; padding: 5px 15px;"
            )
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
            old_layout.setSpacing(12)

        title = QLabel("📅 توزیع سال‌های ثبت")
        title.setStyleSheet("font-size: 17px; font-weight: 700; color: #60A5FA; padding: 8px;")
        old_layout.addWidget(title)

        max_cnt = max((c for _, c in stats['years']), default=1)

        year_colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#A855F7", "#EC4899", "#14B8A6"]

        for i, (year, cnt) in enumerate(stats['years']):
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(10, 5, 10, 5)

            color = year_colors[i % len(year_colors)]

            name = QLabel("📅  " + str(year))
            name.setStyleSheet("padding: 6px; font-size: 14px; font-weight: 700; color: #F1F5F9;")
            row.addWidget(name, 1)

            bar = QProgressBar()
            bar.setMaximum(max_cnt)
            bar.setValue(cnt)
            bar.setTextVisible(False)
            bar.setStyleSheet(
                "QProgressBar { background-color: #334155; border: none; "
                "border-radius: 6px; height: 14px; } "
                "QProgressBar::chunk { background-color: " + color +
                "; border-radius: 6px; }"
            )
            bar.setFixedHeight(14)
            row.addWidget(bar, 4)

            count = QLabel("{:,}".format(cnt))
            count.setStyleSheet(
                "color: " + color + "; font-weight: 900; font-size: 16px; padding: 5px 15px;"
            )
            row.addWidget(count, 1)

            old_layout.addWidget(row_widget)

    def create_results_table(self):
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "ID", "ایدی اینستاگرام", "نام", "نام خانوادگی",
            "شماره تماس", "شماره ملی", "موضوع", "سال"
        ])
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.verticalHeader().setDefaultSectionSize(38)

        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        table.setColumnWidth(0, 70)
        table.setColumnWidth(7, 90)

        return table

    def populate_table(self, table, results):
        table.setRowCount(len(results))
        for row_idx, rec in enumerate(results):
            table.setItem(row_idx, 0, QTableWidgetItem(str(rec.get('id', ''))))
            table.setItem(row_idx, 1, QTableWidgetItem(rec.get('instagram_id', '')))
            table.setItem(row_idx, 2, QTableWidgetItem(rec.get('first_name', '')))
            table.setItem(row_idx, 3, QTableWidgetItem(rec.get('last_name', '')))
            table.setItem(row_idx, 4, QTableWidgetItem(rec.get('phone', '')))
            table.setItem(row_idx, 5, QTableWidgetItem(rec.get('national_id', '')))
            table.setItem(row_idx, 6, QTableWidgetItem(rec.get('subject', '')))
            table.setItem(row_idx, 7, QTableWidgetItem(rec.get('reg_year', '')))

    def get_selected_id(self, table):
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "توجه", "یک ردیف را انتخاب کنید")
            return None
        return int(table.item(row, 0).text())

    def create_search_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        layout.addWidget(self.create_page_header(
            "🔍 جستجوی هوشمند",
            "جستجو در تمام فیلدها همزمان"
        ))

        search_card = QFrame()
        search_card.setObjectName("card")
        search_layout = QHBoxLayout(search_card)
        search_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  نام، شماره، ایدی، موضوع، آدرس ...")
        self.search_input.setMinimumHeight(48)
        self.search_input.setStyleSheet("font-size: 15px; padding: 10px 15px;")
        self.search_input.returnPressed.connect(self.do_search)
        search_layout.addWidget(self.search_input, 5)

        search_btn = QPushButton("🔍 جستجو")
        search_btn.setObjectName("primaryButton")
        search_btn.setMinimumHeight(48)
        search_btn.setStyleSheet("font-size: 15px;")
        search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(search_btn, 1)

        clear_btn = QPushButton("🔄 پاک")
        clear_btn.setMinimumHeight(48)
        clear_btn.clicked.connect(lambda: [
            self.search_input.clear(),
            self.search_table.setRowCount(0),
            self.search_count.setText("")
        ])
        search_layout.addWidget(clear_btn, 1)

        layout.addWidget(search_card)

        self.search_count = QLabel("")
        self.search_count.setStyleSheet(
            "color: #10B981; font-weight: 700; padding: 8px; font-size: 15px;"
        )
        layout.addWidget(self.search_count)

        self.search_table = self.create_results_table()
        layout.addWidget(self.search_table, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        view_btn = QPushButton("👁️ مشاهده کامل")
        view_btn.setObjectName("primaryButton")
        view_btn.setMinimumHeight(42)
        view_btn.clicked.connect(lambda: self.view_record(self.search_table))
        btn_row.addWidget(view_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.setObjectName("warningButton")
        edit_btn.setMinimumHeight(42)
        edit_btn.clicked.connect(lambda: self.edit_record(self.search_table))
        btn_row.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMinimumHeight(42)
        delete_btn.clicked.connect(lambda: self.delete_record(self.search_table))
        btn_row.addWidget(delete_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        return page

    def do_search(self):
        query = self.search_input.text().strip()
        results = self.db.search(query)
        self.populate_table(self.search_table, results)
        self.search_count.setText("✅ {} نتیجه یافت شد".format(len(results)))

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
        dialog.setMinimumSize(700, 600)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        name = "{} {}".format(rec.get('first_name', ''), rec.get('last_name', ''))
        title = QLabel("👤 " + name)
        title.setStyleSheet(
            "font-size: 24px; font-weight: 900; color: #60A5FA; padding: 15px; "
            "background-color: #1E293B; border-radius: 10px;"
        )
        layout.addWidget(title)

        instagram_id = rec.get('instagram_id', '')
        if instagram_id:
            all_subjects = self.get_user_all_subjects(instagram_id)
            if all_subjects:
                subjects_frame = QFrame()
                subjects_frame.setStyleSheet(
                    "background-color: #1E3A8A; border-radius: 10px; padding: 15px;"
                )
                sf_layout = QVBoxLayout(subjects_frame)
                sf_layout.setSpacing(8)

                lbl = QLabel("📂 همه موضوعات ثبت شده برای این کاربر:")
                lbl.setStyleSheet("color: #93C5FD; font-weight: 700; font-size: 15px;")
                sf_layout.addWidget(lbl)

                subjects_row = QHBoxLayout()
                subjects_row.setSpacing(8)
                for subj in all_subjects:
                    color = SUBJECT_COLORS.get(subj, "#60A5FA")
                    badge = QLabel("● " + subj)
                    badge.setStyleSheet(
                        "background-color: " + color + "; color: white; "
                        "padding: 6px 12px; border-radius: 15px; "
                        "font-weight: 700; font-size: 12px;"
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
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(8)

        for key, fa in fa_map.items():
            val = rec.get(key, '')
            if val:
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                row.setContentsMargins(5, 5, 5, 5)

                lbl = QLabel(fa + ":")
                lbl.setStyleSheet(
                    "color: #94A3B8; font-weight: 700; min-width: 170px; font-size: 14px;"
                )
                row.addWidget(lbl)

                val_lbl = QLabel(str(val))
                val_lbl.setStyleSheet(
                    "color: #F1F5F9; padding: 10px 14px; background: #334155; "
                    "border-radius: 8px; font-size: 14px; font-weight: 500;"
                )
                val_lbl.setWordWrap(True)
                row.addWidget(val_lbl, 1)

                content_layout.addWidget(row_widget)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        close_btn = QPushButton("بستن")
        close_btn.setMinimumHeight(45)
        close_btn.setStyleSheet("font-size: 15px;")
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
        name = "{} {}".format(rec.get('first_name', ''), rec.get('last_name', ''))
        reply = QMessageBox.question(
            self, "تأیید حذف",
            "آیا از حذف «" + name + "» مطمئن هستید؟",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_user(rec_id)
            QMessageBox.information(self, "موفق", "✅ حذف شد!")
            self.do_search()

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
        form_layout.setSpacing(15)

        self.adv_filters = {}

        text_fields = [
            'نام', 'نام خانوادگی', 'ایدی اینستاگرام',
            'شماره تماس', 'شماره ملی', 'نشانی',
            'نام پدر', 'کد تارنما'
        ]

        for i, field in enumerate(text_fields):
            row = i // 4
            col = i % 4

            container = QVBoxLayout()
            container.setSpacing(6)
            lbl = QLabel(field)
            lbl.setObjectName("formLabel")
            container.addWidget(lbl)

            inp = QLineEdit()
            inp.setPlaceholderText(field + "...")
            inp.setMinimumHeight(40)
            container.addWidget(inp)
            self.adv_filters[field] = inp

            wrapper = QWidget()
            wrapper.setLayout(container)
            form_layout.addWidget(wrapper, row, col)

        subj_container = QVBoxLayout()
        subj_container.setSpacing(6)
        subj_lbl = QLabel("📂 موضوع ثبت")
        subj_lbl.setObjectName("formLabel")
        subj_container.addWidget(subj_lbl)
        self.adv_subject = QComboBox()
        self.adv_subject.setMinimumHeight(42)
        self.adv_subject.addItems(self.get_subjects_list())
        subj_container.addWidget(self.adv_subject)
        subj_wrapper = QWidget()
        subj_wrapper.setLayout(subj_container)
        form_layout.addWidget(subj_wrapper, 2, 0, 1, 2)

        year_container = QVBoxLayout()
        year_container.setSpacing(6)
        year_lbl = QLabel("📅 سال ثبت")
        year_lbl.setObjectName("formLabel")
        year_container.addWidget(year_lbl)
        self.adv_year = QComboBox()
        self.adv_year.setMinimumHeight(42)
        self.adv_year.addItems(YEARS_LIST)
        year_container.addWidget(self.adv_year)
        year_wrapper = QWidget()
        year_wrapper.setLayout(year_container)
        form_layout.addWidget(year_wrapper, 2, 2, 1, 2)

        layout.addWidget(form_card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        search_btn = QPushButton("🔬 اعمال فیلترها")
        search_btn.setObjectName("primaryButton")
        search_btn.setMinimumHeight(45)
        search_btn.setStyleSheet("font-size: 15px; min-width: 180px;")
        search_btn.clicked.connect(self.do_advanced_search)
        btn_row.addWidget(search_btn)

        clear_btn = QPushButton("🔄 پاک کردن")
        clear_btn.setMinimumHeight(45)
        clear_btn.clicked.connect(self.clear_advanced)
        btn_row.addWidget(clear_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.adv_count = QLabel("")
        self.adv_count.setStyleSheet(
            "color: #10B981; font-weight: 700; padding: 8px; font-size: 15px;"
        )
        layout.addWidget(self.adv_count)

        self.adv_table = self.create_results_table()
        layout.addWidget(self.adv_table, 1)

        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(10)
        view_btn = QPushButton("👁️ مشاهده")
        view_btn.setObjectName("primaryButton")
        view_btn.setMinimumHeight(42)
        view_btn.clicked.connect(lambda: self.view_record(self.adv_table))
        btn_row2.addWidget(view_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.setObjectName("warningButton")
        edit_btn.setMinimumHeight(42)
        edit_btn.clicked.connect(lambda: self.edit_record(self.adv_table))
        btn_row2.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMinimumHeight(42)
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

    def create_form_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        self.form_header = self.create_page_header(
            "➕ ثبت کاربر جدید",
            "اطلاعات کاربر جدید را با دقت وارد کنید"
        )
        layout.addWidget(self.form_header)

        form_card = QFrame()
        form_card.setObjectName("card")
        form_layout = QGridLayout(form_card)
        form_layout.setSpacing(18)

        lbl = QLabel("⭐ ایدی اینستاگرام *")
        lbl.setObjectName("requiredLabel")
        form_layout.addWidget(lbl, 0, 0)
        self.form_instagram = QLineEdit()
        self.form_instagram.setMinimumHeight(44)
        form_layout.addWidget(self.form_instagram, 0, 1)

        lbl2 = QLabel("نام")
        lbl2.setObjectName("formLabel")
        form_layout.addWidget(lbl2, 0, 2)
        self.form_first_name = QLineEdit()
        self.form_first_name.setMinimumHeight(44)
        form_layout.addWidget(self.form_first_name, 0, 3)

        lbl3 = QLabel("نام خانوادگی")
        lbl3.setObjectName("formLabel")
        form_layout.addWidget(lbl3, 1, 0)
        self.form_last_name = QLineEdit()
        self.form_last_name.setMinimumHeight(44)
        form_layout.addWidget(self.form_last_name, 1, 1)

        lbl4 = QLabel("نام پدر")
        lbl4.setObjectName("formLabel")
        form_layout.addWidget(lbl4, 1, 2)
        self.form_father_name = QLineEdit()
        self.form_father_name.setMinimumHeight(44)
        form_layout.addWidget(self.form_father_name, 1, 3)

        lbl5 = QLabel("شماره تماس")
        lbl5.setObjectName("formLabel")
        form_layout.addWidget(lbl5, 2, 0)
        self.form_phone = QLineEdit()
        self.form_phone.setMinimumHeight(44)
        form_layout.addWidget(self.form_phone, 2, 1)

        lbl6 = QLabel("شماره ملی")
        lbl6.setObjectName("formLabel")
        form_layout.addWidget(lbl6, 2, 2)
        self.form_national_id = QLineEdit()
        self.form_national_id.setMinimumHeight(44)
        form_layout.addWidget(self.form_national_id, 2, 3)

        lbl7 = QLabel("📂 موضوع ثبت *")
        lbl7.setObjectName("requiredLabel")
        form_layout.addWidget(lbl7, 3, 0)
        self.form_subject = QComboBox()
        self.form_subject.setMinimumHeight(44)
        self.form_subject.addItems(self.get_subjects_list())
        form_layout.addWidget(self.form_subject, 3, 1)

        lbl8 = QLabel("📅 سال ثبت")
        lbl8.setObjectName("formLabel")
        form_layout.addWidget(lbl8, 3, 2)
        self.form_year = QComboBox()
        self.form_year.setMinimumHeight(44)
        self.form_year.addItems(YEARS_LIST)
        form_layout.addWidget(self.form_year, 3, 3)

        lbl9 = QLabel("کد تارنما")
        lbl9.setObjectName("formLabel")
        form_layout.addWidget(lbl9, 4, 0)
        self.form_tarnama = QLineEdit()
        self.form_tarnama.setMinimumHeight(44)
        form_layout.addWidget(self.form_tarnama, 4, 1)

        lbl10 = QLabel("تاریخ ثبت")
        lbl10.setObjectName("formLabel")
        form_layout.addWidget(lbl10, 4, 2)
        self.form_reg_date = QLineEdit()
        self.form_reg_date.setMinimumHeight(44)
        form_layout.addWidget(self.form_reg_date, 4, 3)

        lbl11 = QLabel("نشانی")
        lbl11.setObjectName("formLabel")
        form_layout.addWidget(lbl11, 5, 0)
        self.form_address = QTextEdit()
        self.form_address.setMaximumHeight(100)
        form_layout.addWidget(self.form_address, 5, 1, 1, 3)

        layout.addWidget(form_card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)

        self.save_btn = QPushButton("✅  ثبت کاربر")
        self.save_btn.setObjectName("successButton")
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setStyleSheet("font-size: 16px; min-width: 200px;")
        self.save_btn.clicked.connect(self.save_form)
        btn_row.addWidget(self.save_btn)

        cancel_btn = QPushButton("❌  انصراف")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setStyleSheet("font-size: 15px; min-width: 150px;")
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

        subj = rec.get('subject', '')
        if '|' in subj:
            subj = subj.split('|')[0].strip()
        idx = self.form_subject.findText(subj)
        if idx >= 0:
            self.form_subject.setCurrentIndex(idx)
        else:
            self.form_subject.setCurrentIndex(0)

        year = rec.get('reg_year', '')
        if '|' in year:
            year = year.split('|')[0].strip()
        idx = self.form_year.findText(year)
        if idx >= 0:
            self.form_year.setCurrentIndex(idx)
        else:
            self.form_year.setCurrentIndex(0)

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
        self.form_subject.setCurrentIndex(0)
        self.form_year.setCurrentIndex(0)

    def save_form(self):
        instagram_id = self.form_instagram.text().strip()
        if not instagram_id:
            QMessageBox.warning(self, "خطا", "⭐ ایدی اینستاگرام الزامی است!")
            return

        subject = self.form_subject.currentText().strip()
        if not subject:
            QMessageBox.warning(self, "خطا", "📂 موضوع ثبت الزامی است!")
            return

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
        }

        if self.edit_id:
            self.db.update_user(self.edit_id, data)
            QMessageBox.information(self, "موفق", "✅ اطلاعات با موفقیت ویرایش شد!")
            self.edit_id = None
        else:
            self.db.add_user(data)
            QMessageBox.information(self, "موفق", "✅ کاربر جدید با موفقیت ثبت شد!")

        self.clear_form()
        self.show_dashboard()

    def cancel_form(self):
        self.clear_form()
        self.edit_id = None
        self.show_dashboard()

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
            "color: #60A5FA; font-weight: 700; padding: 8px; font-size: 15px;"
        )
        layout.addWidget(self.list_count)

        self.list_table = self.create_results_table()
        layout.addWidget(self.list_table, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        view_btn = QPushButton("👁️ مشاهده")
        view_btn.setObjectName("primaryButton")
        view_btn.setMinimumHeight(42)
        view_btn.clicked.connect(lambda: self.view_record(self.list_table))
        btn_row.addWidget(view_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.setObjectName("warningButton")
        edit_btn.setMinimumHeight(42)
        edit_btn.clicked.connect(lambda: self.edit_record(self.list_table))
        btn_row.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("dangerButton")
        delete_btn.setMinimumHeight(42)
        delete_btn.clicked.connect(lambda: self.delete_record(self.list_table))
        btn_row.addWidget(delete_btn)

        export_btn = QPushButton("📥 خروجی اکسل")
        export_btn.setMinimumHeight(42)
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
            "CyberWatch_Export.xlsx",
            "Excel Files (*.xlsx)"
        )
        if path:
            n = self.db.export_excel(path)
            QMessageBox.information(
                self, "موفق",
                "✅ {} رکورد ذخیره شد در:\n{}".format(n, path)
            )

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        layout.addWidget(self.create_page_header(
            "⚙️ تنظیمات",
            "مدیریت دیتابیس و اطلاعات سامانه"
        ))

        tabs = QTabWidget()

        # تب بارگذاری مجدد
        reload_tab = QWidget()
        reload_layout = QVBoxLayout(reload_tab)
        reload_layout.setContentsMargins(20, 20, 20, 20)
        reload_layout.setSpacing(15)

        warn = QLabel("⚠️  توجه: بارگذاری مجدد، تمام داده‌های فعلی را جایگزین می‌کند")
        warn.setStyleSheet(
            "color: #F59E0B; padding: 15px; font-size: 14px; font-weight: 600; "
            "background-color: #78350F; border-radius: 8px;"
        )
        reload_layout.addWidget(warn)

        reload_btn = QPushButton("📂  انتخاب و بارگذاری فایل اکسل")
        reload_btn.setObjectName("primaryButton")
        reload_btn.setMinimumHeight(50)
        reload_btn.setStyleSheet("font-size: 15px;")
        reload_btn.clicked.connect(self.reload_excel_from_settings)
        reload_layout.addWidget(reload_btn)
        reload_layout.addStretch()

        tabs.addTab(reload_tab, "📂  بارگذاری مجدد")

        # تب درباره
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(20, 20, 20, 20)

        subjects_html = ""
        for s in DEFAULT_SUBJECTS:
            if s:
                color = SUBJECT_COLORS.get(s, "#60A5FA")
                subjects_html += (
                    "<span style='background-color:" + color +
                    "; color:white; padding:5px 12px; border-radius:12px; "
                    "margin:3px; display:inline-block; font-weight:600; "
                    "font-size:12px;'>● " + s + "</span> "
                )

        about_text = QLabel(
            "<div style='line-height: 2;'>"
            "<h1 style='color: #60A5FA;'>🔍 CyberWatch v8.0</h1>"
            "<p style='font-size:16px;'><b>سامانه هوشمند جستجو و ثبت کاربران فضای مجازی</b></p>"
            "<hr style='border-color:#334155;'>"
            "<h3 style='color:#10B981;'>✨ ویژگی‌ها:</h3>"
            "<ul style='font-size:14px;'>"
            "<li>✅ جستجوی هوشمند در تمام فیلدها</li>"
            "<li>✅ جستجوی پیشرفته با فیلترهای همزمان</li>"
            "<li>✅ کمبوباکس رنگی برای موضوع و سال</li>"
            "<li>✅ نمایش همه موضوعات یک کاربر با بج رنگی</li>"
            "<li>✅ ثبت، ویرایش، حذف</li>"
            "<li>✅ خروجی اکسل</li>"
            "<li>✅ 100% Desktop - بدون مرورگر</li>"
            "</ul>"
            "<hr style='border-color:#334155;'>"
            "<h3 style='color:#F59E0B;'>📂 موضوعات قابل انتخاب:</h3>"
            "<div style='padding: 10px;'>" + subjects_html + "</div>"
            "<hr style='border-color:#334155;'>"
            "<p style='color:#94A3B8;'><b>مسیر دیتابیس:</b><br>"
            "<code style='color: #60A5FA; background-color:#1E293B; padding:5px;'>"
            + self.db.db_path + "</code></p>"
            "</div>"
        )
        about_text.setWordWrap(True)
        about_text.setStyleSheet("font-size: 14px;")

        scroll_about = QScrollArea()
        scroll_about.setWidgetResizable(True)
        scroll_about.setWidget(about_text)
        about_layout.addWidget(scroll_about)

        tabs.addTab(about_tab, "ℹ️  درباره")

        layout.addWidget(tabs)

        return page

    def reload_excel_from_settings(self):
        """بارگذاری مجدد اکسل از تنظیمات - بدون هنگ"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        # دیالوگ لودینگ
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
        ll.setSpacing(18)

        lbl = QLabel("⏳  در حال بارگذاری فایل اکسل...")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #F1F5F9;")
        ll.addWidget(lbl)

        prog = QProgressBar()
        prog.setMinimum(0)
        prog.setMaximum(0)
        prog.setFixedHeight(24)
        prog.setStyleSheet("""
            QProgressBar {
                background-color: #334155;
                border: none;
                border-radius: 10px;
                height: 24px;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
                border-radius: 10px;
            }
        """)
        ll.addWidget(prog)

        # وسط صفحه
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

    def show_settings(self):
        self.set_active_nav(5)
        self.stack.setCurrentIndex(5)


# ═══════════════════════════════════════════════════════
# نقطه شروع برنامه (اصلاح شده)
# ═══════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    # ── مرحله ۱: Splash Screen ───────────────────────
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

    # ── مرحله ۲: بستن Splash ─────────────────────────
    splash.close()
    splash.deleteLater()
    QApplication.processEvents()

    # ── مرحله ۳: Setup (اگر نیاز بود) ────────────────
    db = Database()
    if not db.is_ready():
        setup_done = show_setup_dialog_standalone(app, db)
        if not setup_done:
            sys.exit(0)

    # ── مرحله ۴: پنجره اصلی ──────────────────────────
    window = CyberWatchApp(db)
    window.show()
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
