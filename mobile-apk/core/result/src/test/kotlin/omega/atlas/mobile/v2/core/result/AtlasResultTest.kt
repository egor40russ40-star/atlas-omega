package omega.atlas.mobile.v2.core.result

import org.junit.Assert.assertEquals
import org.junit.Assert.assertSame
import org.junit.Test

class AtlasResultTest {
    @Test
    fun mapTransformsOnlySuccess() {
        val result: AtlasResult<Int> = AtlasResult.Success(21)
        assertEquals(AtlasResult.Success(42), result.map { it * 2 })
    }

    @Test
    fun mapPreservesFailure() {
        val failure = AtlasResult.Failure(
            AtlasError(
                code = "blocked",
                domain = ErrorDomain.TRUST,
                userMessageKey = "error_blocked",
            )
        )
        assertSame(failure, failure.map { "unused" })
    }
}
