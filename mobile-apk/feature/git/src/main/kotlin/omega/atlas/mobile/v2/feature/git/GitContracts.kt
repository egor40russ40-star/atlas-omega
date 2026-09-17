package omega.atlas.mobile.v2.feature.git

import omega.atlas.mobile.v2.core.result.AtlasResult

enum class GitChangeKind {
    MODIFIED,
    ADDED,
    DELETED,
    RENAMED,
    UNTRACKED,
    CONFLICT,
}

data class GitFileChange(
    val path: String,
    val kind: GitChangeKind,
    val staged: Boolean,
    val additions: Int = 0,
    val deletions: Int = 0,
)

data class GitSnapshot(
    val branch: String,
    val ahead: Int = 0,
    val behind: Int = 0,
    val changes: List<GitFileChange> = emptyList(),
) {
    val isClean: Boolean get() = changes.isEmpty()
}

data class GitDiff(
    val path: String,
    val unifiedDiff: String,
)

interface GitRepository {
    suspend fun status(workspacePath: String): AtlasResult<GitSnapshot>
    suspend fun diff(workspacePath: String, path: String): AtlasResult<GitDiff>
    suspend fun stage(workspacePath: String, path: String): AtlasResult<Unit>
    suspend fun unstage(workspacePath: String, path: String): AtlasResult<Unit>
    suspend fun commit(workspacePath: String, message: String): AtlasResult<String>
}

object GitActionPolicy {
    fun canStage(change: GitFileChange): Boolean = change.kind != GitChangeKind.CONFLICT

    fun requireCommitMessage(message: String): String {
        val normalized = message.trim()
        require(normalized.isNotEmpty()) { "Commit message must not be blank" }
        require(normalized.length <= 200) { "Commit message is too long" }
        return normalized
    }

    fun supportsDestructiveReset(): Boolean = false
    fun supportsForcePush(): Boolean = false
}
