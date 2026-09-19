package omega.atlas.mobile.v2.storage.local

import android.content.Context
import android.content.SharedPreferences
import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.TrustState

/**
 * Persistent connection-profile registry.
 *
 * The first V2 builds stored one profile in flat SharedPreferences keys.
 * The registry keeps those keys as a rollback-compatible mirror while adding
 * multiple named profiles and an explicit active profile.
 *
 * Credentials remain outside this store in AndroidKeystoreCredentialVault.
 */
class SharedPreferencesConnectionProfileStore(context: Context) {
    private val prefs = context.applicationContext.getSharedPreferences(
        PREFS_NAME,
        Context.MODE_PRIVATE,
    )

    fun load(): ConnectionProfile? {
        val activeId = prefs.getString(KEY_ACTIVE_ID, null)
        if (!activeId.isNullOrBlank()) {
            readProfile(activeId)?.let { return it }
        }

        val legacy = readLegacyProfile()
        if (legacy != null) {
            save(legacy)
            return legacy
        }

        val first = list().firstOrNull()
        if (first != null) {
            select(first.id)
        }
        return first
    }

    fun list(): List<ConnectionProfile> {
        val ids = prefs.getStringSet(KEY_PROFILE_IDS, emptySet())
            ?.toSet()
            .orEmpty()

        val registered = ids
            .mapNotNull(::readProfile)
            .sortedWith(compareBy<ConnectionProfile> { it.title.lowercase() }.thenBy { it.id })

        if (registered.isNotEmpty()) return registered
        return listOfNotNull(readLegacyProfile())
    }

    /**
     * Upserts a profile and makes it active.
     *
     * The legacy mirror is deliberately updated too. That gives the user a
     * safe rollback path to an older APK that only understands the single
     * profile schema.
     */
    fun save(profile: ConnectionProfile) {
        require(profile.id.isNotBlank())
        require(profile.host.isNotBlank())
        require(profile.username.isNotBlank())

        val ids = prefs.getStringSet(KEY_PROFILE_IDS, emptySet())
            ?.toMutableSet()
            ?: mutableSetOf()
        ids += profile.id

        prefs.edit()
            .putStringSet(KEY_PROFILE_IDS, ids)
            .putString(KEY_ACTIVE_ID, profile.id)
            .writeProfile(profile)
            .writeLegacyMirror(profile)
            .apply()
    }

    fun select(id: String): ConnectionProfile? {
        val profile = readProfile(id) ?: return null
        prefs.edit()
            .putString(KEY_ACTIVE_ID, profile.id)
            .writeLegacyMirror(profile)
            .apply()
        return profile
    }

    fun contains(id: String): Boolean = readProfile(id) != null

    fun clear() {
        prefs.edit().clear().apply()
    }

    private fun readProfile(id: String): ConnectionProfile? {
        val host = prefs.getString(profileKey(id, FIELD_HOST), null)?.trim().orEmpty()
        val username = prefs.getString(profileKey(id, FIELD_USERNAME), null)?.trim().orEmpty()
        if (host.isBlank() || username.isBlank()) return null

        return ConnectionProfile(
            id = id,
            title = prefs.getString(profileKey(id, FIELD_TITLE), "NucBox") ?: "NucBox",
            host = host,
            port = prefs.getInt(profileKey(id, FIELD_PORT), 22),
            username = username,
            workspaceRoot = prefs.getString(
                profileKey(id, FIELD_WORKSPACE_ROOT),
                DEFAULT_WORKSPACE_ROOT,
            ) ?: DEFAULT_WORKSPACE_ROOT,
            gatewayBaseUrl = prefs.getString(profileKey(id, FIELD_GATEWAY), null),
            trustState = parseTrust(
                prefs.getString(profileKey(id, FIELD_TRUST), TrustState.UNENROLLED.name)
            ),
            autoConnect = prefs.getBoolean(profileKey(id, FIELD_AUTO_CONNECT), false),
        )
    }

    private fun readLegacyProfile(): ConnectionProfile? {
        val host = prefs.getString(LEGACY_HOST, null)?.trim().orEmpty()
        val username = prefs.getString(LEGACY_USERNAME, null)?.trim().orEmpty()
        if (host.isBlank() || username.isBlank()) return null

        return ConnectionProfile(
            id = prefs.getString(LEGACY_ID, DEFAULT_ID) ?: DEFAULT_ID,
            title = prefs.getString(LEGACY_TITLE, "NucBox") ?: "NucBox",
            host = host,
            port = prefs.getInt(LEGACY_PORT, 22),
            username = username,
            workspaceRoot = prefs.getString(
                LEGACY_WORKSPACE_ROOT,
                DEFAULT_WORKSPACE_ROOT,
            ) ?: DEFAULT_WORKSPACE_ROOT,
            gatewayBaseUrl = prefs.getString(LEGACY_GATEWAY, null),
            trustState = parseTrust(
                prefs.getString(LEGACY_TRUST, TrustState.UNENROLLED.name)
            ),
            autoConnect = prefs.getBoolean(LEGACY_AUTO_CONNECT, false),
        )
    }

    private fun SharedPreferences.Editor.writeProfile(
        profile: ConnectionProfile,
    ): SharedPreferences.Editor = apply {
        putString(profileKey(profile.id, FIELD_TITLE), profile.title)
        putString(profileKey(profile.id, FIELD_HOST), profile.host.trim())
        putInt(profileKey(profile.id, FIELD_PORT), profile.port)
        putString(profileKey(profile.id, FIELD_USERNAME), profile.username.trim())
        putString(profileKey(profile.id, FIELD_WORKSPACE_ROOT), profile.workspaceRoot.trim())
        putString(profileKey(profile.id, FIELD_GATEWAY), profile.gatewayBaseUrl)
        putString(profileKey(profile.id, FIELD_TRUST), profile.trustState.name)
        putBoolean(profileKey(profile.id, FIELD_AUTO_CONNECT), profile.autoConnect)
    }

    private fun SharedPreferences.Editor.writeLegacyMirror(
        profile: ConnectionProfile,
    ): SharedPreferences.Editor = apply {
        putString(LEGACY_ID, profile.id)
        putString(LEGACY_TITLE, profile.title)
        putString(LEGACY_HOST, profile.host.trim())
        putInt(LEGACY_PORT, profile.port)
        putString(LEGACY_USERNAME, profile.username.trim())
        putString(LEGACY_WORKSPACE_ROOT, profile.workspaceRoot.trim())
        putString(LEGACY_GATEWAY, profile.gatewayBaseUrl)
        putString(LEGACY_TRUST, profile.trustState.name)
        putBoolean(LEGACY_AUTO_CONNECT, profile.autoConnect)
    }

    private fun parseTrust(raw: String?): TrustState = runCatching {
        TrustState.valueOf(raw ?: TrustState.UNENROLLED.name)
    }.getOrDefault(TrustState.UNENROLLED)

    private fun profileKey(id: String, field: String): String =
        "profile::$id::$field"

    private companion object {
        const val PREFS_NAME = "atlas_v2_connection_profile"

        const val KEY_PROFILE_IDS = "registry_profile_ids"
        const val KEY_ACTIVE_ID = "registry_active_id"

        const val FIELD_TITLE = "title"
        const val FIELD_HOST = "host"
        const val FIELD_PORT = "port"
        const val FIELD_USERNAME = "username"
        const val FIELD_WORKSPACE_ROOT = "workspace_root"
        const val FIELD_GATEWAY = "gateway"
        const val FIELD_TRUST = "trust"
        const val FIELD_AUTO_CONNECT = "auto_connect"

        const val LEGACY_ID = "id"
        const val LEGACY_TITLE = "title"
        const val LEGACY_HOST = "host"
        const val LEGACY_PORT = "port"
        const val LEGACY_USERNAME = "username"
        const val LEGACY_WORKSPACE_ROOT = "workspace_root"
        const val LEGACY_GATEWAY = "gateway"
        const val LEGACY_TRUST = "trust"
        const val LEGACY_AUTO_CONNECT = "auto_connect"

        const val DEFAULT_ID = "nucbox-primary"
        const val DEFAULT_WORKSPACE_ROOT = "/home/test4/ATLAS_EXECUTION_NODE"
    }
}
