package omega.atlas.mobile

import android.annotation.SuppressLint
import android.graphics.Color as AndroidColor
import android.net.Uri
import android.net.http.SslError
import android.os.Bundle
import android.webkit.SslErrorHandler
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import org.connectbot.terminal.Terminal as TerminalView
import org.connectbot.terminal.TerminalEmulator
import org.connectbot.terminal.TerminalEmulatorFactory

class MainActivity : ComponentActivity() {
    private val connectionState = mutableStateOf<TerminalConnectionState>(TerminalConnectionState.Disconnected)
    private val importedKey = mutableStateOf("")
    private val importedKeyName = mutableStateOf("Ключ не выбран")
    private lateinit var emulator: TerminalEmulator
    private lateinit var controller: SshTerminalController
    private var lastProfile: SshProfile? = null

    private val keyPicker = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        if (uri == null) return@registerForActivityResult
        runCatching {
            val text = contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
                ?: error("Не удалось прочитать файл")
            require(text.contains("PRIVATE KEY")) { "Файл не похож на приватный SSH-ключ" }
            importedKey.value = text
            importedKeyName.value = uri.lastPathSegment?.substringAfterLast('/') ?: "SSH-ключ импортирован"
        }.onFailure {
            importedKey.value = ""
            importedKeyName.value = "Ошибка импорта: ${it.message}"
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val prefs = getSharedPreferences("atlas_mobile_v2", MODE_PRIVATE)

        controller = SshTerminalController(
            prefs = prefs,
            onBytes = { bytes -> emulator.writeInput(bytes) },
            onState = { state -> runOnUiThread { connectionState.value = state } },
        )
        emulator = TerminalEmulatorFactory.create(
            initialRows = 24,
            initialCols = 80,
            onKeyboardInput = { bytes -> controller.send(bytes) },
            autoDetectUrls = true,
            boldAsBright = true,
        )

        setContent {
            AtlasTheme {
                AtlasMobileApp(
                    gatewayInitial = prefs.getString("gateway", AtlasConfig.DEFAULT_GATEWAY) ?: AtlasConfig.DEFAULT_GATEWAY,
                    hostInitial = prefs.getString("ssh_host", AtlasConfig.DEFAULT_SSH_HOST) ?: AtlasConfig.DEFAULT_SSH_HOST,
                    portInitial = prefs.getInt("ssh_port", AtlasConfig.DEFAULT_SSH_PORT),
                    userInitial = prefs.getString("ssh_user", AtlasConfig.DEFAULT_SSH_USER) ?: AtlasConfig.DEFAULT_SSH_USER,
                    onPersist = { gateway, host, port, user ->
                        prefs.edit()
                            .putString("gateway", gateway)
                            .putString("ssh_host", host)
                            .putInt("ssh_port", port)
                            .putString("ssh_user", user)
                            .apply()
                    },
                )
            }
        }
    }

    override fun onDestroy() {
        controller.disconnect(false)
        super.onDestroy()
    }

    @OptIn(ExperimentalMaterial3Api::class)
    @Composable
    private fun AtlasMobileApp(
        gatewayInitial: String,
        hostInitial: String,
        portInitial: Int,
        userInitial: String,
        onPersist: (String, String, Int, String) -> Unit,
    ) {
        var tab by remember { mutableIntStateOf(0) }
        var gateway by remember { mutableStateOf(gatewayInitial) }
        var host by remember { mutableStateOf(hostInitial) }
        var portText by remember { mutableStateOf(portInitial.toString()) }
        var user by remember { mutableStateOf(userInitial) }
        var password by remember { mutableStateOf("") }
        var keyPassphrase by remember { mutableStateOf("") }

        val state by connectionState
        val connected = state is TerminalConnectionState.Connected
        val statusText = when (state) {
            TerminalConnectionState.Disconnected -> "ОТКЛЮЧЕНО"
            is TerminalConnectionState.Connecting -> "СОЕДИНЕНИЕ"
            is TerminalConnectionState.HostKeyPending -> "КЛЮЧ SSH"
            is TerminalConnectionState.Connected -> "ТЕРМИНАЛ ГОТОВ"
            is TerminalConnectionState.Failed -> "ОШИБКА"
        }

        Scaffold(
            containerColor = Color(0xFF080B10),
            topBar = {
                TopAppBar(
                    title = {
                        Column {
                            Text("ATLAS Mobile 2", fontSize = 18.sp)
                            Text("$statusText • ${AtlasConfig.VERSION}", fontSize = 11.sp, color = Color(0xFF93A4B8))
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = Color(0xFF11171F)),
                )
            },
            bottomBar = {
                NavigationBar(containerColor = Color(0xFF11171F)) {
                    listOf("Терминал", "ATLAS", "Настройки").forEachIndexed { index, label ->
                        NavigationBarItem(
                            selected = tab == index,
                            onClick = { tab = index },
                            icon = { Text(listOf("⌨", "Ω", "⚙")[index]) },
                            label = { Text(label) },
                        )
                    }
                }
            },
        ) { insets ->
            Box(Modifier.padding(insets).fillMaxSize()) {
                when (tab) {
                    0 -> TerminalScreen(
                        state = state,
                        emulator = emulator,
                        connected = connected,
                        host = host,
                        portText = portText,
                        user = user,
                        password = password,
                        keyPassphrase = keyPassphrase,
                        onHost = { host = it },
                        onPort = { portText = it.filter(Char::isDigit).take(5) },
                        onUser = { user = it },
                        onPassword = { password = it },
                        onKeyPassphrase = { keyPassphrase = it },
                        keyName = importedKeyName.value,
                        onPickKey = { keyPicker.launch(arrayOf("text/*", "application/octet-stream", "*/*")) },
                        onConnect = {
                            val port = portText.toIntOrNull() ?: AtlasConfig.DEFAULT_SSH_PORT
                            onPersist(gateway, host, port, user)
                            emulator.clearScreen()
                            val profile = SshProfile(host.trim(), port, user.trim(), password, importedKey.value, keyPassphrase)
                            lastProfile = profile
                            controller.connect(profile)
                        },
                        onTrust = {
                            if (controller.trustPendingHostKey()) lastProfile?.let(controller::connect)
                        },
                        onDisconnect = { controller.disconnect() },
                        onSend = controller::send,
                    )
                    1 -> GatewayScreen(gateway)
                    else -> SettingsScreen(
                        gateway = gateway,
                        host = host,
                        portText = portText,
                        user = user,
                        onGateway = { gateway = it },
                        onHost = { host = it },
                        onPort = { portText = it.filter(Char::isDigit).take(5) },
                        onUser = { user = it },
                        onSave = {
                            val normalized = AtlasConfig.normalizeGateway(gateway)
                            if (AtlasConfig.isAllowedGateway(normalized)) {
                                gateway = normalized
                                onPersist(normalized, host.trim(), portText.toIntOrNull() ?: 22, user.trim())
                            }
                        },
                    )
                }
            }
        }
    }

    @Composable
    private fun TerminalScreen(
        state: TerminalConnectionState,
        emulator: TerminalEmulator,
        connected: Boolean,
        host: String,
        portText: String,
        user: String,
        password: String,
        keyPassphrase: String,
        onHost: (String) -> Unit,
        onPort: (String) -> Unit,
        onUser: (String) -> Unit,
        onPassword: (String) -> Unit,
        onKeyPassphrase: (String) -> Unit,
        keyName: String,
        onPickKey: () -> Unit,
        onConnect: () -> Unit,
        onTrust: () -> Unit,
        onDisconnect: () -> Unit,
        onSend: (ByteArray) -> Unit,
    ) {
        Column(Modifier.fillMaxSize().background(Color.Black)) {
            if (!connected) {
                ConnectionPanel(
                    state, host, portText, user, password, keyPassphrase,
                    onHost, onPort, onUser, onPassword, onKeyPassphrase,
                    keyName, onPickKey, onConnect, onTrust,
                )
            }

            Box(Modifier.weight(1f).fillMaxWidth().background(Color.Black)) {
                TerminalView(
                    terminalEmulator = emulator,
                    modifier = Modifier.fillMaxSize(),
                    keyboardEnabled = connected,
                    showSoftKeyboard = true,
                    initialFontSize = 12.sp,
                    backgroundColor = Color.Black,
                    foregroundColor = Color(0xFFE6EDF3),
                    onPasteRequest = { pasteClipboard(onSend) },
                )
            }

            TerminalKeyboard(onSend)
            if (connected) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 4.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("SSH через Tailscale • xterm-256color", color = Color(0xFF8FA3B8), fontSize = 11.sp)
                    OutlinedButton(onClick = onDisconnect) { Text("Отключить") }
                }
            }
        }
    }

    @Composable
    private fun ConnectionPanel(
        state: TerminalConnectionState,
        host: String,
        portText: String,
        user: String,
        password: String,
        keyPassphrase: String,
        onHost: (String) -> Unit,
        onPort: (String) -> Unit,
        onUser: (String) -> Unit,
        onPassword: (String) -> Unit,
        onKeyPassphrase: (String) -> Unit,
        keyName: String,
        onPickKey: () -> Unit,
        onConnect: () -> Unit,
        onTrust: () -> Unit,
    ) {
        Card(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF11171F)),
        ) {
            Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                Text("Терминал NucBox", color = Color.White)
                Text(
                    when (state) {
                        TerminalConnectionState.Disconnected -> "Введите параметры SSH. Пароль и приватный ключ не сохраняются приложением."
                        is TerminalConnectionState.Connecting -> state.message
                        is TerminalConnectionState.HostKeyPending -> "Новый ключ сервера: ${state.fingerprint}. Сверьте отпечаток и подтвердите доверие."
                        is TerminalConnectionState.Failed -> state.message
                        is TerminalConnectionState.Connected -> state.endpoint
                    },
                    color = if (state is TerminalConnectionState.Failed) Color(0xFFFF7777) else Color(0xFF9FB0C3),
                    fontSize = 12.sp,
                )
                if (state is TerminalConnectionState.HostKeyPending) {
                    Button(onClick = onTrust) { Text("Доверять этому ключу и подключиться") }
                    return@Column
                }
                OutlinedTextField(host, onHost, label = { Text("Хост") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(user, onUser, label = { Text("Пользователь") }, singleLine = true, modifier = Modifier.weight(1f))
                    OutlinedTextField(portText, onPort, label = { Text("Порт") }, singleLine = true, modifier = Modifier.weight(0.45f))
                }
                OutlinedTextField(
                    password, onPassword, label = { Text("Пароль (если разрешён)") },
                    visualTransformation = PasswordVisualTransformation(), singleLine = true, modifier = Modifier.fillMaxWidth(),
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onPickKey, modifier = Modifier.weight(1f)) { Text("Импорт SSH-ключа") }
                    Text(keyName, color = Color(0xFF9FB0C3), fontSize = 11.sp, modifier = Modifier.weight(1f).padding(top = 12.dp))
                }
                OutlinedTextField(
                    keyPassphrase, onKeyPassphrase, label = { Text("Пароль ключа (если есть)") },
                    visualTransformation = PasswordVisualTransformation(), singleLine = true, modifier = Modifier.fillMaxWidth(),
                )
                Button(onClick = onConnect, enabled = host.isNotBlank() && user.isNotBlank(), modifier = Modifier.fillMaxWidth()) {
                    Text("Подключить терминал")
                }
            }
        }
    }

    @Composable
    private fun TerminalKeyboard(onSend: (ByteArray) -> Unit) {
        val scroll = rememberScrollState()
        Column(Modifier.fillMaxWidth().background(Color(0xFF0E141C)).padding(vertical = 3.dp)) {
            Row(Modifier.horizontalScroll(scroll).padding(horizontal = 4.dp), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                KeyButton("ESC") { onSend(TerminalKeys.esc) }
                KeyButton("TAB") { onSend(TerminalKeys.tab) }
                KeyButton("CTRL+C") { onSend(TerminalKeys.ctrl('C')) }
                KeyButton("CTRL+D") { onSend(TerminalKeys.ctrl('D')) }
                KeyButton("CTRL+Z") { onSend(TerminalKeys.ctrl('Z')) }
                KeyButton("CTRL+L") { onSend(TerminalKeys.ctrl('L')) }
                KeyButton("CTRL+R") { onSend(TerminalKeys.ctrl('R')) }
                KeyButton("CTRL+A") { onSend(TerminalKeys.ctrl('A')) }
                KeyButton("CTRL+E") { onSend(TerminalKeys.ctrl('E')) }
                KeyButton("CTRL+W") { onSend(TerminalKeys.ctrl('W')) }
            }
            Row(Modifier.horizontalScroll(rememberScrollState()).padding(horizontal = 4.dp), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                KeyButton("←") { onSend(TerminalKeys.left) }
                KeyButton("↑") { onSend(TerminalKeys.up) }
                KeyButton("↓") { onSend(TerminalKeys.down) }
                KeyButton("→") { onSend(TerminalKeys.right) }
                listOf("|", "\\", "~", "_", "-", "{", "}", "[", "]", "(", ")", ":", ";", "=", "+").forEach { value ->
                    KeyButton(value) { onSend(TerminalKeys.text(value)) }
                }
            }
        }
    }

    @Composable
    private fun KeyButton(label: String, onClick: () -> Unit) {
        OutlinedButton(onClick = onClick, modifier = Modifier.height(38.dp)) { Text(label, fontSize = 11.sp) }
    }

    @SuppressLint("SetJavaScriptEnabled")
    @Composable
    private fun GatewayScreen(gateway: String) {
        var status by remember(gateway) { mutableStateOf("Подключение…") }
        Column(Modifier.fillMaxSize()) {
            Text("Шлюз ATLAS: $status", color = Color(0xFF9FB0C3), fontSize = 12.sp, modifier = Modifier.padding(8.dp))
            AndroidView(
                modifier = Modifier.fillMaxSize(),
                factory = { context ->
                    WebView(context).apply {
                        setBackgroundColor(AndroidColor.rgb(8, 11, 16))
                        settings.javaScriptEnabled = true
                        settings.domStorageEnabled = true
                        settings.allowFileAccess = false
                        settings.allowContentAccess = true
                        settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
                        settings.userAgentString = settings.userAgentString + " ATLAS-Mobile-Android/0.2.0-alpha1"
                        webViewClient = object : WebViewClient() {
                            override fun onPageFinished(view: WebView?, url: String?) { status = "подключён" }
                            override fun onReceivedError(view: WebView?, request: WebResourceRequest?, error: WebResourceError?) {
                                if (request?.isForMainFrame == true) status = "ошибка: ${error?.description ?: "сеть"}"
                            }
                            override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: SslError?) {
                                handler?.cancel()
                                status = "ошибка TLS — соединение заблокировано"
                            }
                        }
                        if (AtlasConfig.isAllowedGateway(gateway)) loadUrl(gateway)
                    }
                },
                update = { view ->
                    if (AtlasConfig.isAllowedGateway(gateway) && view.url != gateway) view.loadUrl(gateway)
                },
            )
        }
    }

    @Composable
    private fun SettingsScreen(
        gateway: String,
        host: String,
        portText: String,
        user: String,
        onGateway: (String) -> Unit,
        onHost: (String) -> Unit,
        onPort: (String) -> Unit,
        onUser: (String) -> Unit,
        onSave: () -> Unit,
    ) {
        Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Настройки подключения", style = MaterialTheme.typography.titleLarge)
            OutlinedTextField(gateway, onGateway, label = { Text("HTTPS-шлюз ATLAS") }, singleLine = true, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(host, onHost, label = { Text("SSH-хост NucBox") }, singleLine = true, modifier = Modifier.fillMaxWidth())
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(user, onUser, label = { Text("Пользователь") }, singleLine = true, modifier = Modifier.weight(1f))
                OutlinedTextField(portText, onPort, label = { Text("Порт") }, singleLine = true, modifier = Modifier.weight(0.45f))
            }
            Button(onClick = onSave, enabled = AtlasConfig.isAllowedGateway(gateway)) { Text("Сохранить") }
            Spacer(Modifier.height(12.dp))
            Text("Безопасность", style = MaterialTheme.typography.titleMedium)
            Text("• Только HTTPS для шлюза.\n• SSH-ключ сервера закрепляется по SHA-256.\n• Пароль и приватный SSH-ключ не сохраняются.\n• Новому устройству не выдаются торговые права.\n• LIVE_TRADING_ENABLED = NO\n• RESEARCH_ONLY = YES", color = Color(0xFF9FB0C3))
            Text("Интерфейс приложения — русский. Вывод Linux, Git, Python и других инструментов в терминале показывается без перевода.", color = Color(0xFF9FB0C3))
        }
    }

    private fun pasteClipboard(onSend: (ByteArray) -> Unit) {
        val clipboard = getSystemService(CLIPBOARD_SERVICE) as android.content.ClipboardManager
        val text = clipboard.primaryClip?.getItemAt(0)?.coerceToText(this)?.toString() ?: return
        onSend(text.toByteArray(Charsets.UTF_8))
    }
}

private val AtlasColors: ColorScheme = darkColorScheme(
    primary = Color(0xFF4EA1FF),
    secondary = Color(0xFF43C97C),
    background = Color(0xFF080B10),
    surface = Color(0xFF11171F),
    onPrimary = Color.Black,
    onBackground = Color(0xFFE8EEF6),
    onSurface = Color(0xFFE8EEF6),
)

@Composable
private fun AtlasTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = AtlasColors, content = content)
}
