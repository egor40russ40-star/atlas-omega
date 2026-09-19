package omega.atlas.mobile.v2.feature.connections

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.TrustState

@Composable
fun ConnectionListScreen(
    profiles: List<ConnectionProfile>,
    activeProfileId: String? = null,
    onConnect: (ConnectionProfile) -> Unit,
    onEdit: (ConnectionProfile) -> Unit,
    onAdd: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier.padding(12.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Column {
                Text("Подключения", style = MaterialTheme.typography.headlineSmall)
                Text(
                    "Настройте доступ один раз — терминал будет открываться сразу.",
                    style = MaterialTheme.typography.bodySmall,
                )
            }
            Button(onClick = onAdd) { Text("Добавить") }
        }

        LazyColumn(
            modifier = Modifier.padding(top = 12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            items(profiles, key = { it.id }) { profile ->
                ConnectionCard(
                    profile = profile,
                    active = profile.id == activeProfileId,
                    onConnect = onConnect,
                    onEdit = onEdit,
                )
            }
        }
    }
}

@Composable
private fun ConnectionCard(
    profile: ConnectionProfile,
    active: Boolean,
    onConnect: (ConnectionProfile) -> Unit,
    onEdit: (ConnectionProfile) -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Text(profile.title, style = MaterialTheme.typography.titleMedium)
                Column(horizontalAlignment = Alignment.End) {
                    if (active) {
                        Text("Активный", style = MaterialTheme.typography.labelSmall)
                    }
                    Text(trustLabel(profile.trustState), style = MaterialTheme.typography.labelMedium)
                }
            }
            Text(
                "${profile.username}@${profile.host}:${profile.port}",
                style = MaterialTheme.typography.bodyMedium,
            )
            Row(
                modifier = Modifier.padding(top = 10.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Button(
                    onClick = { onConnect(profile) },
                    enabled = profile.trustState != TrustState.REVOKED,
                ) { Text("Подключить") }
                OutlinedButton(onClick = { onEdit(profile) }) { Text("Изменить") }
            }
        }
    }
}

private fun trustLabel(state: TrustState): String = when (state) {
    TrustState.UNENROLLED -> "Не настроено"
    TrustState.PENDING -> "Ожидает доверия"
    TrustState.TRUSTED -> "Доверено"
    TrustState.REVOKED -> "Отозвано"
}
