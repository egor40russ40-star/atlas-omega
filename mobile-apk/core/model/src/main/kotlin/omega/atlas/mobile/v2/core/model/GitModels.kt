package omega.atlas.mobile.v2.core.model

enum class GitFileState {
    UNTRACKED,
    MODIFIED,
    ADDED,
    DELETED,
    RENAMED,
    CONFLICTED,
}

data class GitFileChange(
    val path: String,
    val state: GitFileState,
    val staged: Boolean,
)

data class GitWorkingTreeState(
    val branch: String,
    val head: String? = null,
    val changes: List<GitFileChange> = emptyList(),
    val ahead: Int = 0,
    val behind: Int = 0,
)
