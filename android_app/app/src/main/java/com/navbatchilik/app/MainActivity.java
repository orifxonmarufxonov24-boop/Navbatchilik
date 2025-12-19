package com.navbatchilik.app;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {

    private WebView webView;
    private static final String URL = "https://ttjmchs.streamlit.app/";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Oddiy WebView yaratish (Layout faylsiz)
        webView = new WebView(this);
        setContentView(webView);
        
        // WebView sozlamalari
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        
        // Havolalarni ichida ochish
        webView.setWebViewClient(new WebViewClient());
        
        // Saytni yuklash
        webView.loadUrl(URL);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
