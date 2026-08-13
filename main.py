"""
CyberWatch Desktop v7.0 - PyQt5 نسخه نهایی
سامانه هوشمند جستجو و ثبت کاربران فضای مجازی
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

# لیست نهایی موضوعات (تنها - بدون +)
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


STYLE = """
QMainWindow, QWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    font-family: 'Segoe UI', 'Tahoma', sans-serif;
}

#sidebar {
    background-color: #161B22;
    border-right: 1px solid #21262D;
}

#sidebarLogo {
    color: #58A6FF;
    font-size: 24px;
    font-weight: bold;
    padding: 20px;
}

#sidebarSubtitle {
    color: #8B949E;
    font-size: 11px;
    padding-bottom: 20px;
}

QPushButton#navButton {
    background-color: transparent;
    color: #E6EDF3;
    border: none;
    text-align: right;
    padding: 12px 20px;
    font-size: 13px;
    border-radius: 8px;
    margin: 2px 8px;
}

QPushButton#navButton:hover {
    background-color: #1C2128;
}

QPushButton#navButton:checked {
    background-color: #1F6FEB;
    color: white;
    font-weight: bold;
}

#pageHeader {
    background-color: #1F6FEB;
    border-radius: 12px;
    padding: 15px 25px;
    color: white;
    min-height: 70px;
    max-height: 90px;
}

#pageTitle {
    color: white;
    font-size: 20px;
    font-weight: bold;
    padding: 2px 0;
    background-color: transparent;
}

#pageSubtitle {
    color: #B0D4FF;
    font-size: 11px;
    padding: 2px 0;
    background-color: transparent;
}

#card {
    background-color: #161B22;
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 15px;
}

#statCard {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 15px;
}

QPushButton {
    background-color: #21262D;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #30363D;
    border-color: #58A6FF;
}

QPushButton#primaryButton {
    background-color: #1F6FEB;
    color: white;
    border: none;
    font-weight: bold;
}

QPushButton#primaryButton:hover {
    background-color: #388BFD;
}

QPushButton#successButton {
    background-color: #238636;
    color: white;
    border: none;
    font-weight: bold;
}

QPushButton#successButton:hover {
    background-color: #2EA043;
}

QPushButton#dangerButton {
    background-color: #DA3633;
    color: white;
    border: none;
    font-weight: bold;
}

QPushButton#dangerButton:hover {
    background-color: #F85149;
}

QPushButton#warningButton {
    background-color: #D29922;
    color: white;
    border: none;
    font-weight: bold;
}

QLineEdit, QTextEdit {
    background-color: #0D1117;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    min-height: 20px;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #58A6FF;
}

QComboBox {
    background-color: #21262D;
    color: #E6EDF3;
    border: 2px solid #388BFD;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    min-height: 24px;
    selection-background-color: #1F6FEB;
}

QComboBox:hover {
    border-color: #58A6FF;
    background-color: #30363D;
}

QComboBox:focus {
    border-color: #58A6FF;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top left;
    width: 30px;
    border-left: 1px solid #388BFD;
    background-color: #1F6FEB;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
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
    background-color: #161B22;
    color: #E6EDF3;
    border: 1px solid #388BFD;
    selection-background-color: #1F6FEB;
    padding: 5px;
    outline: 0;
}

QComboBox QAbstractItemView::item {
    padding: 8px;
    min-height: 24px;
    border-bottom: 1px solid #21262D;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #1F3D5F;
    color: white;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #1F6FEB;
    color: white;
}

QTableWidget {
    background-color: #161B22;
    color: #E6EDF3;
    gridline-color: #21262D;
    border: 1px solid #21262D;
    border-radius: 8px;
    selection-background-color: #1F3D5F;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #1F3D5F;
    color: white;
}

QHeaderView::section {
    background-color: #21262D;
    color: #8B949E;
    padding: 10px;
    border: none;
    font-weight: bold;
}

QLabel {
    color: #E6EDF3;
}

QLabel#formLabel {
    color: #8B949E;
    font-size: 12px;
    font-weight: bold;
}

QLabel#requiredLabel {
    color: #D29922;
    font-size: 12px;
    font-weight: bold;
}

QTabWidget::pane {
    border: 1px solid #21262D;
    border-radius: 8px;
    background-color: #161B22;
}

QTabBar::tab {
    background-color: #21262D;
    color: #8B949E;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #1F6FEB;
    color: white;
    font-weight: bold;
}

QScrollBar:vertical {
    background-color: #0D1117;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #30363D;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #484F58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QProgressBar {
    background-color: #21262D;
    border: none;
    border-radius: 5px;
    height: 10px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #1F6FEB;
    border-radius: 5px;
}
"""


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 350)
        self.setLayoutDirection(Qt.RightToLeft)

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 500) // 2
        y = (screen.height() - 350) // 2
        self.move(x, y)

        self.setup_ui()

    def setup_ui(self):
        container = QFrame(self)
        container.setGeometry(0, 0, 500, 350)
        container.setStyleSheet("""
            QFrame {
                background-color: #161B22;
                border: 2px solid #1F6FEB;
                border-radius: 20px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        logo = QLabel("🔍")
        logo.setStyleSheet("font-size: 64px; padding: 5px;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("CyberWatch")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #58A6FF;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("سامانه هوشمند جستجو و ثبت کاربران فضای مجازی")
        subtitle.setStyleSheet("font-size: 12px; color: #8B949E;")
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
                background-color: #21262D;
                border: 1px solid #30363D;
                border-radius: 10px;
                height: 24px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #1F6FEB;
                border-radius: 10px;
            }
        """)
        self.progress.setFixedHeight(28)
        layout.addWidget(self.progress)

        self.status_label = QLabel("در حال آماده‌سازی...")
        self.status_label.setStyleSheet("color: #E6EDF3; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        version = QLabel("نسخه ۷.۰")
        version.setStyleSheet("color: #484F58; font-size: 10px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

    def update_progress(self, value, status=""):
        self.progress.setValue(value)
        if status:
            self.status_label.setText(status)
        QApplication.processEvents()


class CyberWatchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.edit_id = None

        self.setWindowTitle("CyberWatch v7.0 - سامانه هوشمند")
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(1400, 850)
        self.setMinimumSize(1200, 700)

        if not self.db.is_ready():
            self.show_setup_dialog()

        self.setup_ui()
        self.show_dashboard()

    def show_setup_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("راه‌اندازی اولیه")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        title = QLabel("🔍 CyberWatch")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #58A6FF; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = QLabel("برای شروع، فایل اکسل دیتابیس را انتخاب کنید")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #8B949E; padding: 10px;")
        layout.addWidget(info)

        btn = QPushButton("📂 انتخاب فایل اکسل")
        btn.setObjectName("primaryButton")
        btn.setMinimumHeight(45)
        btn.clicked.connect(lambda: self.load_excel_dialog(dialog))
        layout.addWidget(btn)

        skip_btn = QPushButton("رد کردن (شروع با دیتابیس خالی)")
        skip_btn.clicked.connect(lambda: [self.db.create_tables(), dialog.accept()])
        layout.addWidget(skip_btn)

        dialog.exec_()

    def load_excel_dialog(self, parent_dialog=None):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل اکسل",
            "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            try:
                total = self.db.import_excel(file_path)
                QMessageBox.information(
                    self, "موفق",
                    "✅ {:,} رکورد بارگذاری شد!".format(total)
                )
                if parent_dialog:
                    parent_dialog.accept()
                if hasattr(self, 'stack'):
                    self.show_dashboard()
            except Exception as e:
                QMessageBox.critical(self, "خطا", "خطا در بارگذاری:\n" + str(e))

    def get_subjects_list(self):
        """گرفتن لیست موضوعات - فقط پیش‌فرض‌ها بدون + یا ترکیب"""
        return DEFAULT_SUBJECTS

    def get_user_all_subjects(self, instagram_id):
        """گرفتن همه موضوعات یک کاربر بر اساس ایدی اینستاگرام"""
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
            # اگر ترکیبی بود جدا کن
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
        sidebar.setFixedWidth(220)

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
            ("🏠  داشبورد", self.show_dashboard),
            ("🔍  جستجوی هوشمند", self.show_search),
            ("🔬  جستجوی پیشرفته", self.show_advanced),
            ("➕  ثبت کاربر جدید", self.show_form),
            ("📋  همه رکوردها", self.show_list),
            ("⚙️  تنظیمات", self.show_settings),
        ]

        for text, callback in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(callback)
            btn.setMinimumHeight(45)
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        self.records_label = QLabel("کل رکوردها: 0")
        self.records_label.setStyleSheet("color: #58A6FF; padding: 15px; font-weight: bold;")
        self.records_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.records_label)

        version = QLabel("v7.0")
        version.setStyleSheet("color: #484F58; padding: 5px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        return sidebar

    def set_active_nav(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def create_page_header(self, title, subtitle=""):
        header = QFrame()
        header.setObjectName("pageHeader")
        header.setFixedHeight(85)

        layout = QVBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(5)

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
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self.create_page_header(
            "🏠 داشبورد",
            "نمای کلی از وضعیت دیتابیس"
        ))

        self.stats_grid = QGridLayout()
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
        self.records_label.setText("کل رکوردها: {:,}".format(stats['total']))

        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        active_years = len(stats['years'])
        ph_pct = int((stats['filled'].get('phone', 0) / max(stats['total'], 1)) * 100)
        ig_pct = int((stats['filled'].get('instagram_id', 0) / max(stats['total'], 1)) * 100)

        cards = [
            ("📦", "{:,}".format(stats['total']), "کل رکوردها", "#58A6FF"),
            ("📅", str(active_years), "سال فعال", "#3FB950"),
            ("📂", str(len(stats['subjects'])), "موضوعات", "#D29922"),
            ("📱", "{}%".format(ph_pct), "شماره تماس", "#BC8CFF"),
            ("📸", "{}%".format(ig_pct), "ایدی اینستا", "#F85149"),
        ]

        for i, (icon, value, label, color) in enumerate(cards):
            card = QFrame()
            card.setObjectName("statCard")
            card_layout = QVBoxLayout(card)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 32px;")
            icon_lbl.setAlignment(Qt.AlignCenter)

            value_lbl = QLabel(value)
            value_lbl.setStyleSheet(
                "font-size: 28px; font-weight: bold; color: " + color + ";"
            )
            value_lbl.setAlignment(Qt.AlignCenter)

            label_lbl = QLabel(label)
            label_lbl.setStyleSheet("color: #8B949E; font-size: 12px;")
            label_lbl.setAlignment(Qt.AlignCenter)

            card_layout.addWidget(icon_lbl)
            card_layout.addWidget(value_lbl)
            card_layout.addWidget(label_lbl)

            self.stats_grid.addWidget(card, 0, i)

        self.update_subjects_card(stats)
        self.update_years_card(stats)

    def update_subjects_card(self, stats):
        old_layout = self.subjects_card.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            old_layout = QVBoxLayout(self.subjects_card)

        title = QLabel("📂 موضوعات ثبت شده")
        title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 5px;")
        old_layout.addWidget(title)

        colors = ['#58A6FF', '#3FB950', '#D29922', '#F85149',
                  '#BC8CFF', '#79C0FF', '#56D364', '#E3B341']

        max_cnt = max((c for _, c in stats['subjects']), default=1)

        for i, (subj, cnt) in enumerate(stats['subjects'][:8]):
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)

            name = QLabel("▸ " + subj[:30])
            name.setStyleSheet("padding: 5px;")
            row.addWidget(name, 2)

            bar = QProgressBar()
            bar.setMaximum(max_cnt)
            bar.setValue(cnt)
            bar.setTextVisible(False)
            color = colors[i % len(colors)]
            bar.setStyleSheet(
                "QProgressBar { background-color: #21262D; border: none; "
                "border-radius: 4px; height: 8px; } "
                "QProgressBar::chunk { background-color: " + color +
                "; border-radius: 4px; }"
            )
            row.addWidget(bar, 3)

            count = QLabel(str(cnt))
            count.setStyleSheet("color: " + color + "; font-weight: bold;")
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

        title = QLabel("📅 توزیع سال‌های ثبت")
        title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 5px;")
        old_layout.addWidget(title)

        max_cnt = max((c for _, c in stats['years']), default=1)

        for year, cnt in stats['years']:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)

            name = QLabel("📅 " + str(year))
            name.setStyleSheet("padding: 5px;")
            row.addWidget(name, 1)

            bar = QProgressBar()
            bar.setMaximum(max_cnt)
            bar.setValue(cnt)
            bar.setTextVisible(False)
            row.addWidget(bar, 4)

            count = QLabel("{:,}".format(cnt))
            count.setStyleSheet("color: #58A6FF; font-weight: bold;")
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

        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        table.setColumnWidth(0, 60)
        table.setColumnWidth(7, 80)

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
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self.create_page_header(
            "🔍 جستجوی هوشمند",
            "جستجو در تمام فیلدها"
        ))

        search_card = QFrame()
        search_card.setObjectName("card")
        search_layout = QHBoxLayout(search_card)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 نام، شماره، ایدی، موضوع، آدرس ...")
        self.search_input.setMinimumHeight(40)
        self.search_input.returnPressed.connect(self.do_search)
        search_layout.addWidget(self.search_input, 5)

        search_btn = QPushButton("🔍 جستجو")
        search_btn.setObjectName("primaryButton")
        search_btn.setMinimumHeight(40)
        search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(search_btn, 1)

        clear_btn = QPushButton("🔄 پاک")
        clear_btn.setMinimumHeight(40)
        clear_btn.clicked.connect(lambda: [
            self.search_input.clear(),
            self.search_table.setRowCount(0),
            self.search_count.setText("")
        ])
        search_layout.addWidget(clear_btn, 1)

        layout.addWidget(search_card)

        self.search_count = QLabel("")
        self.search_count.setStyleSheet("color: #3FB950; font-weight: bold; padding: 5px;")
        layout.addWidget(self.search_count)

        self.search_table = self.create_results_table()
        layout.addWidget(self.search_table, 1)

        btn_row = QHBoxLayout()

        view_btn = QPushButton("👁️ مشاهده کامل")
        view_btn.setObjectName("primaryButton")
        view_btn.clicked.connect(lambda: self.view_record(self.search_table))
        btn_row.addWidget(view_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.setObjectName("warningButton")
        edit_btn.clicked.connect(lambda: self.edit_record(self.search_table))
        btn_row.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("dangerButton")
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
        dialog.setWindowTitle("مشاهده کامل")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumSize(650, 550)

        layout = QVBoxLayout(dialog)

        name = "{} {}".format(rec.get('first_name', ''), rec.get('last_name', ''))
        title = QLabel("👤 " + name)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #58A6FF; padding: 10px;")
        layout.addWidget(title)

        # نمایش همه موضوعات ثبت شده برای این کاربر
        instagram_id = rec.get('instagram_id', '')
        if instagram_id:
            all_subjects = self.get_user_all_subjects(instagram_id)
            if len(all_subjects) > 1:
                subjects_frame = QFrame()
                subjects_frame.setStyleSheet(
                    "background-color: #1F3D5F; border-radius: 8px; padding: 10px;"
                )
                sf_layout = QVBoxLayout(subjects_frame)

                lbl = QLabel("📂 همه موضوعات ثبت شده برای این کاربر:")
                lbl.setStyleSheet("color: #58A6FF; font-weight: bold; font-size: 13px;")
                sf_layout.addWidget(lbl)

                subjects_text = " • ".join(all_subjects)
                subjects_lbl = QLabel(subjects_text)
                subjects_lbl.setStyleSheet("color: white; font-size: 12px; padding: 5px;")
                subjects_lbl.setWordWrap(True)
                sf_layout.addWidget(subjects_lbl)

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

        for key, fa in fa_map.items():
            val = rec.get(key, '')
            if val:
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                lbl = QLabel(fa + ":")
                lbl.setStyleSheet("color: #8B949E; font-weight: bold; min-width: 150px;")
                row.addWidget(lbl)

                val_lbl = QLabel(str(val))
                val_lbl.setStyleSheet("color: #E6EDF3; padding: 8px; background: #1C2128; border-radius: 6px;")
                val_lbl.setWordWrap(True)
                row.addWidget(val_lbl, 1)

                content_layout.addWidget(row_widget)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        close_btn = QPushButton("بستن")
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
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self.create_page_header(
            "🔬 جستجوی پیشرفته",
            "فیلتر همزمان چند فیلد"
        ))

        form_card = QFrame()
        form_card.setObjectName("card")
        form_layout = QGridLayout(form_card)

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
            lbl = QLabel(field)
            lbl.setObjectName("formLabel")
            container.addWidget(lbl)

            inp = QLineEdit()
            inp.setPlaceholderText(field + "...")
            container.addWidget(inp)
            self.adv_filters[field] = inp

            wrapper = QWidget()
            wrapper.setLayout(container)
            form_layout.addWidget(wrapper, row, col)

        subj_container = QVBoxLayout()
        subj_lbl = QLabel("📂 موضوع ثبت")
        subj_lbl.setObjectName("formLabel")
        subj_container.addWidget(subj_lbl)
        self.adv_subject = QComboBox()
        self.adv_subject.addItems(self.get_subjects_list())
        subj_container.addWidget(self.adv_subject)
        subj_wrapper = QWidget()
        subj_wrapper.setLayout(subj_container)
        form_layout.addWidget(subj_wrapper, 2, 0, 1, 2)

        year_container = QVBoxLayout()
        year_lbl = QLabel("📅 سال ثبت")
        year_lbl.setObjectName("formLabel")
        year_container.addWidget(year_lbl)
        self.adv_year = QComboBox()
        self.adv_year.addItems(YEARS_LIST)
        year_container.addWidget(self.adv_year)
        year_wrapper = QWidget()
        year_wrapper.setLayout(year_container)
        form_layout.addWidget(year_wrapper, 2, 2, 1, 2)

        layout.addWidget(form_card)

        btn_row = QHBoxLayout()
        search_btn = QPushButton("🔬 اعمال فیلترها")
        search_btn.setObjectName("primaryButton")
        search_btn.setMinimumHeight(40)
        search_btn.clicked.connect(self.do_advanced_search)
        btn_row.addWidget(search_btn)

        clear_btn = QPushButton("🔄 پاک کردن")
        clear_btn.setMinimumHeight(40)
        clear_btn.clicked.connect(self.clear_advanced)
        btn_row.addWidget(clear_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.adv_count = QLabel("")
        self.adv_count.setStyleSheet("color: #3FB950; font-weight: bold; padding: 5px;")
        layout.addWidget(self.adv_count)

        self.adv_table = self.create_results_table()
        layout.addWidget(self.adv_table, 1)

        btn_row2 = QHBoxLayout()
        view_btn = QPushButton("👁️ مشاهده")
        view_btn.setObjectName("primaryButton")
        view_btn.clicked.connect(lambda: self.view_record(self.adv_table))
        btn_row2.addWidget(view_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.setObjectName("warningButton")
        edit_btn.clicked.connect(lambda: self.edit_record(self.adv_table))
        btn_row2.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("dangerButton")
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
        self.adv_count.setText("✅ {} نتیجه".format(len(results)))

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
        layout.setContentsMargins(20, 20, 20, 20)

        self.form_header = self.create_page_header(
            "➕ ثبت کاربر جدید",
            "اطلاعات کاربر را وارد کنید"
        )
        layout.addWidget(self.form_header)

        form_card = QFrame()
        form_card.setObjectName("card")
        form_layout = QGridLayout(form_card)

        lbl = QLabel("⭐ ایدی اینستاگرام *")
        lbl.setObjectName("requiredLabel")
        form_layout.addWidget(lbl, 0, 0)
        self.form_instagram = QLineEdit()
        form_layout.addWidget(self.form_instagram, 0, 1)

        form_layout.addWidget(QLabel("نام"), 0, 2)
        self.form_first_name = QLineEdit()
        form_layout.addWidget(self.form_first_name, 0, 3)

        form_layout.addWidget(QLabel("نام خانوادگی"), 1, 0)
        self.form_last_name = QLineEdit()
        form_layout.addWidget(self.form_last_name, 1, 1)

        form_layout.addWidget(QLabel("نام پدر"), 1, 2)
        self.form_father_name = QLineEdit()
        form_layout.addWidget(self.form_father_name, 1, 3)

        form_layout.addWidget(QLabel("شماره تماس"), 2, 0)
        self.form_phone = QLineEdit()
        form_layout.addWidget(self.form_phone, 2, 1)

        form_layout.addWidget(QLabel("شماره ملی"), 2, 2)
        self.form_national_id = QLineEdit()
        form_layout.addWidget(self.form_national_id, 2, 3)

        form_layout.addWidget(QLabel("📂 موضوع ثبت"), 3, 0)
        self.form_subject = QComboBox()
        self.form_subject.addItems(self.get_subjects_list())
        form_layout.addWidget(self.form_subject, 3, 1)

        form_layout.addWidget(QLabel("📅 سال ثبت"), 3, 2)
        self.form_year = QComboBox()
        self.form_year.addItems(YEARS_LIST)
        form_layout.addWidget(self.form_year, 3, 3)

        form_layout.addWidget(QLabel("کد تارنما"), 4, 0)
        self.form_tarnama = QLineEdit()
        form_layout.addWidget(self.form_tarnama, 4, 1)

        form_layout.addWidget(QLabel("تاریخ ثبت"), 4, 2)
        self.form_reg_date = QLineEdit()
        form_layout.addWidget(self.form_reg_date, 4, 3)

        form_layout.addWidget(QLabel("نشانی"), 5, 0)
        self.form_address = QTextEdit()
        self.form_address.setMaximumHeight(80)
        form_layout.addWidget(self.form_address, 5, 1, 1, 3)

        layout.addWidget(form_card)

        btn_row = QHBoxLayout()

        self.save_btn = QPushButton("✅ ثبت کاربر")
        self.save_btn.setObjectName("successButton")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.save_form)
        btn_row.addWidget(self.save_btn)

        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.cancel_form)
        btn_row.addWidget(cancel_btn)

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
        # اگر موضوع ترکیبی بود، اولین بخش رو انتخاب کن
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
            QMessageBox.information(self, "موفق", "✅ ویرایش شد!")
            self.edit_id = None
        else:
            self.db.add_user(data)
            QMessageBox.information(self, "موفق", "✅ کاربر جدید ثبت شد!")

        self.clear_form()
        self.show_dashboard()

    def cancel_form(self):
        self.clear_form()
        self.edit_id = None
        self.show_dashboard()

    def create_list_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self.create_page_header(
            "📋 همه رکوردها",
            "نمایش تمام رکوردهای ثبت شده"
        ))

        self.list_count = QLabel("")
        self.list_count.setStyleSheet("color: #58A6FF; font-weight: bold; padding: 5px;")
        layout.addWidget(self.list_count)

        self.list_table = self.create_results_table()
        layout.addWidget(self.list_table, 1)

        btn_row = QHBoxLayout()

        view_btn = QPushButton("👁️ مشاهده")
        view_btn.setObjectName("primaryButton")
        view_btn.clicked.connect(lambda: self.view_record(self.list_table))
        btn_row.addWidget(view_btn)

        edit_btn = QPushButton("✏️ ویرایش")
        edit_btn.setObjectName("warningButton")
        edit_btn.clicked.connect(lambda: self.edit_record(self.list_table))
        btn_row.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(lambda: self.delete_record(self.list_table))
        btn_row.addWidget(delete_btn)

        export_btn = QPushButton("📥 خروجی اکسل")
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
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self.create_page_header(
            "⚙️ تنظیمات",
            "مدیریت دیتابیس"
        ))

        tabs = QTabWidget()

        reload_tab = QWidget()
        reload_layout = QVBoxLayout(reload_tab)

        warn = QLabel("⚠️ داده‌های فعلی جایگزین می‌شوند")
        warn.setStyleSheet("color: #D29922; padding: 10px;")
        reload_layout.addWidget(warn)

        reload_btn = QPushButton("📂 انتخاب و بارگذاری فایل اکسل")
        reload_btn.setObjectName("primaryButton")
        reload_btn.setMinimumHeight(45)
        reload_btn.clicked.connect(lambda: self.load_excel_dialog())
        reload_layout.addWidget(reload_btn)
        reload_layout.addStretch()

        tabs.addTab(reload_tab, "📂 بارگذاری مجدد")

        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)

        subjects_text = "<br>".join(["• " + s for s in DEFAULT_SUBJECTS if s])

        about_text = QLabel(
            "<div style='line-height: 2;'>"
            "<h2 style='color: #58A6FF;'>🔍 CyberWatch v7.0</h2>"
            "<p><b>سامانه هوشمند جستجو و ثبت کاربران فضای مجازی</b></p>"
            "<hr>"
            "<p><b>ویژگی‌ها:</b></p>"
            "<ul>"
            "<li>✅ جستجوی هوشمند در تمام فیلدها</li>"
            "<li>✅ جستجوی پیشرفته با فیلترهای همزمان</li>"
            "<li>✅ کمبوباکس برای موضوع و سال</li>"
            "<li>✅ نمایش همه موضوعات یک کاربر در پروفایل</li>"
            "<li>✅ ثبت، ویرایش، حذف</li>"
            "<li>✅ خروجی اکسل</li>"
            "<li>✅ 100% Desktop - بدون مرورگر</li>"
            "</ul>"
            "<hr>"
            "<p><b>📂 موضوعات قابل انتخاب:</b></p>"
            "<div style='color: #58A6FF; padding: 10px;'>" + subjects_text + "</div>"
            "<hr>"
            "<p><b>مسیر دیتابیس:</b><br>"
            "<code style='color: #58A6FF;'>" + self.db.db_path + "</code></p>"
            "</div>"
        )
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        about_layout.addStretch()

        tabs.addTab(about_tab, "ℹ️ درباره")

        layout.addWidget(tabs)

        return page

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


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    splash = SplashScreen()
    splash.show()
    QApplication.processEvents()

    steps = [
        (15, "در حال بارگذاری کتابخانه‌ها..."),
        (35, "در حال راه‌اندازی رابط..."),
        (55, "در حال اتصال به دیتابیس..."),
        (75, "در حال آماده‌سازی..."),
        (100, "✅ آماده!"),
    ]

    for value, status in steps:
        splash.update_progress(value, status)
        time.sleep(0.3)

    window = CyberWatchApp()
    splash.close()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
