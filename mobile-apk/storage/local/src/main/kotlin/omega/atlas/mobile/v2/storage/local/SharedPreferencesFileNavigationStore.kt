package omega.atlas.mobile.v2.storage.local

import android.content.Context
import org.json.JSONArray

/**
 * Per-connection-profile navigation convenience state.
 *
 * This store never contains credentials or trust material. Paths are hints only;
 * runtime workspace policy re-validates every path before use.
 */
class SharedPreferencesFileNavigationStore(context: Context) {
    private val prefs = context.applicationContext.getSharedPreferences(
        PREFS_NAME,
        Context.MODE_PRIVATE,
    )

    fun loadFavorites(profileId: String): Set<String> =
        prefs.getStringSet(key(profileId, "favorites"), emptySet())
            ?.toSet()
            .orEmpty()

    fun saveFavorites(profileId: String, paths: Set<String>) {
        prefs.edit()
            .putStringSet(key(profileId, "favorites"), paths.toSet())
            .apply()
    }

    fun loadRecent(profileId: String): List<String> =
        decode(prefs.getString(key(profileId, "recent"), null))

    fun saveRecent(profileId: String, paths: List<String>) {
        prefs.edit()
            .putString(key(profileId, "recent"), encode(paths))
            .apply()
    }

    private fun encode(values: List<String>): String {
        val array = JSONArray()
        values.forEach(array::put)
        return array.toString()
    }

    private fun decode(raw: String?): List<String> {
        if (raw.isNullOrBlank()) return emptyList()
        return runCatching {
            val array = JSONArray(raw)
            buildList {
                for (index in 0 until array.length()) {
                    val value = array.optString(index, "").trim()
                    if (value.isNotEmpty()) add(value)
                }
            }
        }.getOrDefault(emptyList())
    }

    private fun key(profileId: String, field: String): String =
        "profile::" + profileId.trim() + "::" + field

    private companion object {
        const val PREFS_NAME = "atlas_v2_file_navigation"
    }
}
