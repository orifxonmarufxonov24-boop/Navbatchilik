from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/send', methods=['POST'])
def send_sms():
    phone_number = request.form.get('number')
    message = request.form.get('message')
    
    if not phone_number or not message:
        return "Raqam yoki xabar yetishmayapti", 400

    # Termux orqali SMS yuborish buyrug'i
    os.system(f'termux-sms-send -n {phone_number} "{message}"')
    
    print(f"SMS yuborildi: {phone_number} -> {message}")
    return "SMS muvaffaqiyatli yuborildi", 200

if __name__ == '__main__':
    # Barcha IP manzillardan kirishga ruxsat berish
    app.run(host='0.0.0.0', port=5000)
