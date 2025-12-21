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

def send_telegram_to_student(telegram_id, message, student_name=""):
    """Talabaga shaxsiy Telegram xabar yuborish"""
    if not telegram_id:
        return False
    
    # telegram_id ni tozalash
    tg_id = str(telegram_id).replace(".0", "").strip()
    if not tg_id or tg_id == "nan" or len(tg_id) < 5:
        return False
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(url, data={
            "chat_id": tg_id,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        
        if response.status_code == 200:
            # Muvaffaqiyatli - adminga xabar
            send_telegram_alert(f"✅ TG: {student_name} ({tg_id}) - xabar yuborildi")
            return True
        else:
            send_telegram_alert(f"❌ TG: {student_name} ({tg_id}) - xato: {response.status_code}")
            return False
    except Exception as e:
        send_telegram_alert(f"❌ TG: {student_name} ({tg_id}) - xato: {str(e)[:50]}")
        return False

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

# Tugmalarni yashil qilish uchun CSS
st.markdown("""
<style>
    /* Primary tugmalarni yashil qilish */
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
    /* Form submit tugmalari */
    .stFormSubmitButton > button {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
        color: white !important;
    }
    .stFormSubmitButton > button:hover {
        background-color: #218838 !important;
    }
</style>
""", unsafe_allow_html=True)

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
        ws = client.open(GOOGLE_SHEET_NAME).add_worksheet(title="SMS_QUEUE", rows="500", cols="5")
        ws.append_row(["TELEFON", "XABAR", "STATUS", "VAQT", "ISM"])
        return ws

def validate_phone(phone):
    """Telefon raqamini tekshirish va tozalash"""
    if not phone:
        return None
    phone = str(phone).replace("+", "").replace(" ", "").replace("-", "")
    phone = phone.replace("(", "").replace(")", "").replace(".0", "")
    phone = ''.join(filter(str.isdigit, phone))
    if len(phone) < 9:
        return None
    if len(phone) == 9:
        phone = "998" + phone
    return phone

def add_to_sms_queue(queue_sheet, phone, message, student_name=""):
    """SMS navbatiga xavfsiz qo'shish"""
    clean_phone = validate_phone(phone)
    if not clean_phone:
        return False
    timestamp = (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
    queue_sheet.append_row([clean_phone, message, "PENDING", timestamp, student_name])
    return True

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
tab1, tab2, tab3, tab4 = st.tabs(["📝 Navbatchilik", "🛠️ Naryad", "📊 Statistika", "📨 Xabarlar"])

with tab1:
    # --- UI ---
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_date = st.date_input("Sanani tanlang", datetime.now(), key="navbatchilik_date")
        date_str = selected_date.strftime("%Y.%m.%d")
    st.info(f"Tanlangan sana: **{date_str}**")

    # Ism va Xona bo'yicha saralash (o'sish tartibida)
    # Har bir talaba uchun display string va original index mapping
    student_display_to_idx = {}
    for idx, row in df.iterrows():
        display_str = f"{row['ism familiya']} ({row['xona']})"
        student_display_to_idx[display_str] = idx
    
    student_options = sorted(student_display_to_idx.keys())

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
                    # To'g'ri indeksni olish (mapping orqali)
                    idx = student_display_to_idx[student_str]
                    row_idx = idx + 2
                    
                    # Asosiy jadvalga ID yozish
                    sheet.update_cell(row_idx, date_col_idx, type_id)
                    
                    # SMS Navbatiga yozish (validatsiya bilan)
                    phone = df.at[idx, 'telefon raqami']
                    student_name = df.at[idx, 'ism familiya']
                    msg = SMS_TEMPLATES[type_id]
                    add_to_sms_queue(queue_sheet, phone, msg, student_name)
                    
                    # Telegramga xabar yuborish (agar telegram_id bo'lsa)
                    if 'telegram_id' in df.columns:
                        tg_id = df.at[idx, 'telegram_id']
                        send_telegram_alert(f"🔍 DEBUG: {student_name} - tg_id = '{tg_id}'")
                        tg_msg = f"📋 <b>Navbatchilik</b>\n\n{msg}\n\n📅 Sana: {date_str}"
                        send_telegram_to_student(tg_id, tg_msg, student_name)
                    else:
                        send_telegram_alert(f"⚠️ telegram_id ustuni topilmadi! Ustunlar: {list(df.columns)}")
                    
                
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

    # Ism va Xona bo'yicha saralash (mapping bilan)
    naryad_display_to_idx = {}
    for idx, row in df.iterrows():
        display_str = f"{row['ism familiya']} ({row['xona']})"
        naryad_display_to_idx[display_str] = idx
    
    naryad_student_options = sorted(naryad_display_to_idx.keys())

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
                    # To'g'ri indeksni olish (mapping orqali)
                    idx = naryad_display_to_idx[student_str]
                    row_idx = idx + 2
                    
                    # Asosiy jadvalga ID yozish
                    sheet.update_cell(row_idx, date_col_idx, type_id)
                    
                    # SMS Navbatiga yozish (kun bilan)
                    phone = df.at[idx, 'telefon raqami']
                    student_name = df.at[idx, 'ism familiya']
                    joy_nomi = NARYAD_NAMES[type_id]
                    msg = f"Siz {naryad_kunlar} kunga {joy_nomi}ga naryadchisiz. Ishingizga omad!"
                    add_to_sms_queue(queue_sheet, phone, msg, student_name)
                    
                    # Telegramga xabar yuborish (agar telegram_id bo'lsa)
                    if 'telegram_id' in df.columns:
                        tg_id = df.at[idx, 'telegram_id']
                        tg_msg = f"🛠 <b>Naryad</b>\n\n{msg}\n\n📅 Sana: {naryad_date_str}"
                        send_telegram_to_student(tg_id, tg_msg, student_name)
                    
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
        
        def count_naryad_stat(row):
            count = 0
            for col in date_cols:
                val = str(row[col]).strip()
                if val.isdigit():
                    num = int(val)
                    if (num >= 11 and num <= 17) or (num >= 21 and num <= 24):
                        count += 1
            return count
        
        stats['Navbatchilik'] = df.apply(count_navbatchilik, axis=1)
        stats['Naryad'] = df.apply(count_naryad_stat, axis=1)
        stats['Jami'] = stats['Navbatchilik'] + stats['Naryad']
        
        # Saralash (Eng ko'p navbatchi bo'lganlar tepada)
        stats = stats.sort_values(by="Jami", ascending=False).reset_index(drop=True)
        
        st.dataframe(stats, use_container_width=True)
    
    # ============================================================================
    # XONALAR BO'YICHA STATISTIKA
    # ============================================================================
    st.markdown("---")
    st.subheader("🏠 Xonalar Bo'yicha Statistika")
    
    if date_cols:
        # Xonalarni guruhlash
        xona_stats = df.groupby('xona').apply(
            lambda x: pd.Series({
                'Talabalar soni': len(x),
                'Navbatchilik': x.apply(count_navbatchilik, axis=1).sum(),
                'Naryad': x.apply(count_naryad_stat, axis=1).sum()
            })
        ).reset_index()
        xona_stats['Jami'] = xona_stats['Navbatchilik'] + xona_stats['Naryad']
        xona_stats = xona_stats.sort_values(by='Jami', ascending=False).reset_index(drop=True)
        
        st.dataframe(xona_stats, use_container_width=True)
    
    # ============================================================================
    # TALABANI QIDIRISH
    # ============================================================================
    st.markdown("---")
    st.subheader("🔍 Talabani Qidirish")
    
    search_student_options = sorted(df.apply(lambda x: f"{x['ism familiya']} ({x['xona']})", axis=1).tolist())
    
    # Session state
    if "show_student_details" not in st.session_state:
        st.session_state.show_student_details = False
        st.session_state.selected_student_name = None
    
    # Qidirish formasi - form ichida sahifa yangilanmaydi
    with st.form("search_form"):
        selected_search = st.selectbox(
            "Talabani tanlang yoki qidiring",
            options=search_student_options,
            index=None,
            placeholder="Ism yoki xona raqamini yozing...",
            key="search_student_stats"
        )
        
        search_submitted = st.form_submit_button("🔍 Qidirish", type="primary", use_container_width=True)
        
        if search_submitted and selected_search:
            st.session_state.show_student_details = True
            st.session_state.selected_student_name = selected_search
    
    # Agar qidirilgan bo'lsa, natijani ko'rsatish
    if st.session_state.show_student_details and st.session_state.selected_student_name and date_cols:
        selected_search = st.session_state.selected_student_name
        
        # Tanlangan talabani topish
        search_idx = search_student_options.index(selected_search)
        student_row = df.iloc[search_idx]
        student_name = student_row['ism familiya']
        student_xona = student_row['xona']
        
        st.markdown("---")
        st.markdown(f"### 👤 {student_name}")
        st.info(f"🏠 Xona: {student_xona}")
        
        # Joy nomlari
        joy_nomlari = {
            1: "🍳 Katta Oshxona",
            2: "🥪 Kichik Oshxona", 
            3: "🚿 Katta Dush",
            4: "🛁 Kichik Dush",
            11: "🏠 Qo'shimcha Zal",
            12: "🪜 Zina",
            13: "🧹 Kirxona",
            14: "🥕 Sabzavotxona",
            15: "📚 Manaviyat",
            16: "📦 Kladovka",
            21: "🍳 K.Oshxona (Naryad)",
            22: "🥪 Ki.Oshxona (Naryad)",
            23: "🚿 K.Dush (Naryad)",
            24: "🛁 Ki.Dush (Naryad)"
        }
        
        # Statistikani hisoblash - sanalar bilan
        navbatchilik_count = 0
        naryad_count = 0
        joy_statistika = {}  # {joy_nomi: [sana1, sana2, ...]}
        
        for col in date_cols:
            val = str(student_row[col]).strip()
            if val.isdigit():
                num = int(val)
                joy_nomi = joy_nomlari.get(num, f"Noma'lum ({num})")
                
                if num >= 1 and num <= 4:
                    navbatchilik_count += 1
                elif (num >= 11 and num <= 17) or (num >= 21 and num <= 24):
                    naryad_count += 1
                
                # Sanani qo'shish
                if joy_nomi not in joy_statistika:
                    joy_statistika[joy_nomi] = []
                joy_statistika[joy_nomi].append(col)
        
        # Umumiy statistika
        col1, col2, col3 = st.columns(3)
        col1.metric("📝 Navbatchilik", navbatchilik_count)
        col2.metric("🛠️ Naryad", naryad_count)
        col3.metric("📊 Jami", navbatchilik_count + naryad_count)
        
        # Joy bo'yicha batafsil taqsimot
        if joy_statistika:
            st.markdown("#### 📍 Batafsil Ma'lumot:")
            
            # Saralash (eng ko'p birinchi)
            sorted_joy = sorted(joy_statistika.items(), key=lambda x: len(x[1]), reverse=True)
            
            for joy, sanalar in sorted_joy:
                soni = len(sanalar)
                sanalar_str = ", ".join(sanalar)
                
                # Expander ichida ko'rsatish
                with st.expander(f"{joy} - **{soni} marta**", expanded=False):
                    st.markdown(f"**📅 Sanalar:** {sanalar_str}")
                    
                    # Jadval ko'rinishida
                    if soni > 0:
                        for i, sana in enumerate(sanalar, 1):
                            st.write(f"  {i}. {sana}")
        else:
            st.info("Bu talaba hali hech qayerga tayinlanmagan")
        
        # Yopish tugmasi
        if st.button("❌ Yopish", key="close_student_details"):
            st.session_state.show_student_details = False
            st.session_state.selected_student_name = None
            st.rerun()

# ============================================================================
# XABARLAR BO'LIMI - SMS Yuborish
# ============================================================================
with tab4:
    st.subheader("📨 Xabarlar - Tanlangan Talabalarga SMS Yuborish")
    st.info("📌 Xabar yozing va qaysi talabalarga yuborishni tanlang. SMS navbatga qo'shiladi.")
    
    # Talabalar ro'yxati (mapping bilan)
    xabar_display_to_idx = {}
    for idx, row in df.iterrows():
        display_str = f"{row['ism familiya']} ({row['xona']})"
        xabar_display_to_idx[display_str] = idx
    
    xabar_student_options = sorted(xabar_display_to_idx.keys())
    
    with st.form("xabar_form"):
        # Xabar matni
        st.markdown("##### ✍️ Xabar Matni")
        xabar_matni = st.text_area(
            "Xabarni kiriting",
            placeholder="Masalan: Hamma xonasiga qarasin! Bugun tekshiruv bo'ladi.",
            height=100,
            help="Bu xabar tanlangan barcha talabalarga SMS orqali yuboriladi"
        )
        
        st.markdown("---")
        
        # Tez tanlash
        st.markdown("##### 👥 Qabul qiluvchilar")
        
        tez_tanlash = st.radio(
            "Tanlash usuli",
            ["🎯 Alohida tanlash", "👥 Hammaga yuborish"],
            horizontal=True
        )
        
        if tez_tanlash == "🎯 Alohida tanlash":
            # Alohida talabalar tanlash
            tanlangan_talabalar = st.multiselect(
                "Talabalarni tanlang",
                options=xabar_student_options,
                placeholder="Ism yoki xona raqamini yozing...",
                help="Bir nechta talaba tanlashingiz mumkin"
            )
        else:
            tanlangan_talabalar = xabar_student_options  # Hammasi
            st.success(f"✅ Barcha {len(xabar_student_options)} ta talaba tanlandi")
        
        xabar_submitted = st.form_submit_button("📤 Xabarni Yuborish", type="primary")
    
    if xabar_submitted:
        if not xabar_matni.strip():
            st.warning("⚠️ Xabar matnini kiriting!")
        elif not tanlangan_talabalar:
            st.warning("⚠️ Kamida bitta talaba tanlang!")
        else:
            try:
                queue_sheet = get_queue_sheet()
                timestamp = (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
                
                progress_bar = st.progress(0)
                yuborilgan = 0
                
                for i, student_str in enumerate(tanlangan_talabalar):
                    # To'g'ri indeksni olish (mapping orqali)
                    idx = xabar_display_to_idx[student_str]
                    phone = df.at[idx, 'telefon raqami']
                    student_name = df.at[idx, 'ism familiya']
                    
                    # SMS navbatga qo'shish (validatsiya bilan)
                    if add_to_sms_queue(queue_sheet, phone, xabar_matni.strip(), student_name):
                        yuborilgan += 1
                    progress_bar.progress((i + 1) / len(tanlangan_talabalar))
                
                # Admin xabari
                send_telegram_alert(f"📨 YANGI XABAR YUBORILDI!\n\n👥 {yuborilgan} ta talabaga\n📝 Xabar: {xabar_matni[:50]}...\n\n📲 SMS Widget tugmasini bosing!")
                
                st.success(f"✅ Xabar {yuborilgan} ta talabaga navbatga qo'shildi!")
                st.info("📱 Telefoningiz internetga ulanganda SMSlar avtomatik yuboriladi.")
                
                log_activity("Xabar yuborildi", f"{yuborilgan} ta talabaga: {xabar_matni[:30]}...")
                
            except Exception as e:
                st.error(f"Xatolik: {e}")
    
    # Qo'shimcha: Tayyor shablonlar bilan tugmalar
    st.markdown("---")
    st.markdown("##### 📋 Tez Yuborish Shablonlari")
    st.info("👆 Tugmani bosing, talabalarni tanlang va xabar avtomatik yuboriladi!")
    
    # Shablonlar ro'yxati
    shablonlar = [
        ("🏠", "Xonangizga qarang, tekshiruv bo'ladi!"),
        ("🚿", "Dush soat 22:00 da yopiladi"),
        ("📚", "Ertaga dars bo'lmaydi"),
        ("⚠️", "Zudlik bilan yig'ilishga keling!"),
        ("🔔", "Komendant chaqirmoqda"),
        ("📞", "Telefon raqamingizni yangilang"),
    ]
    
    # Session state uchun
    if "shablon_xabar" not in st.session_state:
        st.session_state.shablon_xabar = None
    
    # Tugmalar qatori
    shablon_cols = st.columns(3)
    
    for i, (emoji, matn) in enumerate(shablonlar):
        col_idx = i % 3
        with shablon_cols[col_idx]:
            if st.button(f"{emoji} {matn[:20]}...", key=f"shablon_{i}", use_container_width=True):
                st.session_state.shablon_xabar = matn
    
    # Agar shablon tanlangan bo'lsa
    if st.session_state.shablon_xabar:
        st.markdown("---")
        st.success(f"📝 Tanlangan xabar: **{st.session_state.shablon_xabar}**")
        
        shablon_display_to_idx = {}
        for idx, row in df.iterrows():
            display_str = f"{row['ism familiya']} ({row['xona']})"
            shablon_display_to_idx[display_str] = idx
        
        shablon_talabalar_options = sorted(shablon_display_to_idx.keys())
        
        shablon_tanlash = st.radio(
            "Kimga yuborish?",
            ["🎯 Alohida tanlash", "👥 Hammaga"],
            horizontal=True,
            key="shablon_qabul"
        )
        
        if shablon_tanlash == "🎯 Alohida tanlash":
            shablon_talabalar = st.multiselect(
                "Talabalarni tanlang",
                options=shablon_talabalar_options,
                placeholder="Ism yoki xona raqamini yozing...",
                key="shablon_talabalar_select"
            )
        else:
            shablon_talabalar = shablon_talabalar_options
            st.info(f"✅ Barcha {len(shablon_talabalar_options)} ta talaba tanlandi")
        
        col_send, col_cancel = st.columns(2)
        
        with col_send:
            if st.button("📤 Yuborish", type="primary", use_container_width=True, key="shablon_send"):
                if shablon_talabalar:
                    try:
                        queue_sheet = get_queue_sheet()
                        timestamp = (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
                        
                        sent_count = 0
                        for student_str in shablon_talabalar:
                            # To'g'ri indeksni olish (mapping orqali)
                            idx = shablon_display_to_idx[student_str]
                            phone = df.at[idx, 'telefon raqami']
                            student_name = df.at[idx, 'ism familiya']
                            if add_to_sms_queue(queue_sheet, phone, st.session_state.shablon_xabar, student_name):
                                sent_count += 1
                        
                        send_telegram_alert(f"📨 TEZ XABAR!\\n\\n👥 {len(shablon_talabalar)} ta talabaga\\n📝 {st.session_state.shablon_xabar}\\n\\n📲 SMS Widget!")
                        
                        st.success(f"✅ {len(shablon_talabalar)} ta talabaga yuborildi!")
                        log_activity("Tez xabar", f"{len(shablon_talabalar)} talabaga: {st.session_state.shablon_xabar[:30]}...")
                        st.session_state.shablon_xabar = None
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Xatolik: {e}")
                else:
                    st.warning("⚠️ Kamida bitta talaba tanlang!")
        
        with col_cancel:
            if st.button("❌ Bekor qilish", use_container_width=True, key="shablon_cancel"):
                st.session_state.shablon_xabar = None
                st.rerun()

