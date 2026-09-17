package omega.atlas.mobile.v2.testing.fakes

import omega.atlas.mobile.v2.core.model.ConnectionHealth
import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.LayerStatus
import omega.atlas.mobile.v2.core.model.OperatingMode
import omega.atlas.mobile.v2.core.model.TerminalLifecycleState
import omega.atlas.mobile.v2.core.model.TerminalSessionDescriptor
import omega.atlas.mobile.v2.core.model.TrustState
import omega.atlas.mobile.v2.core.model.WorkspaceDescriptor

object FakeAtlasData {
    val nucBox = ConnectionProfile(
        id = "nucbox",
        title = "NucBox",
        host = "atlas-omega-nucbox.tailnet",
        username = "atlas",
        trustState = TrustState.TRUSTED,
    )

    val healthy = ConnectionHealth(
        network = LayerStatus.READY,
        tailnet = LayerStatus.READY,
        gateway = LayerStatus.READY,
        node = LayerStatus.READY,
        ssh = LayerStatus.READY,
        pty = LayerStatus.READY,
        tmux = LayerStatus.READY,
        sftp = LayerStatus.READY,
        mode = OperatingMode.FULL,
    )

    val workspace = WorkspaceDescriptor(
        id = "atlas-node",
        title = "ATLAS Execution Node",
        connectionProfileId = nucBox.id,
        rootPath = "~/ATLAS_EXECUTION_NODE",
        terminalSessionIds = listOf("shell-main"),
        activeTerminalSessionId = "shell-main",
    )

    val terminal = TerminalSessionDescriptor(
        id = "shell-main",
        workspaceId = workspace.id,
        connectionProfileId = nucBox.id,
        tmuxSessionName = "atlas-mobile-main",
        title = "Основной терминал",
        state = TerminalLifecycleState.READY,
    )
}
