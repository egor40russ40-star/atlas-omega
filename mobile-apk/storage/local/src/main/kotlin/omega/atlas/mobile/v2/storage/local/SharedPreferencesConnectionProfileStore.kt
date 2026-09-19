package omega.atlas.mobile.v2.storage.local

import android.content.Context
import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.TrustState

class SharedPreferencesConnectionProfileStore(context: Context) {
    private val prefs = context.applicationContext.getSharedPreferences(
        "atlas_v2_connection_profile",
        Context.MODE_PRIVATE,
    )

    fun load(): ConnectionProfile? {
        val host = prefs.getString("host", null)?.trim().orEmpty()
        val username = prefs.getString("username", null)?.trim().orEmpty()
        if (host.isBlank() || username.isBlank()) return null
        return ConnectionProfile(
            id = prefs.getString("id", DEFAULT_ID) ?: DEFAULT_ID,
            title = prefs.getString("title", "NucBox") ?: "NucBox",
            host = host,
            port = prefs.getInt("port", 22),
            username = username,
            workspaceRoot = prefs.getString("workspace_root", DEFAULT_WORKSPACE_ROOT)
                ?: DEFAULT_WORKSPACE_ROOT,
            gatewayBaseUrl = prefs.getString("gateway", null),
            trustState = runCatching {
                TrustState.valueOf(prefs.getString("trust", TrustState.UNENROLLED.name)!!)
            }.getOrDefault(TrustState.UNENROLLED),
            autoConnect = prefs.getBoolean("auto_connect", false),
        )
    }

    fun save(profile: ConnectionProfile) {
        prefs.edit()
            .putString("id", profile.id)
            .putString("title", profile.title)
            .putString("host", profile.host.trim())
            .putInt("port", profile.port)
            .putString("username", profile.username.trim())
            .putString("workspace_root", profile.workspaceRoot.trim())
            .putString("gateway", profile.gatewayBaseUrl)
            .putString("trust", profile.trustState.name)
            .putBoolean("auto_connect", profile.autoConnect)
            .apply()
    }

    fun clear() {
        prefs.edit().clear().apply()
    }

    private companion object {
        const val DEFAULT_ID = "nucbox-primary"
        const val DEFAULT_WORKSPACE_ROOT = "/home/test4/ATLAS_EXECUTION_NODE"
    }
}
