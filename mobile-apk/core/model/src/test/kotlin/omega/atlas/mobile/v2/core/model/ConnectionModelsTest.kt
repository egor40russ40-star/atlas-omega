package omega.atlas.mobile.v2.core.model

import org.junit.Assert.assertEquals
import org.junit.Test

class ConnectionModelsTest {
    @Test
    fun terminalOnlyModeCanRepresentGatewayFailureWithoutLosingSsh() {
        val health = ConnectionHealth(
            network = LayerStatus.READY,
            tailnet = LayerStatus.READY,
            gateway = LayerStatus.OFFLINE,
            node = LayerStatus.READY,
            ssh = LayerStatus.READY,
            pty = LayerStatus.READY,
            tmux = LayerStatus.READY,
            sftp = LayerStatus.READY,
            mode = OperatingMode.TERMINAL_ONLY,
        )
        assertEquals(OperatingMode.TERMINAL_ONLY, health.mode)
        assertEquals(LayerStatus.READY, health.ssh)
        assertEquals(LayerStatus.OFFLINE, health.gateway)
    }
}
