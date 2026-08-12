
"""CyberWatch Database Manager"""
import sqlite3
import os
import pandas as pd


def get_db_path():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "cyberwatch.db")


class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def is_ready(self):
        if not os.path.exists(self.db_path):
            return False
        try:
            c = self._conn()
            n = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            c.close()
            return n > 0
        except:
            return False

    def create_tables(self):
        c = self._conn()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                row_number    TEXT DEFAULT '',
                instagram_id  TEXT DEFAULT '',
                first_name    TEXT DEFAULT '',
                last_name     TEXT DEFAULT '',
                father_name   TEXT DEFAULT '',
                phone         TEXT DEFAULT '',
                national_id   TEXT DEFAULT '',
                subject       TEXT DEFAULT '',
                tarnama_code  TEXT DEFAULT '',
                reg_date      TEXT DEFAULT '',
                address       TEXT DEFAULT '',
                reg_year      TEXT DEFAULT '',
                created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at    TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for col in ['instagram_id','first_name','last_name',
                    'phone','national_id','subject','reg_year']:
            c.execute(f"CREATE INDEX IF NOT EXISTS idx_{col} ON users({col})")
        c.commit()
        c.close()

    def import_excel(self, excel_path):
        df = pd.read_excel(excel_path, dtype=str).fillna('')
        self.create_tables()
        c = self._conn()
        c.execute("DELETE FROM users")

        col_map = {
            'ردیف': 'row_number',
            'ایدی اینستاگرام': 'instagram_id',
            'نام': 'first_name',
            'نام خانوادگی': 'last_name',
            'نام پدر': 'father_name',
            'شماره تماس': 'phone',
            'شماره ملی': 'national_id',
            'موضوع ثبت': 'subject',
            'کد تارنما': 'tarnama_code',
            'تاریخ ثبت': 'reg_date',
            'نشانی منزل/ محل کار': 'address',
            'سال ثبت': 'reg_year',
        }

        for _, row in df.iterrows():
            vals = tuple(str(row.get(fa, '')) for fa in col_map.keys())
            c.execute(
                "INSERT INTO users ("
                + ",".join(col_map.values())
                + ") VALUES ("
                + ",".join(["?"] * len(col_map))
                + ")", vals
            )
        c.commit()
        total = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        c.close()
        return total

    def search(self, query, limit=300):
        if not query.strip():
            return self.get_all(limit)
        like = f"%{query.strip()}%"
        c = self._conn()
        rows = c.execute("""
            SELECT * FROM users WHERE
            instagram_id LIKE ? OR first_name LIKE ? OR
            last_name LIKE ? OR father_name LIKE ? OR
            phone LIKE ? OR national_id LIKE ? OR
            subject LIKE ? OR tarnama_code LIKE ? OR
            address LIKE ? OR row_number LIKE ? OR
            reg_year LIKE ?
            LIMIT ?
        """, (like,) * 11 + (limit,)).fetchall()
        c.close()
        return [dict(r) for r in rows]

    def advanced_search(self, filters, limit=300):
        field_map = {
            'نام': 'first_name',
            'نام خانوادگی': 'last_name',
            'ایدی اینستاگرام': 'instagram_id',
            'شماره تماس': 'phone',
            'شماره ملی': 'national_id',
            'موضوع ثبت': 'subject',
            'سال ثبت': 'reg_year',
            'نشانی': 'address',
            'نام پدر': 'father_name',
            'کد تارنما': 'tarnama_code',
        }
        conds, params = [], []
        for fa, val in filters.items():
            if val and val.strip():
                db_col = field_map.get(fa, fa)
                conds.append(f"{db_col} LIKE ?")
                params.append(f"%{val.strip()}%")
        if not conds:
            return self.get_all(limit)
        c = self._conn()
        sql = "SELECT * FROM users WHERE " + " AND ".join(conds) + f" LIMIT {limit}"
        rows = c.execute(sql, params).fetchall()
        c.close()
        return [dict(r) for r in rows]

    def get_all(self, limit=300):
        c = self._conn()
        rows = c.execute("SELECT * FROM users ORDER BY id LIMIT ?", (limit,)).fetchall()
        c.close()
        return [dict(r) for r in rows]

    def get_by_id(self, uid):
        c = self._conn()
        r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        c.close()
        return dict(r) if r else None

    def add_user(self, data):
        c = self._conn()
        cur = c.execute("""
            INSERT INTO users (
                instagram_id, first_name, last_name,
                father_name, phone, national_id,
                subject, tarnama_code, reg_date,
                address, reg_year
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, tuple(data.get(k, '') for k in [
            'instagram_id','first_name','last_name',
            'father_name','phone','national_id',
            'subject','tarnama_code','reg_date',
            'address','reg_year'
        ]))
        c.commit()
        new_id = cur.lastrowid
        c.close()
        return new_id

    def update_user(self, uid, data):
        c = self._conn()
        c.execute("""
            UPDATE users SET
                instagram_id=?, first_name=?, last_name=?,
                father_name=?, phone=?, national_id=?,
                subject=?, tarnama_code=?, reg_date=?,
                address=?, reg_year=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, tuple(data.get(k, '') for k in [
            'instagram_id','first_name','last_name',
            'father_name','phone','national_id',
            'subject','tarnama_code','reg_date',
            'address','reg_year'
        ]) + (uid,))
        c.commit()
        c.close()

    def delete_user(self, uid):
        c = self._conn()
        c.execute("DELETE FROM users WHERE id=?", (uid,))
        c.commit()
        c.close()

    def get_stats(self):
        c = self._conn()
        total = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        subjects = c.execute("""
            SELECT subject, COUNT(*) cnt FROM users WHERE subject != ''
            GROUP BY subject ORDER BY cnt DESC LIMIT 10
        """).fetchall()
        years = c.execute("""
            SELECT reg_year, COUNT(*) cnt FROM users
            WHERE reg_year != '' AND length(reg_year)=4
            GROUP BY reg_year ORDER BY reg_year
        """).fetchall()
        filled = {}
        for col in ['first_name','last_name','father_name',
                    'phone','national_id','instagram_id',
                    'subject','address']:
            n = c.execute(f"SELECT COUNT(*) FROM users WHERE {col} != ''").fetchone()[0]
            filled[col] = n
        c.close()
        return {
            'total': total,
            'subjects': [(r['subject'], r['cnt']) for r in subjects],
            'years': [(r['reg_year'], r['cnt']) for r in years],
            'filled': filled,
        }

    def export_excel(self, path):
        c = self._conn()
        rows = c.execute("SELECT * FROM users ORDER BY id").fetchall()
        c.close()
        if not rows:
            return 0
        data = [dict(r) for r in rows]
        df = pd.DataFrame(data)
        col_rename = {
            'row_number': 'ردیف',
            'instagram_id': 'ایدی اینستاگرام',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'father_name': 'نام پدر',
            'phone': 'شماره تماس',
            'national_id': 'شماره ملی',
            'subject': 'موضوع ثبت',
            'tarnama_code': 'کد تارنما',
            'reg_date': 'تاریخ ثبت',
            'address': 'نشانی منزل/ محل کار',
            'reg_year': 'سال ثبت',
        }
        keep = [c for c in col_rename.keys() if c in df.columns]
        df = df[keep].rename(columns=col_rename)
        df.to_excel(path, index=False)
        return len(df)

    def backup_db(self):
        if not os.path.exists(self.db_path):
            return None
        with open(self.db_path, 'rb') as f:
            return f.read()

    def restore_db(self, data):
        with open(self.db_path, 'wb') as f:
            f.write(data)
        return True
