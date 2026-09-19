package omega.atlas.mobile.v2.feature.files

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class FileNavigationPolicyTest {
    @Test
    fun favoriteToggleAddsAndRemovesWithoutOverflow() {
        val added = FileNavigationPolicy.toggleFavorite(
            favorites = linkedSetOf("/w/a"),
            path = "/w/b",
            maxFavorites = 2,
        )
        assertEquals(linkedSetOf("/w/a", "/w/b"), added)

        val capped = FileNavigationPolicy.toggleFavorite(
            favorites = added,
            path = "/w/c",
            maxFavorites = 2,
        )
        assertFalse("/w/c" in capped)

        val removed = FileNavigationPolicy.toggleFavorite(
            favorites = added,
            path = "/w/a",
            maxFavorites = 2,
        )
        assertFalse("/w/a" in removed)
        assertTrue("/w/b" in removed)
    }

    @Test
    fun recentIsMostRecentFirstUniqueAndBounded() {
        val result = FileNavigationPolicy.pushRecent(
            current = listOf("/w/a", "/w/b", "/w/a", "/w/c"),
            path = "/w/b",
            maxItems = 3,
        )
        assertEquals(listOf("/w/b", "/w/a", "/w/c"), result)
    }

    @Test
    fun normalizeRecentDropsBlanksDuplicatesAndBounds() {
        assertEquals(
            listOf("/a", "/b"),
            FileNavigationPolicy.normalizeRecent(
                listOf(" /a ", "", "/a", "/b", "/c"),
                maxItems = 2,
            ),
        )
    }
}
