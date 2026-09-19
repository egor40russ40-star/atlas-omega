package omega.atlas.mobile.v2.core.model

import org.junit.Assert.assertEquals
import org.junit.Test

class ConnectionModelsTest {
    @Test
    fun profileCarriesMachineSpecificWorkspaceRoot() {
        val profile = ConnectionProfile(
            id = "vm",
            title = "Cloud VM",
            host = "84.201.140.78",
            username = "tivest",
            workspaceRoot = "/home/tivest/ATLAS_MOBILE_VM",
        )
        assertEquals("/home/tivest/ATLAS_MOBILE_VM", profile.workspaceRoot)
    }

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
