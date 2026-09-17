package omega.atlas.mobile.v2.feature.sessions

enum class ReconnectCause {
    NETWORK_LOST,
    APP_RESUME,
    SSH_STREAM_ENDED,
    AUTH_FAILED,
    HOST_KEY_CHANGED,
    AMBIGUOUS_WRITE,
}

data class ReconnectPlan(
    val reconnectTransport: Boolean,
    val replayPendingInput: Boolean,
    val requiresUserAcknowledgement: Boolean,
)

object ReconnectPolicy {
    fun plan(cause: ReconnectCause): ReconnectPlan = when (cause) {
        ReconnectCause.NETWORK_LOST,
        ReconnectCause.APP_RESUME,
        ReconnectCause.SSH_STREAM_ENDED -> ReconnectPlan(
            reconnectTransport = true,
            replayPendingInput = false,
            requiresUserAcknowledgement = false,
        )

        ReconnectCause.AMBIGUOUS_WRITE -> ReconnectPlan(
            reconnectTransport = true,
            replayPendingInput = false,
            requiresUserAcknowledgement = true,
        )

        ReconnectCause.AUTH_FAILED,
        ReconnectCause.HOST_KEY_CHANGED -> ReconnectPlan(
            reconnectTransport = false,
            replayPendingInput = false,
            requiresUserAcknowledgement = true,
        )
    }
}
