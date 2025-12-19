# 📱 Navbatchilik Android Ilova

Bu papkada Android WebView ilovasi uchun asosiy fayllar mavjud.

## Fayllar

| Fayl | Vazifasi |
|------|----------|
| `AndroidManifest.xml` | Ruxsatlar va ilova sozlamalari |
| `MainActivity.java` | Asosiy kod (WebView) |
| `activity_main.xml` | UI layout |

## APK Yaratish

### 1-usul: Android Studio (Tavsiya etiladi)

1. Android Studio ni oching
2. File → New → New Project → Empty Activity
3. Yuqoridagi fayllarni tegishli joylarga joylashtiring:
   - `MainActivity.java` → `app/src/main/java/com/navbatchilik/app/`
   - `activity_main.xml` → `app/src/main/res/layout/`
   - `AndroidManifest.xml` → `app/src/main/`
4. Build → Build Bundle(s) / APK(s) → Build APK(s)

### 2-usul: Online APK Builder

Agar Android Studio o'rnatishni xohlamasangiz:
1. https://appsgeyser.com ga kiring
2. "Website to App" tanlang
3. Streamlit URL ingizni kiriting
4. APK yuklab oling

## MUHIM

`MainActivity.java` faylidagi URL ni o'zgartiring:
```java
private static final String WEBSITE_URL = "https://YOUR-APP.streamlit.app";
```
