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
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
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
    onUndo: () -> Unit,
    onRedo: () -> Unit,
    onTerminalAction: (CodeToTerminalAction, String) -> Unit,
    modifier: Modifier = Modifier,
) {
    var query by remember(path) { mutableStateOf("") }
    var ignoreCase by remember(path) { mutableStateOf(false) }
    val matchCount = remember(text, query, ignoreCase) {
        EditorSearchPolicy.findAll(text, query, ignoreCase).size
    }
    val lineCount = remember(text) { EditorSearchPolicy.lineCount(text) }

    Column(modifier = modifier.fillMaxSize()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 6.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(path, style = MaterialTheme.typography.titleSmall, maxLines = 1)
                Text(
                    buildString {
                        append("Строк: ")
                        append(lineCount)
                        if (dirty) append(" • есть несохранённые изменения")
                    },
                    style = MaterialTheme.typography.labelSmall,
                )
            }
            OutlinedButton(onClick = onUndo, enabled = canUndo) { Text("↶") }
            OutlinedButton(onClick = onRedo, enabled = canRedo) { Text("↷") }
            Button(onClick = onSave, enabled = dirty) { Text("Сохранить") }
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 2.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = { Text("Поиск") },
                singleLine = true,
                modifier = Modifier.weight(1f),
                supportingText = {
                    if (query.isNotEmpty()) Text("Совпадений: $matchCount")
                },
            )
            OutlinedButton(
                onClick = { ignoreCase = !ignoreCase },
            ) {
                Text(if (ignoreCase) "Aa ≈" else "Aa =")
            }
        }

        BasicTextField(
            value = text,
            onValueChange = onTextChange,
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
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            OutlinedButton(
                onClick = { onTerminalAction(CodeToTerminalAction.INSERT, text) },
                modifier = Modifier.weight(1f),
            ) { Text("Вставить в терминал") }
            Button(
                onClick = { onTerminalAction(CodeToTerminalAction.RUN, text) },
                modifier = Modifier.weight(1f),
            ) { Text("Выполнить") }
        }
    }
}
