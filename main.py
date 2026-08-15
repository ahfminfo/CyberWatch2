"""
سامانه کاربران تحت نظارت در فضای مجازی
نسخه 10.0 - نسخه Enterprise با تشخیص تکراری و تکمیل هوشمند
"""
import sys
import os
import time
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QTabWidget, QMessageBox, QFileDialog,
    QHeaderView, QFrame, QStackedWidget, QScrollArea,
    QGridLayout, QProgressBar, QDialog, QCheckBox, QRadioButton,
    QButtonGroup, QCompleter, QGroupBox, QCalendarWidget
)
from PyQt5.QtCore import Qt, QStringListModel, QDate, pyqtSignal
from PyQt5.QtGui import (
    QIntValidator, QRegExpValidator, QColor, QFont
)
from PyQt5.QtCore import QRegExp

from database import Database


# ═══════════════════════════════════════════════════════
# تنظیمات اصلی
# ═══════════════════════════════════════════════════════
APP_NAME = "سامانه کاربران تحت نظارت در فضای مجازی"
APP_SHORT_NAME = "سامانه نظارت"
APP_VERSION = "11.1"

# سال‌های شمسی
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

# وضعیت‌های خانواده و اجتماعی
FAMILY_STATUS_FLAGS = [
    "فرزند طلاق",
    "بدسرپرست",
    "طلاق",
    "فوت همسر",
]

ECONOMIC_STATUS_OPTIONS = [
    "وضعیت اقتصادی ضعیف",
    "وضعیت اقتصادی متوسط",
    "وضعیت اقتصادی مناسب",
]

FAMILY_STATUS_COLORS = {
    "فرزند طلاق": "#EC4899",
    "بدسرپرست": "#EF4444",
    "طلاق": "#F97316",
    "فوت همسر": "#8B5CF6",
    "وضعیت اقتصادی ضعیف": "#DC2626",
    "وضعیت اقتصادی متوسط": "#F59E0B",
    "وضعیت اقتصادی مناسب": "#10B981",
}


# ═══════════════════════════════════════════════════════
# توابع کمکی فالوور
# ═══════════════════════════════════════════════════════
def format_followers(n):
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
# 📅 تبدیل تاریخ شمسی و میلادی (بدون کتابخانه اضافی)
# ═══════════════════════════════════════════════════════
class PersianDate:
    """کلاس تبدیل و مدیریت تاریخ شمسی"""

    PERSIAN_MONTHS = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]

    PERSIAN_DAYS = ["ش", "ی", "د", "س", "چ", "پ", "ج"]

    @staticmethod
    def gregorian_to_jalali(gy, gm, gd):
        """تبدیل میلادی به شمسی"""
        g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        if gy > 1600:
            jy = 979
            gy -= 1600
        else:
            jy = 0
            gy -= 621

        gy2 = gy + 1 if gm > 2 else gy
        days = (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + \
               ((gy2 + 399) // 400) - 80 + gd + g_d_m[gm - 1]

        jy += 33 * (days // 12053)
        days %= 12053
        jy += 4 * (days // 1461)
        days %= 1461

        if days > 365:
            jy += (days - 1) // 365
            days = (days - 1) % 365

        if days < 186:
            jm = 1 + (days // 31)
            jd = 1 + (days % 31)
        else:
            jm = 7 + ((days - 186) // 30)
            jd = 1 + ((days - 186) % 30)

        return jy, jm, jd

    @staticmethod
    def jalali_to_gregorian(jy, jm, jd):
        """تبدیل شمسی به میلادی"""
        if jy > 979:
            gy = 1600
            jy -= 979
        else:
            gy = 621

        days = (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + \
               78 + jd

        if jm < 7:
            days += (jm - 1) * 31
        else:
            days += ((jm - 7) * 30) + 186

        gy += 400 * (days // 146097)
        days %= 146097

        if days > 36524:
            gy += 100 * (--days // 36524) if days > 0 else 0
            days %= 36524
            if days >= 365:
                days += 1

        gy += 4 * (days // 1461)
        days %= 1461

        if days > 365:
            gy += (days - 1) // 365
            days = (days - 1) % 365

        gd = days + 1
        sal_a = [0, 31, (29 if (gy % 4 == 0 and gy % 100 != 0) or
                        (gy % 400 == 0) else 28),
                 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        gm = 0
        while gm < 13 and gd > sal_a[gm]:
            gd -= sal_a[gm]
            gm += 1

        return gy, gm, gd

    @staticmethod
    def today_jalali():
        """تاریخ شمسی امروز"""
        from datetime import date
        today = date.today()
        return PersianDate.gregorian_to_jalali(
            today.year, today.month, today.day
        )

    @staticmethod
    def format_jalali(jy, jm, jd):
        """فرمت خروجی: 1403/05/15"""
        return "{:04d}/{:02d}/{:02d}".format(jy, jm, jd)

    @staticmethod
    def parse_jalali(date_str):
        """تجزیه رشته 1403/05/15 به (سال، ماه، روز)"""
        try:
            parts = date_str.strip().split('/')
            if len(parts) == 3:
                return int(parts[0]), int(parts[1]), int(parts[2])
        except Exception:
            pass
        return None

    @staticmethod
    def is_valid(jy, jm, jd):
        """چک اعتبار تاریخ شمسی"""
        if not (1300 <= jy <= 1500):
            return False
        if not (1 <= jm <= 12):
            return False

        if jm <= 6:
            max_day = 31
        elif jm <= 11:
            max_day = 30
        else:
            # اسفند - بررسی سال کبیسه
            is_leap = ((jy % 33) % 4 == 1)
            max_day = 30 if is_leap else 29

        return 1 <= jd <= max_day


# ═══════════════════════════════════════════════════════
# 📅 Widget تقویم شمسی
# ═══════════════════════════════════════════════════════
class PersianCalendarDialog(QDialog):
    """دیالوگ انتخاب تاریخ شمسی"""

    date_selected = pyqtSignal(str)

    def __init__(self, parent=None, initial_date=None):
        super().__init__(parent)
        self.setWindowTitle("انتخاب تاریخ")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedSize(420, 480)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E293B;
            }
        """)

        if initial_date:
            parsed = PersianDate.parse_jalali(initial_date)
            if parsed:
                self.current_year, self.current_month, self.current_day = parsed
            else:
                self.current_year, self.current_month, self.current_day = \
                    PersianDate.today_jalali()
        else:
            self.current_year, self.current_month, self.current_day = \
                PersianDate.today_jalali()

        self.selected_day = self.current_day
        self.setup_ui()
        self.update_calendar()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # هدر با تنظیم سال و ماه
        header = QHBoxLayout()
        header.setSpacing(8)

        prev_year = QPushButton("<<")
        prev_year.setMaximumWidth(40)
        prev_year.setMinimumHeight(35)
        prev_year.clicked.connect(self.prev_year)
        header.addWidget(prev_year)

        prev_month = QPushButton("<")
        prev_month.setMaximumWidth(40)
        prev_month.setMinimumHeight(35)
        prev_month.clicked.connect(self.prev_month)
        header.addWidget(prev_month)

        self.header_label = QLabel("")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #60A5FA;
            padding: 8px;
            background-color: #0F172A;
            border-radius: 6px;
        """)
        header.addWidget(self.header_label, 1)

        next_month = QPushButton(">")
        next_month.setMaximumWidth(40)
        next_month.setMinimumHeight(35)
        next_month.clicked.connect(self.next_month)
        header.addWidget(next_month)

        next_year = QPushButton(">>")
        next_year.setMaximumWidth(40)
        next_year.setMinimumHeight(35)
        next_year.clicked.connect(self.next_year)
        header.addWidget(next_year)

        layout.addLayout(header)

        # هدر روزهای هفته
        days_header = QHBoxLayout()
        days_header.setSpacing(3)
        for day_name in ["ش", "ی", "د", "س", "چ", "پ", "ج"]:
            lbl = QLabel(day_name)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("""
                font-weight: 700;
                color: #94A3B8;
                padding: 5px;
                background-color: #334155;
                border-radius: 4px;
                font-size: 12px;
            """)
            lbl.setMinimumHeight(30)
            days_header.addWidget(lbl)
        layout.addLayout(days_header)

        # گرید روزها
        self.days_grid = QGridLayout()
        self.days_grid.setSpacing(3)
        layout.addLayout(self.days_grid)

        # دکمه‌های پایین
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        today_btn = QPushButton("📅 امروز")
        today_btn.setMinimumHeight(38)
        today_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        today_btn.clicked.connect(self.go_today)
        btn_layout.addWidget(today_btn)

        ok_btn = QPushButton("✅ تأیید")
        ok_btn.setMinimumHeight(38)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)
        ok_btn.clicked.connect(self.accept_date)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("❌ لغو")
        cancel_btn.setMinimumHeight(38)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #475569;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def update_calendar(self):
        # پاک کردن قبلی
        while self.days_grid.count():
            item = self.days_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # هدر
        self.header_label.setText(
            PersianDate.PERSIAN_MONTHS[self.current_month - 1] +
            " " + str(self.current_year)
        )

        # پیدا کردن روز شروع (شنبه = 0)
        gy, gm, gd = PersianDate.jalali_to_gregorian(
            self.current_year, self.current_month, 1
        )
        from datetime import date
        first_day = date(gy, gm, gd)
        # شنبه = 5 در weekday پایتون (دوشنبه = 0)
        # میخوایم شنبه = 0 باشه
        start_col = (first_day.weekday() + 2) % 7

        # تعداد روزهای ماه
        if self.current_month <= 6:
            days_in_month = 31
        elif self.current_month <= 11:
            days_in_month = 30
        else:
            is_leap = ((self.current_year % 33) % 4 == 1)
            days_in_month = 30 if is_leap else 29

        # امروز
        today_y, today_m, today_d = PersianDate.today_jalali()

        # قرار دادن روزها
        row = 0
        col = start_col

        # سلول‌های خالی ابتدا
        for i in range(start_col):
            empty = QLabel("")
            empty.setMinimumHeight(38)
            self.days_grid.addWidget(empty, 0, i)

        for day in range(1, days_in_month + 1):
            day_btn = QPushButton(str(day))
            day_btn.setMinimumHeight(38)
            day_btn.setCursor(Qt.PointingHandCursor)

            # استایل پیش‌فرض
            is_today = (
                day == today_d and
                self.current_month == today_m and
                self.current_year == today_y
            )
            is_selected = (day == self.selected_day)

            if is_selected:
                style = """
                    QPushButton {
                        background-color: #2563EB;
                        color: white;
                        border: 2px solid #60A5FA;
                        border-radius: 6px;
                        font-weight: 900;
                        font-size: 13px;
                    }
                """
            elif is_today:
                style = """
                    QPushButton {
                        background-color: #10B981;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-weight: 700;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #059669;
                    }
                """
            else:
                style = """
                    QPushButton {
                        background-color: #334155;
                        color: #F1F5F9;
                        border: none;
                        border-radius: 6px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #475569;
                        color: #60A5FA;
                    }
                """

            day_btn.setStyleSheet(style)
            day_btn.clicked.connect(
                lambda checked, d=day: self.select_day(d)
            )

            self.days_grid.addWidget(day_btn, row, col)

            col += 1
            if col > 6:
                col = 0
                row += 1

    def select_day(self, day):
        self.selected_day = day
        self.update_calendar()

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.selected_day = 1
        self.update_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.selected_day = 1
        self.update_calendar()

    def prev_year(self):
        self.current_year -= 1
        self.update_calendar()

    def next_year(self):
        self.current_year += 1
        self.update_calendar()

    def go_today(self):
        y, m, d = PersianDate.today_jalali()
        self.current_year = y
        self.current_month = m
        self.selected_day = d
        self.update_calendar()

    def accept_date(self):
        date_str = PersianDate.format_jalali(
            self.current_year,
            self.current_month,
            self.selected_day
        )
        self.date_selected.emit(date_str)
        self.accept()


# ═══════════════════════════════════════════════════════
# 🎯 Validator های سفارشی
# ═══════════════════════════════════════════════════════
class PersianTextValidator(QRegExpValidator):
    """فقط حروف فارسی و فاصله"""
    def __init__(self, parent=None):
        regex = QRegExp(r"^[\u0600-\u06FF\s]+$")
        super().__init__(regex, parent)


class InstagramIdValidator(QRegExpValidator):
    """ایدی اینستاگرام: حروف انگلیسی، عدد، نقطه، آندرلاین"""
    def __init__(self, parent=None):
        regex = QRegExp(r"^[a-zA-Z0-9._@]+$")
        super().__init__(regex, parent)


class NumberOnlyValidator(QRegExpValidator):
    """فقط عدد"""
    def __init__(self, parent=None):
        regex = QRegExp(r"^[0-9]+$")
        super().__init__(regex, parent)


class TarnamaCodeValidator(QRegExpValidator):
    """کد تارنما: عدد، حرف، / و \\"""
    def __init__(self, parent=None):
        regex = QRegExp(r"^[a-zA-Z0-9/\\\-]+$")
        super().__init__(regex, parent)


class PhoneValidator(QRegExpValidator):
    """شماره تماس: فقط عدد، حداکثر 11 رقم"""
    def __init__(self, parent=None):
        regex = QRegExp(r"^0[0-9]{0,10}$")
        super().__init__(regex, parent)


class NationalIdValidator(QRegExpValidator):
    """کد ملی: فقط 10 رقم"""
    def __init__(self, parent=None):
        regex = QRegExp(r"^[0-9]{0,10}$")
        super().__init__(regex, parent)


class DateValidator(QRegExpValidator):
    """تاریخ شمسی: 1403/05/15"""
    def __init__(self, parent=None):
        regex = QRegExp(r"^[0-9/]*$")
        super().__init__(regex, parent)


def validate_national_id(code):
    """اعتبارسنجی کد ملی ایرانی"""
    if not code or len(code) != 10 or not code.isdigit():
        return False

    check = int(code[9])
    s = sum(int(code[i]) * (10 - i) for i in range(9)) % 11

    if s < 2:
        return check == s
    else:
        return check == (11 - s)
    # ═══════════════════════════════════════════════════════
# استایل کامل (اصلاح شده)
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
    font-size: 20px;
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
    padding: 12px 18px;
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
    padding: 15px;
}

#statCard {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 15px;
}

/* ═══ دکمه‌ها ═══ */
QPushButton {
    background-color: #334155;
    color: #F1F5F9;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 8px 16px;
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

QPushButton#calendarButton {
    background-color: #8B5CF6;
    color: white;
    border: none;
    font-weight: 700;
    padding: 8px 12px;
}

QPushButton#calendarButton:hover {
    background-color: #7C3AED;
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

QLineEdit:disabled, QTextEdit:disabled {
    background-color: #1E293B;
    color: #64748B;
}

QLineEdit[readOnly="true"] {
    background-color: #1E293B;
    color: #94A3B8;
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
}

QComboBox:hover {
    border-color: #60A5FA;
    background-color: #334155;
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

QLabel#hintLabel {
    color: #10B981;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 5px;
}

QLabel#errorLabel {
    color: #EF4444;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 5px;
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

/* ═══ چک باکس و رادیو ═══ */
QCheckBox {
    color: #F1F5F9;
    font-size: 13px;
    font-weight: 600;
    padding: 5px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #475569;
    border-radius: 4px;
    background-color: #0F172A;
}

QCheckBox::indicator:hover {
    border-color: #60A5FA;
}

QCheckBox::indicator:checked {
    background-color: #2563EB;
    border-color: #60A5FA;
    image: none;
}

QCheckBox::indicator:checked:hover {
    background-color: #1D4ED8;
}

QRadioButton {
    color: #F1F5F9;
    font-size: 13px;
    font-weight: 600;
    padding: 5px;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #475569;
    border-radius: 10px;
    background-color: #0F172A;
}

QRadioButton::indicator:hover {
    border-color: #60A5FA;
}

QRadioButton::indicator:checked {
    background-color: #2563EB;
    border-color: #60A5FA;
}

/* ═══ GroupBox ═══ */
QGroupBox {
    color: #60A5FA;
    font-weight: 700;
    font-size: 13px;
    border: 2px solid #334155;
    border-radius: 10px;
    margin-top: 15px;
    padding: 15px 10px 10px 10px;
    background-color: #0F172A;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top right;
    padding: 0 10px;
    background-color: #1E293B;
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
"""


# ═══════════════════════════════════════════════════════
# Splash Screen
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
# Setup Dialog
# ═══════════════════════════════════════════════════════
def show_setup_dialog_standalone(app, db):
    """
    دیالوگ نصب اولیه - اجباری برای بارگذاری دیتاست
    """
    dialog = QDialog()
    dialog.setWindowTitle("راه‌اندازی اولیه سامانه - الزامی")
    dialog.setLayoutDirection(Qt.RightToLeft)
    dialog.setMinimumWidth(650)
    dialog.setMinimumHeight(450)
    dialog.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
    dialog.setStyleSheet("QDialog { background-color: #0F172A; }")

    result = {'done': False}

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(35, 30, 35, 30)
    layout.setSpacing(15)

    # لوگو و عنوان
    title = QLabel("🛡️ " + APP_SHORT_NAME)
    title.setStyleSheet(
        "font-size: 26px; font-weight: 900; color: #60A5FA; padding: 10px;"
    )
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    # هشدار امنیتی
    security_notice = QFrame()
    security_notice.setStyleSheet(
        "background-color: #78350F; border: 2px solid #F59E0B; "
        "border-radius: 10px; padding: 12px;"
    )
    sn_layout = QVBoxLayout(security_notice)
    sn_layout.setSpacing(5)

    sn_title = QLabel("🔒 اطلاعات امنیتی مهم")
    sn_title.setStyleSheet(
        "color: #FCD34D; font-size: 14px; font-weight: 900; "
        "background-color: transparent;"
    )
    sn_layout.addWidget(sn_title)

    sn_text = QLabel(
        "این سامانه حاوی اطلاعات محرمانه است.\n"
        "برای شروع کار، حتماً باید فایل اکسل دیتابیس اصلی را بارگذاری کنید.\n"
        "بدون بارگذاری دیتاست، برنامه اجرا نخواهد شد."
    )
    sn_text.setStyleSheet(
        "color: #FEF3C7; font-size: 12px; font-weight: 600; "
        "background-color: transparent;"
    )
    sn_text.setWordWrap(True)
    sn_layout.addWidget(sn_text)

    layout.addWidget(security_notice)

    # زیرنویس
    subtitle = QLabel("📂 لطفاً فایل اکسل دیتابیس را انتخاب کنید:")
    subtitle.setAlignment(Qt.AlignCenter)
    subtitle.setStyleSheet(
        "color: #94A3B8; font-size: 14px; padding: 8px;"
    )
    layout.addWidget(subtitle)

    # پراگرس بار
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

    # پیام وضعیت
    status_label = QLabel("")
    status_label.setAlignment(Qt.AlignCenter)
    status_label.setStyleSheet(
        "color: #10B981; font-size: 13px; font-weight: 700;"
    )
    status_label.hide()
    layout.addWidget(status_label)

    # دکمه انتخاب فایل
    btn = QPushButton("📂  انتخاب فایل اکسل دیتابیس")
    btn.setMinimumHeight(54)
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

    # دکمه خروج
    exit_btn = QPushButton("❌  خروج از برنامه")
    exit_btn.setMinimumHeight(40)
    exit_btn.setStyleSheet("""
        QPushButton {
            background-color: #7F1D1D;
            color: white;
            border: 1px solid #DC2626;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
        }
        QPushButton:hover { background-color: #991B1B; }
    """)
    layout.addWidget(exit_btn)

    layout.addStretch()

    def load_excel():
        file_path, _ = QFileDialog.getOpenFileName(
            dialog, "انتخاب فایل اکسل دیتابیس", "",
            "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        btn.setEnabled(False)
        exit_btn.setEnabled(False)
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

            if total == 0:
                raise Exception("فایل اکسل خالی است یا فرمت نامعتبر دارد")

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
            exit_btn.setEnabled(True)
            btn.setText("📂  انتخاب فایل اکسل دیتابیس")
            status_label.setText("❌ خطا: " + str(e))
            status_label.setStyleSheet(
                "color: #EF4444; font-size: 12px; font-weight: 700;"
            )
            status_label.show()
            app.processEvents()

    def exit_app():
        result['done'] = False
        dialog.reject()

    btn.clicked.connect(load_excel)
    exit_btn.clicked.connect(exit_app)

    screen = app.primaryScreen().geometry()
    x = (screen.width() - dialog.width()) // 2
    y = (screen.height() - dialog.height()) // 2
    dialog.move(x, y)

    dialog.raise_()
    dialog.activateWindow()
    dialog.exec_()

    return result['done']

# ═══════════════════════════════════════════════════════
# ⚠️ دیالوگ هشدار تکراری (حرفه‌ای)
# ═══════════════════════════════════════════════════════
class DuplicateWarningDialog(QDialog):
    """
    دیالوگ نمایش رکوردهای تکراری قبل از ثبت
    خروجی: True = ثبت جدید، False = انصراف
    """
    def __init__(self, parent, check_result):
        super().__init__(parent)
        self.setWindowTitle("⚠️ هشدار تکراری")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumSize(700, 550)
        self.setStyleSheet("QDialog { background-color: #0F172A; }")

        self.result_action = False  # پیش‌فرض: انصراف
        self.check_result = check_result

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # هدر
        match_type = self.check_result['match_type']
        confidence = self.check_result['confidence']

        if confidence == 'exact':
            header_color = "#DC2626"
            icon = "🚨"
            title_text = "هشدار جدی: رکورد تکراری!"
        else:
            header_color = "#F59E0B"
            icon = "⚠️"
            title_text = "توجه: رکورد مشابه یافت شد"

        header = QFrame()
        header.setStyleSheet(
            "background-color: " + header_color + "; "
            "border-radius: 12px; padding: 15px;"
        )
        h_layout = QVBoxLayout(header)
        h_layout.setSpacing(5)

        title = QLabel(icon + "  " + title_text)
        title.setStyleSheet(
            "color: white; font-size: 18px; font-weight: 900; "
            "background-color: transparent;"
        )
        title.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(title)

        subtitle = QLabel(self.check_result['message'])
        subtitle.setStyleSheet(
            "color: white; font-size: 13px; font-weight: 600; "
            "background-color: transparent;"
        )
        subtitle.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(subtitle)

        layout.addWidget(header)

        # اطلاعیه
        count = len(self.check_result['matches'])
        info = QLabel(
            "🔍  " + str(count) + " رکورد مشابه در سامانه ثبت شده است. "
            "لطفاً بررسی کنید:"
        )
        info.setStyleSheet(
            "color: #60A5FA; font-size: 13px; font-weight: 700; "
            "padding: 8px; background-color: #1E293B; border-radius: 8px;"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # لیست رکوردهای مشابه
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(5, 5, 5, 5)

        for i, match in enumerate(self.check_result['matches'], 1):
            card = self.create_match_card(i, match)
            content_layout.addWidget(card)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # سوال نهایی
        question = QLabel(
            "❓  آیا مطمئن هستید که این شخص جدید است و در سامانه ثبت نشده؟"
        )
        question.setStyleSheet(
            "color: #F1F5F9; font-size: 14px; font-weight: 700; "
            "padding: 15px; background-color: #78350F; border-radius: 10px;"
        )
        question.setAlignment(Qt.AlignCenter)
        question.setWordWrap(True)
        layout.addWidget(question)

        # دکمه‌ها
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("❌  انصراف از ثبت")
        cancel_btn.setObjectName("dangerButton")
        cancel_btn.setMinimumHeight(48)
        cancel_btn.setStyleSheet("font-size: 14px; min-width: 200px;")
        cancel_btn.clicked.connect(self.cancel_registration)
        btn_row.addWidget(cancel_btn)

        register_btn = QPushButton("✅  بله، شخص جدید است. ثبت کن")
        register_btn.setObjectName("successButton")
        register_btn.setMinimumHeight(48)
        register_btn.setStyleSheet("font-size: 14px; min-width: 250px;")
        register_btn.clicked.connect(self.confirm_registration)
        btn_row.addWidget(register_btn)

        layout.addLayout(btn_row)

    def create_match_card(self, index, match):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 2px solid #334155;
                border-radius: 10px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # ردیف اول: شماره و نام
        header = QHBoxLayout()

        num = QLabel("#" + str(index))
        num.setStyleSheet(
            "background-color: #2563EB; color: white; "
            "padding: 4px 10px; border-radius: 12px; "
            "font-weight: 900; font-size: 12px;"
        )
        num.setMaximumWidth(50)
        header.addWidget(num)

        name = QLabel(
            "@" + match.get('instagram_id', '') + "  |  " +
            match.get('first_name', '') + " " +
            match.get('last_name', '')
        )
        name.setStyleSheet(
            "color: #60A5FA; font-weight: 700; font-size: 14px;"
        )
        header.addWidget(name, 1)

        # فالوور اگه داره
        fl = match.get('followers', 0)
        if fl and fl > 0:
            _, c, _ = get_follower_category(fl)
            fl_lbl = QLabel(format_followers(fl))
            fl_lbl.setStyleSheet(
                "background-color: " + c + "; color: white; "
                "padding: 4px 10px; border-radius: 10px; "
                "font-weight: 700; font-size: 11px;"
            )
            header.addWidget(fl_lbl)

        layout.addLayout(header)

        # ردیف اطلاعات
        info_parts = []
        if match.get('national_id'):
            info_parts.append("کد ملی: " + match['national_id'])
        if match.get('phone'):
            info_parts.append("موبایل: " + match['phone'])
        if match.get('father_name'):
            info_parts.append("پدر: " + match['father_name'])

        if info_parts:
            info = QLabel("  |  ".join(info_parts))
            info.setStyleSheet("color: #94A3B8; font-size: 12px;")
            layout.addWidget(info)

        # موضوع
        if match.get('subject'):
            subj = match['subject']
            first_subj = subj.split('|')[0].strip()
            subj_color = SUBJECT_COLORS.get(first_subj, "#60A5FA")

            subj_lbl = QLabel("📂 " + subj)
            subj_lbl.setStyleSheet(
                "color: " + subj_color + "; font-weight: 700; "
                "font-size: 12px; padding: 3px 0;"
            )
            layout.addWidget(subj_lbl)

        # سال ثبت و تاریخ
        date_parts = []
        if match.get('reg_year'):
            date_parts.append("سال: " + match['reg_year'])
        if match.get('reg_date'):
            date_parts.append("تاریخ: " + match['reg_date'])

        if date_parts:
            date_lbl = QLabel("  📅  " + "  |  ".join(date_parts))
            date_lbl.setStyleSheet(
                "color: #94A3B8; font-size: 11px;"
            )
            layout.addWidget(date_lbl)

        return card

    def cancel_registration(self):
        self.result_action = False
        self.reject()

    def confirm_registration(self):
        self.result_action = True
        self.accept()
    # ═══════════════════════════════════════════════════════
# کلاس اصلی برنامه
# ═══════════════════════════════════════════════════════
class CyberWatchApp(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.edit_id = None
        self.completers = {}  # برای نگهداری Completer ها

        self.setWindowTitle(APP_NAME + " - نسخه " + APP_VERSION)
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(1550, 920)
        self.setMinimumSize(1350, 780)

        self.setup_ui()
        self.show_dashboard()

    def closeEvent(self, event):
        """بک‌آپ خودکار هنگام بستن"""
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
        """آمار موضوعات - همه موضوعات از جمله بلاگر"""
        if not self.db.is_ready():
            return []

        conn = self.db._conn()
        rows = conn.execute(
            "SELECT subject FROM users WHERE subject != ''"
        ).fetchall()
        conn.close()

        # همه موضوعات (شامل بلاگر) از لیست پیش‌فرض
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

    def setup_completer(self, line_edit, field_name):
        """اضافه کردن Auto-Complete به یک ورودی"""
        suggestions = self.db.get_all_unique_values(field_name)

        if not suggestions:
            return

        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)

        popup = completer.popup()
        popup.setStyleSheet("""
            QListView {
                background-color: #1E293B;
                color: #F1F5F9;
                border: 2px solid #3B82F6;
                border-radius: 6px;
                padding: 5px;
                font-size: 13px;
                outline: 0;
            }
            QListView::item {
                padding: 8px 12px;
                border-radius: 4px;
                min-height: 24px;
            }
            QListView::item:hover {
                background-color: #334155;
                color: #60A5FA;
            }
            QListView::item:selected {
                background-color: #2563EB;
                color: white;
                font-weight: 700;
            }
        """)

        line_edit.setCompleter(completer)
        self.completers[field_name] = completer

    def refresh_all_completers(self):
        """بروزرسانی همه Completer ها بعد از تغییرات دیتابیس"""
        # این تابع بعد از ثبت/ویرایش/حذف صدا زده میشه
        if hasattr(self, 'form_first_name'):
            self.setup_completer(self.form_first_name, 'first_name')
        if hasattr(self, 'form_last_name'):
            self.setup_completer(self.form_last_name, 'last_name')
        if hasattr(self, 'form_father_name'):
            self.setup_completer(self.form_father_name, 'father_name')
        if hasattr(self, 'form_address'):
            pass  # QTextEdit نمیشه completer داشت

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
            btn.setMinimumHeight(46)
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
    # صفحه داشبورد (اصلاح شده)
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

        self.family_card = QFrame()
        self.family_card.setObjectName("card")
        layout.addWidget(self.family_card)

        layout.addStretch()

        page.setWidget(content)
        return page

    def update_dashboard(self):
        stats = self.db.get_stats()
        clean_subjects = self.get_clean_subject_stats()

        self.records_label.setText(
            "کل رکوردها: {:,}".format(stats['total'])
        )

        # پاک کردن قبلی
        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # فقط سال‌های موجود واقعی محاسبه بشه
        active_years = len(stats['years'])
        total = max(stats['total'], 1)

        ph_pct = int((stats['filled'].get('phone', 0) / total) * 100)
        ig_pct = int((stats['filled'].get('instagram_id', 0) / total) * 100)
        fl_pct = int((stats['filled'].get('followers', 0) / total) * 100)
        fs_pct = int((stats['filled'].get('family_status', 0) / total) * 100)

        cards = [
            ("📦", "{:,}".format(stats['total']),
             "کل رکوردها", "#60A5FA"),
            ("📅", str(active_years), "سال ثبت", "#10B981"),
            ("📂", str(len(clean_subjects)), "موضوعات", "#F59E0B"),
            ("📱", "{}%".format(ph_pct), "شماره تماس", "#A855F7"),
            ("📸", "{}%".format(ig_pct), "ایدی اینستا", "#EF4444"),
            ("👥", "{}%".format(fl_pct), "دارای فالوور", "#EAB308"),
            ("🏠", "{}%".format(fs_pct), "وضعیت خانواده", "#EC4899"),
        ]

        for i, (icon, value, label, color) in enumerate(cards):
            card = QFrame()
            card.setObjectName("statCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(4)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 30px;")
            icon_lbl.setAlignment(Qt.AlignCenter)

            value_lbl = QLabel(value)
            value_lbl.setStyleSheet(
                "font-size: 22px; font-weight: 900; color: " + color + ";"
            )
            value_lbl.setAlignment(Qt.AlignCenter)

            label_lbl = QLabel(label)
            label_lbl.setStyleSheet(
                "color: #94A3B8; font-size: 12px; font-weight: 600;"
            )
            label_lbl.setAlignment(Qt.AlignCenter)

            card_layout.addWidget(icon_lbl)
            card_layout.addWidget(value_lbl)
            card_layout.addWidget(label_lbl)

            self.stats_grid.addWidget(card, 0, i)

        self.update_subjects_card(clean_subjects)
        self.update_years_card(stats)
        self.update_family_card()

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
        """نمایش فقط سال‌های واقعی موجود (بدون تکرار)"""
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

        title = QLabel(
            "📅 توزیع سال‌های ثبت (فقط سال‌های موجود در دیتابیس)"
        )
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
            "#A855F7", "#EC4899", "#14B8A6", "#F97316",
            "#8B5CF6", "#EAB308"
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

    def update_family_card(self):
        """کارت آمار وضعیت اجتماعی-اقتصادی"""
        old_layout = self.family_card.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            old_layout = QVBoxLayout(self.family_card)
            old_layout.setContentsMargins(15, 15, 15, 15)
            old_layout.setSpacing(10)

        title = QLabel("🏠 وضعیت اجتماعی-اقتصادی کاربران")
        title.setStyleSheet(
            "font-size: 16px; font-weight: 700; "
            "color: #60A5FA; padding: 5px;"
        )
        old_layout.addWidget(title)

        # دریافت آمار از دیتابیس
        conn = self.db._conn()
        rows = conn.execute(
            "SELECT family_status FROM users WHERE family_status != ''"
        ).fetchall()
        conn.close()

        all_statuses = FAMILY_STATUS_FLAGS + ECONOMIC_STATUS_OPTIONS
        status_counts = {s: 0 for s in all_statuses}

        for row in rows:
            fs = row['family_status']
            parts = [s.strip() for s in fs.split('|')]
            for p in parts:
                if p in status_counts:
                    status_counts[p] += 1

        active_statuses = [(s, c) for s, c in status_counts.items() if c > 0]
        active_statuses.sort(key=lambda x: x[1], reverse=True)

        if not active_statuses:
            no_data = QLabel(
                "هنوز اطلاعات وضعیت اجتماعی ثبت نشده است"
            )
            no_data.setStyleSheet(
                "color: #64748B; padding: 15px; font-size: 13px;"
            )
            no_data.setAlignment(Qt.AlignCenter)
            old_layout.addWidget(no_data)
            return

        max_cnt = max((c for _, c in active_statuses), default=1)

        for status, cnt in active_statuses:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(8, 3, 8, 3)
            row.setSpacing(10)

            color = FAMILY_STATUS_COLORS.get(status, "#60A5FA")

            name = QLabel("● " + status)
            name.setStyleSheet(
                "padding: 4px; font-size: 13px; "
                "font-weight: 600; color: " + color + ";"
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

    # ═══════════════════════════════════════════════
    # جدول نتایج مشترک
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

            followers = rec.get('followers', 0)
            follower_item = QTableWidgetItem(format_followers(followers))
            _, color, _ = get_follower_category(followers)
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
        dialog.setMinimumSize(720, 700)

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

        # فالوور
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

        # وضعیت خانواده
        family_status = rec.get('family_status', '')
        if family_status:
            fs_frame = QFrame()
            fs_frame.setStyleSheet(
                "background-color: #1E293B; border-radius: 10px; padding: 12px;"
            )
            fs_layout = QVBoxLayout(fs_frame)
            fs_layout.setSpacing(6)

            fs_title = QLabel("🏠 وضعیت اجتماعی-اقتصادی:")
            fs_title.setStyleSheet(
                "color: #EC4899; font-weight: 700; font-size: 13px;"
            )
            fs_layout.addWidget(fs_title)

            fs_badges = QHBoxLayout()
            fs_badges.setSpacing(6)
            for status in family_status.split('|'):
                status = status.strip()
                if status:
                    c = FAMILY_STATUS_COLORS.get(status, "#60A5FA")
                    badge = QLabel("● " + status)
                    badge.setStyleSheet(
                        "background-color: " + c + "; color: white; "
                        "padding: 4px 10px; border-radius: 10px; "
                        "font-weight: 700; font-size: 11px;"
                    )
                    fs_badges.addWidget(badge)
            fs_badges.addStretch()

            fs_widget = QWidget()
            fs_widget.setLayout(fs_badges)
            fs_layout.addWidget(fs_widget)

            layout.addWidget(fs_frame)

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

        # سایر اطلاعات
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
    # 🎯 صفحه فرم ثبت (نسخه Enterprise)
    # ═══════════════════════════════════════════════
    def create_form_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        page.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        self.form_header = self.create_page_header(
            "➕ ثبت کاربر جدید",
            "با اعتبارسنجی هوشمند و تشخیص خودکار تکراری"
        )
        layout.addWidget(self.form_header)

        # ═══ گروه ۱: اطلاعات هویتی ═══
        identity_group = QGroupBox("🆔 اطلاعات هویتی")
        identity_layout = QGridLayout(identity_group)
        identity_layout.setSpacing(12)
        identity_layout.setContentsMargins(15, 20, 15, 15)

        # ایدی اینستاگرام
        lbl_ig = QLabel("⭐ ایدی اینستاگرام *")
        lbl_ig.setObjectName("requiredLabel")
        identity_layout.addWidget(lbl_ig, 0, 0)
        self.form_instagram = QLineEdit()
        self.form_instagram.setMinimumHeight(40)
        self.form_instagram.setPlaceholderText("مثال: user_name123")
        self.form_instagram.setValidator(InstagramIdValidator())
        identity_layout.addWidget(self.form_instagram, 0, 1)

        self.ig_hint = QLabel("")
        self.ig_hint.setObjectName("hintLabel")
        identity_layout.addWidget(self.ig_hint, 0, 2)

        # نام
        lbl_fn = QLabel("نام")
        lbl_fn.setObjectName("formLabel")
        identity_layout.addWidget(lbl_fn, 1, 0)
        self.form_first_name = QLineEdit()
        self.form_first_name.setMinimumHeight(40)
        self.form_first_name.setPlaceholderText("فقط حروف فارسی")
        self.form_first_name.setValidator(PersianTextValidator())
        identity_layout.addWidget(self.form_first_name, 1, 1)

        self.fn_hint = QLabel("💡 پیشنهاد هوشمند فعال")
        self.fn_hint.setObjectName("hintLabel")
        identity_layout.addWidget(self.fn_hint, 1, 2)

        # نام خانوادگی
        lbl_ln = QLabel("نام خانوادگی")
        lbl_ln.setObjectName("formLabel")
        identity_layout.addWidget(lbl_ln, 2, 0)
        self.form_last_name = QLineEdit()
        self.form_last_name.setMinimumHeight(40)
        self.form_last_name.setPlaceholderText("فقط حروف فارسی")
        self.form_last_name.setValidator(PersianTextValidator())
        identity_layout.addWidget(self.form_last_name, 2, 1)

        self.ln_hint = QLabel("💡 پیشنهاد هوشمند فعال")
        self.ln_hint.setObjectName("hintLabel")
        identity_layout.addWidget(self.ln_hint, 2, 2)

        # نام پدر
        lbl_fa = QLabel("نام پدر")
        lbl_fa.setObjectName("formLabel")
        identity_layout.addWidget(lbl_fa, 3, 0)
        self.form_father_name = QLineEdit()
        self.form_father_name.setMinimumHeight(40)
        self.form_father_name.setPlaceholderText("فقط حروف فارسی")
        self.form_father_name.setValidator(PersianTextValidator())
        identity_layout.addWidget(self.form_father_name, 3, 1)

        self.fa_hint = QLabel("💡 پیشنهاد هوشمند فعال")
        self.fa_hint.setObjectName("hintLabel")
        identity_layout.addWidget(self.fa_hint, 3, 2)

        # کد ملی
        lbl_ni = QLabel("شماره ملی")
        lbl_ni.setObjectName("formLabel")
        identity_layout.addWidget(lbl_ni, 4, 0)
        self.form_national_id = QLineEdit()
        self.form_national_id.setMinimumHeight(40)
        self.form_national_id.setPlaceholderText("10 رقم - فقط عدد")
        self.form_national_id.setMaxLength(10)
        self.form_national_id.setValidator(NationalIdValidator())
        identity_layout.addWidget(self.form_national_id, 4, 1)

        self.ni_hint = QLabel("")
        self.ni_hint.setObjectName("hintLabel")
        identity_layout.addWidget(self.ni_hint, 4, 2)

        # تنظیم عرض ستون‌ها
        identity_layout.setColumnStretch(0, 0)
        identity_layout.setColumnStretch(1, 3)
        identity_layout.setColumnStretch(2, 2)

        layout.addWidget(identity_group)

        # ═══ گروه ۲: اطلاعات تماس ═══
        contact_group = QGroupBox("📞 اطلاعات تماس")
        contact_layout = QGridLayout(contact_group)
        contact_layout.setSpacing(12)
        contact_layout.setContentsMargins(15, 20, 15, 15)

        # شماره تماس
        lbl_ph = QLabel("شماره تماس")
        lbl_ph.setObjectName("formLabel")
        contact_layout.addWidget(lbl_ph, 0, 0)
        self.form_phone = QLineEdit()
        self.form_phone.setMinimumHeight(40)
        self.form_phone.setPlaceholderText("مثال: 09121234567")
        self.form_phone.setMaxLength(11)
        self.form_phone.setValidator(PhoneValidator())
        contact_layout.addWidget(self.form_phone, 0, 1)

        # نشانی
        lbl_ad = QLabel("نشانی")
        lbl_ad.setObjectName("formLabel")
        contact_layout.addWidget(lbl_ad, 1, 0, Qt.AlignTop)
        self.form_address = QTextEdit()
        self.form_address.setMaximumHeight(70)
        self.form_address.setPlaceholderText("نشانی محل سکونت...")
        contact_layout.addWidget(self.form_address, 1, 1)

        contact_layout.setColumnStretch(0, 0)
        contact_layout.setColumnStretch(1, 5)

        layout.addWidget(contact_group)

        # ═══ گروه ۳: اطلاعات ثبت ═══
        record_group = QGroupBox("📋 اطلاعات ثبت")
        record_layout = QGridLayout(record_group)
        record_layout.setSpacing(12)
        record_layout.setContentsMargins(15, 20, 15, 15)

        # موضوع
        lbl_sb = QLabel("📂 موضوع ثبت *")
        lbl_sb.setObjectName("requiredLabel")
        record_layout.addWidget(lbl_sb, 0, 0)
        self.form_subject = QComboBox()
        self.form_subject.setMinimumHeight(40)
        self.form_subject.addItems(self.get_subjects_list())
        record_layout.addWidget(self.form_subject, 0, 1)

        # فالوور
        lbl_fl = QLabel("👥 تعداد دنبال‌کننده")
        lbl_fl.setObjectName("formLabel")
        record_layout.addWidget(lbl_fl, 0, 2)
        self.form_followers = QLineEdit()
        self.form_followers.setMinimumHeight(40)
        self.form_followers.setPlaceholderText("مثال: 15000")
        self.form_followers.setValidator(QIntValidator(0, 999999999))
        record_layout.addWidget(self.form_followers, 0, 3)

        # تاریخ ثبت (با تقویم شمسی)
        lbl_dt = QLabel("📅 تاریخ ثبت")
        lbl_dt.setObjectName("formLabel")
        record_layout.addWidget(lbl_dt, 1, 0)

        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(5)

        self.form_reg_date = QLineEdit()
        self.form_reg_date.setMinimumHeight(40)
        self.form_reg_date.setPlaceholderText("1403/05/15")
        self.form_reg_date.setValidator(DateValidator())
        self.form_reg_date.setMaxLength(10)
        date_layout.addWidget(self.form_reg_date, 1)

        calendar_btn = QPushButton("📆")
        calendar_btn.setObjectName("calendarButton")
        calendar_btn.setMinimumHeight(40)
        calendar_btn.setMaximumWidth(50)
        calendar_btn.setToolTip("انتخاب از تقویم")
        calendar_btn.clicked.connect(self.open_calendar)
        date_layout.addWidget(calendar_btn)

        record_layout.addWidget(date_widget, 1, 1)

        # نمایش سال استخراج شده (فقط خواندنی)
        lbl_yr = QLabel("📅 سال (خودکار)")
        lbl_yr.setObjectName("formLabel")
        record_layout.addWidget(lbl_yr, 1, 2)
        self.form_year_display = QLineEdit()
        self.form_year_display.setMinimumHeight(40)
        self.form_year_display.setReadOnly(True)
        self.form_year_display.setPlaceholderText("از تاریخ استخراج می‌شود")
        record_layout.addWidget(self.form_year_display, 1, 3)

        # کد تارنما
        lbl_tc = QLabel("کد تارنما")
        lbl_tc.setObjectName("formLabel")
        record_layout.addWidget(lbl_tc, 2, 0)
        self.form_tarnama = QLineEdit()
        self.form_tarnama.setMinimumHeight(40)
        self.form_tarnama.setPlaceholderText("مثال: 123/45\\67")
        self.form_tarnama.setValidator(TarnamaCodeValidator())
        record_layout.addWidget(self.form_tarnama, 2, 1, 1, 3)

        layout.addWidget(record_group)

        # ═══ گروه ۴: وضعیت اجتماعی-اقتصادی ═══
        family_group = QGroupBox("🏠 وضعیت اجتماعی-اقتصادی")
        family_layout = QVBoxLayout(family_group)
        family_layout.setSpacing(10)
        family_layout.setContentsMargins(15, 20, 15, 15)

        # چک‌باکس‌های وضعیت خانواده
        family_lbl = QLabel("وضعیت خانوادگی:")
        family_lbl.setStyleSheet(
            "color: #EC4899; font-weight: 700; font-size: 13px; padding: 5px 0;"
        )
        family_layout.addWidget(family_lbl)

        self.family_checkboxes = {}
        cb_grid = QGridLayout()
        cb_grid.setSpacing(8)

        for i, flag in enumerate(FAMILY_STATUS_FLAGS):
            cb = QCheckBox(flag)
            self.family_checkboxes[flag] = cb
            cb_grid.addWidget(cb, i // 2, i % 2)

        family_layout.addLayout(cb_grid)

        # جداکننده
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #334155;")
        sep.setMaximumHeight(2)
        family_layout.addWidget(sep)

        # رادیو باتن‌های وضعیت اقتصادی
        econ_lbl = QLabel("وضعیت اقتصادی:")
        econ_lbl.setStyleSheet(
            "color: #F59E0B; font-weight: 700; font-size: 13px; padding: 5px 0;"
        )
        family_layout.addWidget(econ_lbl)

        self.econ_button_group = QButtonGroup()
        self.econ_radios = {}
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(15)

        for opt in ECONOMIC_STATUS_OPTIONS:
            radio = QRadioButton(opt)
            self.econ_button_group.addButton(radio)
            self.econ_radios[opt] = radio
            radio_layout.addWidget(radio)

        radio_layout.addStretch()
        family_layout.addLayout(radio_layout)

        layout.addWidget(family_group)

        # ═══ نوار وضعیت (هشدار تکراری) ═══
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet(
            "background-color: transparent; padding: 0;"
        )
        self.status_frame.setMaximumHeight(0)
        layout.addWidget(self.status_frame)

        # ═══ دکمه‌های عملیات ═══
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.check_btn = QPushButton("🔍  بررسی تکراری")
        self.check_btn.setMinimumHeight(48)
        self.check_btn.setStyleSheet(
            "font-size: 14px; min-width: 180px; "
            "background-color: #8B5CF6; color: white; "
            "border: none; font-weight: 700;"
        )
        self.check_btn.clicked.connect(self.check_duplicate_manually)
        btn_row.addWidget(self.check_btn)

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

        # ═══ اتصال سیگنال‌ها ═══
        self.form_reg_date.textChanged.connect(self.on_date_changed)
        self.form_national_id.textChanged.connect(self.on_field_changed)
        self.form_instagram.textChanged.connect(self.on_field_changed)
        self.form_first_name.textChanged.connect(self.on_field_changed)
        self.form_last_name.textChanged.connect(self.on_field_changed)

        # اضافه کردن Completer به فرم
        self.setup_form_completers()

        page.setWidget(content)
        return page

    # ═══════════════════════════════════════════════
    # تقویم شمسی
    # ═══════════════════════════════════════════════
    def open_calendar(self):
        """باز کردن دیالوگ تقویم شمسی"""
        current_date = self.form_reg_date.text().strip()
        dialog = PersianCalendarDialog(
            self,
            initial_date=current_date if current_date else None
        )
        dialog.date_selected.connect(self.on_date_selected)
        dialog.exec_()

    def on_date_selected(self, date_str):
        """وقتی از تقویم تاریخ انتخاب شد"""
        self.form_reg_date.setText(date_str)

    def on_date_changed(self, text):
        """استخراج خودکار سال از تاریخ"""
        match = re.match(r'^(\d{4})', text.strip())
        if match:
            year = match.group(1)
            self.form_year_display.setText(year)
        else:
            self.form_year_display.clear()

    # ═══════════════════════════════════════════════
    # Auto-Complete
    # ═══════════════════════════════════════════════
    def setup_form_completers(self):
        """اضافه کردن تکمیل هوشمند به فیلدها"""
        self.setup_completer(self.form_first_name, 'first_name')
        self.setup_completer(self.form_last_name, 'last_name')
        self.setup_completer(self.form_father_name, 'father_name')

    # ═══════════════════════════════════════════════
    # تشخیص خودکار تغییرات (Live Check)
    # ═══════════════════════════════════════════════
    def on_field_changed(self):
        """پاک کردن پیام‌های قبلی وقتی کاربر تغییر میده"""
        self.clear_status_message()

        # اعتبارسنجی کد ملی زنده
        ni = self.form_national_id.text().strip()
        if ni:
            if len(ni) == 10:
                if validate_national_id(ni):
                    self.ni_hint.setText("✅ کد ملی معتبر")
                    self.ni_hint.setStyleSheet(
                        "color: #10B981; font-size: 11px; font-weight: 700;"
                    )
                else:
                    self.ni_hint.setText("❌ کد ملی نامعتبر")
                    self.ni_hint.setStyleSheet(
                        "color: #EF4444; font-size: 11px; font-weight: 700;"
                    )
            elif len(ni) > 0:
                self.ni_hint.setText(
                    "⏳ " + str(10 - len(ni)) + " رقم دیگر..."
                )
                self.ni_hint.setStyleSheet(
                    "color: #F59E0B; font-size: 11px; font-weight: 700;"
                )
        else:
            self.ni_hint.setText("")

    def clear_status_message(self):
        """پاک کردن پیام هشدار"""
        old_layout = self.status_frame.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self.status_frame.setMaximumHeight(0)
        self.status_frame.setStyleSheet(
            "background-color: transparent; padding: 0;"
        )

    def show_status_message(self, message, msg_type="info"):
        """نمایش پیام در نوار وضعیت"""
        self.clear_status_message()

        colors = {
            "info": ("#3B82F6", "#1E3A8A"),
            "success": ("#10B981", "#064E3B"),
            "warning": ("#F59E0B", "#78350F"),
            "error": ("#EF4444", "#7F1D1D"),
        }
        border_color, bg_color = colors.get(msg_type, colors["info"])

        self.status_frame.setMaximumHeight(60)
        self.status_frame.setStyleSheet(
            "background-color: " + bg_color + "; "
            "border: 2px solid " + border_color + "; "
            "border-radius: 8px; padding: 8px;"
        )

        layout = self.status_frame.layout()
        if not layout:
            layout = QHBoxLayout(self.status_frame)
            layout.setContentsMargins(15, 8, 15, 8)

        lbl = QLabel(message)
        lbl.setStyleSheet(
            "color: white; font-size: 13px; font-weight: 700; "
            "background-color: transparent; border: none;"
        )
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

    # ═══════════════════════════════════════════════
    # چک تکراری دستی (دکمه بررسی)
    # ═══════════════════════════════════════════════
    def check_duplicate_manually(self):
        """کاربر دکمه بررسی تکراری زده"""
        national_id = self.form_national_id.text().strip()
        instagram_id = self.form_instagram.text().strip()
        first_name = self.form_first_name.text().strip()
        last_name = self.form_last_name.text().strip()

        if not (national_id or instagram_id or (first_name and last_name)):
            self.show_status_message(
                "⚠️ حداقل یکی از: کد ملی، ایدی اینستاگرام یا نام و "
                "نام خانوادگی را وارد کنید",
                "warning"
            )
            return

        result = self.db.check_duplicate(
            national_id=national_id,
            instagram_id=instagram_id,
            first_name=first_name,
            last_name=last_name,
            exclude_id=self.edit_id
        )

        if result['has_duplicate']:
            count = len(result['matches'])
            self.show_status_message(
                "⚠️ " + str(count) + " رکورد مشابه یافت شد! "
                "قبل از ثبت بررسی کنید.",
                "warning"
            )
            # نمایش دیالوگ
            dialog = DuplicateWarningDialog(self, result)
            dialog.exec_()
        else:
            self.show_status_message(
                "✅ هیچ رکورد تکراری یافت نشد. می‌توانید ثبت کنید.",
                "success"
            )

    # ═══════════════════════════════════════════════
    # جمع‌آوری وضعیت خانواده
    # ═══════════════════════════════════════════════
    def collect_family_status(self):
        """جمع‌آوری چک‌باکس‌ها و رادیو باتن‌ها"""
        selected = []

        # چک‌باکس‌ها
        for flag, cb in self.family_checkboxes.items():
            if cb.isChecked():
                selected.append(flag)

        # رادیو
        for opt, radio in self.econ_radios.items():
            if radio.isChecked():
                selected.append(opt)
                break

        return "|".join(selected)

    def load_family_status(self, family_status_str):
        """بارگذاری وضعیت خانواده در فرم"""
        # پاک کردن قبلی
        for cb in self.family_checkboxes.values():
            cb.setChecked(False)
        self.econ_button_group.setExclusive(False)
        for radio in self.econ_radios.values():
            radio.setChecked(False)
        self.econ_button_group.setExclusive(True)

        if not family_status_str:
            return

        parts = [p.strip() for p in family_status_str.split('|')]
        for part in parts:
            if part in self.family_checkboxes:
                self.family_checkboxes[part].setChecked(True)
            elif part in self.econ_radios:
                self.econ_radios[part].setChecked(True)

    # ═══════════════════════════════════════════════
    # بارگذاری و پاک کردن فرم
    # ═══════════════════════════════════════════════
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

        # سال به صورت خودکار از تاریخ استخراج میشه
        self.form_year_display.setText(rec.get('reg_year', ''))

        followers = rec.get('followers', 0)
        self.form_followers.setText(
            str(followers) if followers else ""
        )

        subj = rec.get('subject', '')
        if '|' in subj:
            subj = subj.split('|')[0].strip()
        idx = self.form_subject.findText(subj)
        self.form_subject.setCurrentIndex(idx if idx >= 0 else 0)

        # وضعیت خانواده
        self.load_family_status(rec.get('family_status', ''))

        self.clear_status_message()

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
        self.form_year_display.clear()
        self.form_subject.setCurrentIndex(0)
        self.ni_hint.setText("")

        # پاک کردن چک‌باکس‌ها و رادیو
        for cb in self.family_checkboxes.values():
            cb.setChecked(False)
        self.econ_button_group.setExclusive(False)
        for radio in self.econ_radios.values():
            radio.setChecked(False)
        self.econ_button_group.setExclusive(True)

        self.clear_status_message()

    # ═══════════════════════════════════════════════
    # 🎯 ذخیره فرم (با چک تکراری)
    # ═══════════════════════════════════════════════
    def save_form(self):
        instagram_id = self.form_instagram.text().strip()
        if not instagram_id:
            QMessageBox.warning(
                self, "خطا در ثبت",
                "⭐ ایدی اینستاگرام الزامی است!"
            )
            return

        subject = self.form_subject.currentText().strip()
        if not subject:
            QMessageBox.warning(
                self, "خطا در ثبت",
                "📂 موضوع ثبت الزامی است!"
            )
            return

        # اعتبارسنجی کد ملی اگه وارد شده
        national_id = self.form_national_id.text().strip()
        if national_id:
            if len(national_id) != 10:
                reply = QMessageBox.question(
                    self, "کد ملی ناقص",
                    "کد ملی باید 10 رقم باشد. آیا با این وضعیت ذخیره شود؟",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

        first_name = self.form_first_name.text().strip()
        last_name = self.form_last_name.text().strip()

        # ═══ چک تکراری با اولویت ═══
        if not self.edit_id:  # فقط برای ثبت جدید
            check_result = self.db.check_duplicate(
                national_id=national_id,
                instagram_id=instagram_id,
                first_name=first_name,
                last_name=last_name,
                exclude_id=self.edit_id
            )

            if check_result['has_duplicate']:
                # نمایش دیالوگ هشدار
                dialog = DuplicateWarningDialog(self, check_result)
                dialog.exec_()

                if not dialog.result_action:
                    # کاربر انصراف داد
                    self.show_status_message(
                        "❌ ثبت لغو شد. لطفاً اطلاعات را بررسی کنید.",
                        "error"
                    )
                    return
                # کاربر تأیید کرد که شخص جدیده، ادامه ثبت

        # جمع‌آوری داده‌ها
        followers_text = self.form_followers.text().strip()
        try:
            followers = int(followers_text) if followers_text else 0
        except Exception:
            followers = 0

        reg_date = self.form_reg_date.text().strip()
        reg_year = self.form_year_display.text().strip()

        data = {
            'instagram_id': instagram_id,
            'first_name': first_name,
            'last_name': last_name,
            'father_name': self.form_father_name.text().strip(),
            'phone': self.form_phone.text().strip(),
            'national_id': national_id,
            'subject': subject,
            'tarnama_code': self.form_tarnama.text().strip(),
            'reg_date': reg_date,
            'address': self.form_address.toPlainText().strip(),
            'reg_year': reg_year,
            'followers': followers,
            'family_status': self.collect_family_status(),
        }

        try:
            if self.edit_id:
                self.db.update_user(self.edit_id, data)
                QMessageBox.information(
                    self, "موفق",
                    "✅ اطلاعات با موفقیت ویرایش شد!"
                )
                self.edit_id = None
            else:
                self.db.add_user(data)
                QMessageBox.information(
                    self, "موفق",
                    "✅ کاربر جدید با موفقیت ثبت شد!"
                )

            self.clear_form()
            self.refresh_all_completers()
            self.show_dashboard()

        except Exception as e:
            QMessageBox.critical(
                self, "خطا",
                "❌ خطا در ذخیره:\n" + str(e)
            )

    def cancel_form(self):
        self.clear_form()
        self.edit_id = None
        self.show_dashboard()
        # ═══════════════════════════════════════════════
    # 📊 صفحه تحلیل هوشمند
    # ═══════════════════════════════════════════════
    def create_analytics_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        layout.addWidget(self.create_page_header(
            "📊 تحلیل هوشمند",
            "تحلیل تخصصی موضوعات، فالوور، وضعیت اجتماعی و مقایسه‌های آماری"
        ))

        self.analytics_tabs = QTabWidget()

        self.analytics_tabs.addTab(
            self.create_single_analysis_tab(),
            "🎯  تحلیل یک موضوع"
        )
        self.analytics_tabs.addTab(
            self.create_compare_analysis_tab(),
            "🔄  مقایسه دو موضوع"
        )
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

        # دسته‌بندی فالوور
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
            info = QLabel(str(cnt) + " نفر  (" + str(pct) + "%)")
            info.setStyleSheet(
                "color: " + c + "; font-weight: 900; "
                "font-size: 13px; padding: 3px 10px;"
            )
            info.setMinimumWidth(120)
            row.addWidget(info)

            cat_layout.addWidget(row_widget)

        self.single_result_layout.addWidget(cat_card)

        # وضعیت اجتماعی-اقتصادی
        if analysis.get('family_stats'):
            fs_card = QFrame()
            fs_card.setObjectName("card")
            fs_layout = QVBoxLayout(fs_card)
            fs_layout.setContentsMargins(15, 15, 15, 15)
            fs_layout.setSpacing(8)

            fs_title = QLabel("🏠 وضعیت اجتماعی-اقتصادی این گروه")
            fs_title.setStyleSheet(
                "font-size: 15px; font-weight: 700; "
                "color: #60A5FA; padding: 5px;"
            )
            fs_layout.addWidget(fs_title)

            max_fs = max(c for _, c in analysis['family_stats'])
            total = analysis['total']

            for status, cnt in analysis['family_stats']:
                row_widget = QWidget()
                row = QHBoxLayout(row_widget)
                row.setContentsMargins(8, 3, 8, 3)
                row.setSpacing(10)

                c = FAMILY_STATUS_COLORS.get(status, "#60A5FA")

                n_lbl = QLabel("● " + status)
                n_lbl.setStyleSheet(
                    "font-size: 13px; font-weight: 600; color: " + c + ";"
                )
                n_lbl.setMinimumWidth(220)
                row.addWidget(n_lbl)

                bar = QProgressBar()
                bar.setMaximum(max_fs)
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

                pct = int((cnt / total) * 100)
                info = QLabel(str(cnt) + " (" + str(pct) + "%)")
                info.setStyleSheet(
                    "color: " + c + "; font-weight: 900; "
                    "font-size: 13px; padding: 3px 10px;"
                )
                info.setMinimumWidth(100)
                row.addWidget(info)

                fs_layout.addWidget(row_widget)

            self.single_result_layout.addWidget(fs_card)

        # Top 10
        if analysis['top_users']:
            top_card = QFrame()
            top_card.setObjectName("card")
            top_layout = QVBoxLayout(top_card)
            top_layout.setContentsMargins(15, 15, 15, 15)
            top_layout.setSpacing(8)

            top_title = QLabel("🏆 Top 10 کاربران با بیشترین دنبال‌کننده")
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

        # توزیع سالانه
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
                info = QLabel("{:,}".format(cnt) + "  (" + str(pct) + "%)")
                info.setStyleSheet(
                    "color: #60A5FA; font-weight: 900; "
                    "font-size: 13px; padding: 3px 10px;"
                )
                info.setMinimumWidth(100)
                row.addWidget(info)

                year_layout.addWidget(row_widget)

            self.single_result_layout.addWidget(year_card)

        # موضوعات مرتبط
        if analysis['related_subjects']:
            rel_card = QFrame()
            rel_card.setObjectName("card")
            rel_layout = QVBoxLayout(rel_card)
            rel_layout.setContentsMargins(15, 15, 15, 15)
            rel_layout.setSpacing(8)

            r_title = QLabel("🔗 موضوعات مرتبط (کاربران چند موضوعه)")
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

                badge = QLabel(subject + "  +  " + related_subj)
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

        # کیفیت اطلاعات
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
            ("🏠 دارای وضعیت خانواده",
             quality.get('has_family_status', 0), "#EC4899"),
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
            n_lbl.setMinimumWidth(200)
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
            info = QLabel(str(cnt) + " (" + str(pct) + "%)")
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
    # تب مقایسه دو موضوع
    # ═══════════════════════════════════════════════
    def create_compare_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

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
                self, "توجه", "دو موضوع متفاوت انتخاب کنید"
            )
            return

        result = self.db.compare_two_subjects(s1, s2)

        while self.compare_result_layout.count():
            item = self.compare_result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not result:
            no_data = QLabel("❌ داده‌ای برای مقایسه یافت نشد")
            no_data.setStyleSheet(
                "color: #EF4444; font-size: 15px; padding: 40px;"
            )
            no_data.setAlignment(Qt.AlignCenter)
            self.compare_result_layout.addWidget(no_data)
            return

        a1 = result['subject1']
        a2 = result['subject2']

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
    # تب نمای کلی
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

        info = QLabel("📊 مقایسه آماری همه موضوعات با یکدیگر")
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

        # نمودار توزیع
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
            n_lbl.setMinimumWidth(220)
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

            info_txt = "{:,}".format(item['total']) + \
                       " | " + format_followers(item['total_followers'])
            info = QLabel(info_txt)
            info.setStyleSheet(
                "color: " + c + "; font-weight: 900; "
                "font-size: 13px; padding: 3px 10px;"
            )
            info.setMinimumWidth(150)
            info.setAlignment(Qt.AlignCenter)
            row.addWidget(info)

            chart_layout.addWidget(row_widget)

        self.overview_layout.addWidget(chart_card)
        self.overview_layout.addStretch()

    # ═══════════════════════════════════════════════
    # صفحه لیست
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

        # تب بارگذاری مجدد + ادغام
        reload_tab = QWidget()
        reload_layout = QVBoxLayout(reload_tab)
        reload_layout.setContentsMargins(20, 20, 20, 20)
        reload_layout.setSpacing(15)

        # ═══ گروه ۱: بارگذاری از صفر ═══
        fresh_group = QGroupBox("🗑️ بارگذاری از صفر (پاک و شروع تازه)")
        fresh_layout = QVBoxLayout(fresh_group)
        fresh_layout.setSpacing(10)
        fresh_layout.setContentsMargins(15, 20, 15, 15)

        warn_fresh = QLabel(
            "⚠️  توجه: تمام داده‌های فعلی حذف و با داده‌های جدید "
            "جایگزین می‌شود.\n(بک‌آپ خودکار قبل از عملیات گرفته می‌شود)"
        )
        warn_fresh.setStyleSheet(
            "color: #F59E0B; padding: 12px; font-size: 12px; "
            "font-weight: 600; background-color: #78350F; border-radius: 8px;"
        )
        warn_fresh.setWordWrap(True)
        fresh_layout.addWidget(warn_fresh)

        reload_btn = QPushButton("📂  انتخاب و بارگذاری کامل فایل اکسل")
        reload_btn.setObjectName("dangerButton")
        reload_btn.setMinimumHeight(46)
        reload_btn.setStyleSheet("font-size: 14px;")
        reload_btn.clicked.connect(self.reload_excel_from_settings)
        fresh_layout.addWidget(reload_btn)

        reload_layout.addWidget(fresh_group)

        # ═══ گروه ۲: ادغام و بروزرسانی ═══
        merge_group = QGroupBox(
            "🔄 بروزرسانی و ادغام دیتاست جدید (بدون حذف داده‌های موجود)"
        )
        merge_layout = QVBoxLayout(merge_group)
        merge_layout.setSpacing(10)
        merge_layout.setContentsMargins(15, 20, 15, 15)

        info_merge = QLabel(
            "✅ داده‌های فعلی حفظ می‌شوند\n"
            "✅ کاربران جدید اضافه می‌شوند\n"
            "✅ کاربران موجود بروزرسانی می‌شوند\n"
            "✅ موضوع، تاریخ و سال ثبت به صورت تجمیعی اضافه می‌شوند"
        )
        info_merge.setStyleSheet(
            "color: #10B981; padding: 12px; font-size: 12px; "
            "font-weight: 600; background-color: #064E3B; border-radius: 8px;"
        )
        info_merge.setWordWrap(True)
        merge_layout.addWidget(info_merge)

        # مرحله ۱: انتخاب فایل
        step1_lbl = QLabel("📌 مرحله ۱: انتخاب فایل اکسل جدید")
        step1_lbl.setStyleSheet(
            "color: #60A5FA; font-size: 13px; font-weight: 700; "
            "padding: 8px 0;"
        )
        merge_layout.addWidget(step1_lbl)

        self.merge_file_path = None

        self.select_merge_btn = QPushButton("📂  انتخاب فایل اکسل جدید")
        self.select_merge_btn.setObjectName("primaryButton")
        self.select_merge_btn.setMinimumHeight(44)
        self.select_merge_btn.setStyleSheet("font-size: 13px;")
        self.select_merge_btn.clicked.connect(self.select_merge_file)
        merge_layout.addWidget(self.select_merge_btn)

        # نمایش نام فایل انتخاب شده
        self.merge_file_label = QLabel("هیچ فایلی انتخاب نشده است")
        self.merge_file_label.setStyleSheet(
            "color: #94A3B8; font-size: 12px; font-style: italic; "
            "padding: 8px; background-color: #1E293B; "
            "border-radius: 6px;"
        )
        self.merge_file_label.setWordWrap(True)
        merge_layout.addWidget(self.merge_file_label)

        # مرحله ۲: ادغام
        step2_lbl = QLabel("📌 مرحله ۲: ادغام و بروزرسانی")
        step2_lbl.setStyleSheet(
            "color: #60A5FA; font-size: 13px; font-weight: 700; "
            "padding: 8px 0;"
        )
        merge_layout.addWidget(step2_lbl)

        self.merge_btn = QPushButton("🔄  ادغام و بروزرسانی دیتابیس")
        self.merge_btn.setObjectName("successButton")
        self.merge_btn.setMinimumHeight(48)
        self.merge_btn.setStyleSheet("font-size: 14px;")
        self.merge_btn.setEnabled(False)  # پیش‌فرض غیرفعال
        self.merge_btn.clicked.connect(self.perform_merge)
        merge_layout.addWidget(self.merge_btn)

        reload_layout.addWidget(merge_group)
        reload_layout.addStretch()

        tabs.addTab(reload_tab, "📂  مدیریت دیتاست")

        # تب بک‌آپ
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
                    "; color:white; padding:4px 10px; border-radius:10px; "
                    "margin:2px; display:inline-block; font-weight:600; "
                    "font-size:11px;'>● " + s + "</span> "
                )

        about_text = QLabel(
            "<div style='line-height: 1.8;'>"
            "<h1 style='color: #60A5FA;'>🛡️ " + APP_NAME + "</h1>"
            "<p style='font-size:15px;'><b>نسخه " + APP_VERSION + "</b></p>"
            "<hr style='border-color:#334155;'>"
            "<h3 style='color:#10B981;'>✨ ویژگی‌های نسخه 10.0:</h3>"
            "<ul style='font-size:13px;'>"
            "<li>✅ تشخیص هوشمند رکوردهای تکراری</li>"
            "<li>✅ تکمیل هوشمند نام‌ها از دیتابیس</li>"
            "<li>✅ تقویم شمسی داخلی</li>"
            "<li>✅ اعتبارسنجی کد ملی</li>"
            "<li>✅ استخراج خودکار سال از تاریخ</li>"
            "<li>✅ Validator های تخصصی برای هر فیلد</li>"
            "<li>✅ وضعیت اجتماعی-اقتصادی</li>"
            "<li>✅ تحلیل هوشمند موضوعات</li>"
            "<li>✅ بک‌آپ خودکار</li>"
            "</ul>"
            "<hr style='border-color:#334155;'>"
            "<h3 style='color:#F59E0B;'>📂 موضوعات:</h3>"
            "<div style='padding: 8px;'>" + subjects_html + "</div>"
            "<hr style='border-color:#334155;'>"
            "<h3 style='color:#EC4899;'>🏠 وضعیت‌های اجتماعی-اقتصادی:</h3>"
            "<ul style='font-size:13px;'>"
            "<li><b>فرزند طلاق</b>، <b>بدسرپرست</b>، "
            "<b>طلاق</b>، <b>فوت همسر</b></li>"
            "<li>وضعیت اقتصادی: <b>ضعیف / متوسط / مناسب</b></li>"
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
                QMessageBox.warning(self, "خطا", "نتوانستم بک‌آپ بگیرم")
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

    # ═══════════════════════════════════════════════
    # 🔄 توابع ادغام دیتاست
    # ═══════════════════════════════════════════════
    def select_merge_file(self):
        """انتخاب فایل اکسل برای ادغام"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل اکسل جدید برای ادغام", "",
            "Excel Files (*.xlsx *.xls)"
        )

        if not file_path:
            return

        self.merge_file_path = file_path
        file_name = os.path.basename(file_path)

        self.merge_file_label.setText(
            "✅ فایل انتخاب شده:\n📄 " + file_name
        )
        self.merge_file_label.setStyleSheet(
            "color: #10B981; font-size: 12px; font-weight: 700; "
            "padding: 10px; background-color: #064E3B; "
            "border-radius: 6px;"
        )

        # فعال کردن دکمه ادغام
        self.merge_btn.setEnabled(True)
        self.merge_btn.setText("🔄  ادغام و بروزرسانی دیتابیس (آماده)")

    def perform_merge(self):
        """اجرای عملیات ادغام"""
        if not self.merge_file_path:
            QMessageBox.warning(
                self, "خطا", "ابتدا فایل اکسل را انتخاب کنید"
            )
            return

        # تأیید نهایی
        reply = QMessageBox.question(
            self,
            "تأیید ادغام",
            "آیا مطمئن هستید که می‌خواهید این فایل با دیتابیس ادغام شود؟\n\n"
            "📄 فایل: " + os.path.basename(self.merge_file_path) + "\n\n"
            "✅ داده‌های فعلی حفظ می‌شوند\n"
            "✅ داده‌های جدید اضافه می‌شوند\n"
            "✅ داده‌های تکراری بروزرسانی می‌شوند",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # دیالوگ لودینگ
        loading = QDialog(self)
        loading.setWindowTitle("در حال ادغام...")
        loading.setLayoutDirection(Qt.RightToLeft)
        loading.setFixedSize(400, 170)
        loading.setWindowFlags(
            Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
        )
        loading.setStyleSheet("""
            QDialog {
                background-color: #1E293B;
                border: 2px solid #10B981;
                border-radius: 15px;
            }
        """)

        ll = QVBoxLayout(loading)
        ll.setContentsMargins(30, 30, 30, 30)
        ll.setSpacing(15)

        lbl = QLabel("🔄  در حال ادغام دیتاست...")
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
                background-color: #10B981;
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
            # گرفتن تعداد قبلی
            old_stats = self.db.get_stats()
            old_total = old_stats['total']

            # اجرای ادغام
            merge_stats = self.db.merge_excel(self.merge_file_path)

            # گرفتن تعداد جدید
            new_stats = self.db.get_stats()
            new_total = new_stats['total']

            loading.close()
            loading.deleteLater()

            # نمایش گزارش
            self.show_merge_report(
                merge_stats, old_total, new_total
            )

            # ریست کردن UI
            self.merge_file_path = None
            self.merge_file_label.setText("هیچ فایلی انتخاب نشده است")
            self.merge_file_label.setStyleSheet(
                "color: #94A3B8; font-size: 12px; font-style: italic; "
                "padding: 8px; background-color: #1E293B; "
                "border-radius: 6px;"
            )
            self.merge_btn.setEnabled(False)
            self.merge_btn.setText("🔄  ادغام و بروزرسانی دیتابیس")

            # بروزرسانی داشبورد
            self.refresh_all_completers()
            self.show_dashboard()

        except Exception as e:
            loading.close()
            loading.deleteLater()
            QMessageBox.critical(
                self, "خطا",
                "❌ خطا در ادغام:\n" + str(e)
            )

    def show_merge_report(self, stats, old_total, new_total):
        """نمایش گزارش ادغام"""
        dialog = QDialog(self)
        dialog.setWindowTitle("گزارش ادغام")
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setMinimumSize(500, 480)
        dialog.setStyleSheet("QDialog { background-color: #0F172A; }")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # هدر موفقیت
        success_frame = QFrame()
        success_frame.setStyleSheet(
            "background-color: #10B981; border-radius: 12px; padding: 15px;"
        )
        sf_layout = QVBoxLayout(success_frame)

        success_icon = QLabel("✅")
        success_icon.setStyleSheet(
            "font-size: 48px; background-color: transparent;"
        )
        success_icon.setAlignment(Qt.AlignCenter)
        sf_layout.addWidget(success_icon)

        success_title = QLabel("ادغام با موفقیت انجام شد!")
        success_title.setStyleSheet(
            "font-size: 18px; font-weight: 900; color: white; "
            "background-color: transparent;"
        )
        success_title.setAlignment(Qt.AlignCenter)
        sf_layout.addWidget(success_title)

        layout.addWidget(success_frame)

        # کارت‌های آمار
        stats_data = [
            ("📄", "{:,}".format(stats['total_rows']),
             "کل رکوردهای فایل اکسل", "#60A5FA"),
            ("🆕", "{:,}".format(stats['new_users']),
             "کاربران جدید اضافه شد", "#10B981"),
            ("🔄", "{:,}".format(stats['updated_users']),
             "کاربران بروزرسانی شد", "#F59E0B"),
            ("⚠️", "{:,}".format(stats['skipped']),
             "رکوردهای رد شده (بدون ایدی)", "#94A3B8"),
        ]

        for icon, value, label, color in stats_data:
            card = QFrame()
            card.setStyleSheet(
                "background-color: #1E293B; border: 1px solid #334155; "
                "border-radius: 10px; padding: 12px;"
            )
            cl = QHBoxLayout(card)
            cl.setContentsMargins(15, 8, 15, 8)
            cl.setSpacing(15)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(
                "font-size: 32px; background-color: transparent;"
            )
            cl.addWidget(icon_lbl)

            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)

            label_lbl = QLabel(label)
            label_lbl.setStyleSheet(
                "color: #94A3B8; font-size: 12px; font-weight: 600;"
            )
            info_layout.addWidget(label_lbl)

            value_lbl = QLabel(value)
            value_lbl.setStyleSheet(
                "font-size: 22px; font-weight: 900; color: " + color + ";"
            )
            info_layout.addWidget(value_lbl)

            cl.addLayout(info_layout, 1)
            layout.addWidget(card)

        # جداکننده
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #334155;")
        sep.setMaximumHeight(2)
        layout.addWidget(sep)

        # آمار کلی
        total_frame = QFrame()
        total_frame.setStyleSheet(
            "background-color: #1E3A8A; border-radius: 10px; padding: 15px;"
        )
        tl = QVBoxLayout(total_frame)
        tl.setSpacing(8)

        row1 = QHBoxLayout()
        row1_lbl = QLabel("📊 قبل از ادغام:")
        row1_lbl.setStyleSheet(
            "color: #93C5FD; font-size: 13px; font-weight: 700; "
            "background-color: transparent;"
        )
        row1.addWidget(row1_lbl)

        row1_val = QLabel("{:,}".format(old_total) + " رکورد")
        row1_val.setStyleSheet(
            "color: white; font-size: 15px; font-weight: 900; "
            "background-color: transparent;"
        )
        row1_val.setAlignment(Qt.AlignLeft)
        row1.addWidget(row1_val, 1)
        tl.addLayout(row1)

        row2 = QHBoxLayout()
        row2_lbl = QLabel("📈 بعد از ادغام:")
        row2_lbl.setStyleSheet(
            "color: #93C5FD; font-size: 13px; font-weight: 700; "
            "background-color: transparent;"
        )
        row2.addWidget(row2_lbl)

        row2_val = QLabel("{:,}".format(new_total) + " رکورد")
        row2_val.setStyleSheet(
            "color: #10B981; font-size: 15px; font-weight: 900; "
            "background-color: transparent;"
        )
        row2_val.setAlignment(Qt.AlignLeft)
        row2.addWidget(row2_val, 1)
        tl.addLayout(row2)

        # افزایش
        increase = new_total - old_total
        row3 = QHBoxLayout()
        row3_lbl = QLabel("✨ افزایش:")
        row3_lbl.setStyleSheet(
            "color: #93C5FD; font-size: 13px; font-weight: 700; "
            "background-color: transparent;"
        )
        row3.addWidget(row3_lbl)

        row3_val = QLabel("+{:,}".format(increase) + " رکورد")
        row3_val.setStyleSheet(
            "color: #FCD34D; font-size: 15px; font-weight: 900; "
            "background-color: transparent;"
        )
        row3_val.setAlignment(Qt.AlignLeft)
        row3.addWidget(row3_val, 1)
        tl.addLayout(row3)

        layout.addWidget(total_frame)

        # دکمه تأیید
        ok_btn = QPushButton("✅ تأیید")
        ok_btn.setObjectName("successButton")
        ok_btn.setMinimumHeight(46)
        ok_btn.setStyleSheet("font-size: 15px;")
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        dialog.exec_()
    
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
            self.refresh_all_completers()
            self.show_dashboard()

        except Exception as e:
            loading.close()
            loading.deleteLater()
            QMessageBox.critical(
                self, "خطا",
                "❌ خطا در بارگذاری:\n" + str(e)
            )

    # ═══════════════════════════════════════════════
    # ناوبری
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
        self.setup_form_completers()

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

    # ─── مرحله ۱: Splash ───────────────────────────
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

    splash.close()
    splash.deleteLater()
    QApplication.processEvents()

    # ─── مرحله ۲: بررسی دیتابیس ────────────────────
    db = Database()

    # اگر دیتابیس آماده نیست، حتماً باید Excel بارگذاری بشه
    if not db.is_ready():
        setup_done = show_setup_dialog_standalone(app, db)

        # بعد از دیالوگ، دوباره چک کنیم
        if not db.is_ready():
            # کاربر بارگذاری نکرد
            QMessageBox.critical(
                None,
                "خطا در راه‌اندازی",
                "🔒 برنامه بدون بارگذاری فایل دیتابیس اجرا نمی‌شود.\n\n"
                "لطفاً برنامه را دوباره اجرا کرده و فایل دیتابیس اکسل را "
                "بارگذاری کنید."
            )
            sys.exit(0)

    # ─── مرحله ۳: پنجره اصلی ───────────────────────
    window = CyberWatchApp(db)
    window.show()
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
