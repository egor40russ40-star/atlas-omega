package omega.atlas.mobile.v2.core.model

data class WorkspaceDescriptor(
    val id: String,
    val title: String,
    val connectionProfileId: String,
    val rootPath: String,
    val lastOpenFile: String? = null,
    val lastOpenLine: Int? = null,
    val terminalSessionIds: List<String> = emptyList(),
    val activeTerminalSessionId: String? = null,
)

data class RemoteFileSnapshot(
    val path: String,
    val sizeBytes: Long,
    val modifiedEpochMillis: Long,
    val contentHash: String? = null,
)

data class EditorLocation(
    val path: String,
    val line: Int? = null,
    val column: Int? = null,
)
