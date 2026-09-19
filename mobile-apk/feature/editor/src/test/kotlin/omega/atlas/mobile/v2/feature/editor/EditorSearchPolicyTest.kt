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
    fun cursorLocationTracksLineAndColumn() {
        val text = "abc\ndef"
        assertEquals(EditorCursorLocation(1, 1), EditorSearchPolicy.locationAt(text, 0))
        assertEquals(EditorCursorLocation(1, 4), EditorSearchPolicy.locationAt(text, 3))
        assertEquals(EditorCursorLocation(2, 1), EditorSearchPolicy.locationAt(text, 4))
        assertEquals(EditorCursorLocation(2, 4), EditorSearchPolicy.locationAt(text, 7))
    }

    @Test
    fun lineCountAlwaysHasAtLeastOneLine() {
        assertEquals(1, EditorSearchPolicy.lineCount(""))
        assertEquals(3, EditorSearchPolicy.lineCount("a\nb\n"))
    }
}
