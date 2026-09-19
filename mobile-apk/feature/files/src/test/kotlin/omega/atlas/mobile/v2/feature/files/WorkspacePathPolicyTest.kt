package omega.atlas.mobile.v2.feature.files

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class WorkspacePathPolicyTest {
    private val root = "/home/test4/ATLAS_EXECUTION_NODE"

    @Test
    fun resolvesChildrenAndClampsParentAtRoot() {
        assertEquals(
            "$root/modules/core",
            WorkspacePathPolicy.resolve(root, "modules/core"),
        )
        assertEquals(root, WorkspacePathPolicy.parent(root, root))
        assertEquals(root, WorkspacePathPolicy.parent(root, "$root/modules"))
    }

    @Test
    fun rejectsLexicalEscape() {
        assertFalse(WorkspacePathPolicy.isWithin(root, "$root/../../etc"))
        assertFalse(WorkspacePathPolicy.isWithin(root, "/etc/passwd"))
        assertTrue(WorkspacePathPolicy.isWithin(root, "$root/data"))
    }

    @Test
    fun normalizesDotsAndDuplicateSeparators() {
        assertEquals(
            "$root/data/x",
            WorkspacePathPolicy.resolve(root, "$root//modules/../data/./x"),
        )
    }
}
