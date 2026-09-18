package omega.atlas.mobile.v2.app

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import omega.atlas.mobile.v2.core.model.TerminalLifecycleState
import omega.atlas.mobile.v2.feature.terminal.TerminalWorkspaceChrome

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
fun AtlasMobileV2Shell() {
    var destination by remember { mutableStateOf(RootDestination.TERMINAL) }
    var secondaryTitle by remember { mutableStateOf<String?>(null) }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(secondaryTitle ?: destination.title)
                        Text(
                            "ATLAS Mobile 2 • alpha2-dev",
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
                secondaryTitle != null -> SecondaryWorkspace(
                    title = secondaryTitle!!,
                    onBack = { secondaryTitle = null },
                )
                destination == RootDestination.TERMINAL -> TerminalHome()
                destination == RootDestination.CODE -> CodeHome()
                destination == RootDestination.FILES -> FilesHome()
                destination == RootDestination.ATLAS -> AtlasHome()
                else -> MoreHome(onOpen = { secondaryTitle = it })
            }
        }
    }
}

@Composable
private fun TerminalHome() {
    TerminalWorkspaceChrome(
        title = "Рабочая сессия",
        state = TerminalLifecycleState.DISCONNECTED,
        onKeyboardAction = {},
        terminalContent = {
            Box(
                Modifier
                    .fillMaxSize()
                    .background(MaterialTheme.colorScheme.background),
                contentAlignment = Alignment.Center,
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        ">_",
                        style = MaterialTheme.typography.displaySmall,
                        fontFamily = FontFamily.Monospace,
                        color = MaterialTheme.colorScheme.primary,
                    )
                    Text("Терминал готов к подключению профиля")
                    Text(
                        "Параметры SSH больше не занимают рабочий экран",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        },
    )
}

@Composable
private fun CodeHome() = WorkspacePlaceholder(
    title = "Редактор кода",
    subtitle = "Открытие path:line, сохранение с conflict guard и отправка в терминал",
    glyph = "{ }",
)

@Composable
private fun FilesHome() = WorkspacePlaceholder(
    title = "Файлы",
    subtitle = "Удалённое дерево проекта через защищённый SFTP",
    glyph = "▤",
)

@Composable
private fun AtlasHome() = WorkspacePlaceholder(
    title = "ATLAS",
    subtitle = "Машины, задания, здоровье системы и AI-помощник",
    glyph = "Ω",
)

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
private fun SecondaryWorkspace(title: String, onBack: () -> Unit) {
    Column(
        Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Card(onClick = onBack) {
            Text("← Назад", modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp))
        }
        WorkspacePlaceholder(
            title = title,
            subtitle = when (title) {
                "Git" -> "Безопасный diff-first workflow; destructive-операции не выполняются автоматически"
                "Подключения" -> "Настройка профиля вынесена из терминала и выполняется один раз"
                "Мониторинг" -> "Послойная диагностика вместо ложного ONLINE"
                else -> "Раздел включён в новый V2 shell"
            },
            glyph = when (title) {
                "Git" -> "git"
                "Подключения" -> "↔"
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
