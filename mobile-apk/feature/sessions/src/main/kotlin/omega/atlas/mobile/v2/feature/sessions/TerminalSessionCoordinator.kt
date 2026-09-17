package omega.atlas.mobile.v2.feature.sessions

import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.TerminalSessionDescriptor
import omega.atlas.mobile.v2.core.result.AtlasError
import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.result.ErrorDomain
import omega.atlas.mobile.v2.feature.terminal.DeliveryCertainty
import omega.atlas.mobile.v2.feature.terminal.TerminalSessionPort

class TerminalSessionCoordinator(
    private val terminal: TerminalSessionPort,
) {
    suspend fun open(
        profile: ConnectionProfile,
        session: TerminalSessionDescriptor,
    ): AtlasResult<Unit> {
        when (val connected = terminal.connect(profile, session)) {
            is AtlasResult.Failure -> return connected
            is AtlasResult.Success -> Unit
        }

        return attachTmux(session)
    }

    suspend fun reconnect(
        cause: ReconnectCause,
        profile: ConnectionProfile,
        session: TerminalSessionDescriptor,
    ): AtlasResult<Unit> {
        val plan = ReconnectPolicy.plan(cause)
        if (!plan.reconnectTransport) {
            return AtlasResult.Failure(
                AtlasError(
                    code = "reconnect_blocked",
                    domain = ErrorDomain.VALIDATION,
                    userMessageKey = "error_reconnect_requires_action",
                    technicalDetail = cause.name,
                    retryable = false,
                )
            )
        }

        // Important: pending user input is never replayed here.
        // Only the idempotent tmux attach/create bootstrap is issued after a fresh transport.
        return open(profile, session)
    }

    suspend fun detach(): AtlasResult<Unit> = terminal.detach()

    suspend fun closeRemoteSession(): AtlasResult<Unit> = terminal.closeRemoteSession()

    private suspend fun attachTmux(session: TerminalSessionDescriptor): AtlasResult<Unit> {
        val command = try {
            TmuxSessionCommands.attachOrCreate(session.tmuxSessionName)
        } catch (e: IllegalArgumentException) {
            return AtlasResult.Failure(
                AtlasError(
                    code = "tmux_name_invalid",
                    domain = ErrorDomain.VALIDATION,
                    userMessageKey = "error_tmux_name_invalid",
                    technicalDetail = e.message,
                    retryable = false,
                )
            )
        }

        return when (val write = terminal.send(command)) {
            is AtlasResult.Failure -> write
            is AtlasResult.Success -> {
                if (write.value.certainty == DeliveryCertainty.DELIVERED) {
                    AtlasResult.Success(Unit)
                } else {
                    AtlasResult.Failure(
                        AtlasError(
                            code = "tmux_attach_delivery_unknown",
                            domain = ErrorDomain.TMUX,
                            userMessageKey = "error_tmux_attach_delivery_unknown",
                            technicalDetail = "Attach command may have reached the remote shell; it will not be replayed automatically.",
                            retryable = false,
                        )
                    )
                }
            }
        }
    }
}
