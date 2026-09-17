package omega.atlas.mobile.v2.feature.terminal

import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.TerminalLifecycleState
import omega.atlas.mobile.v2.core.model.TerminalSessionDescriptor
import omega.atlas.mobile.v2.core.result.AtlasResult

interface TerminalSessionPort {
    suspend fun connect(
        profile: ConnectionProfile,
        session: TerminalSessionDescriptor,
    ): AtlasResult<Unit>

    suspend fun send(bytes: ByteArray): AtlasResult<TerminalWriteReceipt>
    suspend fun resize(columns: Int, rows: Int): AtlasResult<Unit>
    suspend fun detach(): AtlasResult<Unit>
    suspend fun closeRemoteSession(): AtlasResult<Unit>

    fun setListener(listener: Listener?)

    interface Listener {
        fun onStateChanged(state: TerminalLifecycleState)
        fun onOutput(bytes: ByteArray)
    }
}

enum class DeliveryCertainty {
    DELIVERED,
    UNKNOWN_AFTER_WRITE_STARTED,
}

data class TerminalWriteReceipt(
    val bytesAccepted: Int,
    val certainty: DeliveryCertainty,
)
