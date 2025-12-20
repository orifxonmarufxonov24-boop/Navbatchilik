"""
Face Recognition Module - Yo'qlama Tizimi
==========================================
110 talaba yuzlarini aniqlash uchun modul

Copyright (c) 2024 Orifxon Marufxonov
"""

import os
import pickle
import numpy as np
from PIL import Image
import io
import base64

# face_recognition o'rnatilganligini tekshirish
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("[WARNING] face_recognition kutubxonasi ornatilmagan!")

# Sozlamalar
FACES_DIR = os.path.join(os.path.dirname(__file__), "faces")
ENCODINGS_FILE = os.path.join(os.path.dirname(__file__), "face_encodings.pkl")
TOLERANCE = 0.6  # Yuz aniqlash sezgirligi (0.4-0.6 oralig'i yaxshi)


def ensure_faces_dir():
    """faces papkasini yaratish"""
    if not os.path.exists(FACES_DIR):
        os.makedirs(FACES_DIR)
        print(f"📁 '{FACES_DIR}' papkasi yaratildi")
    return FACES_DIR


def detect_face_in_image(image_source):
    """
    Rasmda yuz bor-yo'qligini tekshirish va joylashuvini qaytarish
    Bank ilovasidagi kabi yuzni aniqlash uchun
    
    Args:
        image_source: Rasm (base64 yoki numpy array)
    
    Returns:
        dict: {
            "found": bool,
            "count": int,
            "faces": [(top, right, bottom, left), ...],
            "image_with_boxes": base64 encoded image with green boxes
        }
    """
    try:
        import cv2
        
        # Rasmni yuklash
        if isinstance(image_source, str):
            if image_source.startswith("data:image"):
                base64_data = image_source.split(",")[1]
                image_data = base64.b64decode(base64_data)
            else:
                image_data = base64.b64decode(image_source)
            
            # OpenCV orqali yuklash
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_source, np.ndarray):
            image = image_source
        else:
            return {"found": False, "count": 0, "faces": [], "image_with_boxes": None, "message": "Noto'g'ri rasm formati"}
        
        if image is None:
            return {"found": False, "count": 0, "faces": [], "image_with_boxes": None, "message": "Rasmni yuklashda xatolik"}
        
        # Grayscale ga o'tkazish
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Haar Cascade yuz aniqlash
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        if len(faces) > 0:
            # Yashil ramka chizish
            image_with_boxes = image.copy()
            
            for (x, y, w, h) in faces:
                # Yashil ramka
                cv2.rectangle(image_with_boxes, (x, y), (x+w, y+h), (0, 255, 0), 3)
                # "Yuz topildi" yozuvi
                cv2.putText(image_with_boxes, "Yuz topildi!", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Base64 ga o'tkazish
            _, buffer = cv2.imencode('.jpg', image_with_boxes)
            image_b64 = base64.b64encode(buffer).decode()
            
            # face_locations format: (top, right, bottom, left)
            face_locations = [(y, x+w, y+h, x) for (x, y, w, h) in faces]
            
            return {
                "found": True,
                "count": len(faces),
                "faces": face_locations,
                "image_with_boxes": image_b64,
                "message": f"✅ {len(faces)} ta yuz topildi!"
            }
        else:
            return {
                "found": False,
                "count": 0,
                "faces": [],
                "image_with_boxes": None,
                "message": "❌ Rasmda yuz topilmadi! Iltimos, yuzingiz aniq ko'rinadigan rasm oling."
            }
            
    except Exception as e:
        return {
            "found": False,
            "count": 0,
            "faces": [],
            "image_with_boxes": None,
            "message": f"❌ Xatolik: {str(e)}"
        }



def load_image_from_base64(base64_string):
    """Base64 stringdan rasm yuklash"""
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    return np.array(image)


def load_image_from_file(file_path):
    """Fayldan rasm yuklash"""
    return face_recognition.load_image_file(file_path)


def encode_face(image_array):
    """
    Rasmdan yuz encodingini olish
    
    Returns:
        encoding yoki None (agar yuz topilmasa)
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return None
    
    face_locations = face_recognition.face_locations(image_array)
    if len(face_locations) == 0:
        return None
    
    # Birinchi topilgan yuzni olish
    encodings = face_recognition.face_encodings(image_array, face_locations)
    if len(encodings) > 0:
        return encodings[0]
    return None


def register_student(student_id, student_name, image_source):
    """
    Talabani ro'yxatdan o'tkazish
    
    Args:
        student_id: Talaba ID raqami
        student_name: Talaba ismi
        image_source: Rasm (fayl yo'li, base64, yoki numpy array)
    
    Returns:
        dict: {"success": bool, "message": str}
    """
    try:
        import cv2
        ensure_faces_dir()
        
        # Rasmni yuklash
        if isinstance(image_source, str):
            if os.path.exists(image_source):
                image = cv2.imread(image_source)
            elif image_source.startswith("data:image"):
                base64_data = image_source.split(",")[1]
                image_data = base64.b64decode(base64_data)
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                image_data = base64.b64decode(image_source)
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_source, np.ndarray):
            image = image_source
        else:
            return {"success": False, "message": "Noto'g'ri rasm formati"}
        
        if image is None:
            return {"success": False, "message": "Rasmni yuklashda xatolik"}
        
        # OpenCV bilan yuz tekshirish
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return {"success": False, "message": "Rasmda yuz topilmadi!"}
        
        # Rasmni saqlash
        image_path = os.path.join(FACES_DIR, f"{student_id}.jpg")
        cv2.imwrite(image_path, image)
        
        # Encoding saqlash (agar face_recognition mavjud bo'lsa)
        if FACE_RECOGNITION_AVAILABLE:
            # RGB ga o'tkazish (face_recognition uchun)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encoding = encode_face(image_rgb)
            if encoding is not None:
                encodings = load_all_encodings()
                encodings[student_id] = {
                    "name": student_name,
                    "encoding": encoding
                }
                save_all_encodings(encodings)
        else:
            # face_recognition yo'q bo'lsa, faqat metadata saqlash
            encodings = load_all_encodings()
            encodings[student_id] = {
                "name": student_name,
                "encoding": None,  # Placeholder
                "image_path": image_path
            }
            save_all_encodings(encodings)
        
        return {"success": True, "message": f"✅ {student_name} muvaffaqiyatli ro'yxatdan o'tdi!"}
        
    except Exception as e:
        return {"success": False, "message": f"Xatolik: {str(e)}"}


def load_all_encodings():
    """Barcha talabalar encodinglarini yuklash"""
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            return pickle.load(f)
    return {}


def save_all_encodings(encodings):
    """Barcha encodinglarni saqlash"""
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(encodings, f)


def recognize_faces_in_frame(frame_image):
    """
    Kadrdan yuzlarni aniqlash
    
    Args:
        frame_image: Kamera kadri (numpy array yoki base64)
    
    Returns:
        list: Aniqlangan talabalar ro'yxati
        [{"student_id": "001", "name": "Ali Valiyev", "location": (top, right, bottom, left)}]
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return []
    
    # Rasmni yuklash
    if isinstance(frame_image, str):
        if frame_image.startswith("data:image"):
            base64_data = frame_image.split(",")[1]
            image = load_image_from_base64(base64_data)
        else:
            image = load_image_from_base64(frame_image)
    else:
        image = frame_image
    
    # Barcha talabalar encodinglarini yuklash
    all_encodings = load_all_encodings()
    if not all_encodings:
        return []
    
    # Kadrdagi yuzlarni topish
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    recognized = []
    known_encodings = [data["encoding"] for data in all_encodings.values()]
    known_ids = list(all_encodings.keys())
    
    for face_encoding, face_location in zip(face_encodings, face_locations):
        # Har bir yuzni ma'lum yuzlar bilan solishtirish
        matches = face_recognition.compare_faces(known_encodings, face_encoding, TOLERANCE)
        
        if True in matches:
            match_index = matches.index(True)
            student_id = known_ids[match_index]
            student_data = all_encodings[student_id]
            
            recognized.append({
                "student_id": student_id,
                "name": student_data["name"],
                "location": face_location
            })
    
    return recognized


def take_attendance(frame_image):
    """
    Yo'qlama olish - rasmdan borlarni aniqlash
    
    Args:
        frame_image: Guruh rasmi
    
    Returns:
        dict: {
            "present": [{"id": "001", "name": "Ali Valiyev"}, ...],
            "absent": [{"id": "002", "name": "Vali Aliyev"}, ...],
            "total": 110,
            "present_count": 95,
            "absent_count": 15
        }
    """
    # Aniqlangan yuzlar
    recognized = recognize_faces_in_frame(frame_image)
    present_ids = set(r["student_id"] for r in recognized)
    
    # Barcha talabalar
    all_encodings = load_all_encodings()
    all_ids = set(all_encodings.keys())
    
    # Kelmayganlar
    absent_ids = all_ids - present_ids
    
    present = [{"id": sid, "name": all_encodings[sid]["name"]} for sid in present_ids]
    absent = [{"id": sid, "name": all_encodings[sid]["name"]} for sid in absent_ids]
    
    return {
        "present": present,
        "absent": absent,
        "total": len(all_ids),
        "present_count": len(present),
        "absent_count": len(absent)
    }


def get_registered_students():
    """Ro'yxatdan o'tgan talabalar ro'yxati"""
    all_encodings = load_all_encodings()
    return [
        {"id": sid, "name": data["name"]}
        for sid, data in all_encodings.items()
    ]


def delete_student(student_id):
    """Talabani o'chirish"""
    encodings = load_all_encodings()
    if student_id in encodings:
        del encodings[student_id]
        save_all_encodings(encodings)
        
        # Rasmni ham o'chirish
        image_path = os.path.join(FACES_DIR, f"{student_id}.jpg")
        if os.path.exists(image_path):
            os.remove(image_path)
        
        return {"success": True, "message": "Talaba o'chirildi"}
    return {"success": False, "message": "Talaba topilmadi"}


# Test uchun
if __name__ == "__main__":
    ensure_faces_dir()
    print(f"✅ Face Recognition Module yuklandi")
    print(f"📁 Yuzlar papkasi: {FACES_DIR}")
    print(f"📊 Ro'yxatdan o'tgan talabalar: {len(get_registered_students())}")
