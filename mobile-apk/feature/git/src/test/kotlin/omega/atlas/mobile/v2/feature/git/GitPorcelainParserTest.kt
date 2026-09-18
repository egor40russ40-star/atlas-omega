package omega.atlas.mobile.v2.feature.git

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class GitPorcelainParserTest {
    @Test
    fun parsesBranchAheadBehindAndChanges() {
        val raw = "## main...origin/main [ahead 2, behind 1]\u0000 M src/Main.kt\u0000M  README.md\u0000?? note.txt\u0000"
        val snapshot = GitPorcelainParser.parseStatus(raw)

        assertEquals("main", snapshot.branch)
        assertEquals(2, snapshot.ahead)
        assertEquals(1, snapshot.behind)
        assertEquals(3, snapshot.changes.size)
        assertFalse(snapshot.changes[0].staged)
        assertTrue(snapshot.changes[1].staged)
        assertEquals(GitChangeKind.UNTRACKED, snapshot.changes[2].kind)
    }

    @Test
    fun conflictIsRecognized() {
        val snapshot = GitPorcelainParser.parseStatus("## main\u0000UU conflicted.kt\u0000")
        assertEquals(GitChangeKind.CONFLICT, snapshot.changes.single().kind)
    }

    @Test
    fun renameConsumesSecondPathRecord() {
        val snapshot = GitPorcelainParser.parseStatus("## main\u0000R  new.kt\u0000old.kt\u0000")
        assertEquals(1, snapshot.changes.size)
        assertEquals("new.kt", snapshot.changes.single().path)
        assertEquals(GitChangeKind.RENAMED, snapshot.changes.single().kind)
    }
}
