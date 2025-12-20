"""
============================================================================
NAVBATCHILIK - Yotoqxona Navbatchilik Tizimi
============================================================================

Copyright (c) 2024 Orifxon Marufxonov
Barcha huquqlar himoyalangan / All Rights Reserved

Bog'lanish: @Sheeyh_o5 (Telegram)
============================================================================
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import requests

# --- TELEGRAM SOZLAMALARI ---
TELEGRAM_TOKEN = "8259734572:AAGeJLKmmruLByDjx81gdi1VcjNt3ZnX894"
ADMIN_CHAT_ID = "7693191223"
TTJ_GROUP_ID = "-1002623014807"  # Shaxsiy kanal

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID, "text": message}, timeout=3)
    except:
        pass

def send_to_ttj_group(message):
    """TTJ guruhiga xabar yuborish"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": TTJ_GROUP_ID, 
            "text": message, 
            "parse_mode": "HTML"
        }, timeout=5)
    except:
        pass

# ============================================================================
# XAVFSIZLIK TIZIMI / SECURITY SYSTEM
# Copyright (c) 2024 Orifxon Marufxonov
# ============================================================================

# Xavfsizlik sozlamalari
MAX_LOGIN_ATTEMPTS = 5  # Maksimal urinishlar soni
BLOCK_TIME_MINUTES = 30  # Bloklash vaqti (daqiqa)
ALERT_THRESHOLD = 3  # Ogohlantirishdan oldin urinishlar

def get_security_state():
    """Xavfsizlik holatini olish"""
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "blocked_until" not in st.session_state:
        st.session_state.blocked_until = None
    if "last_attempt_time" not in st.session_state:
        st.session_state.last_attempt_time = None
    return st.session_state

def is_blocked():
    """Foydalanuvchi bloklangan yoki yo'qligini tekshirish"""
    state = get_security_state()
    if state.blocked_until:
        if datetime.now() < state.blocked_until:
            return True
        else:
            # Bloklash muddati tugadi
            state.blocked_until = None
            state.login_attempts = 0
    return False

def record_failed_login():
    """Muvaffaqiyatsiz kirishni qayd qilish"""
    state = get_security_state()
    state.login_attempts += 1
    state.last_attempt_time = datetime.now()
    
    # Ogohlantirishni yuborish
    if state.login_attempts >= ALERT_THRESHOLD:
        send_security_alert(state.login_attempts)
    
    # Maksimal urinishlardan oshsa bloklash
    if state.login_attempts >= MAX_LOGIN_ATTEMPTS:
        state.blocked_until = datetime.now() + timedelta(minutes=BLOCK_TIME_MINUTES)
        send_block_alert()

def reset_login_attempts():
    """Muvaffaqiyatli kirishdan keyin urinishlarni tozalash"""
    state = get_security_state()
    state.login_attempts = 0
    state.blocked_until = None

def send_security_alert(attempts):
    """Xavfsizlik ogohlantirishi yuborish"""
    tashkent_time = (datetime.utcnow() + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
    msg = f"""🚨 XAVFSIZLIK OGOHLANTIRISHI!

⚠️ Shubhali faoliyat aniqlandi!
📊 Noto'g'ri parol urinishlari: {attempts}
🕐 Vaqt: {tashkent_time} (Toshkent)

Agar bu siz bo'lmasangiz, parolni o'zgartiring!"""
    send_telegram_alert(msg)

def send_block_alert():
    """Bloklash haqida xabar yuborish"""
    tashkent_time = (datetime.utcnow() + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
    msg = f"""🔒 FOYDALANUVCHI BLOKLANDI!

❌ {MAX_LOGIN_ATTEMPTS} marta noto'g'ri parol kiritildi
⏱️ Bloklash muddati: {BLOCK_TIME_MINUTES} daqiqa
🕐 Vaqt: {tashkent_time} (Toshkent)

Ehtimol brute-force hujumi!"""
    send_telegram_alert(msg)

def get_tashkent_time():
    """Toshkent vaqtini olish (UTC+5)"""
    return (datetime.utcnow() + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')

def get_device_type():
    """Qurilma turini aniqlash"""
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        user_agent = headers.get("User-Agent", "").lower() if headers else ""
        
        if "android" in user_agent or "mobile" in user_agent:
            return "📱 Mobil ilova"
        elif "iphone" in user_agent or "ipad" in user_agent:
            return "🍎 iOS qurilma"
        else:
            return "💻 Kompyuter/Brauzer"
    except:
        return "🌐 Noma'lum qurilma"

def send_successful_login_alert():
    """Muvaffaqiyatli kirish haqida xabar"""
    device = get_device_type()
    tashkent_time = get_tashkent_time()
    
    msg = f"""✅ TIZIMGA KIRISH

🕐 Vaqt: {tashkent_time} (Toshkent)
{device}

Agar bu siz bo'lmasangiz - darhol parolni o'zgartiring!"""
    send_telegram_alert(msg)

def log_activity(action, details=""):
    """Muhim faoliyatni qayd qilish va xabar yuborish"""
    tashkent_time = get_tashkent_time()
    msg = f"""📋 FAOLIYAT LOGI

📌 Harakat: {action}
📝 Tafsilotlar: {details}
🕐 Vaqt: {tashkent_time} (Toshkent)"""
    send_telegram_alert(msg)

# --- KONFIGURATSIYA ---
GOOGLE_SHEET_NAME = "Navbatchilik_Jadvali"

DUTY_TYPES = {
    "Katta Oshxona (2 kishi)": 1,
    "Kichik Oshxona (2 kishi)": 2,
    "Katta Dush (2 kishi)": 3,
    "Kichik Dush (1 kishi)": 4
}
SMS_TEMPLATES = {
    1: "Siz bugun Katta oshxonaga navbatchisiz. Ishingizga omad!",
    2: "Siz bugun Kichik oshxonaga navbatchisiz. Ishingizga omad!",
    3: "Siz bugun Katta dushga navbatchisiz. Ishingizga omad!",
    4: "Siz bugun Kichik dushga navbatchisiz. Ishingizga omad!"
}

# --- NARYAD KONFIGURATSIYA ---
NARYAD_TYPES = {
    "Qo'shimcha Zal": 11,
    "Zina": 12,
    "Kirxona": 13,
    "Sabzavotxona": 14,
    "Manaviyat": 15,
    "Kladovka": 16,
    "Katta Oshxona": 21,
    "Kichik Oshxona": 22,
    "Katta Dush": 23,
    "Kichik Dush": 24
}
# Naryad joylari nomlari (SMS uchun)
NARYAD_NAMES = {
    11: "Qo'shimcha Zal",
    12: "Zina",
    13: "Kirxona",
    14: "Sabzavotxona",
    15: "Manaviyat",
    16: "Kladovka",
    21: "Katta Oshxona",
    22: "Kichik Oshxona",
    23: "Katta Dush",
    24: "Kichik Dush"
}

st.set_page_config(page_title="Navbatchilik Taqsimoti (Online)", layout="wide")
st.title("📅 Yotoqxona Navbatchilik Taqsimoti (Google Sheets + Bot)")

@st.cache_resource
def get_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # 1. Streamlit Cloud Secrets (Agar internetda bo'lsa)
    if "gcp_service_account" in st.secrets:
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    # 2. Lokal fayl (Agar kompyuterda bo'lsa)
    elif os.path.exists("credentials.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    else:
        st.error("Kalit topilmadi! (credentials.json ham, Secrets ham yo'q)")
        st.stop()
        
    client = gspread.authorize(creds)
    return client

def check_password():
    """Returns `True` if the user had the correct password."""
    
    # Query params orqali sessiyani saqlash
    if "auth" in st.query_params:
        if st.query_params["auth"] == "ok":
            st.session_state["password_correct"] = True
            return True

    if st.session_state.get("password_correct", False):
        return True
    
    # Bloklash tekshiruvi
    if is_blocked():
        state = get_security_state()
        remaining = state.blocked_until - datetime.now()
        minutes_left = int(remaining.total_seconds() / 60) + 1
        st.error(f"🔒 Siz {minutes_left} daqiqaga bloklangansiz! Keyinroq urinib ko'ring.")
        st.warning(f"⚠️ Sabab: Juda ko'p noto'g'ri parol urinishlari")
        return False

    # Rasmni base64 ga o'tkazish
    import base64
    with open("login_bg.png", "rb") as f:
        bg_image = base64.b64encode(f.read()).decode()
    
    # Fullscreen background CSS
    st.markdown(f"""
    <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bg_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Login box styling */
        .login-box {{
            background: rgba(0, 0, 0, 0.7);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 400px;
            margin: 0 auto;
            margin-top: 5vh;
        }}
        
        .login-title {{
            color: #4FC3F7;
            text-align: center;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .login-subtitle {{
            color: #aaa;
            text-align: center;
            font-style: italic;
            margin-bottom: 30px;
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)
    
    # Markazlashtirilgan login box
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<p class="login-title">🔒 Tizimga kirish</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">TTJ Yotoqxona Navbatchilik Tizimi</p>', unsafe_allow_html=True)
        
        # Qolgan urinishlar haqida ogohlantirish
        state = get_security_state()
        if state.login_attempts > 0:
            remaining_attempts = MAX_LOGIN_ATTEMPTS - state.login_attempts
            if remaining_attempts <= 3:
                st.warning(f"⚠️ Qolgan urinishlar: {remaining_attempts}")
        
        # Form (Enter bilan ishlaydi)
        with st.form("login_form"):
            password = st.text_input("Parolni kiriting", type="password", placeholder="Parolni kiriting va Enter bosing...", label_visibility="collapsed")
            submit_button = st.form_submit_button("🚀 Kirish", use_container_width=True)

            if submit_button:
                # Parolni tekshirish (bo'sh joylarni olib tashlab)
                if password.strip() == st.secrets["password"]:
                    reset_login_attempts()
                    send_successful_login_alert()
                    st.session_state["password_correct"] = True
                    st.query_params["auth"] = "ok"
                    st.rerun()
                else:
                    record_failed_login()
                    st.error("😕 Parol xato! Qaytadan urinib ko'ring.")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
                
    return False

if not check_password():
    st.stop()

def get_main_sheet():
    return get_client().open(GOOGLE_SHEET_NAME).sheet1

def get_queue_sheet():
    client = get_client()
    try:
        return client.open(GOOGLE_SHEET_NAME).worksheet("SMS_QUEUE")
    except:
        ws = client.open(GOOGLE_SHEET_NAME).add_worksheet(title="SMS_QUEUE", rows="100", cols="4")
        ws.append_row(["TELEFON", "XABAR", "STATUS", "VAQT"])
        return ws

# --- MA'LUMOTNI O'QISH ---
try:
    sheet = get_main_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df['telefon raqami'] = df['telefon raqami'].astype(str).str.replace(".0", "", regex=False)
except Exception as e:
    st.error(f"Google Sheetga ulanishda xatolik: {e}")
    st.stop()

# --- TABLAR ---
tab1, tab2, tab3, tab4 = st.tabs(["📝 Navbatchilik", "🛠️ Naryad", "📊 Statistika", "📸 Yo'qlama"])

with tab1:
    # --- UI ---
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_date = st.date_input("Sanani tanlang", datetime.now(), key="navbatchilik_date")
        date_str = selected_date.strftime("%Y.%m.%d")
    st.info(f"Tanlangan sana: **{date_str}**")

    # Ism va Xona bo'yicha saralash (o'sish tartibida)
    student_options = sorted(df.apply(lambda x: f"{x['ism familiya']} ({x['xona']})", axis=1).tolist())

    with st.form("duty_form"):
        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)
        
        ka_o = c1.multiselect("🍳 Katta Oshxona", options=student_options, max_selections=2, placeholder="Ism yoki xona raqamini yozing")
        ki_o = c2.multiselect("🥪 Kichik Oshxona", options=student_options, max_selections=2, placeholder="Ism yoki xona raqamini yozing")
        ka_d = c3.multiselect("🚿 Katta Dush", options=student_options, max_selections=2, placeholder="Ism yoki xona raqamini yozing")
        ki_d = c4.multiselect("🛁 Kichik Dush", options=student_options, max_selections=1, placeholder="Ism yoki xona raqamini yozing")
        
        submitted = st.form_submit_button("💾 Saqlash va SMS Navbatiga Qo'shish", type="primary")

    if submitted:
        selections = []
        for s in ka_o: selections.append((s, 1))
        for s in ki_o: selections.append((s, 2))
        for s in ka_d: selections.append((s, 3))
        for s in ki_d: selections.append((s, 4))
        
        if not selections:
            st.warning("Hech kim tanlanmadi!")
        else:
            try:
                # 1. Asosiy Jadvalga yozish
                headers = sheet.row_values(1)
                if date_str not in headers:
                    sheet.update_cell(1, len(headers) + 1, date_str)
                    headers = sheet.row_values(1)
                
                date_col_idx = headers.index(date_str) + 1
                queue_sheet = get_queue_sheet()
                # Toshkent vaqti (UTC+5)
                timestamp = (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
                
                progress_bar = st.progress(0)
                
                for i, (student_str, type_id) in enumerate(selections):
                    idx = student_options.index(student_str)
                    row_idx = idx + 2
                    
                    # Asosiy jadvalga ID yozish
                    sheet.update_cell(row_idx, date_col_idx, type_id)
                    
                    # SMS Navbatiga yozish
                    phone = df.at[idx, 'telefon raqami']
                    msg = SMS_TEMPLATES[type_id]
                    
                    # [TELEFON, XABAR, STATUS, VAQT]
                    queue_sheet.append_row([phone, msg, "PENDING", timestamp])
                    
                    progress_bar.progress((i + 1) / len(selections))
                
                # ADMINGA XABAR YUBORISH
                send_telegram_alert("🚨 DIQQAT: Yangi navbatchilar belgilandi!\n\n📲 Iltimos, telefoningizdagi 'SMS Widget' tugmasini bosing.")
                
                # TTJ GURUHIGA XABAR YUBORISH
                group_msg = f"📅 <b>Bugungi Navbatchilar ({date_str})</b>\n\n"
                
                if ka_o:
                    group_msg += "🍳 <b>Katta Oshxona:</b>\n"
                    for s in ka_o:
                        group_msg += f"  • {s}\n"
                    group_msg += "\n"
                
                if ki_o:
                    group_msg += "🥪 <b>Kichik Oshxona:</b>\n"
                    for s in ki_o:
                        group_msg += f"  • {s}\n"
                    group_msg += "\n"
                
                if ka_d:
                    group_msg += "🚿 <b>Katta Dush:</b>\n"
                    for s in ka_d:
                        group_msg += f"  • {s}\n"
                    group_msg += "\n"
                
                if ki_d:
                    group_msg += "🛁 <b>Kichik Dush:</b>\n"
                    for s in ki_d:
                        group_msg += f"  • {s}\n"
                    group_msg += "\n"
                
                group_msg += "✅ <i>Ishingizga omad!</i>"
                send_to_ttj_group(group_msg)

                st.success("✅ Muvaffaqiyatli saqlandi! SMSlar navbatga qo'shildi. Telefoningiz internetga ulanganda ular avtomatik ketadi.")
                st.rerun()
                
            except Exception as e:
                st.error(f"Xatolik: {e}")

    st.markdown("---")
    st.subheader("📋 Asosiy Jadval")
    st.dataframe(df, use_container_width=True)

    st.subheader("📨 SMS Navbati Statusi (Barcha Tarix)")
    try:
        qs = get_queue_sheet()
        q_data = qs.get_all_records()
        # Tarixni teskarisiga aylantiramiz (eng yangisi tepada)
        st.dataframe(pd.DataFrame(q_data)[::-1], use_container_width=True)
    except:
        st.info("Navbat bo'sh")

with tab2:
    st.subheader("🛠️ Naryad Taqsimoti")
    
    # --- UI ---
    col1, col2 = st.columns([1, 3])
    with col1:
        naryad_date = st.date_input("Sanani tanlang", datetime.now(), key="naryad_date")
        naryad_date_str = naryad_date.strftime("%Y.%m.%d")
    st.info(f"Tanlangan sana: **{naryad_date_str}**")

    # Ism va Xona bo'yicha saralash
    naryad_student_options = sorted(df.apply(lambda x: f"{x['ism familiya']} ({x['xona']})", axis=1).tolist())

    with st.form("naryad_form"):
        # Kun kiritish
        st.markdown("##### 📅 Naryad muddati")
        naryad_kunlar = st.number_input("Necha kunga naryad?", min_value=1, max_value=30, value=1, step=1)
        
        st.markdown("##### 🏠 Boshqa Joylar")
        nc1, nc2 = st.columns(2)
        nc3, nc4 = st.columns(2)
        nc5, nc6 = st.columns(2)
        
        qosh_zal = nc1.multiselect("🏠 Qo'shimcha Zal", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing")
        zina = nc2.multiselect("🪜 Zina", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing")
        kirxona = nc3.multiselect("🧹 Kirxona", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing")
        sabzavotxona = nc4.multiselect("🥕 Sabzavotxona", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing")
        manaviyat = nc5.multiselect("📚 Manaviyat", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing")
        kladovka = nc6.multiselect("📦 Kladovka", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing")
        
        st.markdown("##### 🍳 Oshxona va Dush")
        oc1, oc2 = st.columns(2)
        oc3, oc4 = st.columns(2)
        
        n_ka_oshxona = oc1.multiselect("🍳 Katta Oshxona", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing", key="n_ka_o")
        n_ki_oshxona = oc2.multiselect("🥪 Kichik Oshxona", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing", key="n_ki_o")
        n_ka_dush = oc3.multiselect("🚿 Katta Dush", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing", key="n_ka_d")
        n_ki_dush = oc4.multiselect("🛁 Kichik Dush", options=naryad_student_options, placeholder="Ism yoki xona raqamini yozing", key="n_ki_d")
        
        naryad_submitted = st.form_submit_button("💾 Saqlash va SMS Navbatiga Qo'shish", type="primary")

    if naryad_submitted:
        naryad_selections = []
        for s in qosh_zal: naryad_selections.append((s, 11))
        for s in zina: naryad_selections.append((s, 12))
        for s in kirxona: naryad_selections.append((s, 13))
        for s in sabzavotxona: naryad_selections.append((s, 14))
        for s in manaviyat: naryad_selections.append((s, 15))
        for s in kladovka: naryad_selections.append((s, 16))
        for s in n_ka_oshxona: naryad_selections.append((s, 21))
        for s in n_ki_oshxona: naryad_selections.append((s, 22))
        for s in n_ka_dush: naryad_selections.append((s, 23))
        for s in n_ki_dush: naryad_selections.append((s, 24))
        
        if not naryad_selections:
            st.warning("Hech kim tanlanmadi!")
        else:
            try:
                # 1. Asosiy Jadvalga yozish
                headers = sheet.row_values(1)
                if naryad_date_str not in headers:
                    sheet.update_cell(1, len(headers) + 1, naryad_date_str)
                    headers = sheet.row_values(1)
                
                date_col_idx = headers.index(naryad_date_str) + 1
                queue_sheet = get_queue_sheet()
                # Toshkent vaqti (UTC+5)
                timestamp = (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
                
                progress_bar = st.progress(0)
                
                for i, (student_str, type_id) in enumerate(naryad_selections):
                    idx = naryad_student_options.index(student_str)
                    row_idx = idx + 2
                    
                    # Asosiy jadvalga ID yozish
                    sheet.update_cell(row_idx, date_col_idx, type_id)
                    
                    # SMS Navbatiga yozish (kun bilan)
                    phone = df.at[idx, 'telefon raqami']
                    joy_nomi = NARYAD_NAMES[type_id]
                    msg = f"Siz {naryad_kunlar} kunga {joy_nomi}ga naryadchisiz. Ishingizga omad!"
                    
                    # [TELEFON, XABAR, STATUS, VAQT]
                    queue_sheet.append_row([phone, msg, "PENDING", timestamp])
                    
                    progress_bar.progress((i + 1) / len(naryad_selections))
                
                # ADMINGA XABAR YUBORISH
                send_telegram_alert("🚨 DIQQAT: Yangi naryadchilar belgilandi!\n\n📲 Iltimos, telefoningizdagi 'SMS Widget' tugmasini bosing.")
                
                # TTJ GURUHIGA XABAR YUBORISH
                naryad_group_msg = f"🛠 <b>Naryad ({naryad_date_str}) - {naryad_kunlar} kunga</b>\n\n"
                
                naryad_items = [
                    ("🏠", "Qo'shimcha Zal", qosh_zal),
                    ("🪜", "Zina", zina),
                    ("🧹", "Kirxona", kirxona),
                    ("🥕", "Sabzavotxona", sabzavotxona),
                    ("📚", "Manaviyat", manaviyat),
                    ("📦", "Kladovka", kladovka),
                    ("🍳", "Katta Oshxona", n_ka_oshxona),
                    ("🥪", "Kichik Oshxona", n_ki_oshxona),
                    ("🚿", "Katta Dush", n_ka_dush),
                    ("🛁", "Kichik Dush", n_ki_dush),
                ]
                
                for emoji, name, students in naryad_items:
                    if students:
                        naryad_group_msg += f"{emoji} <b>{name}:</b>\n"
                        for s in students:
                            naryad_group_msg += f"  • {s}\n"
                        naryad_group_msg += "\n"
                
                naryad_group_msg += "✅ <i>Ishingizga omad!</i>"
                send_to_ttj_group(naryad_group_msg)

                st.success("✅ Muvaffaqiyatli saqlandi! SMSlar navbatga qo'shildi. Telefoningiz internetga ulanganda ular avtomatik ketadi.")
                st.rerun()
                
            except Exception as e:
                st.error(f"Xatolik: {e}")

    st.markdown("---")
    st.subheader("📋 Asosiy Jadval")
    st.dataframe(df, use_container_width=True)
    
    # Naryad statistikasi
    st.subheader("🏆 Naryad Statistikasi")
    date_cols = [c for c in df.columns if len(str(c)) == 10 and c[4] == '.' and c[7] == '.']
    
    if date_cols:
        naryad_stats = df[['ism familiya', 'xona']].copy()
        # Naryad IDlari: 11-17 va 21-24
        def count_naryad(row):
            count = 0
            for col in date_cols:
                val = str(row[col]).strip()
                if val.isdigit():
                    num = int(val)
                    if (num >= 11 and num <= 17) or (num >= 21 and num <= 24):
                        count += 1
            return count
        
        naryad_stats['Jami Naryad'] = df.apply(count_naryad, axis=1)
        naryad_stats = naryad_stats.sort_values(by="Jami Naryad", ascending=False).reset_index(drop=True)
        st.dataframe(naryad_stats, use_container_width=True)
        st.bar_chart(naryad_stats.set_index("ism familiya")["Jami Naryad"])
    else:
        st.warning("Hozircha hech qanday ma'lumot yo'q.")

with tab3:
    st.subheader("🏆 Navbatchilik Statistikasi")
    
    # Faqat sana ustunlarini ajratib olish (regex yordamida YYYY.MM.DD)
    date_cols = [c for c in df.columns if len(str(c)) == 10 and c[4] == '.' and c[7] == '.']
    
    if not date_cols:
        st.warning("Hozircha hech qanday ma'lumot yo'q.")
    else:
        # Har bir talaba uchun navbatchiliklarni sanash (faqat 1-4 IDlar)
        stats = df[['ism familiya', 'xona']].copy()
        
        def count_navbatchilik(row):
            count = 0
            for col in date_cols:
                val = str(row[col]).strip()
                if val.isdigit() and int(val) >= 1 and int(val) <= 4:
                    count += 1
            return count
        
        stats['Jami Navbatchilik'] = df.apply(count_navbatchilik, axis=1)
        
        # Saralash (Eng ko'p navbatchi bo'lganlar tepad)
        stats = stats.sort_values(by="Jami Navbatchilik", ascending=False).reset_index(drop=True)
        
        st.dataframe(stats, use_container_width=True)
        
        # Grafik
        st.bar_chart(stats.set_index("ism familiya")["Jami Navbatchilik"])

# ============================================================================
# YO'QLAMA TIZIMI - FACE RECOGNITION
# ============================================================================
with tab4:
    st.subheader("📸 Face ID Yo'qlama Tizimi")
    
    # Sub-tablar (yangi tartib)
    yoqlama_tab1, yoqlama_tab2, yoqlama_tab3 = st.tabs([
        "📸 Yo'qlama Olish",
        "📋 Yo'qlama Tarixi",
        "👤 Talaba Ro'yxatdan O'tkazish"
    ])
    
    # --- YO'QLAMA OLISH (1-tab) ---
    with yoqlama_tab1:
        st.markdown("### 📸 Yo'qlama Olish")
        st.info("📌 Kamerani oching yoki rasm yuklang. Tizim avtomatik yuzlarni aniqlaydi.")
        
        # Rasm olish usuli
        input_method = st.radio(
            "Rasm olish usuli",
            ["📷 Kameradan olish", "📁 Fayl yuklash"],
            horizontal=True,
            key="attendance_method"
        )
        
        frame_image = None
        
        if input_method == "📷 Kameradan olish":
            camera_image = st.camera_input("📷 Guruh rasmini oling")
            if camera_image:
                frame_image = camera_image.read()
        else:
            uploaded_frame = st.file_uploader(
                "Guruh rasmini yuklang",
                type=["jpg", "jpeg", "png"],
                key="attendance_image"
            )
            if uploaded_frame:
                st.image(uploaded_frame, caption="Yuklangan guruh rasmi", use_container_width=True)
                frame_image = uploaded_frame.read()
        
        if st.button("🔍 Yo'qlama Olish", type="primary", disabled=frame_image is None):
            if frame_image:
                with st.spinner("Yuzlar aniqlanmoqda..."):
                    try:
                        import base64
                        import sys
                        import os
                        
                        yangi_path = os.path.join(os.path.dirname(__file__), "yangi")
                        if yangi_path not in sys.path:
                            sys.path.insert(0, yangi_path)
                        
                        try:
                            import face_module as fm
                            
                            image_base64 = base64.b64encode(frame_image).decode()
                            result = fm.take_attendance(image_base64)
                            
                            # Natijalar
                            col1, col2, col3 = st.columns(3)
                            col1.metric("👥 Jami", result["total"])
                            col2.metric("✅ Borlar", result["present_count"])
                            col3.metric("❌ Yo'qlar", result["absent_count"])
                            
                            st.markdown("---")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown("### ✅ Kelganlar")
                                if result["present"]:
                                    for p in result["present"]:
                                        st.write(f"✅ {p['name']}")
                                else:
                                    st.warning("Hech kim aniqlanmadi")
                            
                            with c2:
                                st.markdown("### ❌ Kelmayganlar")
                                if result["absent"]:
                                    for a in result["absent"]:
                                        st.write(f"❌ {a['name']}")
                                else:
                                    st.success("Hamma kelgan!")
                            
                            log_activity("Yo'qlama olindi", f"Borlar: {result['present_count']}, Yo'qlar: {result['absent_count']}")
                            
                        except ImportError:
                            st.error("⚠️ Face recognition moduli yuklanmadi!")
                            st.code("pip install face_recognition", language="bash")
                            
                    except Exception as e:
                        st.error(f"Xatolik: {e}")
    
    # --- YO'QLAMA TARIXI (2-tab) ---
    with yoqlama_tab2:
        st.markdown("### 📋 Yo'qlama Tarixi")
        st.info("🚧 Bu bo'lim tez orada qo'shiladi...")
        # TODO: Google Sheetsda yo'qlama tarixini saqlash
    
    # --- TALABA RO'YXATDAN O'TKAZISH (3-tab) ---
    with yoqlama_tab3:
        st.markdown("### 👤 Talaba Yuzini Ro'yxatdan O'tkazish")
        st.info("📌 Har bir talabani bir marta ro'yxatdan o'tkazish kerak.")
        
        # Talaba tanlash
        student_options_for_face = sorted(df.apply(lambda x: f"{x['ism familiya']} ({x['xona']})", axis=1).tolist())
        selected_student = st.selectbox(
            "Talabani tanlang",
            options=student_options_for_face,
            placeholder="Ism yoki xona raqamini yozing...",
            key="register_student"
        )
        
        st.markdown("---")
        
        # Rasm olish usuli
        register_method = st.radio(
            "Rasm olish usuli",
            ["📷 Kameradan olish", "📁 Fayl yuklash"],
            horizontal=True,
            key="register_method"
        )
        
        face_image = None
        face_detected = False
        
        if register_method == "📷 Kameradan olish":
            camera_face = st.camera_input("📷 Talaba yuzini rasmga oling", key="register_camera")
            if camera_face:
                face_image = camera_face.read()
        else:
            uploaded_face = st.file_uploader(
                "Talaba yuz rasmini yuklang",
                type=["jpg", "jpeg", "png"],
                help="Aniq ko'rinadigan yuz rasmi yuklang",
                key="register_upload"
            )
            if uploaded_face:
                face_image = uploaded_face.read()
        
        # Yuz aniqlash va ko'rsatish
        if face_image:
            try:
                import base64
                import sys
                import os
                
                yangi_path = os.path.join(os.path.dirname(__file__), "yangi")
                if yangi_path not in sys.path:
                    sys.path.insert(0, yangi_path)
                
                try:
                    import face_module as fm
                    
                    # Yuz aniqlash
                    image_base64 = base64.b64encode(face_image).decode()
                    detection = fm.detect_face_in_image(image_base64)
                    
                    if detection["found"]:
                        face_detected = True
                        st.success(detection["message"])
                        
                        # Yashil ramkali rasmni ko'rsatish
                        if detection["image_with_boxes"]:
                            st.image(
                                base64.b64decode(detection["image_with_boxes"]),
                                caption="✅ Yuz aniqlandi!",
                                width=300
                            )
                        else:
                            # Oddiy rasmni ko'rsatish
                            st.image(face_image, caption="✅ Yuz topildi!", width=200)
                    else:
                        face_detected = False
                        st.error(detection["message"])
                        st.image(face_image, caption="❌ Yuz topilmadi", width=200)
                        
                except ImportError:
                    # Face module yuklanmasa, oddiy ko'rsatish
                    st.image(face_image, caption="Yuklangan rasm", width=200)
                    st.warning("⚠️ Yuz aniqlash moduli yuklanmadi. Lekin davom etishingiz mumkin.")
                    face_detected = True  # Davom etish imkonini berish
                    
            except Exception as e:
                st.image(face_image, caption="Yuklangan rasm", width=200)
                st.warning(f"⚠️ Yuz tekshirib bo'lmadi: {e}")
                face_detected = True  # Davom etish imkonini berish
        
        if st.button("✅ Ro'yxatdan O'tkazish", type="primary", disabled=face_image is None):
            if selected_student and face_image:
                try:
                    import base64
                    import sys
                    import os
                    
                    yangi_path = os.path.join(os.path.dirname(__file__), "yangi")
                    if yangi_path not in sys.path:
                        sys.path.insert(0, yangi_path)
                    
                    try:
                        import face_module as fm
                        
                        student_idx = student_options_for_face.index(selected_student)
                        student_id = str(student_idx).zfill(3)
                        student_name = selected_student.split(" (")[0]
                        
                        image_base64 = base64.b64encode(face_image).decode()
                        result = fm.register_student(student_id, student_name, image_base64)
                        
                        if result["success"]:
                            st.success(result["message"])
                            log_activity("Yo'qlama ro'yxatidan o'tkazish", f"{student_name} ro'yxatdan o'tdi")
                        else:
                            st.error(result["message"])
                            
                    except ImportError:
                        st.warning("⚠️ Face recognition moduli yuklanmadi.")
                        st.code("pip install face_recognition", language="bash")
                        
                except Exception as e:
                    st.error(f"Xatolik: {e}")
        
        # Ro'yxatdan o'tgan talabalar
        st.markdown("---")
        st.markdown("### 📋 Ro'yxatdan O'tgan Talabalar")
        
        try:
            import sys
            import os
            yangi_path = os.path.join(os.path.dirname(__file__), "yangi")
            if yangi_path not in sys.path:
                sys.path.insert(0, yangi_path)
            
            try:
                import face_module as fm
                registered = fm.get_registered_students()
                
                if registered:
                    st.success(f"✅ Jami: {len(registered)} talaba ro'yxatdan o'tgan")
                    for s in registered:
                        col1, col2 = st.columns([4, 1])
                        col1.write(f"👤 {s['name']}")
                        if col2.button("🗑️", key=f"del_{s['id']}"):
                            fm.delete_student(s['id'])
                            st.rerun()
                else:
                    st.info("Hali hech kim ro'yxatdan o'tmagan")
            except ImportError:
                st.info("📌 Face recognition moduli hali o'rnatilmagan")
        except:
            st.info("📌 Ro'yxatdagi talabalarni ko'rish uchun lokal server kerak")
        
        # --- MA'LUMOTNI TAHRIRLASH ---
        st.markdown("---")
        st.markdown("### ✏️ Talaba Ma'lumotlarini Tahrirlash")
        st.info("📌 Ism, familiya, xona raqami yoki yuz rasmini o'zgartirish uchun talabani tanlang.")
        
        # Qidiruv
        search_query = st.text_input(
            "🔍 Qidirish",
            placeholder="Ism, familiya yoki xona raqamini kiriting...",
            key="search_student"
        )
        
        # Filtrlash
        if search_query:
            filtered_students = df[
                df['ism familiya'].str.contains(search_query, case=False, na=False) |
                df['xona'].astype(str).str.contains(search_query, case=False, na=False)
            ]
        else:
            filtered_students = df
        
        if len(filtered_students) > 0:
            # Talabani tanlash
            edit_options = filtered_students.apply(
                lambda x: f"{x['ism familiya']} ({x['xona']})", axis=1
            ).tolist()
            
            selected_for_edit = st.selectbox(
                "Tahrirlash uchun talabani tanlang",
                options=edit_options,
                key="edit_student_select"
            )
            
            if selected_for_edit:
                # Tanlangan talabaning indeksini topish
                selected_idx = edit_options.index(selected_for_edit)
                original_row = filtered_students.iloc[selected_idx]
                
                # Joriy ma'lumotlarni ko'rsatish
                st.markdown(f"**📋 Joriy ma'lumotlar:**")
                
                # Joriy yuz rasmini ko'rsatish
                import os as os_module
                faces_dir = os_module.path.join(os_module.path.dirname(__file__), "yangi", "faces")
                
                # Talaba ID sini topish
                original_df_idx = df[
                    (df['ism familiya'] == original_row['ism familiya']) &
                    (df['xona'].astype(str) == str(original_row['xona']))
                ].index[0]
                current_student_id = str(original_df_idx).zfill(3)
                current_face_path = os_module.path.join(faces_dir, f"{current_student_id}.jpg")
                
                img_col, info_col = st.columns([1, 3])
                
                with img_col:
                    if os_module.path.exists(current_face_path):
                        st.image(current_face_path, caption="Joriy rasm", width=100)
                    else:
                        st.info("📷 Rasm yo'q")
                
                with info_col:
                    st.info(f"👤 {original_row['ism familiya']}")
                    st.info(f"🏠 Xona: {original_row['xona']}")
                    if 'telefon raqami' in original_row:
                        st.info(f"📱 {original_row['telefon raqami']}")
                
                st.markdown("---")
                st.markdown("**✏️ Yangi ma'lumotlarni kiriting:**")
                
                # Tahrirlash formasi
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input(
                        "Ism Familiya",
                        value=original_row['ism familiya'],
                        key=f"edit_name_{selected_idx}"
                    )
                
                with col2:
                    new_xona = st.text_input(
                        "Xona raqami",
                        value=str(original_row['xona']),
                        key=f"edit_xona_{selected_idx}"
                    )
                
                # Telefon raqami
                if 'telefon raqami' in original_row:
                    new_phone = st.text_input(
                        "Telefon raqami",
                        value=str(original_row['telefon raqami']),
                        key=f"edit_phone_{selected_idx}"
                    )
                else:
                    new_phone = None
                
                # Yuz rasmini o'zgartirish
                st.markdown("---")
                st.markdown("**📷 Yuz Rasmini O'zgartirish (ixtiyoriy):**")
                
                edit_face_method = st.radio(
                    "Rasm olish usuli",
                    ["❌ O'zgartirmaslik", "📷 Kameradan olish", "📁 Fayl yuklash"],
                    horizontal=True,
                    key=f"edit_face_method_{selected_idx}"
                )
                
                new_face_image = None
                
                if edit_face_method == "📷 Kameradan olish":
                    edit_camera = st.camera_input("📷 Yangi yuz rasmi", key=f"edit_camera_{selected_idx}")
                    if edit_camera:
                        new_face_image = edit_camera.read()
                elif edit_face_method == "📁 Fayl yuklash":
                    edit_upload = st.file_uploader(
                        "Yangi yuz rasmini yuklang",
                        type=["jpg", "jpeg", "png"],
                        key=f"edit_upload_{selected_idx}"
                    )
                    if edit_upload:
                        st.image(edit_upload, caption="Yangi rasm", width=150)
                        new_face_image = edit_upload.read()
                
                # Saqlash tugmasi
                if st.button("💾 O'zgarishlarni Saqlash", type="primary", key=f"save_edit_{selected_idx}"):
                    try:
                        # Google Sheetdagi qatorni yangilash
                        original_df_idx = df[
                            (df['ism familiya'] == original_row['ism familiya']) &
                            (df['xona'].astype(str) == str(original_row['xona']))
                        ].index[0]
                        
                        sheet = get_main_sheet()
                        row_number = original_df_idx + 2  # Header + 0-index
                        
                        # Ism Familiyani yangilash (1-ustun)
                        sheet.update_cell(row_number, 1, new_name)
                        
                        # Xonani yangilash (2-ustun)
                        sheet.update_cell(row_number, 2, new_xona)
                        
                        # Telefon raqamini yangilash (3-ustun)
                        if new_phone:
                            sheet.update_cell(row_number, 3, new_phone)
                        
                        # Yuz rasmini yangilash
                        if new_face_image:
                            try:
                                import base64
                                import sys
                                import os
                                
                                yangi_path = os.path.join(os.path.dirname(__file__), "yangi")
                                if yangi_path not in sys.path:
                                    sys.path.insert(0, yangi_path)
                                
                                import face_module as fm
                                
                                student_id = str(original_df_idx).zfill(3)
                                image_base64 = base64.b64encode(new_face_image).decode()
                                
                                # Eski yuzni o'chirish va yangisini qo'shish
                                fm.delete_student(student_id)
                                fm.register_student(student_id, new_name, image_base64)
                                
                                st.success(f"✅ {new_name} - ma'lumotlar va yuz rasmi yangilandi!")
                            except ImportError:
                                st.success(f"✅ {new_name} ma'lumotlari saqlandi! (Yuz rasmi alohida o'zgartiring)")
                        else:
                            st.success(f"✅ {new_name} ma'lumotlari saqlandi!")
                        
                        log_activity("Talaba ma'lumoti tahrirlandi", f"{original_row['ism familiya']} → {new_name}")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Xatolik: {e}")
        else:
            st.warning("Qidiruv natijasi topilmadi")

