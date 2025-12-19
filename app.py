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
TTJ_GROUP_ID = "2623014807"  # TTJ guruhi

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

    if st.session_state.get("password_correct", False):
        return True

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
        
        # Form (Enter bilan ishlaydi)
        with st.form("login_form"):
            password = st.text_input("Parolni kiriting", type="password", placeholder="Parolni kiriting va Enter bosing...", label_visibility="collapsed")
            submit_button = st.form_submit_button("🚀 Kirish", use_container_width=True)

            if submit_button:
                # Parolni tekshirish (bo'sh joylarni olib tashlab)
                if password.strip() == st.secrets["password"]:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("😕 Parol xato! Qaytadan urinib ko'ring.")
        
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
tab1, tab2, tab3 = st.tabs(["📝 Navbatchilik", "�️ Naryad", "�📊 Statistika"])

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

