"""
Face Recognition Flask Server - Lokal Server
=============================================
Telefon ilovasidan so'rovlarni qabul qiladi

Copyright (c) 2024 Orifxon Marufxonov
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import face_module as fm
import json

app = Flask(__name__)
CORS(app)  # CORS ni yoqish (telefon ilovasidan so'rov qabul qilish uchun)

# Server holati
SERVER_STATUS = {
    "active": True,
    "version": "1.0.0",
    "name": "Face Recognition Local Server"
}


@app.route("/", methods=["GET"])
def home():
    """Bosh sahifa - server holatini tekshirish"""
    return jsonify({
        "status": "running",
        "message": "🏠 Face Recognition Server ishlamoqda!",
        "registered_students": len(fm.get_registered_students())
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Server holatini tekshirish (fallback uchun)"""
    return jsonify({"status": "ok", "server": "local"})


@app.route("/api/register", methods=["POST"])
def register_student():
    """
    Yangi talabani ro'yxatdan o'tkazish
    
    Body:
        {
            "student_id": "001",
            "student_name": "Ali Valiyev",
            "image": "base64 encoded image"
        }
    """
    try:
        data = request.json
        student_id = data.get("student_id")
        student_name = data.get("student_name")
        image = data.get("image")
        
        if not all([student_id, student_name, image]):
            return jsonify({"success": False, "message": "Barcha maydonlar to'ldirilishi kerak!"})
        
        result = fm.register_student(student_id, student_name, image)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Xatolik: {str(e)}"})


@app.route("/api/recognize", methods=["POST"])
def recognize_faces():
    """
    Kadrdagi yuzlarni aniqlash
    
    Body:
        {
            "frame": "base64 encoded image"
        }
    """
    try:
        data = request.json
        frame = data.get("frame")
        
        if not frame:
            return jsonify({"success": False, "faces": [], "message": "Rasm kerak!"})
        
        recognized = fm.recognize_faces_in_frame(frame)
        return jsonify({
            "success": True,
            "faces": recognized,
            "count": len(recognized)
        })
    
    except Exception as e:
        return jsonify({"success": False, "faces": [], "message": f"Xatolik: {str(e)}"})


@app.route("/api/attendance", methods=["POST"])
def take_attendance():
    """
    Yo'qlama olish (DeepFace bilan)
    
    Body:
        {
            "frame": "base64 encoded image"
        }
    """
    try:
        data = request.json
        frame = data.get("frame")
        
        if not frame:
            return jsonify({"success": False, "message": "Rasm kerak!"})
        
        # Avval DeepFace bilan sinab ko'rish
        if hasattr(fm, 'take_attendance_deepface') and fm.DEEPFACE_AVAILABLE:
            result = fm.take_attendance_deepface(frame)
        else:
            # DeepFace yo'q bo'lsa oddiy funksiya
            result = fm.take_attendance(frame)
            result["success"] = True
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Xatolik: {str(e)}"})


@app.route("/api/students", methods=["GET"])
def get_students():
    """Ro'yxatdan o'tgan talabalar ro'yxati"""
    students = fm.get_registered_students()
    return jsonify({
        "success": True,
        "students": students,
        "count": len(students)
    })


@app.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    """Talabani o'chirish"""
    result = fm.delete_student(student_id)
    return jsonify(result)


if __name__ == "__main__":
    import sys
    
    # ngrok ishlatish (internet orqali kirish uchun)
    use_ngrok = "--ngrok" in sys.argv or "-n" in sys.argv
    
    print("=" * 50)
    print("Face Recognition Server")
    print("=" * 50)
    print(f"Ro'yxatdan o'tgan talabalar: {len(fm.get_registered_students())}")
    print("")
    
    if use_ngrok:
        try:
            from pyngrok import ngrok
            
            # ngrok tunnel ochish
            public_url = ngrok.connect(5000)
            print(f"INTERNET MANZIL: {public_url}")
            print("")
            print("Telefondan shu manzilni oching!")
            print("(Bu manzil har safar o'zgaradi)")
            
        except ImportError:
            print("[XATOLIK] pyngrok o'rnatilmagan!")
            print("O'rnatish: pip install pyngrok")
            use_ngrok = False
        except Exception as e:
            print(f"[XATOLIK] ngrok: {e}")
            use_ngrok = False
    
    print(f"Lokal manzil: http://localhost:5000")
    print("")
    print("Serverni to'xtatish: Ctrl+C")
    print("=" * 50)
    
    # Serverni ishga tushirish
    app.run(host="0.0.0.0", port=5000, debug=False)

