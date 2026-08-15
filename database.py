"""
سامانه کاربران تحت نظارت در فضای مجازی
ماژول دیتابیس SQLite - نسخه 11.0
با تفکیک سال‌های ترکیبی و پاکسازی امن دیتابیس
"""
import os
import sys
import sqlite3
import shutil
import re
from datetime import datetime
import pandas as pd


def get_data_dir():
    """
    مسیر ذخیره داده‌ها:
    اگر برنامه از Setup نصب شده باشه، در ProgramData ذخیره میشه
    در غیر این صورت در User folder
    """
    # چک کنیم که آیا داخل نصب شده اجرا میشیم یا نه
    if getattr(sys, 'frozen', False):
        # داخل EXE هستیم
        try:
            program_data = os.environ.get('PROGRAMDATA',
                                           os.path.expanduser("~"))
            base = os.path.join(program_data, "SamanehNezarat")
        except Exception:
            base = os.path.join(
                os.path.expanduser("~"), "CyberWatchData"
            )
    else:
        # داخل Python هستیم (توسعه)
        base = os.path.join(
            os.path.expanduser("~"), "CyberWatchData"
        )

    return base


class Database:
    def __init__(self):
        self.base_dir = get_data_dir()
        os.makedirs(self.base_dir, exist_ok=True)

        self.db_path = os.path.join(self.base_dir, "users.db")
        self.backup_dir = os.path.join(self.base_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

        if os.path.exists(self.db_path):
            self._migrate_database()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def is_ready(self):
        """چک کنه که دیتابیس حاوی داده هست یا نه"""
        if not os.path.exists(self.db_path):
            return False
        try:
            conn = self._conn()
            cur = conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='users'"
            )
            if not cur.fetchone():
                conn.close()
                return False

            # چک کنه داده داشته باشه
            cur = conn.execute("SELECT COUNT(*) as c FROM users")
            count = cur.fetchone()['c']
            conn.close()
            return count > 0
        except Exception:
            return False

    def has_database(self):
        """چک کنه فایل دیتابیس وجود داره (حتی خالی)"""
        return os.path.exists(self.db_path)

    def reset_database(self):
        """پاکسازی کامل دیتابیس (برای شروع تازه)"""
        try:
            # بک‌آپ قبل از پاک کردن
            if os.path.exists(self.db_path):
                self.create_backup()

            # حذف فایل
            if os.path.exists(self.db_path):
                os.remove(self.db_path)

            # ساخت جدول جدید
            self.create_tables()
            return True
        except Exception as e:
            print("خطا در پاکسازی: " + str(e))
            return False

    # ═══════════════════════════════════════════════
    # ساخت جداول
    # ═══════════════════════════════════════════════
    def create_tables(self):
        conn = self._conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instagram_id TEXT NOT NULL,
                first_name TEXT DEFAULT '',
                last_name TEXT DEFAULT '',
                father_name TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                national_id TEXT DEFAULT '',
                subject TEXT DEFAULT '',
                tarnama_code TEXT DEFAULT '',
                reg_date TEXT DEFAULT '',
                address TEXT DEFAULT '',
                reg_year TEXT DEFAULT '',
                followers INTEGER DEFAULT 0,
                family_status TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        for idx_sql in [
            "CREATE INDEX IF NOT EXISTS idx_instagram ON users(instagram_id)",
            "CREATE INDEX IF NOT EXISTS idx_phone ON users(phone)",
            "CREATE INDEX IF NOT EXISTS idx_subject ON users(subject)",
            "CREATE INDEX IF NOT EXISTS idx_year ON users(reg_year)",
            "CREATE INDEX IF NOT EXISTS idx_followers ON users(followers)",
            "CREATE INDEX IF NOT EXISTS idx_national ON users(national_id)",
            "CREATE INDEX IF NOT EXISTS idx_first_name ON users(first_name)",
            "CREATE INDEX IF NOT EXISTS idx_last_name ON users(last_name)",
        ]:
            conn.execute(idx_sql)

        conn.commit()
        conn.close()

    def _migrate_database(self):
        try:
            conn = self._conn()
            cur = conn.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cur.fetchall()]

            if 'followers' not in columns:
                conn.execute(
                    "ALTER TABLE users ADD COLUMN "
                    "followers INTEGER DEFAULT 0"
                )
                print("✅ Migration: ستون followers اضافه شد")

            if 'family_status' not in columns:
                conn.execute(
                    "ALTER TABLE users ADD COLUMN "
                    "family_status TEXT DEFAULT ''"
                )
                print("✅ Migration: ستون family_status اضافه شد")

            for idx_sql in [
                "CREATE INDEX IF NOT EXISTS idx_followers ON users(followers)",
                "CREATE INDEX IF NOT EXISTS idx_national ON users(national_id)",
                "CREATE INDEX IF NOT EXISTS idx_first_name ON users(first_name)",
                "CREATE INDEX IF NOT EXISTS idx_last_name ON users(last_name)",
            ]:
                conn.execute(idx_sql)

            conn.commit()
            conn.close()
        except Exception as e:
            print("خطا در migration: " + str(e))

    # ═══════════════════════════════════════════════
    # بک‌آپ
    # ═══════════════════════════════════════════════
    def create_backup(self):
        try:
            if not os.path.exists(self.db_path):
                return None

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = "backup_" + timestamp + ".db"
            backup_path = os.path.join(self.backup_dir, backup_name)

            shutil.copy2(self.db_path, backup_path)
            self._cleanup_old_backups(keep=5)

            return backup_path
        except Exception as e:
            print("خطا در بک‌آپ: " + str(e))
            return None

    def _cleanup_old_backups(self, keep=5):
        try:
            files = [
                f for f in os.listdir(self.backup_dir)
                if f.startswith("backup_") and f.endswith(".db")
            ]
            files.sort(reverse=True)
            for old in files[keep:]:
                os.remove(os.path.join(self.backup_dir, old))
        except Exception:
            pass

    def get_backups_list(self):
        try:
            files = [
                f for f in os.listdir(self.backup_dir)
                if f.startswith("backup_") and f.endswith(".db")
            ]
            files.sort(reverse=True)
            return files
        except Exception:
            return []

    def restore_backup(self, backup_name):
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.db_path)
                return True
            return False
        except Exception:
            return False

    # ═══════════════════════════════════════════════
    # Import از Excel
    # ═══════════════════════════════════════════════
    def import_excel(self, file_path):
        if os.path.exists(self.db_path):
            self.create_backup()

        conn = self._conn()
        conn.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        conn.close()

        self.create_tables()

        df = pd.read_excel(file_path, dtype=str)
        df = df.fillna('')

        column_map = {
            'ایدی اینستاگرام': 'instagram_id',
            'آیدی اینستاگرام': 'instagram_id',
            'اینستاگرام': 'instagram_id',
            'instagram_id': 'instagram_id',
            'نام': 'first_name',
            'first_name': 'first_name',
            'نام خانوادگی': 'last_name',
            'last_name': 'last_name',
            'نام پدر': 'father_name',
            'father_name': 'father_name',
            'شماره تماس': 'phone',
            'موبایل': 'phone',
            'phone': 'phone',
            'شماره ملی': 'national_id',
            'کد ملی': 'national_id',
            'national_id': 'national_id',
            'موضوع': 'subject',
            'موضوع ثبت': 'subject',
            'subject': 'subject',
            'کد تارنما': 'tarnama_code',
            'تارنما': 'tarnama_code',
            'tarnama_code': 'tarnama_code',
            'تاریخ ثبت': 'reg_date',
            'تاریخ': 'reg_date',
            'reg_date': 'reg_date',
            'نشانی': 'address',
            'آدرس': 'address',
            'address': 'address',
            'سال ثبت': 'reg_year',
            'سال': 'reg_year',
            'reg_year': 'reg_year',
            'تعداد دنبال‌کننده': 'followers',
            'تعداد دنبال کننده': 'followers',
            'فالوور': 'followers',
            'دنبال‌کننده': 'followers',
            'followers': 'followers',
            'وضعیت خانواده': 'family_status',
            'وضعیت اجتماعی': 'family_status',
            'family_status': 'family_status',
        }

        detected_columns = {}
        for col in df.columns:
            col_clean = str(col).strip()
            if col_clean in column_map:
                detected_columns[col] = column_map[col_clean]

        conn = self._conn()
        count = 0

        for _, row in df.iterrows():
            data = {
                'instagram_id': '',
                'first_name': '',
                'last_name': '',
                'father_name': '',
                'phone': '',
                'national_id': '',
                'subject': '',
                'tarnama_code': '',
                'reg_date': '',
                'address': '',
                'reg_year': '',
                'followers': 0,
                'family_status': '',
            }

            for excel_col, db_col in detected_columns.items():
                value = str(row[excel_col]).strip()
                if value and value.lower() != 'nan':
                    if db_col == 'followers':
                        try:
                            clean_val = value.replace(',', '').replace(' ', '')
                            data[db_col] = int(float(clean_val))
                        except Exception:
                            data[db_col] = 0
                    else:
                        data[db_col] = value

            if not data['reg_year'] and data['reg_date']:
                data['reg_year'] = self._extract_year(data['reg_date'])

            if data['instagram_id']:
                conn.execute("""
                    INSERT INTO users (
                        instagram_id, first_name, last_name, father_name,
                        phone, national_id, subject, tarnama_code,
                        reg_date, address, reg_year, followers, family_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['instagram_id'], data['first_name'],
                    data['last_name'], data['father_name'],
                    data['phone'], data['national_id'],
                    data['subject'], data['tarnama_code'],
                    data['reg_date'], data['address'],
                    data['reg_year'], data['followers'],
                    data['family_status']
                ))
                count += 1

        conn.commit()
        conn.close()
        return count

    def _extract_year(self, date_str):
        """استخراج سال از تاریخ"""
        match = re.match(r'^(\d{4})', date_str.strip())
        if match:
            return match.group(1)
        return ''

    # ═══════════════════════════════════════════════
    # 🔄 ادغام دیتاست جدید (Merge)
    # ═══════════════════════════════════════════════
    def merge_excel(self, file_path):
        """
        ادغام فایل اکسل جدید با دیتابیس موجود
        بدون پاک کردن داده‌های قبلی
        
        منطق:
        - اگر ایدی موجود بود → بروزرسانی
        - اگر ایدی جدید بود → اضافه
        - فیلدهای تجمیعی: موضوع، تاریخ ثبت، سال ثبت
        """
        # بک‌آپ قبل از ادغام
        if os.path.exists(self.db_path):
            self.create_backup()

        # خواندن اکسل
        df = pd.read_excel(file_path, dtype=str)
        df = df.fillna('')

        column_map = {
            'ایدی اینستاگرام': 'instagram_id',
            'آیدی اینستاگرام': 'instagram_id',
            'اینستاگرام': 'instagram_id',
            'instagram_id': 'instagram_id',
            'نام': 'first_name',
            'first_name': 'first_name',
            'نام خانوادگی': 'last_name',
            'last_name': 'last_name',
            'نام پدر': 'father_name',
            'father_name': 'father_name',
            'شماره تماس': 'phone',
            'موبایل': 'phone',
            'phone': 'phone',
            'شماره ملی': 'national_id',
            'کد ملی': 'national_id',
            'national_id': 'national_id',
            'موضوع': 'subject',
            'موضوع ثبت': 'subject',
            'subject': 'subject',
            'کد تارنما': 'tarnama_code',
            'تارنما': 'tarnama_code',
            'tarnama_code': 'tarnama_code',
            'تاریخ ثبت': 'reg_date',
            'تاریخ': 'reg_date',
            'reg_date': 'reg_date',
            'نشانی': 'address',
            'آدرس': 'address',
            'address': 'address',
            'سال ثبت': 'reg_year',
            'سال': 'reg_year',
            'reg_year': 'reg_year',
            'تعداد دنبال‌کننده': 'followers',
            'تعداد دنبال کننده': 'followers',
            'فالوور': 'followers',
            'دنبال‌کننده': 'followers',
            'followers': 'followers',
            'وضعیت خانواده': 'family_status',
            'وضعیت اجتماعی': 'family_status',
            'family_status': 'family_status',
        }

        detected_columns = {}
        for col in df.columns:
            col_clean = str(col).strip()
            if col_clean in column_map:
                detected_columns[col] = column_map[col_clean]

        # آمار عملیات
        stats = {
            'total_rows': len(df),
            'new_users': 0,
            'updated_users': 0,
            'skipped': 0,
        }

        conn = self._conn()

        for _, row in df.iterrows():
            new_data = {
                'instagram_id': '',
                'first_name': '',
                'last_name': '',
                'father_name': '',
                'phone': '',
                'national_id': '',
                'subject': '',
                'tarnama_code': '',
                'reg_date': '',
                'address': '',
                'reg_year': '',
                'followers': 0,
                'family_status': '',
            }

            for excel_col, db_col in detected_columns.items():
                value = str(row[excel_col]).strip()
                if value and value.lower() != 'nan':
                    if db_col == 'followers':
                        try:
                            clean_val = value.replace(',', '').replace(' ', '')
                            new_data[db_col] = int(float(clean_val))
                        except Exception:
                            new_data[db_col] = 0
                    else:
                        new_data[db_col] = value

            # اگر ایدی نداشت، رد کن
            if not new_data['instagram_id']:
                stats['skipped'] += 1
                continue

            # استخراج سال از تاریخ
            if not new_data['reg_year'] and new_data['reg_date']:
                new_data['reg_year'] = self._extract_year(new_data['reg_date'])

            # چک کن آیا کاربر موجود هست
            existing = conn.execute(
                "SELECT * FROM users WHERE LOWER(instagram_id) = LOWER(?)",
                (new_data['instagram_id'],)
            ).fetchone()

            if existing:
                # 🔄 کاربر موجود → بروزرسانی
                existing_dict = dict(existing)
                merged = self._merge_user(existing_dict, new_data)

                conn.execute("""
                    UPDATE users SET
                        first_name=?, last_name=?, father_name=?,
                        phone=?, national_id=?, subject=?,
                        tarnama_code=?, reg_date=?, address=?,
                        reg_year=?, followers=?, family_status=?
                    WHERE id=?
                """, (
                    merged['first_name'],
                    merged['last_name'],
                    merged['father_name'],
                    merged['phone'],
                    merged['national_id'],
                    merged['subject'],
                    merged['tarnama_code'],
                    merged['reg_date'],
                    merged['address'],
                    merged['reg_year'],
                    merged['followers'],
                    merged['family_status'],
                    existing_dict['id']
                ))
                stats['updated_users'] += 1
            else:
                # 🆕 کاربر جدید → اضافه
                conn.execute("""
                    INSERT INTO users (
                        instagram_id, first_name, last_name, father_name,
                        phone, national_id, subject, tarnama_code,
                        reg_date, address, reg_year, followers, family_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    new_data['instagram_id'],
                    new_data['first_name'],
                    new_data['last_name'],
                    new_data['father_name'],
                    new_data['phone'],
                    new_data['national_id'],
                    new_data['subject'],
                    new_data['tarnama_code'],
                    new_data['reg_date'],
                    new_data['address'],
                    new_data['reg_year'],
                    new_data['followers'],
                    new_data['family_status']
                ))
                stats['new_users'] += 1

        conn.commit()
        conn.close()

        return stats

    def _merge_user(self, existing, new_data):
        """
        ادغام هوشمند اطلاعات کاربر
        - فیلدهای معمولی: اگه جدید پر بود → جایگزین کن
                        اگه جدید خالی بود → قدیم حفظ کن
        - فیلدهای تجمیعی: با | ادغام کن
        """
        merged = existing.copy()

        # فیلدهای بروزرسانی شونده (Update)
        update_fields = [
            'first_name', 'last_name', 'father_name',
            'phone', 'national_id', 'tarnama_code',
            'address', 'family_status'
        ]

        for field in update_fields:
            new_val = str(new_data.get(field, '')).strip()
            if new_val:  # فقط اگه مقدار جدید داشتیم
                merged[field] = new_val
            # در غیر این صورت، مقدار قدیمی حفظ میشه

        # فالوور: اگه عدد جدید بزرگتر بود، جایگزین کن
        new_followers = int(new_data.get('followers', 0) or 0)
        if new_followers > 0:
            merged['followers'] = new_followers

        # فیلدهای تجمیعی (Append with |)
        append_fields = ['subject', 'reg_date', 'reg_year']

        for field in append_fields:
            new_val = str(new_data.get(field, '')).strip()
            if new_val:
                existing_val = str(merged.get(field, '')).strip()
                if existing_val:
                    # چک کن آیا مقدار جدید در قدیم موجود هست
                    existing_parts = [
                        p.strip() for p in existing_val.split('|')
                    ]
                    if new_val not in existing_parts:
                        # اضافه کن
                        merged[field] = existing_val + ' | ' + new_val
                    # اگه تکراری بود، دست نزن
                else:
                    merged[field] = new_val

        return merged
        
    
    def _split_years(self, year_str):
        """
        تفکیک سال‌های ترکیبی
        مثال: "1403 | 1404" → ["1403", "1404"]
        """
        if not year_str:
            return []
        parts = re.split(r'[|,،/\s]+', year_str)
        return [p.strip() for p in parts if p.strip() and p.strip().isdigit()]

    def export_excel(self, file_path):
        conn = self._conn()
        df = pd.read_sql_query(
            "SELECT * FROM users ORDER BY id DESC", conn
        )
        conn.close()

        df = df.rename(columns={
            'id': 'شناسه',
            'instagram_id': 'ایدی اینستاگرام',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'father_name': 'نام پدر',
            'phone': 'شماره تماس',
            'national_id': 'شماره ملی',
            'subject': 'موضوع',
            'tarnama_code': 'کد تارنما',
            'reg_date': 'تاریخ ثبت',
            'address': 'نشانی',
            'reg_year': 'سال ثبت',
            'followers': 'تعداد دنبال‌کننده',
            'family_status': 'وضعیت خانواده',
            'created_at': 'تاریخ ایجاد',
        })

        df.to_excel(file_path, index=False)
        return len(df)

    # ═══════════════════════════════════════════════
    # CRUD
    # ═══════════════════════════════════════════════
    def add_user(self, data):
        reg_year = data.get('reg_year', '')
        if not reg_year and data.get('reg_date'):
            reg_year = self._extract_year(data['reg_date'])

        conn = self._conn()
        conn.execute("""
            INSERT INTO users (
                instagram_id, first_name, last_name, father_name,
                phone, national_id, subject, tarnama_code,
                reg_date, address, reg_year, followers, family_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('instagram_id', ''),
            data.get('first_name', ''),
            data.get('last_name', ''),
            data.get('father_name', ''),
            data.get('phone', ''),
            data.get('national_id', ''),
            data.get('subject', ''),
            data.get('tarnama_code', ''),
            data.get('reg_date', ''),
            data.get('address', ''),
            reg_year,
            int(data.get('followers', 0) or 0),
            data.get('family_status', ''),
        ))
        conn.commit()
        conn.close()

    def update_user(self, user_id, data):
        reg_year = data.get('reg_year', '')
        if not reg_year and data.get('reg_date'):
            reg_year = self._extract_year(data['reg_date'])

        conn = self._conn()
        conn.execute("""
            UPDATE users SET
                instagram_id=?, first_name=?, last_name=?,
                father_name=?, phone=?, national_id=?,
                subject=?, tarnama_code=?, reg_date=?,
                address=?, reg_year=?, followers=?, family_status=?
            WHERE id=?
        """, (
            data.get('instagram_id', ''),
            data.get('first_name', ''),
            data.get('last_name', ''),
            data.get('father_name', ''),
            data.get('phone', ''),
            data.get('national_id', ''),
            data.get('subject', ''),
            data.get('tarnama_code', ''),
            data.get('reg_date', ''),
            data.get('address', ''),
            reg_year,
            int(data.get('followers', 0) or 0),
            data.get('family_status', ''),
            user_id
        ))
        conn.commit()
        conn.close()

    def delete_user(self, user_id):
        conn = self._conn()
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

    def get_by_id(self, user_id):
        conn = self._conn()
        row = conn.execute(
            "SELECT * FROM users WHERE id=?", (user_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all(self, limit=1000):
        conn = self._conn()
        rows = conn.execute(
            "SELECT * FROM users ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ═══════════════════════════════════════════════
    # چک تکراری
    # ═══════════════════════════════════════════════
    def check_duplicate(self, national_id="", instagram_id="",
                        first_name="", last_name="", exclude_id=None):
        conn = self._conn()

        if national_id and national_id.strip():
            exclude_sql = ""
            params = [national_id.strip()]
            if exclude_id:
                exclude_sql = " AND id != ?"
                params.append(exclude_id)

            rows = conn.execute(
                "SELECT * FROM users WHERE national_id = ?" + exclude_sql,
                params
            ).fetchall()

            if rows:
                conn.close()
                return {
                    'has_duplicate': True,
                    'match_type': 'national_id',
                    'confidence': 'exact',
                    'message': 'کد ملی تکراری است',
                    'matches': [dict(r) for r in rows]
                }

        if instagram_id and instagram_id.strip():
            ig_clean = instagram_id.strip().lower().replace('@', '')

            exclude_sql = ""
            params = [ig_clean]
            if exclude_id:
                exclude_sql = " AND id != ?"
                params.append(exclude_id)

            rows = conn.execute(
                "SELECT * FROM users WHERE LOWER(instagram_id) = ?" +
                exclude_sql,
                params
            ).fetchall()

            if rows:
                conn.close()
                return {
                    'has_duplicate': True,
                    'match_type': 'instagram',
                    'confidence': 'exact',
                    'message': 'ایدی اینستاگرام تکراری است',
                    'matches': [dict(r) for r in rows]
                }

            similar = self._fuzzy_match_instagram(
                ig_clean, exclude_id, threshold=2
            )
            if similar:
                conn.close()
                return {
                    'has_duplicate': True,
                    'match_type': 'instagram',
                    'confidence': 'similar',
                    'message': 'ایدی اینستاگرام مشابه یافت شد',
                    'matches': similar
                }

        if first_name and last_name and first_name.strip() and last_name.strip():
            exclude_sql = ""
            params = [first_name.strip(), last_name.strip()]
            if exclude_id:
                exclude_sql = " AND id != ?"
                params.append(exclude_id)

            rows = conn.execute(
                "SELECT * FROM users WHERE first_name = ? AND last_name = ?" +
                exclude_sql,
                params
            ).fetchall()

            if rows:
                conn.close()
                return {
                    'has_duplicate': True,
                    'match_type': 'name',
                    'confidence': 'exact',
                    'message': 'نام و نام خانوادگی تکراری است',
                    'matches': [dict(r) for r in rows]
                }

        conn.close()
        return {
            'has_duplicate': False,
            'match_type': None,
            'confidence': None,
            'message': '',
            'matches': []
        }

    def _fuzzy_match_instagram(self, target, exclude_id=None, threshold=2):
        conn = self._conn()

        exclude_sql = ""
        params = []
        if exclude_id:
            exclude_sql = " WHERE id != ?"
            params.append(exclude_id)

        rows = conn.execute(
            "SELECT * FROM users" + exclude_sql,
            params
        ).fetchall()
        conn.close()

        matches = []
        target_lower = target.lower()

        for r in rows:
            ig = r['instagram_id'].lower().replace('@', '')
            if not ig or ig == target_lower:
                continue

            if abs(len(ig) - len(target_lower)) > threshold:
                continue

            distance = self._levenshtein(ig, target_lower)
            if 0 < distance <= threshold:
                match = dict(r)
                match['_distance'] = distance
                matches.append(match)

        matches.sort(key=lambda x: x['_distance'])
        return matches[:5]

    def _levenshtein(self, s1, s2):
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(
                    min(insertions, deletions, substitutions)
                )
            previous_row = current_row

        return previous_row[-1]

    # ═══════════════════════════════════════════════
    # Auto-Complete
    # ═══════════════════════════════════════════════
    def get_suggestions(self, field, partial_text="", limit=10):
        if field not in ['first_name', 'last_name', 'father_name',
                         'subject', 'address', 'instagram_id']:
            return []

        conn = self._conn()

        if partial_text:
            rows = conn.execute(
                "SELECT DISTINCT " + field + " FROM users WHERE " +
                field + " LIKE ? AND " + field + " != '' " +
                "ORDER BY " + field + " LIMIT ?",
                ("%" + partial_text + "%", limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT DISTINCT " + field + " FROM users WHERE " +
                field + " != '' ORDER BY " + field + " LIMIT ?",
                (limit,)
            ).fetchall()

        conn.close()
        return [r[field] for r in rows]

    def get_all_unique_values(self, field):
        if field not in ['first_name', 'last_name', 'father_name',
                         'subject', 'address', 'instagram_id']:
            return []

        conn = self._conn()
        rows = conn.execute(
            "SELECT DISTINCT " + field + " FROM users WHERE " +
            field + " != '' ORDER BY " + field
        ).fetchall()
        conn.close()
        return [r[field] for r in rows]

    # ═══════════════════════════════════════════════
    # جستجو
    # ═══════════════════════════════════════════════
    def search(self, query):
        if not query:
            return []
        conn = self._conn()
        q = "%" + query + "%"
        rows = conn.execute("""
            SELECT * FROM users WHERE
                instagram_id LIKE ? OR
                first_name LIKE ? OR
                last_name LIKE ? OR
                father_name LIKE ? OR
                phone LIKE ? OR
                national_id LIKE ? OR
                subject LIKE ? OR
                tarnama_code LIKE ? OR
                address LIKE ?
            ORDER BY id DESC LIMIT 500
        """, (q, q, q, q, q, q, q, q, q)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def advanced_search(self, filters):
        if not filters:
            return []

        field_map = {
            'نام': 'first_name',
            'نام خانوادگی': 'last_name',
            'ایدی اینستاگرام': 'instagram_id',
            'شماره تماس': 'phone',
            'شماره ملی': 'national_id',
            'نشانی': 'address',
            'نام پدر': 'father_name',
            'کد تارنما': 'tarnama_code',
            'موضوع ثبت': 'subject',
            'سال ثبت': 'reg_year',
        }

        conditions = []
        params = []

        for key, value in filters.items():
            db_field = field_map.get(key)
            if db_field and value:
                conditions.append(db_field + " LIKE ?")
                params.append("%" + value + "%")

        if not conditions:
            return []

        query = (
            "SELECT * FROM users WHERE " +
            " AND ".join(conditions) +
            " ORDER BY id DESC LIMIT 500"
        )

        conn = self._conn()
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ═══════════════════════════════════════════════
    # 🎯 آمار (با تفکیک سال‌های ترکیبی)
    # ═══════════════════════════════════════════════
    def get_stats(self):
        conn = self._conn()

        total = conn.execute(
            "SELECT COUNT(*) as c FROM users"
        ).fetchone()['c']

        # ═══ تفکیک سال‌های ترکیبی ═══
        # مثال: "1403 | 1404" باید به 1403 و 1404 جدا بشه
        # و هر کدوم یک عدد به شمارش اضافه بشه
        year_rows = conn.execute("""
            SELECT reg_year FROM users
            WHERE reg_year != ''
        """).fetchall()

        year_counts = {}
        for row in year_rows:
            years_in_row = self._split_years(row['reg_year'])
            for y in years_in_row:
                year_counts[y] = year_counts.get(y, 0) + 1

        # مرتب‌سازی نزولی (سال جدیدتر اول)
        years = sorted(
            year_counts.items(),
            key=lambda x: x[0],
            reverse=True
        )

        # فیلدهای پر شده
        filled = {}
        for field in ['phone', 'instagram_id', 'national_id',
                      'address', 'followers', 'family_status']:
            if field == 'followers':
                count = conn.execute(
                    "SELECT COUNT(*) as c FROM users WHERE followers > 0"
                ).fetchone()['c']
            else:
                count = conn.execute(
                    "SELECT COUNT(*) as c FROM users WHERE " +
                    field + " != ''"
                ).fetchone()['c']
            filled[field] = count

        conn.close()
        return {
            'total': total,
            'years': years,
            'filled': filled,
        }

    # ═══════════════════════════════════════════════
    # تحلیل هوشمند
    # ═══════════════════════════════════════════════
    def get_subject_analysis(self, subject):
        conn = self._conn()

        pattern = "%" + subject + "%"
        rows = conn.execute(
            "SELECT * FROM users WHERE subject LIKE ?",
            (pattern,)
        ).fetchall()

        matching = []
        for r in rows:
            parts = [s.strip() for s in r['subject'].split('|')]
            if subject in parts:
                matching.append(dict(r))

        if not matching:
            conn.close()
            return None

        followers_list = [
            r['followers'] for r in matching
            if r['followers'] and r['followers'] > 0
        ]

        total_followers = sum(followers_list)
        count_with_followers = len(followers_list)
        avg_followers = (
            total_followers // count_with_followers
            if count_with_followers > 0 else 0
        )
        max_followers = max(followers_list) if followers_list else 0
        min_followers = min(followers_list) if followers_list else 0

        median_followers = 0
        if followers_list:
            sorted_f = sorted(followers_list)
            n = len(sorted_f)
            if n % 2 == 0:
                median_followers = (sorted_f[n//2-1] + sorted_f[n//2]) // 2
            else:
                median_followers = sorted_f[n//2]

        categories = {
            'mega': 0, 'macro': 0, 'middle': 0, 'micro': 0, 'nano': 0,
        }
        for f in followers_list:
            if f > 1000000:
                categories['mega'] += 1
            elif f >= 100000:
                categories['macro'] += 1
            elif f >= 10000:
                categories['middle'] += 1
            elif f >= 1000:
                categories['micro'] += 1
            else:
                categories['nano'] += 1

        top_users = sorted(
            [r for r in matching if r['followers'] > 0],
            key=lambda x: x['followers'],
            reverse=True
        )[:10]

        # 🎯 توزیع سالانه با تفکیک ترکیبی
        year_dist = {}
        for r in matching:
            years_in_row = self._split_years(r['reg_year'])
            if years_in_row:
                for y in years_in_row:
                    year_dist[y] = year_dist.get(y, 0) + 1
            else:
                year_dist['نامشخص'] = year_dist.get('نامشخص', 0) + 1

        year_dist_list = sorted(
            year_dist.items(), key=lambda x: x[0], reverse=True
        )

        related = {}
        for r in matching:
            parts = [s.strip() for s in r['subject'].split('|')]
            for p in parts:
                if p and p != subject:
                    related[p] = related.get(p, 0) + 1
        related_list = sorted(
            related.items(), key=lambda x: x[1], reverse=True
        )[:10]

        family_stats = {}
        for r in matching:
            fs = r.get('family_status', '')
            if fs:
                parts = [s.strip() for s in fs.split('|')]
                for p in parts:
                    if p:
                        family_stats[p] = family_stats.get(p, 0) + 1
        family_stats_list = sorted(
            family_stats.items(), key=lambda x: x[1], reverse=True
        )

        quality = {
            'has_phone': sum(1 for r in matching if r['phone']),
            'has_national_id': sum(1 for r in matching if r['national_id']),
            'has_address': sum(1 for r in matching if r['address']),
            'has_followers': count_with_followers,
            'has_family_status': sum(
                1 for r in matching if r.get('family_status', '')
            ),
        }

        conn.close()

        return {
            'subject': subject,
            'total': len(matching),
            'total_followers': total_followers,
            'avg_followers': avg_followers,
            'max_followers': max_followers,
            'min_followers': min_followers,
            'median_followers': median_followers,
            'count_with_followers': count_with_followers,
            'categories': categories,
            'top_users': top_users,
            'year_distribution': year_dist_list,
            'related_subjects': related_list,
            'family_stats': family_stats_list,
            'quality': quality,
        }

    def get_all_subjects_comparison(self, subjects_list):
        results = []
        for subj in subjects_list:
            if not subj:
                continue
            analysis = self.get_subject_analysis(subj)
            if analysis and analysis['total'] > 0:
                results.append({
                    'subject': subj,
                    'total': analysis['total'],
                    'total_followers': analysis['total_followers'],
                    'avg_followers': analysis['avg_followers'],
                    'max_followers': analysis['max_followers'],
                    'count_with_followers': analysis['count_with_followers'],
                })

        results.sort(key=lambda x: x['total'], reverse=True)
        return results

    def compare_two_subjects(self, subject1, subject2):
        a1 = self.get_subject_analysis(subject1)
        a2 = self.get_subject_analysis(subject2)

        if not a1 or not a2:
            return None

        conn = self._conn()
        pattern1 = "%" + subject1 + "%"
        pattern2 = "%" + subject2 + "%"
        rows = conn.execute("""
            SELECT * FROM users
            WHERE subject LIKE ? AND subject LIKE ?
        """, (pattern1, pattern2)).fetchall()

        both = []
        for r in rows:
            parts = [s.strip() for s in r['subject'].split('|')]
            if subject1 in parts and subject2 in parts:
                both.append(dict(r))

        conn.close()

        return {
            'subject1': a1,
            'subject2': a2,
            'both_count': len(both),
            'both_users': both[:10],
        }
