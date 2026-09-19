package omega.atlas.mobile.v2.feature.editor

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class EditorHistoryTest {
    @Test
    fun undoRedoIsDeterministic() {
        val history = EditorHistory("a", maxEntries = 4)
        history.record("ab")
        history.record("abc")

        assertTrue(history.canUndo)
        assertEquals("ab", history.undo())
        assertEquals("a", history.undo())
        assertNull(history.undo())
        assertTrue(history.canRedo)
        assertEquals("ab", history.redo())
    }

    @Test
    fun newEditDropsRedoBranch() {
        val history = EditorHistory("a")
        history.record("ab")
        history.record("abc")
        assertEquals("ab", history.undo())
        history.record("ab!")

        assertFalse(history.canRedo)
        assertEquals("ab!", history.current())
    }

    @Test
    fun historyIsBounded() {
        val history = EditorHistory("0", maxEntries = 3)
        history.record("1")
        history.record("2")
        history.record("3")
        assertEquals("2", history.undo())
        assertEquals("1", history.undo())
        assertNull(history.undo())
    }
}
