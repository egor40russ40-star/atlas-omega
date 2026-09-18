package omega.atlas.mobile.v2.feature.connections

import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.TrustState

object ConnectionLaunchPolicy {
    fun canAutoConnect(profile: ConnectionProfile): Boolean =
        profile.autoConnect && profile.trustState == TrustState.TRUSTED
}
