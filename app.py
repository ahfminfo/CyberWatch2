
"""CyberWatch v4.0 - Web UI"""
import streamlit as st
import pandas as pd
import os
import time
from database import Database

st.set_page_config(
    page_title="CyberWatch | سامانه هوشمند",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700;900&display=swap');
    * { font-family: 'Vazirmatn', 'Segoe UI', sans-serif !important; }
    .stApp {
        background: linear-gradient(135deg, #0D1117 0%, #161B22 100%);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1117 0%, #1A1F2E 100%);
        border-right: 1px solid #21262D;
    }
    .main-header {
        background: linear-gradient(135deg, #1F6FEB 0%, #388BFD 50%, #58A6FF 100%);
        padding: 28px 35px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(31,111,235,0.3);
    }
    .main-header h1 {
        color: white !important;
        font-size: 28px !important;
        font-weight: 900 !important;
        margin: 0 !important;
    }
    .main-header p {
        color: #B0D4FF !important;
        font-size: 14px !important;
        margin: 8px 0 0 0 !important;
    }
    .stat-card {
        background: linear-gradient(145deg, #161B22, #1C2128);
        border: 1px solid #30363D;
        border-radius: 14px;
        padding: 22px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        border-color: #388BFD;
        transform: translateY(-3px);
    }
    .stat-card .icon { font-size: 36px; margin-bottom: 8px; }
    .stat-card .value {
        font-size: 32px;
        font-weight: 900;
        margin: 5px 0;
    }
    .stat-card .label { color: #8B949E; font-size: 13px; }
    .blue .value   { color: #58A6FF; }
    .green .value  { color: #3FB950; }
    .orange .value { color: #D29922; }
    .red .value    { color: #F85149; }
    .purple .value { color: #BC8CFF; }
    .card {
        background: #161B22;
        border: 1px solid #21262D;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 15px;
    }
    .card-title {
        color: #F0F6FC;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #21262D;
    }
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1F6FEB, #388BFD) !important;
        color: white !important;
    }
    .progress-bar {
        background: #21262D;
        border-radius: 8px;
        height: 10px;
        overflow: hidden;
        margin: 5px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 8px;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-blue   { background: #1F3D5F; color: #58A6FF; }
    .badge-green  { background: #1B3D2F; color: #3FB950; }
    .badge-red    { background: #3D1B1B; color: #F85149; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

db = Database()

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 15px 0;">
        <div style="font-size: 42px;">🔍</div>
        <h2 style="color: #58A6FF; margin: 5px 0;">CyberWatch</h2>
        <p style="color: #8B949E; font-size: 12px;">
            سامانه هوشمند<br>فضای مجازی
        </p>
    </div>
    <hr style="border-color: #21262D;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "ناوبری",
        ["🏠 داشبورد", "🔍 جستجوی هوشمند",
         "🔬 جستجوی پیشرفته", "➕ ثبت کاربر جدید",
         "📋 همه رکوردها", "⚙️ تنظیمات"],
        label_visibility="collapsed",
    )

    if db.is_ready():
        stats = db.get_stats()
        st.markdown(f"""
        <div style="background: #1C2128; border-radius: 10px;
                    padding: 12px; text-align: center; margin-top: 15px;">
            <div style="color: #8B949E; font-size: 11px;">کل رکوردها</div>
            <div style="color: #58A6FF; font-size: 24px; font-weight: 900;">
                {stats['total']:,}
            </div>
        </div>
        """, unsafe_allow_html=True)


if not db.is_ready():
    st.markdown("""
    <div class="main-header">
        <h1>🔍 CyberWatch</h1>
        <p>به سامانه هوشمند خوش آمدید</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="card-title">📂 راه‌اندازی اولیه</div>
        <p style="color: #8B949E;">فایل اکسل دیتابیس را بارگذاری کنید.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("فایل اکسل", type=["xlsx", "xls"])
    if uploaded:
        tmp_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "_temp_upload.xlsx"
        )
        with open(tmp_path, 'wb') as f:
            f.write(uploaded.read())
        with st.spinner("⏳ در حال بارگذاری..."):
            total = db.import_excel(tmp_path)
        os.remove(tmp_path)
        st.success(f"✅ {total:,} رکورد بارگذاری شد!")
        st.balloons()
        time.sleep(2)
        st.rerun()
    st.stop()


# ================= داشبورد =================
if page == "🏠 داشبورد":
    stats = db.get_stats()
    st.markdown("""
    <div class="main-header">
        <h1>🏠 داشبورد</h1>
        <p>نمای کلی از وضعیت دیتابیس</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="stat-card blue">
            <div class="icon">📦</div>
            <div class="value">{stats['total']:,}</div>
            <div class="label">کل رکوردها</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card green">
            <div class="icon">📅</div>
            <div class="value">{len(stats['years'])}</div>
            <div class="label">سال فعال</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card orange">
            <div class="icon">📂</div>
            <div class="value">{len(stats['subjects'])}</div>
            <div class="label">موضوعات</div>
        </div>
        """, unsafe_allow_html=True)
    ph_pct = int((stats['filled'].get('phone', 0) / max(stats['total'], 1)) * 100)
    with c4:
        st.markdown(f"""
        <div class="stat-card purple">
            <div class="icon">📱</div>
            <div class="value">{ph_pct}%</div>
            <div class="label">شماره تماس</div>
        </div>
        """, unsafe_allow_html=True)
    ig_pct = int((stats['filled'].get('instagram_id', 0) / max(stats['total'], 1)) * 100)
    with c5:
        st.markdown(f"""
        <div class="stat-card red">
            <div class="icon">📸</div>
            <div class="value">{ig_pct}%</div>
            <div class="label">ایدی اینستا</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("""
        <div class="card">
            <div class="card-title">📂 موضوعات</div>
        </div>
        """, unsafe_allow_html=True)
        colors = ['#58A6FF','#3FB950','#D29922','#F85149',
                  '#BC8CFF','#79C0FF','#56D364','#E3B341',
                  '#FF7B72','#D2A8FF']
        max_cnt = max((c for _, c in stats['subjects']), default=1)
        for i, (subj, cnt) in enumerate(stats['subjects']):
            pct = int((cnt / max_cnt) * 100)
            color = colors[i % len(colors)]
            st.markdown(f"""
            <div style="margin: 8px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #E6EDF3; font-size: 13px;">{subj[:25]}</span>
                    <span style="color: {color}; font-weight: 700;">{cnt}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{pct}%; background:{color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_r:
        st.markdown("""
        <div class="card">
            <div class="card-title">📅 سال‌های ثبت</div>
        </div>
        """, unsafe_allow_html=True)
        if stats['years']:
            year_df = pd.DataFrame(stats['years'], columns=['سال', 'تعداد'])
            st.bar_chart(year_df.set_index('سال'), color='#388BFD')


# ================= جستجوی هوشمند =================
elif page == "🔍 جستجوی هوشمند":
    st.markdown("""
    <div class="main-header">
        <h1>🔍 جستجوی هوشمند</h1>
        <p>جستجو در تمام فیلدها</p>
    </div>
    """, unsafe_allow_html=True)

    query = st.text_input("جستجو",
        placeholder="🔍 نام، شماره، ایدی، موضوع، آدرس ...",
        label_visibility="collapsed")

    if query:
        results = db.search(query)
        badge = "green" if results else "red"
        st.markdown(f'<span class="badge badge-{badge}">✅ {len(results)} نتیجه</span>',
                    unsafe_allow_html=True)

        if results:
            df = pd.DataFrame(results)
            show = {
                'id': 'ID', 'instagram_id': 'ایدی',
                'first_name': 'نام', 'last_name': 'نام خانوادگی',
                'phone': 'شماره تماس', 'subject': 'موضوع', 'reg_year': 'سال',
            }
            df_s = df[[c for c in show if c in df.columns]].rename(columns=show)
            st.dataframe(df_s, use_container_width=True, hide_index=True, height=450)

            st.markdown("<br>", unsafe_allow_html=True)
            sel_id = st.selectbox("انتخاب رکورد",
                options=[r['id'] for r in results],
                format_func=lambda x: f"ID {x} - {next((r['first_name']+' '+r['last_name'] for r in results if r['id']==x), '')}")

            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                if st.button("👁️ مشاهده", use_container_width=True, type="primary"):
                    rec = db.get_by_id(sel_id)
                    if rec:
                        fa_map = {
                            'instagram_id': 'ایدی اینستاگرام',
                            'first_name': 'نام', 'last_name': 'نام خانوادگی',
                            'father_name': 'نام پدر', 'phone': 'شماره تماس',
                            'national_id': 'شماره ملی', 'subject': 'موضوع ثبت',
                            'tarnama_code': 'کد تارنما', 'reg_date': 'تاریخ ثبت',
                            'address': 'نشانی', 'reg_year': 'سال ثبت',
                        }
                        for key, fa in fa_map.items():
                            val = rec.get(key, '')
                            if val:
                                st.markdown(f"""
                                <div style="background: #1C2128; padding: 10px 15px;
                                            border-radius: 8px; margin: 4px 0;
                                            display: flex; justify-content: space-between;">
                                    <span style="color: #8B949E; font-weight: 600;">{fa}</span>
                                    <span style="color: #E6EDF3;">{val}</span>
                                </div>
                                """, unsafe_allow_html=True)
            with cc2:
                if st.button("✏️ ویرایش", use_container_width=True):
                    st.session_state['edit_id'] = sel_id
                    st.rerun()
            with cc3:
                if st.button("🗑️ حذف", use_container_width=True):
                    st.session_state['delete_id'] = sel_id

            if 'delete_id' in st.session_state:
                did = st.session_state['delete_id']
                rec = db.get_by_id(did)
                if rec:
                    name = f"{rec.get('first_name','')} {rec.get('last_name','')}"
                    st.warning(f"⚠️ حذف «{name}»?")
                    ccc1, ccc2 = st.columns(2)
                    with ccc1:
                        if st.button("✅ بله", type="primary"):
                            db.delete_user(did)
                            del st.session_state['delete_id']
                            st.success("✅ حذف شد!")
                            time.sleep(1)
                            st.rerun()
                    with ccc2:
                        if st.button("❌ خیر"):
                            del st.session_state['delete_id']
                            st.rerun()


# ================= جستجوی پیشرفته =================
elif page == "🔬 جستجوی پیشرفته":
    st.markdown("""
    <div class="main-header">
        <h1>🔬 جستجوی پیشرفته</h1>
        <p>فیلتر همزمان چند فیلد</p>
    </div>
    """, unsafe_allow_html=True)

    fields = ['نام','نام خانوادگی','ایدی اینستاگرام','شماره تماس',
              'شماره ملی','موضوع ثبت','سال ثبت','نشانی',
              'نام پدر','کد تارنما']
    cols = st.columns(4)
    filters = {}
    for i, key in enumerate(fields):
        with cols[i % 4]:
            filters[key] = st.text_input(key, placeholder=f"{key}...")

    if st.button("🔬 اعمال فیلترها", type="primary"):
        active = {k: v for k, v in filters.items() if v}
        if active:
            results = db.advanced_search(active)
            st.markdown(f'<span class="badge badge-green">✅ {len(results)} نتیجه</span>',
                        unsafe_allow_html=True)
            if results:
                df = pd.DataFrame(results)
                show = {
                    'id': 'ID', 'instagram_id': 'ایدی',
                    'first_name': 'نام', 'last_name': 'نام خانوادگی',
                    'phone': 'شماره تماس', 'subject': 'موضوع',
                    'reg_year': 'سال',
                }
                df_s = df[[c for c in show if c in df.columns]].rename(columns=show)
                st.dataframe(df_s, use_container_width=True, hide_index=True, height=450)


# ================= ثبت / ویرایش =================
elif page == "➕ ثبت کاربر جدید":
    edit_id = st.session_state.get('edit_id')
    prefill = {}
    is_edit = False
    if edit_id:
        prefill = db.get_by_id(edit_id) or {}
        is_edit = True

    title = "✏️ ویرایش کاربر" if is_edit else "➕ ثبت کاربر جدید"
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
    </div>
    """, unsafe_allow_html=True)

    with st.form("user_form"):
        c1, c2 = st.columns(2)
        with c1:
            instagram_id = st.text_input("⭐ ایدی اینستاگرام *", value=prefill.get('instagram_id',''))
            first_name = st.text_input("نام", value=prefill.get('first_name',''))
            last_name = st.text_input("نام خانوادگی", value=prefill.get('last_name',''))
            father_name = st.text_input("نام پدر", value=prefill.get('father_name',''))
            phone = st.text_input("شماره تماس", value=prefill.get('phone',''))
        with c2:
            national_id = st.text_input("شماره ملی", value=prefill.get('national_id',''))
            subject = st.text_input("موضوع ثبت", value=prefill.get('subject',''))
            tarnama_code = st.text_input("کد تارنما", value=prefill.get('tarnama_code',''))
            reg_date = st.text_input("تاریخ ثبت", value=prefill.get('reg_date',''))
            reg_year = st.text_input("سال ثبت", value=prefill.get('reg_year',''))
        address = st.text_area("نشانی", value=prefill.get('address',''), height=80)

        submitted = st.form_submit_button(
            "💾 ذخیره" if is_edit else "✅ ثبت",
            type="primary")

        if submitted:
            if not instagram_id.strip():
                st.error("⭐ ایدی اینستاگرام الزامی است!")
            else:
                data = {
                    'instagram_id': instagram_id.strip(),
                    'first_name': first_name.strip(),
                    'last_name': last_name.strip(),
                    'father_name': father_name.strip(),
                    'phone': phone.strip(),
                    'national_id': national_id.strip(),
                    'subject': subject.strip(),
                    'tarnama_code': tarnama_code.strip(),
                    'reg_date': reg_date.strip(),
                    'address': address.strip(),
                    'reg_year': reg_year.strip(),
                }
                if is_edit:
                    db.update_user(edit_id, data)
                    del st.session_state['edit_id']
                    st.success("✅ ویرایش شد!")
                else:
                    db.add_user(data)
                    st.success("✅ ثبت شد!")
                    st.balloons()
                time.sleep(2)
                st.rerun()


# ================= همه رکوردها =================
elif page == "📋 همه رکوردها":
    st.markdown("""
    <div class="main-header">
        <h1>📋 همه رکوردها</h1>
    </div>
    """, unsafe_allow_html=True)

    all_data = db.get_all(limit=1000)
    st.markdown(f'<span class="badge badge-blue">📦 {len(all_data)} رکورد</span>',
                unsafe_allow_html=True)

    if all_data:
        df = pd.DataFrame(all_data)
        show = {
            'id': 'ID', 'instagram_id': 'ایدی',
            'first_name': 'نام', 'last_name': 'نام خانوادگی',
            'phone': 'شماره تماس', 'subject': 'موضوع', 'reg_year': 'سال',
        }
        df_s = df[[c for c in show if c in df.columns]].rename(columns=show)
        st.dataframe(df_s, use_container_width=True, hide_index=True, height=550)

    if st.button("📥 خروجی اکسل", type="primary"):
        export_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "export.xlsx")
        n = db.export_excel(export_path)
        with open(export_path, 'rb') as ef:
            st.download_button("⬇️ دانلود", data=ef.read(),
                file_name="CyberWatch_Export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ================= تنظیمات =================
elif page == "⚙️ تنظیمات":
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #30363D, #484F58);">
        <h1>⚙️ تنظیمات</h1>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📂 بارگذاری مجدد", "💾 بکاپ", "ℹ️ درباره"])

    with tab1:
        st.markdown("""
        <div class="card">
            <div class="card-title">📂 بارگذاری مجدد</div>
            <p style="color: #8B949E;">⚠️ داده‌های فعلی جایگزین می‌شوند</p>
        </div>
        """, unsafe_allow_html=True)
        new_file = st.file_uploader("فایل اکسل", type=["xlsx", "xls"], key="s1")
        if new_file and st.button("⚠️ بارگذاری", type="primary"):
            tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_temp.xlsx")
            with open(tmp, 'wb') as f:
                f.write(new_file.read())
            with st.spinner("در حال بارگذاری..."):
                total = db.import_excel(tmp)
            os.remove(tmp)
            st.success(f"✅ {total:,} رکورد!")
            time.sleep(2)
            st.rerun()

    with tab2:
        st.markdown("""
        <div class="card">
            <div class="card-title">💾 بکاپ و بازیابی</div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 دانلود بکاپ", type="primary", use_container_width=True):
                data = db.backup_db()
                if data:
                    st.download_button("⬇️ ذخیره", data=data,
                        file_name="cyberwatch_backup.db",
                        mime="application/octet-stream")
        with col2:
            restore_file = st.file_uploader("🔄 بازیابی", type=["db"], key="r1")
            if restore_file and st.button("⚠️ بازیابی", use_container_width=True):
                db.restore_db(restore_file.read())
                st.success("✅ بازیابی شد!")
                time.sleep(2)
                st.rerun()

    with tab3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">ℹ️ درباره</div>
            <div style="color: #E6EDF3; line-height: 2;">
                <b>🔍 CyberWatch v4.0</b><br>
                سامانه هوشمند جستجو و ثبت کاربران فضای مجازی<br><br>
                <b>مسیر دیتابیس:</b><br>
                <code style="color: #58A6FF;">{db.db_path}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)
