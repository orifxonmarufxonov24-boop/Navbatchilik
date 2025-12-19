# ============================================================================
# ProGuard Rules - NAVBATCHILIK
# Copyright (c) 2024 Orifxon Marufxonov - Barcha huquqlar himoyalangan
# ============================================================================

# =========================
# KUCHLI OBFUSKATSIYA
# =========================

# Barcha paketlarni bitta joyga yig'ish
-repackageclasses 'o'
-allowaccessmodification

# Maksimal optimallashtirish
-optimizationpasses 10
-optimizations !code/simplification/cast,!field/*,!class/merging/*

# Aggressive obfuskatsiya
-flattenpackagehierarchy
-overloadaggressively

# =========================
# KERAKLI KLASSLARNI SAQLASH
# =========================

# Activity va WebView
-keep class com.navbatchilik.app.MainActivity { *; }
-keepclassmembers class * extends android.webkit.WebViewClient { *; }

# AndroidX
-keep class androidx.swiperefreshlayout.widget.SwipeRefreshLayout { *; }

# =========================
# LOG VA DEBUG OLIB TASHLASH
# =========================

-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
    public static *** w(...);
    public static *** e(...);
}

# =========================
# ANTI-TAMPERING
# =========================

# Source fayl nomlarini yashirish
-renamesourcefileattribute ''
-keepattributes SourceFile,LineNumberTable

# Native metodlarni saqlash
-keepclasseswithmembernames class * {
    native <methods>;
}

# Enum
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# =========================
# KODNI HIMOYALASH
# =========================

# String shifrlash (R8 uchun)
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# Reflection himoyasi
-keepattributes Signature
-keepattributes *Annotation*
