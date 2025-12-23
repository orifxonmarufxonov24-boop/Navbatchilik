# 📚 FACE ID YO'QLAMA TIZIMI - TO'LIQ QO'LLANMA

## 📋 MUNDARIJA

1. [Tizim Haqida Umumiy Ma'lumot](#tizim-haqida)
2. [Texnologiyalar](#texnologiyalar)
3. [Arxitektura](#arxitektura)
4. [O'rnatish](#ornatish)
5. [Foydalanish](#foydalanish)
6. [Kod Tuzilishi](#kod-tuzilishi)
7. [API Hujjatlari](#api)
8. [Xatoliklarni Tuzatish](#xatoliklar)

---

## 1. TIZIM HAQIDA UMUMIY MA'LUMOT {#tizim-haqida}

### Nima uchun kerak?
Bu tizim yuzni aniqlash (Face Recognition) texnologiyasi yordamida yo'qlama olish imkonini beradi. 
Har bir talabaning yuzi oldindan ro'yxatdan o'tkaziladi, keyin yig'ilish paytida kamera orqali 
kim kelganini avtomatik aniqlaydi.

### Asosiy xususiyatlar:
- ✅ Yuzni aniqlash va ro'yxatdan o'tkazish
- ✅ Yo'qlama olish (kim kelgan, kim kelmagan)
- ✅ Telefondan ishlash
- ✅ Lokal server orqali ishlash
- ✅ Google Sheets bilan integratsiya

---

## 2. TEXNOLOGIYALAR {#texnologiyalar}

### Frontend (Foydalanuvchi Interfeysi):
| Texnologiya | Vazifasi |
|-------------|----------|
| **Streamlit** | Web sahifa yaratish |
| **HTML/CSS** | Sahifa ko'rinishi |
| **JavaScript** | Interaktiv elementlar |

### Backend (Server Qismi):
| Texnologiya | Vazifasi |
|-------------|----------|
| **Flask** | Lokal API server |
| **Python** | Asosiy dasturlash tili |

### Yuz Aniqlash:
| Texnologiya | Vazifasi |
|-------------|----------|
| **OpenCV** | Rasmlarni qayta ishlash |
| **DeepFace** | Yuzni tanish (recognition) |
| **Haar Cascade** | Yuzni aniqlash (detection) |

### Ma'lumotlar Bazasi:
| Texnologiya | Vazifasi |
|-------------|----------|
| **Google Sheets** | Talabalar ro'yxati |
| **Pickle (.pkl)** | Yuz encodinglari |
| **JPEG** | Yuz rasmlari |

### Mobil Ilova:
| Texnologiya | Vazifasi |
|-------------|----------|
| **Android WebView** | Streamlit sahifani ko'rsatish |
| **Java** | Android dasturlash |

---

## 3. ARXITEKTURA {#arxitektura}

### Umumiy Tuzilma:
```
┌─────────────────────────────────────────────────────────────────┐
│                         FOYDALANUVCHI                           │
│                    (Telefon yoki Kompyuter)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT WEB APP                          │
│                   (app.py - Streamlit Cloud)                    │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────────┐          │
│  │Navbat   │ │ Naryad  │ │Statistika│ │   Yo'qlama  │          │
│  └─────────┘ └─────────┘ └──────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ (HTTP So'rov)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOKAL FLASK SERVER                           │
│                 (face_server.py - Kompyuter)                    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    face_module.py                        │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐  │   │
│  │  │ Yuz Aniqlash  │  │ Ro'yxatdan    │  │  Yo'qlama   │  │   │
│  │  │  (OpenCV)     │  │  O'tkazish    │  │   Olish     │  │   │
│  │  └───────────────┘  └───────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MA'LUMOTLAR BAZASI                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Google Sheets  │  │ face_encodings  │  │    faces/       │ │
│  │ (Talabalar)     │  │    .pkl         │  │   001.jpg       │ │
│  └─────────────────┘  └─────────────────┘  │   002.jpg       │ │
│                                            │   ...           │ │
│                                            └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Yo'qlama Olish Jarayoni (Batafsil):
```
1. Foydalanuvchi rasmga oladi
        │
        ▼
2. Rasm base64 formatga o'giriladi
        │
        ▼
3. HTTP POST so'rov yuboriladi
   Endpoint: /api/attendance
   Body: {"frame": "base64_encoded_image"}
        │
        ▼
4. Flask server so'rovni qabul qiladi
        │
        ▼
5. face_module.take_attendance_deepface() chaqiriladi
        │
        ├── 5.1 Rasm vaqtincha faylga saqlanadi
        │
        ├── 5.2 Har bir ro'yxatdagi talaba uchun:
        │       │
        │       ├── DeepFace.verify() chaqiriladi
        │       │   (Ikki rasmni solishtiradi)
        │       │
        │       └── Agar mos kelsa → "present" ga qo'shiladi
        │           Agar mos kelmasa → "absent" ga qo'shiladi
        │
        └── 5.3 Natija qaytariladi
        │
        ▼
6. Streamlit natijani ko'rsatadi
   - Kelganlar ro'yxati
   - Kelmayganlar ro'yxati
   - Statistika
```

---

## 4. O'RNATISH {#ornatish}

### 4.1 Talablar:
- Python 3.10+
- Windows 10/11
- Android 7.0+ (mobil uchun)
- Kamera

### 4.2 Python Kutubxonalari:
```bash
pip install streamlit pandas gspread oauth2client requests
pip install flask flask-cors
pip install opencv-python-headless Pillow numpy
pip install deepface tf-keras pyngrok
```

### 4.3 Fayllar Tuzilishi:
```
loyiha/
├── app.py                    # Streamlit web ilova
├── requirements.txt          # Python kutubxonalari
├── version.json              # Versiya ma'lumotlari
├── START_SERVER.vbs          # Server ishga tushirish
├── start_server.ps1          # PowerShell versiya
│
├── yangi/                    # Face ID moduli
│   ├── face_module.py        # Yuz aniqlash funksiyalari
│   ├── face_server.py        # Flask API server
│   ├── face_encodings.pkl    # Yuz encodinglari
│   └── faces/                # Yuz rasmlari
│       ├── 001.jpg
│       ├── 002.jpg
│       └── ...
│
└── android_app/              # Android ilova
    ├── app/
    │   ├── src/main/
    │   │   ├── java/.../MainActivity.java
    │   │   ├── res/layout/activity_main.xml
    │   │   └── AndroidManifest.xml
    │   └── build.gradle
    └── gradlew.cmd
```

### 4.4 Google Sheets Sozlash:
1. Google Cloud Console'da yangi loyiha yarating
2. Google Sheets API ni yoqing
3. Service Account yarating
4. JSON kalitni yuklab oling
5. `credits.json` sifatida saqlang
6. Google Sheets'ni Service Account bilan ulashing

---

## 5. FOYDALANISH {#foydalanish}

### 5.1 Serverni Ishga Tushirish:
```
1. START_SERVER.vbs ni ikki marta bosing
2. "Internet orqali kirish kerakmi?" - HA yoki YO'Q tanlang
3. Server ishga tushadi
```

### 5.2 Talabani Ro'yxatdan O'tkazish:
```
1. Streamlit saytga kiring
2. "📸 Yo'qlama" → "👤 Talaba Ro'yxatdan O'tkazish"
3. Talabani tanlang
4. Kameradan rasm oling yoki fayl yuklang
5. Yuz aniqlangan bo'lsa → "Ro'yxatdan O'tkazish" bosing
```

### 5.3 Yo'qlama Olish:
```
1. Server ishlab turganligini tekshiring
2. "📸 Yo'qlama" → "📸 Yo'qlama Olish"
3. Kameradan rasm oling
4. "🔍 Yo'qlama Olish" bosing
5. Natijalar ko'rsatiladi
```

### 5.4 Talaba Ma'lumotlarini Tahrirlash:
```
1. "📸 Yo'qlama" → "👤 Talaba Ro'yxatdan O'tkazish"
2. Pastda "✏️ Talaba Ma'lumotlarini Tahrirlash"
3. Talabani qidiring va tanlang
4. Ma'lumotlarni o'zgartiring
5. Yangi yuz rasmi yuklang (ixtiyoriy)
6. "💾 O'zgarishlarni Saqlash" bosing
```

---

## 6. KOD TUZILISHI {#kod-tuzilishi}

### 6.1 face_module.py - Asosiy Funksiyalar:

#### detect_face_in_image(image_source)
```python
"""
Rasmda yuz bor-yo'qligini aniqlaydi.

Parametrlar:
    image_source: base64 string yoki numpy array

Qaytaradi:
    {
        "found": True/False,
        "count": 1,
        "faces": [(top, right, bottom, left)],
        "image_with_boxes": "base64 (yashil ramka bilan)",
        "message": "✅ 1 ta yuz topildi!"
    }
    
Qanday ishlaydi:
1. Rasmni OpenCV formatiga o'giradi
2. Haar Cascade yordamida yuz qidiradi
3. Topilgan yuz atrofiga yashil ramka chizadi
4. Natijani qaytaradi
"""
```

#### register_student(student_id, student_name, image_source)
```python
"""
Yangi talabani ro'yxatdan o'tkazadi.

Parametrlar:
    student_id: "001" - Talaba ID
    student_name: "Ali Valiyev" - Ism
    image_source: base64 string - Yuz rasmi

Qaytaradi:
    {"success": True, "message": "✅ Ali Valiyev ro'yxatdan o'tdi!"}
    yoki
    {"success": False, "message": "Rasmda yuz topilmadi!"}

Qanday ishlaydi:
1. Rasmni OpenCV formatiga o'giradi
2. Haar Cascade bilan yuz bor-yo'qligini tekshiradi
3. Rasmni faces/001.jpg ga saqlaydi
4. Ma'lumotni face_encodings.pkl ga yozadi
"""
```

#### take_attendance_deepface(frame_image)
```python
"""
DeepFace yordamida yo'qlama oladi.

Parametrlar:
    frame_image: base64 string - Kamera rasmi

Qaytaradi:
    {
        "success": True,
        "present": [{"id": "001", "name": "Ali Valiyev"}],
        "absent": [{"id": "002", "name": "Vali Aliyev"}],
        "total": 110,
        "present_count": 95,
        "absent_count": 15
    }

Qanday ishlaydi:
1. Kamera rasmini vaqtincha faylga saqlaydi
2. Har bir ro'yxatdagi talaba uchun:
   - DeepFace.verify() chaqiradi
   - Ikki rasmni solishtiradi
   - Agar mos → "present" ga qo'shadi
   - Agar mos emas → "absent" ga qo'shadi
3. Natijani qaytaradi
"""
```

### 6.2 face_server.py - API Endpointlari:

| Endpoint | Method | Vazifasi |
|----------|--------|----------|
| `/` | GET | Server holatini tekshirish |
| `/api/health` | GET | Health check |
| `/api/register` | POST | Talaba ro'yxatdan o'tkazish |
| `/api/recognize` | POST | Yuzlarni aniqlash |
| `/api/attendance` | POST | Yo'qlama olish |
| `/api/students` | GET | Talabalar ro'yxati |
| `/api/students/<id>` | DELETE | Talabani o'chirish |

### 6.3 app.py - Streamlit Sahifalar:

```python
# Asosiy tablar
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Navbatchilik",  # Navbat ro'yxati
    "🛠️ Naryad",        # Naryad tuzish
    "📊 Statistika",    # Hisobotlar
    "📸 Yo'qlama"       # Face ID tizimi
])

# Yo'qlama ichki tablari
yoqlama_tab1, yoqlama_tab2, yoqlama_tab3 = st.tabs([
    "📸 Yo'qlama Olish",
    "📋 Yo'qlama Tarixi",
    "👤 Talaba Ro'yxatdan O'tkazish"
])
```

---

## 7. API HUJJATLARI {#api}

### 7.1 Talaba Ro'yxatdan O'tkazish

**Endpoint:** `POST /api/register`

**Request Body:**
```json
{
    "student_id": "001",
    "student_name": "Ali Valiyev",
    "image": "base64_encoded_image_string"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "✅ Ali Valiyev muvaffaqiyatli ro'yxatdan o'tdi!"
}
```

**Response (Error):**
```json
{
    "success": false,
    "message": "Rasmda yuz topilmadi!"
}
```

### 7.2 Yo'qlama Olish

**Endpoint:** `POST /api/attendance`

**Request Body:**
```json
{
    "frame": "base64_encoded_image_string"
}
```

**Response:**
```json
{
    "success": true,
    "present": [
        {"id": "001", "name": "Ali Valiyev"},
        {"id": "003", "name": "Salim Akbarov"}
    ],
    "absent": [
        {"id": "002", "name": "Vali Aliyev"}
    ],
    "total": 3,
    "present_count": 2,
    "absent_count": 1
}
```

### 7.3 Server Holati

**Endpoint:** `GET /`

**Response:**
```json
{
    "status": "running",
    "message": "Face Recognition Server ishlamoqda!",
    "registered_students": 110
}
```

---

## 8. XATOLIKLARNI TUZATISH {#xatoliklar}

### Xatolik: "Server ishlamayapti!"
**Sabab:** Lokal Flask server ishga tushmagan.
**Yechim:** 
1. `START_SERVER.vbs` ni qayta bosing
2. Konsol oynasi ochilganini tekshiring
3. "Running on http://localhost:5000" yozuvini ko'ring

### Xatolik: "Rasmda yuz topilmadi!"
**Sabab:** Haar Cascade yuzni topa olmadi.
**Yechim:**
1. Yuzni to'g'ridan-to'g'ri kameraga qarating
2. Yaxshi yoritilgan joyda rasm oling
3. Kamera sifatini tekshiring

### Xatolik: "DeepFace o'rnatilmagan!"
**Sabab:** DeepFace kutubxonasi o'rnatilmagan.
**Yechim:**
```bash
pip install deepface tf-keras --user
```

### Xatolik: ngrok authentication failed
**Sabab:** ngrok ro'yxatdan o'tish kerak.
**Yechim:**
1. https://dashboard.ngrok.com/signup - ro'yxatdan o'ting
2. Authtoken oling
3. `ngrok config add-authtoken YOUR_TOKEN` ishga tushiring

### Xatolik: Telefon serverga ulana olmayapti
**Sabab:** Telefon va kompyuter turli tarmoqlarda.
**Yechim:**
1. Ikkalasi bir WiFi ga ulaning
2. Yoki telefondan hotspot yoqib, kompyuterni ulang

---

## 📞 Muallif

**Orifxon Marufxonov**
- GitHub: @orifxonmarufxonov24-boop
- Loyiha: Navbatchilik (Face ID Yo'qlama Tizimi)

---

*Yaratilgan: 2024*
*Oxirgi yangilanish: 2024-12-23*
