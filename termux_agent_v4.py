import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import subprocess

# --- SOZLAMALAR ---
FLOOR_SHEETS = {
    "4-etaj": "Navbatchilik_Jadvali",
    "3-etaj": "TTJ 3-etaj Navbatchilik"
}
CREDS_FILE = "credentials.json"
TELEGRAM_TOKEN = "8259734572:AAGeJLKmmruLByDjx81gdi1VcjNt3ZnX894"
ADMIN_CHAT_ID = "7693191223"

# --- UYQUDAN UYG'OTISH (WAKE LOCK) ---
try:
    os.system("termux-wake-lock")
except:
    pass

# --- GOOGLE SHEETGA ULANISH ---
def get_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    return client

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID, "text": message}, timeout=5)
    except:
        pass

def send_sms_via_termux(phone, message):
    try:
        phone = str(phone).replace("+", "").replace(" ", "").replace(".0", "")
        # subprocess ishlatamiz - ishonchliroq
        result = subprocess.run(
            ["termux-sms-send", "-n", phone, message],
            capture_output=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"SMS Error: {e}")
        return False

print("SMS AGENT (v4.1 - MULTI-FLOOR)...")
send_telegram("Agent ishga tushdi (v4.1 - 4 va 3 etaj)...")

# --- ASOSIY LOOP ---
while True:
    try:
        client = get_client()
        total_sms_sent = 0
        
        # Har bir etajni tekshirish
        for floor_name, sheet_name in FLOOR_SHEETS.items():
            try:
                # Sheetni ochish
                spreadsheet = client.open(sheet_name)
                try:
                    queue_sheet = spreadsheet.worksheet("SMS_QUEUE")
                except:
                    # Agar SMS_QUEUE bo'lmasa, keyingi etajga o'tish
                    continue
                    
                queue_data = queue_sheet.get_all_values()
                
                # Header bormi?
                if len(queue_data) <= 1:
                    continue
                
                for r_idx, row in enumerate(queue_data):
                    # Header va bo'sh qatorlarni o'tkazib yuborish
                    if r_idx == 0 or len(row) < 3:
                        continue
                    
                    if row[2] == "PENDING":
                        phone, msg = row[0], row[1]
                        print(f"[{floor_name}] SMS: {phone}")
                        
                        try:
                            if send_sms_via_termux(phone, msg):
                                queue_sheet.update_cell(r_idx + 1, 3, "SENT")
                                total_sms_sent += 1
                                print(f"OK: {phone}")
                            else:
                                queue_sheet.update_cell(r_idx + 1, 3, "ERROR")
                                print(f"ERROR: {phone}")
                        except Exception as e:
                            print(f"Update error: {e}")
                            # Agar xato bo'lsa, statusni ERROR ga o'zgartirib qo'yamiz
                            # queue_sheet.update_cell(r_idx + 1, 3, "ERROR")
                        
                        # Har bir SMS orasida 3 sekund kutish
                        time.sleep(3)
                        
            except Exception as e_inner:
                print(f"Error processing {floor_name}: {e_inner}")
                continue
        
        if total_sms_sent > 0:
            send_telegram(f"✅ Jami {total_sms_sent} ta SMS yuborildi!")
        
        # 10 sekund kutish (keyingi tekshiruvgacha)
        time.sleep(10)
        
    except Exception as e:
        print(f"Global Error: {e}")
        time.sleep(10)
