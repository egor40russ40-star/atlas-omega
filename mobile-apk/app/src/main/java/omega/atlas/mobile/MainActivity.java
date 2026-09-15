package omega.atlas.mobile;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.net.http.SslError;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.SslErrorHandler;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.util.Locale;

public final class MainActivity extends Activity {
    private static final String PREFS = "atlas_mobile";
    private static final String KEY_URL = "backend_url";
    private static final int FILE_CHOOSER_REQUEST = 7001;

    private WebView webView;
    private TextView stateLabel;
    private ValueCallback<Uri[]> fileCallback;
    private SharedPreferences prefs;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        buildUi();
        String url = prefs.getString(KEY_URL, "");
        if (url == null || url.isBlank()) {
            showWelcome();
        } else {
            loadBackend(url);
        }
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(11, 15, 20));

        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setPadding(dp(12), dp(8), dp(8), dp(8));
        bar.setBackgroundColor(Color.rgb(17, 23, 31));

        TextView title = new TextView(this);
        title.setText("ATLAS Mobile");
        title.setTextColor(Color.WHITE);
        title.setTextSize(18);
        title.setTypeface(null, 1);
        bar.addView(title, new LinearLayout.LayoutParams(0, dp(44), 1));

        stateLabel = new TextView(this);
        stateLabel.setText("RC0");
        stateLabel.setTextColor(Color.rgb(78, 161, 255));
        stateLabel.setTextSize(12);
        stateLabel.setGravity(Gravity.CENTER);
        bar.addView(stateLabel, new LinearLayout.LayoutParams(dp(64), dp(44)));

        Button reload = topButton("↻");
        reload.setContentDescription("Reload");
        reload.setOnClickListener(v -> webView.reload());
        bar.addView(reload, new LinearLayout.LayoutParams(dp(48), dp(44)));

        Button settingsButton = topButton("⚙");
        settingsButton.setContentDescription("Backend settings");
        settingsButton.setOnClickListener(v -> showSettings());
        bar.addView(settingsButton, new LinearLayout.LayoutParams(dp(48), dp(44)));

        root.addView(bar, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(60)));

        webView = new WebView(this);
        configureWebView(webView);
        root.addView(webView, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1));
        setContentView(root);
    }

    private Button topButton(String text) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(18);
        b.setTextColor(Color.WHITE);
        b.setBackgroundColor(Color.TRANSPARENT);
        b.setAllCaps(false);
        b.setPadding(0, 0, 0, 0);
        return b;
    }

    private void configureWebView(WebView view) {
        WebSettings s = view.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setMediaPlaybackRequiresUserGesture(true);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setUserAgentString(s.getUserAgentString() + " ATLAS-Mobile-Android/0.1.0-rc0");

        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(view, false);

        view.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest request) {
                Uri uri = request.getUrl();
                String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase(Locale.ROOT);
                if (scheme.equals("https") || (BuildConfig.DEBUG && scheme.equals("http") && isLocalHost(uri.getHost()))) {
                    return false;
                }
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, uri));
                } catch (Exception ignored) {
                    Toast.makeText(MainActivity.this, "Cannot open link", Toast.LENGTH_SHORT).show();
                }
                return true;
            }

            @Override
            public void onReceivedSslError(WebView v, SslErrorHandler handler, SslError error) {
                handler.cancel();
                stateLabel.setText("TLS ERR");
                stateLabel.setTextColor(Color.rgb(255, 90, 90));
                Toast.makeText(MainActivity.this, "TLS certificate error. Connection blocked.", Toast.LENGTH_LONG).show();
            }

            @Override
            public void onPageFinished(WebView v, String url) {
                super.onPageFinished(v, url);
                stateLabel.setText("ONLINE");
                stateLabel.setTextColor(Color.rgb(67, 201, 124));
            }
        });

        view.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                Intent intent = params.createIntent();
                try {
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                    return true;
                } catch (Exception e) {
                    fileCallback = null;
                    Toast.makeText(MainActivity.this, "File picker unavailable", Toast.LENGTH_SHORT).show();
                    return false;
                }
            }
        });
    }

    private void showWelcome() {
        stateLabel.setText("SETUP");
        String html = "<!doctype html><html><meta name='viewport' content='width=device-width,initial-scale=1'>" +
                "<body style='margin:0;background:#0b0f14;color:#e8eef6;font-family:sans-serif;padding:28px'>" +
                "<h1 style='margin-top:40px'>ATLAS Mobile</h1>" +
                "<p style='color:#9fb0c3;line-height:1.55'>Android shell RC0 установлен. Укажите защищённый HTTPS-адрес ATLAS Mobile backend через кнопку ⚙.</p>" +
                "<div style='margin-top:28px;padding:18px;border-radius:14px;background:#11171f'>" +
                "<b>STAGED RC0</b><br><span style='color:#9fb0c3'>NucBox/VM подключаются позже без пересборки APK.</span></div>" +
                "</body></html>";
        webView.loadDataWithBaseURL("https://atlas.invalid/", html, "text/html", "UTF-8", null);
    }

    private void showSettings() {
        EditText input = new EditText(this);
        input.setSingleLine(true);
        input.setHint("https://atlas.example.com");
        input.setText(prefs.getString(KEY_URL, ""));
        int p = dp(20);
        LinearLayout wrap = new LinearLayout(this);
        wrap.setPadding(p, 0, p, 0);
        wrap.addView(input, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        new AlertDialog.Builder(this)
                .setTitle("ATLAS backend")
                .setMessage(BuildConfig.DEBUG ? "HTTPS recommended. Debug also permits localhost HTTP for ADB reverse." : "Only HTTPS endpoints are permitted.")
                .setView(wrap)
                .setPositiveButton("Save & connect", (d, w) -> {
                    String value = normalizeUrl(input.getText().toString());
                    if (!isAllowedBackend(value)) {
                        Toast.makeText(this, "Use a valid HTTPS URL" + (BuildConfig.DEBUG ? " or localhost HTTP" : ""), Toast.LENGTH_LONG).show();
                        return;
                    }
                    prefs.edit().putString(KEY_URL, value).apply();
                    loadBackend(value);
                })
                .setNeutralButton("Clear", (d, w) -> {
                    prefs.edit().remove(KEY_URL).apply();
                    showWelcome();
                })
                .setNegativeButton("Cancel", null)
                .show();
    }

    private String normalizeUrl(String raw) {
        String value = raw == null ? "" : raw.trim();
        while (value.endsWith("/")) value = value.substring(0, value.length() - 1);
        return value;
    }

    private boolean isAllowedBackend(String value) {
        try {
            Uri uri = Uri.parse(value);
            String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase(Locale.ROOT);
            if (scheme.equals("https") && uri.getHost() != null) return true;
            return BuildConfig.DEBUG && scheme.equals("http") && isLocalHost(uri.getHost());
        } catch (Exception e) {
            return false;
        }
    }

    private boolean isLocalHost(String host) {
        if (host == null) return false;
        String h = host.toLowerCase(Locale.ROOT);
        return h.equals("127.0.0.1") || h.equals("localhost") || h.equals("::1");
    }

    private void loadBackend(String url) {
        if (!isAllowedBackend(url)) {
            prefs.edit().remove(KEY_URL).apply();
            showWelcome();
            Toast.makeText(this, "Unsafe backend URL rejected", Toast.LENGTH_LONG).show();
            return;
        }
        stateLabel.setText("LOAD");
        stateLabel.setTextColor(Color.rgb(78, 161, 255));
        webView.loadUrl(url);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST && fileCallback != null) {
            Uri[] result = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
            fileCallback.onReceiveValue(result);
            fileCallback = null;
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.stopLoading();
            webView.destroy();
        }
        super.onDestroy();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
