package omega.atlas.mobile.v2.feature.editor

import org.junit.Assert.assertEquals
import org.junit.Test

class TracebackLocationParserTest {
    @Test
    fun parsesPythonTraceback() {
        val location = TracebackLocationParser.firstLocation(
            "  File \"/home/test4/ATLAS_EXECUTION_NODE/tools/run.py\", line 157, in main"
        )!!
        assertEquals("/home/test4/ATLAS_EXECUTION_NODE/tools/run.py", location.path)
        assertEquals(157, location.line)
    }

    @Test
    fun parsesGenericPathLineColumn() {
        val location = TracebackLocationParser.firstLocation("src/main.kt:42:7 error")!!
        assertEquals("src/main.kt", location.path)
        assertEquals(42, location.line)
        assertEquals(7, location.column)
    }
}
