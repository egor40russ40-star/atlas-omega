package omega.atlas.mobile.v2.feature.git

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp

@Composable
fun GitScreen(
    snapshot: GitSnapshot,
    selectedPath: String?,
    diffText: String?,
    onSelectFile: (String) -> Unit,
    onStage: (String) -> Unit,
    onUnstage: (String) -> Unit,
    onCommitRequested: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Text("Git", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Ветка: ${snapshot.branch}  ↑${snapshot.ahead}  ↓${snapshot.behind}",
            style = MaterialTheme.typography.bodyMedium,
        )

        if (snapshot.isClean) {
            Surface(
                tonalElevation = 1.dp,
                shape = MaterialTheme.shapes.medium,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(
                    "Рабочее дерево чистое",
                    modifier = Modifier.padding(14.dp),
                )
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                snapshot.changes.forEach { change ->
                    GitChangeRow(
                        change = change,
                        selected = change.path == selectedPath,
                        onSelect = { onSelectFile(change.path) },
                        onStage = { onStage(change.path) },
                        onUnstage = { onUnstage(change.path) },
                    )
                }
            }
        }

        if (selectedPath != null && diffText != null) {
            HorizontalDivider()
            Text("Изменения: $selectedPath", style = MaterialTheme.typography.titleMedium)
            Surface(
                tonalElevation = 1.dp,
                shape = MaterialTheme.shapes.small,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(180.dp),
            ) {
                Text(
                    diffText,
                    modifier = Modifier
                        .padding(10.dp)
                        .verticalScroll(rememberScrollState()),
                    fontFamily = FontFamily.Monospace,
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        }

        Spacer(Modifier.height(2.dp))
        Button(
            onClick = onCommitRequested,
            enabled = snapshot.changes.any { it.staged },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("Создать commit")
        }
    }
}

@Composable
private fun GitChangeRow(
    change: GitFileChange,
    selected: Boolean,
    onSelect: () -> Unit,
    onStage: () -> Unit,
    onUnstage: () -> Unit,
) {
    Surface(
        tonalElevation = if (selected) 3.dp else 0.dp,
        shape = MaterialTheme.shapes.small,
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onSelect),
    ) {
        Column(Modifier.padding(horizontal = 10.dp, vertical = 8.dp)) {
            Text(change.path, style = MaterialTheme.typography.bodyMedium)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(
                    "${change.kind.name.lowercase()}  +${change.additions}  -${change.deletions}",
                    style = MaterialTheme.typography.labelMedium,
                )
                if (change.staged) {
                    OutlinedButton(onClick = onUnstage) { Text("Убрать из stage") }
                } else {
                    OutlinedButton(
                        onClick = onStage,
                        enabled = GitActionPolicy.canStage(change),
                    ) { Text("В stage") }
                }
            }
        }
    }
}
