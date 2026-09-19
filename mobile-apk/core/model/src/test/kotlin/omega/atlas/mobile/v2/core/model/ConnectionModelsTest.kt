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
    fun sshEndpointsKeepPrimaryFirstAndDeduplicateRoutes() {
        val profile = ConnectionProfile(
            id = "vm",
            title = "Cloud VM",
            host = "tinvest-robot.tailnet",
            username = "tivest",
            fallbackSshEndpoints = listOf(
                SshEndpoint("same", "Duplicate", "tinvest-robot.tailnet", 22),
                SshEndpoint("public", "Public recovery", "84.201.140.78", 22),
            ),
        )

        val endpoints = profile.sshEndpoints()
        assertEquals(2, endpoints.size)
        assertEquals(SshEndpointKind.PRIMARY, endpoints[0].kind)
        assertEquals("tinvest-robot.tailnet", endpoints[0].host)
        assertEquals("84.201.140.78", endpoints[1].host)
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
