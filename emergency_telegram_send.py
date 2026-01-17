#!/usr/bin/env python3
"""
=============================================================================
EMERGENCY TELEGRAM SENDER - SMS o'rniga Telegram orqali xabar yuborish
=============================================================================
Bu skript SMS navbatidagi PENDING xabarlarni Telegram orqali yuboradi.
SMS ishlamayotgan paytda foydalaning!
=============================================================================
"""

import os
import sys
import requests
import time

# Google Sheets uchun
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    print("O'rnatish: pip install gspread oauth2client requests")
    sys.exit(1)

# =============================================================================
# SOZLAMALAR
# =============================================================================
TELEGRAM_TOKEN = "8259734572:AAGeJLKmmruLByDjx81gdi1VcjNt3ZnX894"
ADMIN_CHAT_ID = "7693191223"

# Google Sheets nomlari
SHEETS = {
    "4-etaj": "Navbatchilik_Jadvali",
    "3-etaj": "TTJ 3-etaj Navbatchilik"
}

# Credentials fayl yo'li
CREDS_FILE = "credentials.json"

# =============================================================================
# FUNKSIYALAR
# =============================================================================

def log(msg, level="INFO"):
    """Log chiqarish"""
    timestamp = time.strftime("%H:%M:%S")
    try:
        print(f"[{timestamp}] [{level}] {msg}")
    except UnicodeEncodeError:
        # Emojilarni olib tashlash
        clean_msg = msg.encode('ascii', 'ignore').decode('ascii')
        print(f"[{timestamp}] [{level}] {clean_msg}")

def send_telegram_to_admin(message):
    """Adminga xabar yuborish"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID, "text": message}, timeout=10)
    except:
        pass

def send_telegram_to_user(telegram_id, message):
    """Foydalanuvchiga Telegram xabar yuborish"""
    if not telegram_id:
        return False
    
    # ID ni tozalash
    tg_id = str(telegram_id).replace(".0", "").strip()
    if not tg_id or tg_id == "nan" or len(tg_id) < 5:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={
            "chat_id": tg_id,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            log(f"Telegram xato: {response.json().get('description', 'Unknown')}", "ERROR")
            return False
    except Exception as e:
        log(f"Telegram xato: {e}", "ERROR")
        return False

def get_google_client():
    """Google Sheets clientini olish"""
    if not os.path.exists(CREDS_FILE):
        log(f"credentials.json topilmadi!", "ERROR")
        return None
    
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        log(f"Google Sheets xato: {e}", "ERROR")
        return None

def get_student_telegram_ids(client, sheet_name):
    """Talabalarning telegram_id larini olish (telefon raqami bo'yicha)"""
    try:
        spreadsheet = client.open(sheet_name)
        main_sheet = spreadsheet.sheet1
        data = main_sheet.get_all_records()
        
        # {telefon_raqami: telegram_id} mapping
        phone_to_telegram = {}
        for row in data:
            phone = str(row.get('telefon raqami', '')).replace('.0', '').strip()
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) == 9:
                phone = "998" + phone
            
            tg_id = str(row.get('telegram_id', '')).replace('.0', '').strip()
            
            if phone and tg_id and tg_id != 'nan':
                phone_to_telegram[phone] = tg_id
        
        return phone_to_telegram
    except Exception as e:
        log(f"Talabalar ma'lumotini olishda xato: {e}", "ERROR")
        return {}

def process_pending_sms(client):
    """PENDING SMSlarni Telegram orqali yuborish"""
    try:
        # 4-etaj sheet'dan SMS_QUEUE ni olish
        spreadsheet = client.open(SHEETS["4-etaj"])
        
        try:
            queue_sheet = spreadsheet.worksheet("SMS_QUEUE")
        except:
            log("SMS_QUEUE topilmadi!", "ERROR")
            return 0, 0
        
        # Barcha talabalarning telegram_id larini olish (har ikkala etajdan)
        all_phone_to_telegram = {}
        for floor, sheet_name in SHEETS.items():
            phone_to_tg = get_student_telegram_ids(client, sheet_name)
            all_phone_to_telegram.update(phone_to_tg)
            log(f"{floor}: {len(phone_to_tg)} ta telegram_id topildi")
        
        # SMS navbatini o'qish
        all_data = queue_sheet.get_all_values()
        
        if len(all_data) <= 1:
            log("SMS navbati bo'sh")
            return 0, 0
        
        sent_count = 0
        not_found = 0
        
        log(f"Jami {len(all_data) - 1} ta SMS navbatda")
        
        for row_idx, row in enumerate(all_data):
            if row_idx == 0:  # Header
                continue
            
            if len(row) < 3:
                continue
            
            phone = row[0]
            message = row[1]
            status = row[2]
            student_name = row[4] if len(row) > 4 else ""
            
            # Faqat PENDING
            if status != "PENDING":
                continue
            
            # Telefon raqamini tozalash
            clean_phone = ''.join(filter(str.isdigit, str(phone)))
            if len(clean_phone) == 9:
                clean_phone = "998" + clean_phone
            
            # Telegram ID ni topish
            tg_id = all_phone_to_telegram.get(clean_phone)
            
            if tg_id:
                # Telegram orqali yuborish
                tg_message = f"📨 <b>Xabar</b>\n\n{message}"
                
                if send_telegram_to_user(tg_id, tg_message):
                    log(f"✅ Yuborildi: {student_name} ({clean_phone})")
                    queue_sheet.update_cell(row_idx + 1, 3, "SENT_TG")
                    sent_count += 1
                else:
                    log(f"❌ Yuborilmadi: {student_name} ({clean_phone})", "ERROR")
                    queue_sheet.update_cell(row_idx + 1, 3, "TG_ERROR")
            else:
                log(f"⚠️ Telegram ID topilmadi: {student_name} ({clean_phone})", "WARN")
                not_found += 1
            
            # Telegram limitlaridan qochish uchun kutish
            time.sleep(0.5)
        
        return sent_count, not_found
        
    except Exception as e:
        log(f"Xato: {e}", "ERROR")
        return 0, 0

# =============================================================================
# ASOSIY
# =============================================================================

def main():
    log("=" * 50)
    log("🚀 EMERGENCY TELEGRAM SENDER ishga tushdi!")
    log("=" * 50)
    
    send_telegram_to_admin("🚨 Emergency Telegram Sender ishga tushdi!")
    
    # Google Sheets ga ulanish
    client = get_google_client()
    if not client:
        log("Google Sheets ga ulanib bo'lmadi!", "ERROR")
        return
    
    # PENDING SMSlarni yuborish
    sent, not_found = process_pending_sms(client)
    
    # Natija
    log("=" * 50)
    log(f"✅ Yuborildi: {sent} ta")
    log(f"⚠️ Telegram ID topilmadi: {not_found} ta")
    log("=" * 50)
    
    # Adminga xabar
    send_telegram_to_admin(f"📊 Natija:\n✅ Telegram orqali: {sent} ta yuborildi\n⚠️ TG ID yo'q: {not_found} ta")

if __name__ == "__main__":
    main()
