"""
سامانه کاربران تحت نظارت در فضای مجازی
ماژول دیتابیس SQLite
نسخه 9.0 - با پشتیبانی از فالوور و تحلیل هوشمند
"""
import os
import sqlite3
import shutil
from datetime import datetime
import pandas as pd


class Database:
    def __init__(self):
        # مسیر دیتابیس
        self.base_dir = os.path.join(
            os.path.expanduser("~"), "CyberWatchData"
        )
        os.makedirs(self.base_dir, exist_ok=True)

        self.db_path = os.path.join(self.base_dir, "users.db")
        self.backup_dir = os.path.join(self.base_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

        # اگر دیتابیس هست، migration انجام بده
        if os.path.exists(self.db_path):
            self._migrate_database()

    # ═══════════════════════════════════════════════
    # اتصال به دیتابیس
    # ═══════════════════════════════════════════════
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def is_ready(self):
        """چک میکنه دیتابیس و جدول users وجود داره یا نه"""
        if not os.path.exists(self.db_path):
            return False
        try:
            conn = self._conn()
            cur = conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='users'"
            )
            result = cur.fetchone() is not None
            conn.close()
            return result
        except Exception:
            return False

    # ═══════════════════════════════════════════════
    # ساخت جداول و Index ها
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Index ها برای سرعت بالا
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_instagram "
            "ON users(instagram_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_phone ON users(phone)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_subject ON users(subject)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_year ON users(reg_year)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_followers "
            "ON users(followers)"
        )

        conn.commit()
        conn.close()

    # ═══════════════════════════════════════════════
    # Migration - اضافه کردن ستون followers به دیتابیس قدیم
    # ═══════════════════════════════════════════════
    def _migrate_database(self):
        """اضافه کردن ستون followers اگر نداشته باشه"""
        try:
            conn = self._conn()
            cur = conn.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cur.fetchall()]

            if 'followers' not in columns:
                conn.execute(
                    "ALTER TABLE users ADD COLUMN "
                    "followers INTEGER DEFAULT 0"
                )
                conn.commit()
                print("✅ Migration: ستون followers اضافه شد")

            # ساخت index ها اگر نیستن
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_followers "
                "ON users(followers)"
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print("خطا در migration: " + str(e))

    # ═══════════════════════════════════════════════
    # بک‌آپ خودکار
    # ═══════════════════════════════════════════════
    def create_backup(self):
        """گرفتن بک‌آپ از دیتابیس"""
        try:
            if not os.path.exists(self.db_path):
                return None

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = "backup_" + timestamp + ".db"
            backup_path = os.path.join(self.backup_dir, backup_name)

            shutil.copy2(self.db_path, backup_path)

            # نگهداری فقط ۵ بک‌آپ آخر
            self._cleanup_old_backups(keep=5)

            return backup_path
        except Exception as e:
            print("خطا در بک‌آپ: " + str(e))
            return None

    def _cleanup_old_backups(self, keep=5):
        """پاک کردن بک‌آپ‌های قدیمی"""
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
        """لیست بک‌آپ‌های موجود"""
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
        """بازیابی از بک‌آپ"""
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
        """بارگذاری از فایل اکسل"""
        # بک‌آپ قبل از تغییر
        if self.is_ready():
            self.create_backup()

        # پاک کردن جدول قبلی و ساخت جدید
        conn = self._conn()
        conn.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        conn.close()

        self.create_tables()

        # خواندن اکسل
        df = pd.read_excel(file_path, dtype=str)
        df = df.fillna('')

        # نگاشت ستون‌های اکسل به دیتابیس
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
        }

        # تشخیص ستون‌ها
        detected_columns = {}
        for col in df.columns:
            col_clean = str(col).strip()
            if col_clean in column_map:
                detected_columns[col] = column_map[col_clean]

        # درج داده‌ها
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
            }

            for excel_col, db_col in detected_columns.items():
                value = str(row[excel_col]).strip()
                if value and value.lower() != 'nan':
                    if db_col == 'followers':
                        # تبدیل به عدد
                        try:
                            # حذف کاما و کاراکترهای اضافی
                            clean_val = value.replace(',', '').replace(' ', '')
                            data[db_col] = int(float(clean_val))
                        except Exception:
                            data[db_col] = 0
                    else:
                        data[db_col] = value

            # فقط اگر instagram_id داشت ذخیره کن
            if data['instagram_id']:
                conn.execute("""
                    INSERT INTO users (
                        instagram_id, first_name, last_name, father_name,
                        phone, national_id, subject, tarnama_code,
                        reg_date, address, reg_year, followers
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data['instagram_id'], data['first_name'],
                    data['last_name'], data['father_name'],
                    data['phone'], data['national_id'],
                    data['subject'], data['tarnama_code'],
                    data['reg_date'], data['address'],
                    data['reg_year'], data['followers']
                ))
                count += 1

        conn.commit()
        conn.close()
        return count

    # ═══════════════════════════════════════════════
    # Export به Excel
    # ═══════════════════════════════════════════════
    def export_excel(self, file_path):
        """خروجی به اکسل"""
        conn = self._conn()
        df = pd.read_sql_query(
            "SELECT * FROM users ORDER BY id DESC", conn
        )
        conn.close()

        # نام‌های فارسی ستون‌ها
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
            'created_at': 'تاریخ ایجاد',
        })

        df.to_excel(file_path, index=False)
        return len(df)

    # ═══════════════════════════════════════════════
    # عملیات CRUD
    # ═══════════════════════════════════════════════
    def add_user(self, data):
        conn = self._conn()
        conn.execute("""
            INSERT INTO users (
                instagram_id, first_name, last_name, father_name,
                phone, national_id, subject, tarnama_code,
                reg_date, address, reg_year, followers
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            data.get('reg_year', ''),
            int(data.get('followers', 0) or 0),
        ))
        conn.commit()
        conn.close()

    def update_user(self, user_id, data):
        conn = self._conn()
        conn.execute("""
            UPDATE users SET
                instagram_id=?, first_name=?, last_name=?,
                father_name=?, phone=?, national_id=?,
                subject=?, tarnama_code=?, reg_date=?,
                address=?, reg_year=?, followers=?
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
            data.get('reg_year', ''),
            int(data.get('followers', 0) or 0),
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
    # آمار عمومی
    # ═══════════════════════════════════════════════
    def get_stats(self):
        conn = self._conn()

        total = conn.execute(
            "SELECT COUNT(*) as c FROM users"
        ).fetchone()['c']

        # آمار سال‌ها
        years_rows = conn.execute("""
            SELECT reg_year, COUNT(*) as c FROM users
            WHERE reg_year != ''
            GROUP BY reg_year ORDER BY reg_year DESC
        """).fetchall()
        years = [(r['reg_year'], r['c']) for r in years_rows]

        # فیلدهای پر شده
        filled = {}
        for field in ['phone', 'instagram_id', 'national_id',
                      'address', 'followers']:
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
    # 🔬 توابع تحلیلی جدید
    # ═══════════════════════════════════════════════
    def get_subject_analysis(self, subject):
        """تحلیل کامل یک موضوع خاص"""
        conn = self._conn()

        # همه رکوردهایی که این موضوع رو دارند (ترکیبی هم شامل)
        pattern = "%" + subject + "%"
        rows = conn.execute("""
            SELECT * FROM users
            WHERE subject LIKE ?
        """, (pattern,)).fetchall()

        # فیلتر دقیق: فقط کسانی که واقعاً این موضوع رو دارند
        matching = []
        for r in rows:
            parts = [s.strip() for s in r['subject'].split('|')]
            if subject in parts:
                matching.append(dict(r))

        if not matching:
            conn.close()
            return None

        # آمار فالوور
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

        # میانه
        median_followers = 0
        if followers_list:
            sorted_f = sorted(followers_list)
            n = len(sorted_f)
            if n % 2 == 0:
                median_followers = (sorted_f[n//2-1] + sorted_f[n//2]) // 2
            else:
                median_followers = sorted_f[n//2]

        # دسته‌بندی فالوور
        categories = {
            'mega': 0,      # > 1M
            'macro': 0,     # 100K - 1M
            'middle': 0,    # 10K - 100K
            'micro': 0,     # 1K - 10K
            'nano': 0,      # < 1K
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

        # Top 10
        top_users = sorted(
            [r for r in matching if r['followers'] > 0],
            key=lambda x: x['followers'],
            reverse=True
        )[:10]

        # توزیع سالانه
        year_dist = {}
        for r in matching:
            year = r['reg_year'] if r['reg_year'] else 'نامشخص'
            year_dist[year] = year_dist.get(year, 0) + 1
        year_dist_list = sorted(
            year_dist.items(), key=lambda x: x[0], reverse=True
        )

        # موضوعات مرتبط (چند موضوعه)
        related = {}
        for r in matching:
            parts = [s.strip() for s in r['subject'].split('|')]
            for p in parts:
                if p and p != subject:
                    related[p] = related.get(p, 0) + 1
        related_list = sorted(
            related.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # کیفیت اطلاعات
        quality = {
            'has_phone': sum(1 for r in matching if r['phone']),
            'has_national_id': sum(1 for r in matching if r['national_id']),
            'has_address': sum(1 for r in matching if r['address']),
            'has_followers': count_with_followers,
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
            'quality': quality,
        }

    def get_all_subjects_comparison(self, subjects_list):
        """مقایسه همه موضوعات با هم"""
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

        # مرتب بر اساس تعداد
        results.sort(key=lambda x: x['total'], reverse=True)
        return results

    def compare_two_subjects(self, subject1, subject2):
        """مقایسه دو موضوع"""
        a1 = self.get_subject_analysis(subject1)
        a2 = self.get_subject_analysis(subject2)

        if not a1 or not a2:
            return None

        # کسانی که هر دو موضوع رو دارند
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
