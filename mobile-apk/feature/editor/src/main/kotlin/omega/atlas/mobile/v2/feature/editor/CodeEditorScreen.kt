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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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
    onTerminalAction: (CodeToTerminalAction, String) -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier.fillMaxSize()) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(path, style = MaterialTheme.typography.titleSmall, maxLines = 1)
                if (dirty) Text("Есть несохранённые изменения", style = MaterialTheme.typography.labelSmall)
            }
            Button(onClick = onSave, enabled = dirty) { Text("Сохранить") }
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
