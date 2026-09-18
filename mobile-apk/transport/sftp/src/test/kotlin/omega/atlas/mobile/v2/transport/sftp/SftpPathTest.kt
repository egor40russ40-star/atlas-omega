package omega.atlas.mobile.v2.transport.sftp

import org.junit.Assert.assertEquals
import org.junit.Test

class SftpPathTest {
    @Test
    fun childPreservesRoot() {
        assertEquals("/tmp", SftpPath.child("/", "tmp"))
        assertEquals("/home/u/a.kt", SftpPath.child("/home/u", "a.kt"))
    }

    @Test
    fun temporaryStaysInSameDirectory() {
        assertEquals(
            "/home/u/.main.py.atlas-abc123.tmp",
            SftpPath.temporaryFor("/home/u/main.py", "abc-123"),
        )
    }
}
