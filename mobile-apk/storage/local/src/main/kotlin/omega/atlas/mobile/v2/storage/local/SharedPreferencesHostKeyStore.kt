package omega.atlas.mobile.v2.storage.local

import android.content.Context
import omega.atlas.mobile.v2.core.security.HostKeyFingerprintStore

class SharedPreferencesHostKeyStore(context: Context) : HostKeyFingerprintStore {
    private val prefs = context.applicationContext.getSharedPreferences(
        "atlas_v2_host_key_pins",
        Context.MODE_PRIVATE,
    )

    override fun read(host: String, port: Int, algorithm: String): String? =
        prefs.getString(key(host, port, algorithm), null)

    override fun write(host: String, port: Int, algorithm: String, fingerprint: String) {
        prefs.edit().putString(key(host, port, algorithm), fingerprint).apply()
    }

    override fun clear(host: String, port: Int) {
        val prefix = "$host::$port::"
        val editor = prefs.edit()
        prefs.all.keys.filter { it.startsWith(prefix) }.forEach(editor::remove)
        editor.apply()
    }

    private fun key(host: String, port: Int, algorithm: String): String =
        "$host::$port::$algorithm"
}
