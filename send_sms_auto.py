import pandas as pd
import os
import keyboard
import time

# Excel fayl manzili
excel_path = r"C:\Users\orifx\attendance_system\Yoqlama_Navbatchilik.xlsx"

# Termux orqali SMS yuborish funksiyasi
def send_sms(phone_number, message):
    command = f'termux-sms-send -n {phone_number} "{message}"'
    os.system(command)

# Asosiy funksiya
def send_from_excel():
    df = pd.read_excel(excel_path)

    # Eng so‘nggi sanani avtomatik topish
    last_date = df.columns[-1]

    for index, row in df.iterrows():
        duty_type = str(row[last_date])
        phone = str(row["telefon raqami"])

        # Faqat navbatchilik belgilanganga yuboriladi
        if duty_type in ['1', '2', '3', '4']:
            if duty_type == '1':
                place = "Katta oshxona"
            elif duty_type == '2':
                place = "Kichik oshxona"
            elif duty_type == '3':
                place = "Katta dush"
            elif duty_type == '4':
                place = "Kichik dush"
            else:
                place = "Navbatchilik"

            message = f"Salom {row['ism familiya']}, siz bugun {place}da navbatchisiz."
            print(f"📤 {row['ism familiya']} ({phone}) ga SMS yuborilmoqda...")
            send_sms(phone, message)
            time.sleep(1)

    print("\n✅ Barcha SMSlar yuborildi!")

# Klavish kuzatuvchi qism
print("📄 Excel faylni tahrirlang, saqlang (Ctrl+S), keyin Ctrl+Q bosing SMS yuborish uchun...")
keyboard.add_hotkey('ctrl+q', send_from_excel)

# Doimiy ish holatida ushlab turadi
keyboard.wait('esc')  # ESC bosilsa dasturdan chiqadi
