package omega.atlas.mobile.v2.core.model

enum class TrustState {
    UNENROLLED,
    PENDING,
    TRUSTED,
    REVOKED,
}

enum class OperatingMode {
    FULL,
    TERMINAL_ONLY,
    CONTROL_ONLY,
    LOCAL_CONTEXT_ONLY,
    RECOVERY,
}

enum class LayerStatus {
    UNKNOWN,
    CHECKING,
    READY,
    DEGRADED,
    BLOCKED,
    OFFLINE,
}

data class ConnectionProfile(
    val id: String,
    val title: String,
    val host: String,
    val port: Int = 22,
    val username: String,
    val workspaceRoot: String = "/home/test4/ATLAS_EXECUTION_NODE",
    val gatewayBaseUrl: String? = null,
    val trustState: TrustState = TrustState.UNENROLLED,
    val autoConnect: Boolean = true,
)

data class ConnectionHealth(
    val network: LayerStatus = LayerStatus.UNKNOWN,
    val tailnet: LayerStatus = LayerStatus.UNKNOWN,
    val gateway: LayerStatus = LayerStatus.UNKNOWN,
    val node: LayerStatus = LayerStatus.UNKNOWN,
    val ssh: LayerStatus = LayerStatus.UNKNOWN,
    val pty: LayerStatus = LayerStatus.UNKNOWN,
    val tmux: LayerStatus = LayerStatus.UNKNOWN,
    val sftp: LayerStatus = LayerStatus.UNKNOWN,
    val mode: OperatingMode = OperatingMode.LOCAL_CONTEXT_ONLY,
)
