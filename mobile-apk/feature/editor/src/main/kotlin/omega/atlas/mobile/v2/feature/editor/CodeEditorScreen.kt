package omega.atlas.mobile.v2.feature.editor

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp

@Composable
fun CodeEditorScreen(
    path: String,
    text: String,
    dirty: Boolean,
    onTextChange: (String) -> Unit,
    onSave: () -> Unit,
    canUndo: Boolean,
    canRedo: Boolean,
    conflict: Boolean,
    onUndo: () -> Unit,
    onRedo: () -> Unit,
    onReloadConflict: () -> Unit,
    onTerminalAction: (CodeToTerminalAction, String) -> Unit,
    modifier: Modifier = Modifier,
) {
    var query by remember(path) { mutableStateOf("") }
    var ignoreCase by remember(path) { mutableStateOf(false) }
    var matchIndex by remember(path, query, ignoreCase) { mutableIntStateOf(0) }
    var confirmReload by remember(path) { mutableStateOf(false) }
    var fieldValue by remember(path) { mutableStateOf(TextFieldValue(text)) }

    LaunchedEffect(text) {
        if (fieldValue.text != text) {
            val start = fieldValue.selection.start.coerceIn(0, text.length)
            val end = fieldValue.selection.end.coerceIn(0, text.length)
            fieldValue = TextFieldValue(
                text = text,
                selection = TextRange(start, end),
            )
        }
    }

    val matches = remember(text, query, ignoreCase) {
        EditorSearchPolicy.findAll(text, query, ignoreCase)
    }
    val lineCount = remember(text) { EditorSearchPolicy.lineCount(text) }
    val cursor = EditorSearchPolicy.locationAt(text, fieldValue.selection.end)

    fun selectMatch(index: Int) {
        if (matches.isEmpty()) return
        val normalized = ((index % matches.size) + matches.size) % matches.size
        matchIndex = normalized
        val match = matches[normalized]
        fieldValue = fieldValue.copy(selection = TextRange(match.start, match.endExclusive))
    }

    Column(modifier = modifier.fillMaxSize()) {
        if (conflict) {
            Card(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 4.dp),
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(10.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    Text(
                        "Файл изменился на сервере. Черновик не перезаписан.",
                        modifier = Modifier.weight(1f),
                        style = MaterialTheme.typography.bodySmall,
                    )
                    OutlinedButton(onClick = { confirmReload = true }) { Text("Перезагрузить") }
                }
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 6.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(path, style = MaterialTheme.typography.titleSmall, maxLines = 1)
                Text(
                    buildString {
                        append("Строк: ")
                        append(lineCount)
                        append(" • Ln ")
                        append(cursor.line)
                        append(", Col ")
                        append(cursor.column)
                        if (dirty) append(" • изменён")
                    },
                    style = MaterialTheme.typography.labelSmall,
                )
            }
            OutlinedButton(onClick = onUndo, enabled = canUndo) { Text("↶") }
            OutlinedButton(onClick = onRedo, enabled = canRedo) { Text("↷") }
            Button(onClick = onSave, enabled = dirty && !conflict) { Text("Сохранить") }
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 2.dp),
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = { Text("Поиск") },
                singleLine = true,
                modifier = Modifier.weight(1f),
                supportingText = {
                    if (query.isNotEmpty()) {
                        Text(if (matches.isEmpty()) "Нет совпадений" else "${matchIndex + 1}/${matches.size}")
                    }
                },
            )
            OutlinedButton(onClick = { ignoreCase = !ignoreCase }) {
                Text(if (ignoreCase) "Aa ≈" else "Aa =")
            }
            OutlinedButton(
                onClick = { selectMatch(matchIndex - 1) },
                enabled = matches.isNotEmpty(),
            ) { Text("↑") }
            OutlinedButton(
                onClick = { selectMatch(matchIndex + 1) },
                enabled = matches.isNotEmpty(),
            ) { Text("↓") }
        }

        BasicTextField(
            value = fieldValue,
            onValueChange = { updated ->
                val changed = updated.text != fieldValue.text
                fieldValue = updated
                if (changed) onTextChange(updated.text)
            },
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.background)
                .horizontalScroll(rememberScrollState())
                .padding(12.dp),
            textStyle = TextStyle(
                color = MaterialTheme.colorScheme.onBackground,
                fontFamily = FontFamily.Monospace,
            ),
            cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
        )

        Row(
            modifier = Modifier.fillMaxWidth().padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            OutlinedButton(
                onClick = { onTerminalAction(CodeToTerminalAction.INSERT, fieldValue.text) },
                modifier = Modifier.weight(1f),
            ) { Text("Вставить в терминал") }
            Button(
                onClick = { onTerminalAction(CodeToTerminalAction.RUN, fieldValue.text) },
                modifier = Modifier.weight(1f),
            ) { Text("Выполнить") }
        }
    }

    if (confirmReload) {
        AlertDialog(
            onDismissRequest = { confirmReload = false },
            title = { Text("Отбросить локальный черновик?") },
            text = {
                Text("Будет загружена текущая версия файла с сервера. Несохранённые локальные изменения будут потеряны.")
            },
            confirmButton = {
                Button(
                    onClick = {
                        confirmReload = false
                        onReloadConflict()
                    }
                ) { Text("Перезагрузить") }
            },
            dismissButton = {
                OutlinedButton(onClick = { confirmReload = false }) { Text("Отмена") }
            },
        )
    }
}
