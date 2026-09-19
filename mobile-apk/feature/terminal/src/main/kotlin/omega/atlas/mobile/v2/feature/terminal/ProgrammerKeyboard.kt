package omega.atlas.mobile.v2.feature.terminal

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import omega.atlas.mobile.v2.core.ui.AtlasDimensions

sealed interface KeyboardAction {
    data class Special(val key: TerminalKey) : KeyboardAction
    data class Control(val character: Char) : KeyboardAction
    data class TextInput(val text: String) : KeyboardAction
}

private val PrimaryActions = listOf(
    "ESC" to KeyboardAction.Special(TerminalKey.ESC),
    "TAB" to KeyboardAction.Special(TerminalKey.TAB),
    "ENTER" to KeyboardAction.Special(TerminalKey.ENTER),
    "CTRL+C" to KeyboardAction.Control('C'),
    "CTRL+D" to KeyboardAction.Control('D'),
    "CTRL+Z" to KeyboardAction.Control('Z'),
    "↑" to KeyboardAction.Special(TerminalKey.UP),
    "↓" to KeyboardAction.Special(TerminalKey.DOWN),
    "←" to KeyboardAction.Special(TerminalKey.LEFT),
    "→" to KeyboardAction.Special(TerminalKey.RIGHT),
)

private val CodeActions = listOf(
    "|" to KeyboardAction.TextInput("|"),
    "\\" to KeyboardAction.TextInput("\\"),
    "~" to KeyboardAction.TextInput("~"),
    "_" to KeyboardAction.TextInput("_"),
    "-" to KeyboardAction.TextInput("-"),
    "{" to KeyboardAction.TextInput("{"),
    "}" to KeyboardAction.TextInput("}"),
    "[" to KeyboardAction.TextInput("["),
    "]" to KeyboardAction.TextInput("]"),
    "HOME" to KeyboardAction.Special(TerminalKey.HOME),
    "END" to KeyboardAction.Special(TerminalKey.END),
)

@Composable
fun ProgrammerKeyboard(
    onAction: (KeyboardAction) -> Unit,
    modifier: Modifier = Modifier,
) {
    KeyboardRow(PrimaryActions, onAction, modifier)
    KeyboardRow(CodeActions, onAction, modifier)
}

@Composable
private fun KeyboardRow(
    actions: List<Pair<String, KeyboardAction>>,
    onAction: (KeyboardAction) -> Unit,
    modifier: Modifier,
) {
    Row(
        modifier = modifier
            .height(AtlasDimensions.keyboardRowHeight)
            .horizontalScroll(rememberScrollState())
            .padding(horizontal = 6.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        actions.forEach { (label, action) ->
            AssistChip(
                onClick = { onAction(action) },
                label = { Text(label) },
            )
        }
    }
}
