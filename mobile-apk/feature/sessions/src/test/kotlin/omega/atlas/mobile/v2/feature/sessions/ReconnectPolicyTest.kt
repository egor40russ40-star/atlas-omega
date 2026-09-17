package omega.atlas.mobile.v2.feature.sessions

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ReconnectPolicyTest {
    @Test
    fun networkReconnectNeverReplaysPendingInput() {
        val plan = ReconnectPolicy.plan(ReconnectCause.NETWORK_LOST)
        assertTrue(plan.reconnectTransport)
        assertFalse(plan.replayPendingInput)
        assertFalse(plan.requiresUserAcknowledgement)
    }

    @Test
    fun ambiguousWriteReconnectsButRequiresAcknowledgementAndNeverReplays() {
        val plan = ReconnectPolicy.plan(ReconnectCause.AMBIGUOUS_WRITE)
        assertTrue(plan.reconnectTransport)
        assertFalse(plan.replayPendingInput)
        assertTrue(plan.requiresUserAcknowledgement)
    }

    @Test
    fun changedHostKeyCannotAutoReconnect() {
        val plan = ReconnectPolicy.plan(ReconnectCause.HOST_KEY_CHANGED)
        assertFalse(plan.reconnectTransport)
        assertFalse(plan.replayPendingInput)
        assertTrue(plan.requiresUserAcknowledgement)
    }
}
