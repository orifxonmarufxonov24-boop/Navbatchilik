/*
 * ============================================================================
 * NAVBATCHILIK - Yotoqxona Navbatchilik Tizimi
 * ============================================================================
 * 
 * Copyright (c) 2024 Orifxon Marufxonov
 * Barcha huquqlar himoyalangan / All Rights Reserved
 * 
 * Bu dastur Orifxon Marufxonov tomonidan yaratilgan va uning intellektual 
 * mulki hisoblanadi. Ruxsatsiz nusxalash, tarqatish, o'zgartirish yoki 
 * tijorat maqsadlarida foydalanish qat'iyan man etiladi.
 * 
 * This software is created by Orifxon Marufxonov and is his intellectual 
 * property. Unauthorized copying, distribution, modification, or commercial 
 * use is strictly prohibited.
 * 
 * Bog'lanish / Contact: @Sheeyh_o5 (Telegram)
 * 
 * ============================================================================
 */

package com.navbatchilik.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;
import java.io.File;
import java.security.MessageDigest;

public class MainActivity extends Activity {

    private WebView webView;
    private SwipeRefreshLayout swipeRefresh;
    private static final String URL = "https://ttjmchs.streamlit.app/";
    
    // Mualliflik ma'lumotlari
    private static final String AUTHOR = "Orifxon Marufxonov";
    private static final String COPYRIGHT = "© 2024 " + AUTHOR + ". Barcha huquqlar himoyalangan.";
    private static final String VERSION = "1.0.0";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Xavfsizlik tekshiruvi
        if (!isSecure()) {
            showSecurityAlert();
            return;
        }
        
        setContentView(R.layout.activity_main);
        
        // SwipeRefreshLayout va WebView ni topish
        swipeRefresh = findViewById(R.id.swipeRefresh);
        webView = findViewById(R.id.webview);
        
        // WebView sozlamalari
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        
        // SSL xatolarini bloklash (xavfsizlik uchun)
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        
        // Havolalarni ichida ochish
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                swipeRefresh.setRefreshing(false);
            }
            
            @Override
            public void onReceivedSslError(WebView view, android.webkit.SslErrorHandler handler, android.net.http.SslError error) {
                // SSL xatolarini qabul qilmaslik (xavfsizlik)
                handler.cancel();
            }
        });
        
        // Pull to Refresh
        swipeRefresh.setOnRefreshListener(() -> webView.reload());
        
        swipeRefresh.setColorSchemeColors(
            getResources().getColor(android.R.color.holo_blue_bright),
            getResources().getColor(android.R.color.holo_green_light)
        );
        
        webView.loadUrl(URL);
    }
    
    /**
     * Xavfsizlik tekshiruvi
     * - Root tekshiruvi
     * - Debugger tekshiruvi
     * - Emulator tekshiruvi
     */
    private boolean isSecure() {
        // Root tekshiruvi
        if (isRooted()) {
            return false;
        }
        
        // Debugger tekshiruvi
        if (android.os.Debug.isDebuggerConnected()) {
            return false;
        }
        
        return true;
    }
    
    private boolean isRooted() {
        String[] paths = {
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su"
        };
        
        for (String path : paths) {
            if (new File(path).exists()) {
                return true;
            }
        }
        return false;
    }
    
    private void showSecurityAlert() {
        new AlertDialog.Builder(this)
            .setTitle("⚠️ Xavfsizlik")
            .setMessage("Bu ilova xavfsiz muhitda ishlamaydi.\n\n" + COPYRIGHT)
            .setPositiveButton("Chiqish", (dialog, which) -> finish())
            .setCancelable(false)
            .show();
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
    
    /**
     * Mualliflik ma'lumotlarini olish
     */
    public static String getAuthor() {
        return AUTHOR;
    }
    
    public static String getCopyright() {
        return COPYRIGHT;
    }
    
    public static String getVersion() {
        return VERSION;
    }
}
