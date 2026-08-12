# ============================================================
#  ساخت Workflow جدید و پایدار برای exe
# ============================================================

import os

PROJECT = '/content/CyberWatch_Fix'
os.makedirs(PROJECT, exist_ok=True)

# ============================================================
#  فایل ۱: launcher.py - راه‌انداز اصلی برنامه
# ============================================================

launcher_code = '''"""CyberWatch Launcher - راه‌انداز برنامه"""
import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path


def get_base_path():
    """مسیر اصلی برنامه"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_python_exe():
    """مسیر Python در exe یا سیستم"""
    if getattr(sys, 'frozen', False):
        # در حالت exe، از Python داخلی استفاده کن
        return sys.executable
    return sys.executable


def run_streamlit():
    """اجرای Streamlit در پس‌زمینه"""
    base = get_base_path()
    app_path = os.path.join(base, 'app.py')
    
    # مطمئن شو app.py وجود دارد
    if not os.path.exists(app_path):
        # جستجو در _internal
        alt_path = os.path.join(base, '_internal', 'app.py')
        if os.path.exists(alt_path):
            app_path = alt_path
    
    env = os.environ.copy()
    env['STREAMLIT_SERVER_HEADLESS'] = 'true'
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    env['STREAMLIT_SERVER_PORT'] = '8501'
    env['STREAMLIT_SERVER_ADDRESS'] = '127.0.0.1'
    
    # اجرا با subprocess
    if sys.platform == 'win32':
        creation_flags = subprocess.CREATE_NO_WINDOW
    else:
        creation_flags = 0
    
    try:
        # استفاده از streamlit به عنوان ماژول
        import streamlit.web.cli as stcli
        sys.argv = [
            'streamlit', 'run', app_path,
            '--server.port=8501',
            '--server.address=127.0.0.1',
            '--server.headless=true',
            '--browser.gatherUsageStats=false',
            '--global.developmentMode=false',
        ]
        stcli.main()
    except Exception as e:
        print(f"Error: {e}")
        # جایگزین: استفاده از subprocess
        subprocess.run([
            get_python_exe(), '-m', 'streamlit', 'run', app_path,
            '--server.port=8501',
            '--server.address=127.0.0.1',
            '--server.headless=true',
            '--browser.gatherUsageStats=false',
        ], env=env, creationflags=creation_flags)


def open_browser():
    """باز کردن مرورگر بعد از راه‌اندازی سرور"""
    time.sleep(5)  # صبر برای آماده شدن سرور
    webbrowser.open('http://127.0.0.1:8501')


if __name__ == '__main__':
    # جلوگیری از اجرای چندگانه
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', 8502))  # پورت قفل
    except OSError:
        # برنامه در حال اجراست، فقط مرورگر را باز کن
        webbrowser.open('http://127.0.0.1:8501')
        sys.exit(0)
    
    # باز کردن مرورگر در پس‌زمینه
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # اجرای Streamlit
    run_streamlit()
'''

with open(f'{PROJECT}/launcher.py', 'w', encoding='utf-8') as f:
    f.write(launcher_code)
print("✅ launcher.py ساخته شد")


# ============================================================
#  فایل ۲: Workflow جدید و پایدار
# ============================================================

workflow_code = '''name: Build CyberWatch EXE v2

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Setup Python 3.11
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install streamlit pandas openpyxl pyinstaller
    
    - name: Build EXE with PyInstaller
      run: |
        pyinstaller --onefile --console --name "CyberWatch" `
          --add-data "app.py;." `
          --add-data "database.py;." `
          --add-data ".streamlit;.streamlit" `
          --hidden-import streamlit `
          --hidden-import streamlit.web.cli `
          --hidden-import streamlit.runtime.scriptrunner.magic_funcs `
          --hidden-import pandas `
          --hidden-import openpyxl `
          --hidden-import sqlite3 `
          --collect-all streamlit `
          --collect-all pandas `
          --collect-all openpyxl `
          --collect-all altair `
          --collect-all pyarrow `
          launcher.py
    
    - name: Upload EXE
      uses: actions/upload-artifact@v4
      with:
        name: CyberWatch-Windows-v2
        path: dist/CyberWatch.exe
        retention-days: 30
'''

with open(f'{PROJECT}/build-exe.yml', 'w', encoding='utf-8') as f:
    f.write(workflow_code)
print("✅ build-exe.yml ساخته شد")

# دانلود
from google.colab import files
files.download(f'{PROJECT}/launcher.py')
files.download(f'{PROJECT}/build-exe.yml')

print("""
========================================
✅ دو فایل دانلود شد:
   1. launcher.py
   2. build-exe.yml

مراحل بعد:
1. به GitHub بروید
2. فایل launcher.py را اضافه کنید
3. Workflow قدیمی را با build-exe.yml جدید جایگزین کنید
4. Commit کنید
5. صبر کنید تا exe جدید ساخته شود
========================================
""")
