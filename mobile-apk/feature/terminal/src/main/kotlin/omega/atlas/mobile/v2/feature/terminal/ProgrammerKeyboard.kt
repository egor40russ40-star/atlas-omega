package omega.atlas.mobile.v2.feature.terminal

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material3.AssistChip
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import omega.atlas.mobile.v2.core.ui.AtlasDimensions

sealed interface KeyboardAction {
    data class Special(val key: TerminalKey) : KeyboardAction
    data class Control(val character: Char) : KeyboardAction
    data class TextInput(val text: String) : KeyboardAction
}

private enum class KeyboardLayer(val label: String) {
    BASIC("BASIC"),
    SHELL("SHELL"),
    CODE("CODE"),
}

internal val CriticalActions = listOf(
    "ESC" to KeyboardAction.Special(TerminalKey.ESC),
    "TAB" to KeyboardAction.Special(TerminalKey.TAB),
    "ENTER" to KeyboardAction.Special(TerminalKey.ENTER),
    "C-C" to KeyboardAction.Control('C'),
    "↑" to KeyboardAction.Special(TerminalKey.UP),
    "↓" to KeyboardAction.Special(TerminalKey.DOWN),
    "←" to KeyboardAction.Special(TerminalKey.LEFT),
    "→" to KeyboardAction.Special(TerminalKey.RIGHT),
)

private val BasicActions = listOf(
    "HOME" to KeyboardAction.Special(TerminalKey.HOME),
    "END" to KeyboardAction.Special(TerminalKey.END),
    "PG↑" to KeyboardAction.Special(TerminalKey.PAGE_UP),
    "PG↓" to KeyboardAction.Special(TerminalKey.PAGE_DOWN),
    "C-A" to KeyboardAction.Control('A'),
    "C-E" to KeyboardAction.Control('E'),
)

private val ShellActions = listOf(
    "C-D" to KeyboardAction.Control('D'),
    "C-Z" to KeyboardAction.Control('Z'),
    "C-L" to KeyboardAction.Control('L'),
    "C-R" to KeyboardAction.Control('R'),
    "C-W" to KeyboardAction.Control('W'),
    "C-U" to KeyboardAction.Control('U'),
    "C-K" to KeyboardAction.Control('K'),
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
    "(" to KeyboardAction.TextInput("("),
    ")" to KeyboardAction.TextInput(")"),
    ":" to KeyboardAction.TextInput(":"),
    ";" to KeyboardAction.TextInput(";"),
    "=" to KeyboardAction.TextInput("="),
    "+" to KeyboardAction.TextInput("+"),
    "'" to KeyboardAction.TextInput("'"),
    "\"" to KeyboardAction.TextInput("\""),
    "`" to KeyboardAction.TextInput("`"),
    "&" to KeyboardAction.TextInput("&"),
    "<" to KeyboardAction.TextInput("<"),
    ">" to KeyboardAction.TextInput(">"),
)

@Composable
fun ProgrammerKeyboard(
    onAction: (KeyboardAction) -> Unit,
    modifier: Modifier = Modifier,
) {
    var layer by remember { mutableStateOf(KeyboardLayer.BASIC) }

    CriticalKeyboardRow(CriticalActions, onAction, modifier)

    Row(
        modifier = modifier
            .fillMaxWidth()
            .height(AtlasDimensions.keyboardRowHeight)
            .horizontalScroll(rememberScrollState())
            .padding(horizontal = 6.dp),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        KeyboardLayer.entries.forEach { item ->
            AssistChip(
                onClick = { layer = item },
                label = { Text(if (layer == item) "● ${item.label}" else item.label, fontSize = 10.sp) },
            )
        }

        val actions = when (layer) {
            KeyboardLayer.BASIC -> BasicActions
            KeyboardLayer.SHELL -> ShellActions
            KeyboardLayer.CODE -> CodeActions
        }
        actions.forEach { (label, action) ->
            AssistChip(
                onClick = { onAction(action) },
                label = { Text(label, fontSize = 10.sp) },
            )
        }
    }
}

@Composable
private fun CriticalKeyboardRow(
    actions: List<Pair<String, KeyboardAction>>,
    onAction: (KeyboardAction) -> Unit,
    modifier: Modifier,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .height(AtlasDimensions.keyboardRowHeight)
            .padding(horizontal = 4.dp),
        horizontalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        actions.forEach { (label, action) ->
            OutlinedButton(
                onClick = { onAction(action) },
                modifier = Modifier
                    .weight(1f)
                    .height(AtlasDimensions.keyboardRowHeight),
                contentPadding = PaddingValues(0.dp),
            ) {
                Text(label, fontSize = 9.sp, maxLines = 1)
            }
        }
    }
}
