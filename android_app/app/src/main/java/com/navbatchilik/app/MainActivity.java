/*
 * ============================================================================
 * NAVBATCHILIK - Yotoqxona Navbatchilik Tizimi
 * ============================================================================
 * Copyright (c) 2024 Orifxon Marufxonov - Barcha huquqlar himoyalangan
 * ============================================================================
 */

package com.navbatchilik.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.AsyncTask;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;
import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import org.json.JSONObject;

public class MainActivity extends Activity {

    private WebView webView;
    private SwipeRefreshLayout swipeRefresh;
    private static final String APP_URL = "https://ttjmchs.streamlit.app/";
    private static final String VERSION_URL = "https://raw.githubusercontent.com/orifxonmarufxonov24-boop/Navbatchilik/main/version.json";
    
    // Mualliflik ma'lumotlari
    private static final String AUTHOR = "Orifxon Marufxonov";
    private static final String COPYRIGHT = "© 2024 " + AUTHOR;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Xavfsizlik tekshiruvi
        if (!isSecure()) {
            showSecurityAlert();
            return;
        }
        
        setContentView(R.layout.activity_main);
        
        // Yangilanish tekshiruvi
        checkForUpdates();
        
        // SwipeRefreshLayout va WebView ni topish
        swipeRefresh = findViewById(R.id.swipeRefresh);
        webView = findViewById(R.id.webview);
        
        // WebView sozlamalari
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        
        // Havolalarni ichida ochish
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                swipeRefresh.setRefreshing(false);
            }
            
            @Override
            public void onReceivedSslError(WebView view, android.webkit.SslErrorHandler handler, android.net.http.SslError error) {
                handler.cancel();
            }
        });
        
        // Pull to Refresh
        swipeRefresh.setOnRefreshListener(() -> webView.reload());
        
        swipeRefresh.setColorSchemeColors(
            getResources().getColor(android.R.color.holo_blue_bright),
            getResources().getColor(android.R.color.holo_green_light)
        );
        
        webView.loadUrl(APP_URL);
    }
    
    /**
     * Yangilanish tekshiruvi
     */
    private void checkForUpdates() {
        new AsyncTask<Void, Void, JSONObject>() {
            @Override
            protected JSONObject doInBackground(Void... voids) {
                try {
                    URL url = new URL(VERSION_URL);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("GET");
                    conn.setConnectTimeout(5000);
                    conn.setReadTimeout(5000);
                    
                    BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }
                    reader.close();
                    
                    return new JSONObject(response.toString());
                } catch (Exception e) {
                    return null;
                }
            }
            
            @Override
            protected void onPostExecute(JSONObject versionInfo) {
                if (versionInfo != null) {
                    try {
                        int serverVersionCode = versionInfo.getInt("versionCode");
                        String serverVersion = versionInfo.getString("version");
                        String releaseNotes = versionInfo.getString("releaseNotes");
                        String downloadUrl = versionInfo.getString("downloadUrl");
                        boolean forceUpdate = versionInfo.optBoolean("forceUpdate", false);
                        
                        int currentVersionCode = getCurrentVersionCode();
                        
                        if (serverVersionCode > currentVersionCode) {
                            showUpdateDialog(serverVersion, releaseNotes, downloadUrl, forceUpdate);
                        }
                    } catch (Exception e) {
                        // Ignore
                    }
                }
            }
        }.execute();
    }
    
    private int getCurrentVersionCode() {
        try {
            PackageInfo pInfo = getPackageManager().getPackageInfo(getPackageName(), 0);
            return pInfo.versionCode;
        } catch (PackageManager.NameNotFoundException e) {
            return 1;
        }
    }
    
    private void showUpdateDialog(String version, String notes, String downloadUrl, boolean force) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("🎉 Yangi versiya mavjud!");
        builder.setMessage("Versiya: " + version + "\n\n" + notes + "\n\nYangilashni xohlaysizmi?");
        builder.setPositiveButton("✅ Yangilash", (dialog, which) -> {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(downloadUrl));
            startActivity(intent);
        });
        
        if (!force) {
            builder.setNegativeButton("❌ Keyinroq", (dialog, which) -> dialog.dismiss());
        }
        
        builder.setCancelable(!force);
        builder.show();
    }
    
    private boolean isSecure() {
        if (isRooted()) return false;
        if (android.os.Debug.isDebuggerConnected()) return false;
        return true;
    }
    
    private boolean isRooted() {
        String[] paths = {
            "/system/app/Superuser.apk", "/sbin/su", "/system/bin/su",
            "/system/xbin/su", "/data/local/xbin/su", "/data/local/bin/su"
        };
        for (String path : paths) {
            if (new File(path).exists()) return true;
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
}
