package omega.atlas.mobile.v2.core.result

enum class ErrorDomain {
    NETWORK,
    TRUST,
    AUTH,
    SSH,
    PTY,
    TMUX,
    SFTP,
    FILE_CONFLICT,
    GATEWAY,
    STORAGE,
    VALIDATION,
    INTERNAL,
}

data class AtlasError(
    val code: String,
    val domain: ErrorDomain,
    val userMessageKey: String,
    val technicalDetail: String? = null,
    val retryable: Boolean = false,
)
