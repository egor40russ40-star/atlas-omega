package omega.atlas.mobile.v2.app

import androidx.compose.foundation.background
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.clickable
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Checkbox
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import omega.atlas.mobile.v2.core.model.LayerStatus
import omega.atlas.mobile.v2.core.model.TerminalLifecycleState
import omega.atlas.mobile.v2.feature.connections.ConnectionLaunchPolicy
import omega.atlas.mobile.v2.feature.connections.ConnectionListScreen
import omega.atlas.mobile.v2.feature.editor.CodeEditorScreen
import omega.atlas.mobile.v2.feature.editor.CodeToTerminalAction
import omega.atlas.mobile.v2.feature.git.GitScreen
import omega.atlas.mobile.v2.feature.terminal.KeyboardAction
import omega.atlas.mobile.v2.feature.terminal.PasteSafety
import omega.atlas.mobile.v2.feature.terminal.TerminalInputEncoder
import omega.atlas.mobile.v2.feature.terminal.TerminalKey
import omega.atlas.mobile.v2.feature.terminal.TerminalKeyEncoder
import omega.atlas.mobile.v2.feature.terminal.TerminalWorkspaceChrome
import org.connectbot.terminal.Terminal
import org.connectbot.terminal.TerminalEmulator

private enum class RootDestination(
    val title: String,
    val glyph: String,
) {
    TERMINAL("Терминал", ">_"),
    CODE("Код", "{ }"),
    FILES("Файлы", "▤"),
    ATLAS("ATLAS", "Ω"),
    MORE("Ещё", "•••"),
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AtlasMobileV2Shell(
    emulator: TerminalEmulator,
    runtime: AtlasTerminalRuntime,
    onImportPrivateKey: (String?) -> Unit,
) {
    var destination by remember { mutableStateOf(RootDestination.TERMINAL) }
    var secondaryTitle by remember { mutableStateOf<String?>(null) }
    val state by runtime.state
    val profile by runtime.profile
    val message by runtime.message

    LaunchedEffect(Unit) {
        if (ConnectionLaunchPolicy.canAutoConnect(profile)) {
            runtime.connect()
        }
    }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(secondaryTitle ?: destination.title)
                        Text(
                            "${statusLabel(state)} • ${profile.title}",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            )
        },
        bottomBar = {
            NavigationBar {
                RootDestination.entries.forEach { item ->
                    NavigationBarItem(
                        selected = destination == item && secondaryTitle == null,
                        onClick = {
                            destination = item
                            secondaryTitle = null
                        },
                        icon = { Text(item.glyph) },
                        label = { Text(item.title) },
                    )
                }
            }
        },
    ) { padding ->
        Box(
            Modifier
                .padding(padding)
                .fillMaxSize()
        ) {
            when {
                secondaryTitle == "Git" -> GitHome(
                    runtime = runtime,
                    onBack = { secondaryTitle = null },
                )
                secondaryTitle == "Мониторинг" -> MonitoringHome(
                    runtime = runtime,
                    onBack = { secondaryTitle = null },
                )
                secondaryTitle == "Подключения" -> ConnectionsWorkspace(
                    runtime = runtime,
                    onBack = { secondaryTitle = null },
                    onOpenTerminal = {
                        secondaryTitle = null
                        destination = RootDestination.TERMINAL
                    },
                    onImportPrivateKey = onImportPrivateKey,
                )
                secondaryTitle != null -> SecondaryWorkspace(
                    title = secondaryTitle!!,
                    onBack = { secondaryTitle = null },
                )
                destination == RootDestination.TERMINAL -> TerminalHome(
                    emulator = emulator,
                    runtime = runtime,
                )
                destination == RootDestination.CODE -> CodeHome(runtime)
                destination == RootDestination.FILES -> FilesHome(
                    runtime = runtime,
                    onFileOpened = { destination = RootDestination.CODE },
                )
                destination == RootDestination.ATLAS -> AtlasHome(runtime)
                else -> MoreHome(onOpen = { secondaryTitle = it })
            }
        }
    }
}

@Composable
private fun TerminalHome(
    emulator: TerminalEmulator,
    runtime: AtlasTerminalRuntime,
) {
    val state by runtime.state
    val profile by runtime.profile
    val message by runtime.message
    val pendingTrust by runtime.pendingTrust
    val clipboard = LocalClipboardManager.current
    var terminalDraft by remember(profile.id) { mutableStateOf("") }

    Column(Modifier.fillMaxSize()) {
        if (pendingTrust != null) {
            val observation = pendingTrust!!
            Card(Modifier.fillMaxWidth().padding(8.dp)) {
                Column(
                    Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text("Подтвердите SSH-сервер", style = MaterialTheme.typography.titleMedium)
                    Text("${observation.host}:${observation.port}")
                    Text(
                        observation.fingerprint,
                        fontFamily = FontFamily.Monospace,
                        style = MaterialTheme.typography.bodySmall,
                    )
                    Text(
                        "Доверие не выдаётся автоматически. Сверьте отпечаток перед подтверждением.",
                        style = MaterialTheme.typography.bodySmall,
                    )
                    Button(onClick = runtime::trustAndReconnect) {
                        Text("Доверять и подключиться")
                    }
                }
            }
        }

        TerminalWorkspaceChrome(
            title = profile.title,
            state = state,
            onKeyboardAction = { runtime.send(encodeKeyboardAction(it)) },
            terminalContent = {
                Terminal(
                    terminalEmulator = emulator,
                    modifier = Modifier.fillMaxSize(),
                    keyboardEnabled = state == TerminalLifecycleState.READY,
                    // Soft IME uses the explicit command field below. Keeping the raw
                    // terminal IME hidden avoids device-specific text composition bugs,
                    // while hardware keyboards remain enabled by termlib.
                    showSoftKeyboard = false,
                    onPasteRequest = {
                        clipboard.getText()?.text?.takeIf { it.isNotEmpty() }?.let {
                            terminalDraft = it
                        }
                    },
                    initialFontSize = 13.sp,
                    backgroundColor = Color.Black,
                    foregroundColor = Color(0xFFE6EDF3),
                )
            },
            modifier = Modifier.weight(1f),
        )

        TerminalInputBar(
            ready = state == TerminalLifecycleState.READY,
            draft = terminalDraft,
            onDraftChange = { terminalDraft = it },
            onSend = runtime::send,
        )

        Row(
            Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp, vertical = 5.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                message,
                modifier = Modifier.weight(1f),
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (state == TerminalLifecycleState.READY) {
                OutlinedButton(onClick = runtime::disconnect) { Text("Отключить") }
            } else if (pendingTrust == null) {
                Button(onClick = runtime::connect) { Text("Подключить") }
            }
        }
    }
}

@Composable
private fun TerminalInputBar(
    ready: Boolean,
    draft: String,
    onDraftChange: (String) -> Unit,
    onSend: (ByteArray) -> Unit,
) {
    val clipboard = LocalClipboardManager.current
    var confirmMultiline by remember { mutableStateOf(false) }

    fun sendDraftNow() {
        if (draft.isEmpty()) return
        onSend(TerminalInputEncoder.run(draft))
        onDraftChange("")
        confirmMultiline = false
    }

    fun requestSend() {
        if (draft.isEmpty()) return
        if (PasteSafety.requiresConfirmation(draft)) {
            confirmMultiline = true
        } else {
            sendDraftNow()
        }
    }

    Column(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp, vertical = 4.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        OutlinedTextField(
            value = draft,
            onValueChange = onDraftChange,
            label = { Text("Команда / текст") },
            enabled = ready,
            maxLines = 2,
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
            keyboardActions = KeyboardActions(onSend = { requestSend() }),
            modifier = Modifier.fillMaxWidth(),
        )
        Row(
            Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            OutlinedButton(
                onClick = {
                    val text = clipboard.getText()?.text.orEmpty()
                    if (text.isNotEmpty()) onDraftChange(text)
                },
                enabled = ready,
                modifier = Modifier.weight(1f),
            ) { Text("Вставить") }

            OutlinedButton(
                onClick = { onSend(TerminalKeyEncoder.encode(TerminalKey.ENTER)) },
                enabled = ready,
                modifier = Modifier.weight(1f),
            ) { Text("Enter") }

            Button(
                onClick = { requestSend() },
                enabled = ready && draft.isNotEmpty(),
                modifier = Modifier.weight(1f),
            ) { Text("Отправить") }
        }
    }

    if (confirmMultiline) {
        val lines = draft.lineSequence().count()
        AlertDialog(
            onDismissRequest = { confirmMultiline = false },
            title = { Text("Многострочная команда") },
            text = {
                Text(
                    "В буфере $lines строк. «Отправить» передаст их в терминал и затем Enter. Проверьте текст перед выполнением."
                )
            },
            confirmButton = {
                Button(onClick = { sendDraftNow() }) { Text("Отправить") }
            },
            dismissButton = {
                OutlinedButton(onClick = { confirmMultiline = false }) { Text("Отмена") }
            },
        )
    }
}

@Composable
private fun ConnectionsWorkspace(
    runtime: AtlasTerminalRuntime,
    onBack: () -> Unit,
    onOpenTerminal: () -> Unit,
    onImportPrivateKey: (String?) -> Unit,
) {
    val profiles by runtime.profiles
    val active by runtime.profile
    var editing by remember { mutableStateOf(false) }

    if (editing) {
        ConnectionSetup(
            runtime = runtime,
            onBack = {
                runtime.cancelProfileEdit()
                editing = false
            },
            onImportPrivateKey = onImportPrivateKey,
        )
        return
    }

    Column(Modifier.fillMaxSize()) {
        OutlinedButton(
            onClick = onBack,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
        ) { Text("← Назад") }

        ConnectionListScreen(
            profiles = profiles,
            activeProfileId = active.id,
            onConnect = { selected ->
                runtime.selectProfile(selected.id, connectAfterSelection = true)
                onOpenTerminal()
            },
            onEdit = { selected ->
                runtime.selectProfile(selected.id, connectAfterSelection = false)
                editing = true
            },
            onAdd = {
                runtime.beginNewProfile()
                editing = true
            },
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun ConnectionSetup(
    runtime: AtlasTerminalRuntime,
    onBack: () -> Unit,
    onImportPrivateKey: (String?) -> Unit,
) {
    val current by runtime.profile
    val credentialStatus by runtime.credentialStatus
    var title by remember(current.id) { mutableStateOf(current.title) }
    var host by remember(current.id) { mutableStateOf(current.host) }
    var port by remember(current.id) { mutableStateOf(current.port.toString()) }
    var username by remember(current.id) { mutableStateOf(current.username) }
    var fallbackHost by remember(current.id) {
        mutableStateOf(current.fallbackSshEndpoints.firstOrNull()?.host.orEmpty())
    }
    var fallbackPort by remember(current.id) {
        mutableStateOf(current.fallbackSshEndpoints.firstOrNull()?.port?.toString() ?: "22")
    }
    var workspaceRoot by remember(current.id) { mutableStateOf(current.workspaceRoot) }
    var gateway by remember(current.id) {
        mutableStateOf(current.gatewayBaseUrl ?: "https://tinvest-robot.tailf87948.ts.net")
    }
    var password by remember { mutableStateOf("") }
    var keyPassphrase by remember { mutableStateOf("") }
    var autoConnect by remember(current.id) { mutableStateOf(current.autoConnect) }

    LazyColumn(
        Modifier
            .fillMaxSize()
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            OutlinedButton(onClick = onBack) { Text("← Назад") }
        }
        item {
            Text("Профиль подключения", style = MaterialTheme.typography.headlineSmall)
            Text(
                "Эти параметры настраиваются один раз и больше не занимают экран терминала.",
                style = MaterialTheme.typography.bodySmall,
            )
        }
        item {
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                label = { Text("Название") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            OutlinedTextField(
                value = host,
                onValueChange = { host = it },
                label = { Text("SSH-хост") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            OutlinedTextField(
                value = gateway,
                onValueChange = { gateway = it },
                label = { Text("HTTPS Gateway ATLAS") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = username,
                    onValueChange = { username = it },
                    label = { Text("Пользователь") },
                    singleLine = true,
                    modifier = Modifier.weight(1f),
                )
                OutlinedTextField(
                    value = port,
                    onValueChange = { port = it.filter(Char::isDigit).take(5) },
                    label = { Text("Порт") },
                    singleLine = true,
                    modifier = Modifier.weight(0.45f),
                )
            }
        }
        item {
            Text("Резервный SSH-маршрут", style = MaterialTheme.typography.titleSmall)
            Text(
                "Используется только при сетевой недоступности основного адреса. Новый host key всё равно требует проверки.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = fallbackHost,
                    onValueChange = { fallbackHost = it },
                    label = { Text("Резервный хост") },
                    singleLine = true,
                    modifier = Modifier.weight(1f),
                )
                OutlinedTextField(
                    value = fallbackPort,
                    onValueChange = { fallbackPort = it.filter(Char::isDigit).take(5) },
                    label = { Text("Порт") },
                    singleLine = true,
                    modifier = Modifier.weight(0.45f),
                )
            }
        }
        item {
            OutlinedTextField(
                value = workspaceRoot,
                onValueChange = { workspaceRoot = it },
                label = { Text("Рабочая папка") },
                supportingText = { Text("Корень для Файлов, редактора, Git и self-test") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Checkbox(checked = autoConnect, onCheckedChange = { autoConnect = it })
                Text("Автоподключение после запуска (после успешной настройки)")
            }
        }
        item {
            Button(
                onClick = {
                    runtime.saveProfile(
                        title = title,
                        host = host,
                        port = port.toIntOrNull() ?: 22,
                        username = username,
                        fallbackHost = fallbackHost,
                        fallbackPort = fallbackPort.toIntOrNull() ?: 22,
                        workspaceRoot = workspaceRoot,
                        gatewayBaseUrl = gateway,
                        autoConnect = autoConnect,
                    )
                },
                enabled = host.isNotBlank() && username.isNotBlank(),
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Сохранить профиль") }
        }
        item {
            Text("Данные доступа", style = MaterialTheme.typography.titleMedium)
            Text(credentialStatus, style = MaterialTheme.typography.bodySmall)
        }
        item {
            OutlinedTextField(
                value = password,
                onValueChange = { password = it },
                label = { Text("SSH-пароль") },
                visualTransformation = PasswordVisualTransformation(),
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            Button(
                onClick = {
                    runtime.savePassword(password)
                    password = ""
                },
                enabled = password.isNotEmpty(),
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Сохранить пароль защищённо") }
        }
        item {
            OutlinedTextField(
                value = keyPassphrase,
                onValueChange = { keyPassphrase = it },
                label = { Text("Пароль приватного ключа, если есть") },
                visualTransformation = PasswordVisualTransformation(),
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
        }
        item {
            OutlinedButton(
                onClick = { onImportPrivateKey(keyPassphrase.ifBlank { null }) },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Импортировать приватный SSH-ключ") }
        }
        item {
            OutlinedButton(
                onClick = runtime::removeCredential,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Удалить сохранённые данные доступа") }
        }
        item {
            Text(
                "LIVE_TRADING_ENABLED = NO • RESEARCH_ONLY = YES",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun CodeHome(runtime: AtlasTerminalRuntime) {
    val editor by runtime.editor
    val fileMessage by runtime.filesMessage

    if (!editor.loaded) {
        WorkspacePlaceholder(
            title = if (editor.path.isBlank()) "Редактор кода" else editor.path,
            subtitle = if (editor.path.isBlank()) {
                "Откройте файл в разделе «Файлы»"
            } else {
                fileMessage
            },
            glyph = "{ }",
        )
        return
    }

    Column(Modifier.fillMaxSize()) {
        CodeEditorScreen(
            path = editor.path,
            text = editor.text,
            dirty = editor.dirty,
            onTextChange = runtime::updateEditorText,
            onSave = runtime::saveEditor,
            onTerminalAction = { action, _ ->
                runtime.insertEditorIntoTerminal(action == CodeToTerminalAction.RUN)
            },
            modifier = Modifier.weight(1f),
        )
        Text(
            if (editor.saving) "Сохранение…" else fileMessage,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun FilesHome(
    runtime: AtlasTerminalRuntime,
    onFileOpened: () -> Unit,
) {
    val path by runtime.directoryPath
    val entries by runtime.files
    val message by runtime.filesMessage
    val busy by runtime.filesBusy

    Column(Modifier.fillMaxSize()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            OutlinedButton(
                onClick = runtime::openParentDirectory,
                enabled = path != "/" && !busy,
            ) { Text("↑") }
            Text(
                path,
                modifier = Modifier.weight(1f),
                style = MaterialTheme.typography.bodySmall,
                fontFamily = FontFamily.Monospace,
                maxLines = 2,
            )
            Button(
                onClick = { runtime.refreshFiles() },
                enabled = !busy,
            ) { Text(if (busy) "…" else "Обновить") }
        }

        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            items(entries, key = { it.path }) { entry ->
                Surface(
                    tonalElevation = if (entry.directory) 1.dp else 0.dp,
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(enabled = !busy) {
                            runtime.openRemoteEntry(entry, onFileOpened)
                        },
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(if (entry.directory) "▸" else "·", modifier = Modifier.padding(end = 8.dp))
                        Column(Modifier.weight(1f)) {
                            Text(entry.name)
                            if (!entry.directory) {
                                Text(
                                    "${entry.sizeBytes} байт",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        }
                    }
                }
            }
        }

        Text(
            message,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun AtlasHome(runtime: AtlasTerminalRuntime) {
    val version by runtime.gatewayVersion
    val message by runtime.gatewayMessage
    val busy by runtime.gatewayBusy
    val profile by runtime.profile

    LaunchedEffect(profile.gatewayBaseUrl) {
        runtime.refreshGateway()
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text("ATLAS Gateway", style = MaterialTheme.typography.headlineSmall)
                    Text(
                        profile.gatewayBaseUrl ?: "Gateway не настроен",
                        style = MaterialTheme.typography.bodySmall,
                        fontFamily = FontFamily.Monospace,
                    )
                }
                Button(onClick = runtime::refreshGateway, enabled = !busy) {
                    Text(if (busy) "…" else "Проверить")
                }
            }
        }

        item {
            Card(Modifier.fillMaxWidth()) {
                Column(
                    Modifier.padding(14.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    Text(message, style = MaterialTheme.typography.bodyMedium)
                    val current = version
                    if (current != null) {
                        StatusRow("Продукт", current.product)
                        StatusRow("Версия", current.version)
                        StatusRow("API", current.apiVersion)
                        StatusRow("Режим", current.mode)
                        StatusRow("Identity", current.identityMode)
                        StatusRow("Live authority", current.liveTradingAuthority)
                    }
                }
            }
        }

        item {
            Card(Modifier.fillMaxWidth()) {
                Column(
                    Modifier.padding(14.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    Text("Безопасность клиента", style = MaterialTheme.typography.titleMedium)
                    StatusRow("LIVE_TRADING_ENABLED", "NO")
                    StatusRow("RESEARCH_ONLY", "YES")
                    Text(
                        "Приложение не получает торговые полномочия автоматически.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}

@Composable
private fun StatusRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, style = MaterialTheme.typography.bodySmall)
        Text(
            value,
            style = MaterialTheme.typography.bodySmall,
            fontFamily = FontFamily.Monospace,
        )
    }
}

@Composable
private fun MoreHome(onOpen: (String) -> Unit) {
    val sections = listOf(
        "Git" to "Diff, stage и commit",
        "Подключения" to "Профили SSH, доверие и ключи",
        "Задания" to "История и состояние задач ATLAS",
        "Мониторинг" to "Gateway, NucBox, SSH, PTY, tmux и SFTP",
        "Настройки" to "Терминал, клавиатура, язык и внешний вид",
    )
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        items(sections) { (title, subtitle) ->
            Card(onClick = { onOpen(title) }, modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp)) {
                    Text(title, style = MaterialTheme.typography.titleMedium)
                    Text(
                        subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}

@Composable
private fun GitHome(
    runtime: AtlasTerminalRuntime,
    onBack: () -> Unit,
) {
    val snapshot by runtime.gitSnapshot
    val selectedPath by runtime.gitSelectedPath
    val diff by runtime.gitDiff
    val message by runtime.gitMessage
    val busy by runtime.gitBusy
    var showCommitDialog by remember { mutableStateOf(false) }
    var commitMessage by remember { mutableStateOf("") }

    Column(Modifier.fillMaxSize()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            OutlinedButton(onClick = onBack) { Text("← Назад") }
            Text(
                message,
                modifier = Modifier.weight(1f),
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Button(onClick = runtime::refreshGit, enabled = !busy) {
                Text(if (busy) "…" else "Обновить Git")
            }
        }

        GitScreen(
            snapshot = snapshot,
            selectedPath = selectedPath,
            diffText = diff,
            onSelectFile = runtime::selectGitPath,
            onStage = runtime::stageGit,
            onUnstage = runtime::unstageGit,
            onCommitRequested = { showCommitDialog = true },
            modifier = Modifier.weight(1f),
        )
    }

    if (showCommitDialog) {
        AlertDialog(
            onDismissRequest = { if (!busy) showCommitDialog = false },
            title = { Text("Создать Git commit") },
            text = {
                OutlinedTextField(
                    value = commitMessage,
                    onValueChange = { commitMessage = it.take(200) },
                    label = { Text("Сообщение commit") },
                    modifier = Modifier.fillMaxWidth(),
                )
            },
            confirmButton = {
                Button(
                    onClick = {
                        runtime.commitGit(commitMessage)
                        commitMessage = ""
                        showCommitDialog = false
                    },
                    enabled = commitMessage.isNotBlank() && !busy,
                ) { Text("Создать") }
            },
            dismissButton = {
                OutlinedButton(
                    onClick = { showCommitDialog = false },
                    enabled = !busy,
                ) { Text("Отмена") }
            },
        )
    }
}

@Composable
private fun MonitoringHome(
    runtime: AtlasTerminalRuntime,
    onBack: () -> Unit,
) {
    val probes by runtime.healthProbes
    val busy by runtime.healthBusy
    val message by runtime.healthMessage

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                OutlinedButton(onClick = onBack) { Text("← Назад") }
                Column(Modifier.weight(1f)) {
                    Text("Мониторинг", style = MaterialTheme.typography.headlineSmall)
                    Text(
                        message,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Button(onClick = runtime::runHealthCheck, enabled = !busy) {
                    Text(if (busy) "…" else "Проверить всё")
                }
            }
        }

        items(probes, key = { it.label }) { probe ->
            var showTechnical by remember(probe.label, probe.technicalDetail) { mutableStateOf(false) }
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(14.dp)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            healthGlyph(probe.status),
                            modifier = Modifier.padding(end = 10.dp),
                            fontFamily = FontFamily.Monospace,
                        )
                        Column(Modifier.weight(1f)) {
                            Text(probe.label, style = MaterialTheme.typography.titleMedium)
                            Text(
                                probe.detail,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                        Text(
                            probe.status.name,
                            style = MaterialTheme.typography.labelSmall,
                            fontFamily = FontFamily.Monospace,
                        )
                    }
                    probe.nextAction?.let {
                        Text(
                            "Дальше: $it",
                            modifier = Modifier.padding(top = 8.dp),
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                    probe.technicalDetail?.let { technical ->
                        OutlinedButton(
                            onClick = { showTechnical = !showTechnical },
                            modifier = Modifier.padding(top = 6.dp),
                        ) {
                            Text(if (showTechnical) "Скрыть детали" else "Технические детали")
                        }
                        if (showTechnical) {
                            Text(
                                technical,
                                modifier = Modifier.padding(top = 6.dp),
                                style = MaterialTheme.typography.labelSmall,
                                fontFamily = FontFamily.Monospace,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
            }
        }

        item {
            Text(
                "Self-test использует только безопасные чтения/проверки: /version, printf-маркер SSH, SFTP list и Git status. Команды пользователя не повторяются.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

private fun healthGlyph(status: LayerStatus): String = when (status) {
    LayerStatus.READY -> "●"
    LayerStatus.CHECKING -> "◌"
    LayerStatus.BLOCKED -> "!"
    LayerStatus.DEGRADED -> "△"
    LayerStatus.OFFLINE -> "×"
    LayerStatus.UNKNOWN -> "○"
}

@Composable
private fun SecondaryWorkspace(title: String, onBack: () -> Unit) {
    Column(
        Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        OutlinedButton(onClick = onBack) { Text("← Назад") }
        WorkspacePlaceholder(
            title = title,
            subtitle = when (title) {
                "Git" -> "Безопасный diff-first workflow; destructive-операции не выполняются автоматически"
                "Мониторинг" -> "Послойная диагностика вместо ложного ONLINE"
                else -> "Раздел включён в новый V2 shell"
            },
            glyph = when (title) {
                "Git" -> "git"
                "Мониторинг" -> "◎"
                else -> "•"
            },
        )
    }
}

@Composable
private fun WorkspacePlaceholder(
    title: String,
    subtitle: String,
    glyph: String,
) {
    Surface(Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                glyph,
                style = MaterialTheme.typography.displayMedium,
                fontFamily = FontFamily.Monospace,
                color = MaterialTheme.colorScheme.primary,
            )
            Text(title, style = MaterialTheme.typography.headlineSmall)
            Text(
                subtitle,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

private fun encodeKeyboardAction(action: KeyboardAction): ByteArray = when (action) {
    is KeyboardAction.Special -> TerminalKeyEncoder.encode(action.key)
    is KeyboardAction.Control -> TerminalKeyEncoder.ctrl(action.character)
    is KeyboardAction.TextInput -> action.text.encodeToByteArray()
}

private fun statusLabel(state: TerminalLifecycleState): String = when (state) {
    TerminalLifecycleState.DISCONNECTED -> "Отключено"
    TerminalLifecycleState.CONNECTING -> "Подключение"
    TerminalLifecycleState.AUTHENTICATING -> "Проверка доступа"
    TerminalLifecycleState.OPENING_PTY -> "Открытие PTY"
    TerminalLifecycleState.ATTACHING_TMUX -> "Восстановление tmux"
    TerminalLifecycleState.READY -> "Терминал готов"
    TerminalLifecycleState.RECONNECTING -> "Восстановление связи"
    TerminalLifecycleState.BLOCKED -> "Требуется подтверждение"
    TerminalLifecycleState.ERROR -> "Ошибка"
}
