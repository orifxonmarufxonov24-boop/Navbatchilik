/*
 * NAVBATCHILIK - Orifxon Marufxonov
 * v1.2.0 - Kamera va Face ID qo'llab-quvvatlash
 */
package com.navbatchilik.app;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.View;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.Toast;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends Activity {

    private WebView webView;
    private ValueCallback<Uri[]> filePathCallback;
    private String cameraPhotoPath;
    
    private static final int CAMERA_PERMISSION_REQUEST = 100;
    private static final int FILE_CHOOSER_REQUEST = 101;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Kamera ruxsatini so'rash
        requestCameraPermission();
        
        webView = findViewById(R.id.webview);
        Button refreshButton = findViewById(R.id.refreshButton);
        
        // Refresh tugmasi
        refreshButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                webView.reload();
            }
        });
        
        // WebView sozlamalari
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        
        // WebViewClient - linklar shu ilovada ochilsin
        webView.setWebViewClient(new WebViewClient());
        
        // WebChromeClient - kamera va fayl yuklash uchun
        webView.setWebChromeClient(new WebChromeClient() {
            
            // Kamera ruxsati (WebRTC uchun)
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        request.grant(request.getResources());
                    }
                });
            }
            
            // Fayl tanlash (input type="file" uchun)
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {
                
                if (MainActivity.this.filePathCallback != null) {
                    MainActivity.this.filePathCallback.onReceiveValue(null);
                }
                MainActivity.this.filePathCallback = filePathCallback;
                
                // Kamera uchun intent yaratish
                Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
                    File photoFile = null;
                    try {
                        photoFile = createImageFile();
                    } catch (IOException ex) {
                        Toast.makeText(MainActivity.this, "Rasm yaratishda xatolik", Toast.LENGTH_SHORT).show();
                    }
                    
                    if (photoFile != null) {
                        cameraPhotoPath = "file:" + photoFile.getAbsolutePath();
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                            takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT,
                                FileProvider.getUriForFile(MainActivity.this,
                                    getApplicationContext().getPackageName() + ".fileprovider",
                                    photoFile));
                        } else {
                            takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, Uri.fromFile(photoFile));
                        }
                    } else {
                        takePictureIntent = null;
                    }
                }
                
                // Galereyadan tanlash uchun intent
                Intent contentSelectionIntent = new Intent(Intent.ACTION_GET_CONTENT);
                contentSelectionIntent.addCategory(Intent.CATEGORY_OPENABLE);
                contentSelectionIntent.setType("image/*");
                
                // Tanlash dialogini ko'rsatish
                Intent[] intentArray;
                if (takePictureIntent != null) {
                    intentArray = new Intent[]{takePictureIntent};
                } else {
                    intentArray = new Intent[0];
                }
                
                Intent chooserIntent = new Intent(Intent.ACTION_CHOOSER);
                chooserIntent.putExtra(Intent.EXTRA_INTENT, contentSelectionIntent);
                chooserIntent.putExtra(Intent.EXTRA_TITLE, "Rasm tanlang");
                chooserIntent.putExtra(Intent.EXTRA_INITIAL_INTENTS, intentArray);
                
                startActivityForResult(chooserIntent, FILE_CHOOSER_REQUEST);
                return true;
            }
        });
        
        webView.loadUrl("https://ttjmchs.streamlit.app/");
    }
    
    // Rasm faylini yaratish
    private File createImageFile() throws IOException {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        
        File image = File.createTempFile(imageFileName, ".jpg", storageDir);
        cameraPhotoPath = "file:" + image.getAbsolutePath();
        return image;
    }
    
    // Kamera ruxsatini so'rash
    private void requestCameraPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    new String[]{
                        Manifest.permission.CAMERA,
                        Manifest.permission.READ_EXTERNAL_STORAGE,
                        Manifest.permission.WRITE_EXTERNAL_STORAGE
                    },
                    CAMERA_PERMISSION_REQUEST);
        }
    }
    
    // Fayl tanlash natijasi
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        
        if (requestCode == FILE_CHOOSER_REQUEST) {
            if (filePathCallback == null) return;
            
            Uri[] results = null;
            
            if (resultCode == Activity.RESULT_OK) {
                if (data != null && data.getData() != null) {
                    // Galereyadan tanlangan
                    results = new Uri[]{data.getData()};
                } else if (cameraPhotoPath != null) {
                    // Kameradan olingan
                    results = new Uri[]{Uri.parse(cameraPhotoPath)};
                }
            }
            
            filePathCallback.onReceiveValue(results);
            filePathCallback = null;
        }
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
