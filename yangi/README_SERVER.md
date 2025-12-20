# Face Recognition Server - Ishga tushirish
# Bu faylni PowerShell da ishga tushiring

# 1. Kerakli kutubxonalarni o'rnatish
pip install flask flask-cors opencv-python-headless pillow numpy

# 2. Face recognition o'rnatish (Windows uchun qiyinroq bo'lishi mumkin)
# Agar xatolik chiqsa: pip install cmake dlib face_recognition
pip install face_recognition

# 3. Serverni ishga tushirish
cd yangi
python face_server.py
