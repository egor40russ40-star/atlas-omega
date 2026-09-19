package omega.atlas.mobile.v2.feature.files

/**
 * Pure navigation-list rules used by Files UI and persistence.
 */
object FileNavigationPolicy {
    fun toggleFavorite(
        favorites: Set<String>,
        path: String,
        maxFavorites: Int,
    ): Set<String> {
        require(maxFavorites > 0)
        if (path in favorites) return favorites - path
        if (favorites.size >= maxFavorites) return favorites
        return LinkedHashSet<String>(favorites).apply { add(path) }
    }

    fun pushRecent(
        current: List<String>,
        path: String,
        maxItems: Int,
    ): List<String> {
        require(maxItems > 0)
        if (path.isBlank()) return normalizeRecent(current, maxItems)
        val normalized = normalizeRecent(current, Int.MAX_VALUE)
        return buildList {
            add(path)
            normalized.forEach { if (it != path) add(it) }
        }.take(maxItems)
    }

    fun normalizeRecent(
        current: List<String>,
        maxItems: Int,
    ): List<String> {
        require(maxItems > 0)
        val seen = linkedSetOf<String>()
        current.forEach {
            val value = it.trim()
            if (value.isNotEmpty()) seen += value
        }
        return seen.take(maxItems)
    }
}
