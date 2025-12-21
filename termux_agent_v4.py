import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import subprocess

# --- SOZLAMALAR ---
GOOGLE_SHEET_NAME = "Navbatchilik_Jadvali"
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

print("SMS AGENT (v4.0 - STABLE)...")
send_telegram("Agent ishga tushdi (v4.0)...")

# --- ASOSIY LOOP ---
while True:
    try:
        client = get_client()
        spreadsheet = client.open(GOOGLE_SHEET_NAME)
        queue_sheet = spreadsheet.worksheet("SMS_QUEUE")
        queue_data = queue_sheet.get_all_values()
        
        sms_count = 0
        
        for r_idx, row in enumerate(queue_data):
            if r_idx == 0 or len(row) < 3:
                continue
            
            if row[2] == "PENDING":
                phone, msg = row[0], row[1]
                print(f"SMS: {phone}")
                
                try:
                    if send_sms_via_termux(phone, msg):
                        queue_sheet.update_cell(r_idx + 1, 3, "SENT")
                        sms_count += 1
                        print(f"OK: {phone}")
                    else:
                        queue_sheet.update_cell(r_idx + 1, 3, "ERROR")
                        print(f"ERROR: {phone}")
                except Exception as e:
                    print(f"Update error: {e}")
                
                # Har bir SMS orasida 2 sekund kutish
                time.sleep(2)
        
        if sms_count > 0:
            send_telegram(f"{sms_count} ta SMS yuborildi!")
        
        # 10 sekund kutish
        time.sleep(10)
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(10)
