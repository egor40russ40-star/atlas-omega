package omega.atlas.mobile.v2.feature.terminal

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import omega.atlas.mobile.v2.core.model.TerminalLifecycleState

@Composable
fun TerminalWorkspaceChrome(
    title: String,
    state: TerminalLifecycleState,
    onKeyboardAction: (KeyboardAction) -> Unit,
    terminalContent: @Composable () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier.fillMaxSize()) {
        Surface(tonalElevation = 1.dp) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(title, style = MaterialTheme.typography.titleSmall, modifier = Modifier.weight(1f))
                Text(statusLabel(state), style = MaterialTheme.typography.labelMedium)
            }
        }
        HorizontalDivider()
        Box(modifier = Modifier.weight(1f).fillMaxWidth()) {
            terminalContent()
        }
        HorizontalDivider()
        ProgrammerKeyboard(onAction = onKeyboardAction)
    }
}

private fun statusLabel(state: TerminalLifecycleState): String = when (state) {
    TerminalLifecycleState.READY -> "Подключено"
    TerminalLifecycleState.CONNECTING -> "Подключение"
    TerminalLifecycleState.AUTHENTICATING -> "Проверка доступа"
    TerminalLifecycleState.OPENING_PTY -> "Открытие терминала"
    TerminalLifecycleState.ATTACHING_TMUX -> "Восстановление сессии"
    TerminalLifecycleState.RECONNECTING -> "Восстановление связи"
    TerminalLifecycleState.BLOCKED -> "Требуется действие"
    TerminalLifecycleState.ERROR -> "Ошибка"
    TerminalLifecycleState.DISCONNECTED -> "Отключено"
}
