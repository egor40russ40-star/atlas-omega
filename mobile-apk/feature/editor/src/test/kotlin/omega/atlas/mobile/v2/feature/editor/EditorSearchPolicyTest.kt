package omega.atlas.mobile.v2.feature.editor

import org.junit.Assert.assertEquals
import org.junit.Test

class EditorSearchPolicyTest {
    @Test
    fun findsExactMatchesAndLineNumbers() {
        val matches = EditorSearchPolicy.findAll(
            "alpha\nbeta alpha\nALPHA",
            "alpha",
        )
        assertEquals(listOf(1, 2), matches.map { it.line })
    }

    @Test
    fun optionalCaseInsensitiveSearchWorks() {
        val matches = EditorSearchPolicy.findAll(
            "alpha\nALPHA",
            "alpha",
            ignoreCase = true,
        )
        assertEquals(2, matches.size)
    }

    @Test
    fun lineCountAlwaysHasAtLeastOneLine() {
        assertEquals(1, EditorSearchPolicy.lineCount(""))
        assertEquals(3, EditorSearchPolicy.lineCount("a\nb\n"))
    }
}
