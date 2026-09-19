package omega.atlas.mobile.v2.feature.editor

data class EditorMatch(
    val start: Int,
    val endExclusive: Int,
    val line: Int,
)

object EditorSearchPolicy {
    fun findAll(
        text: String,
        query: String,
        ignoreCase: Boolean = false,
        maxMatches: Int = 2_000,
    ): List<EditorMatch> {
        require(maxMatches > 0)
        if (query.isEmpty() || text.isEmpty()) return emptyList()

        val result = ArrayList<EditorMatch>()
        var fromIndex = 0
        var line = 1
        var lineScanIndex = 0

        while (fromIndex <= text.length - query.length && result.size < maxMatches) {
            val index = text.indexOf(query, startIndex = fromIndex, ignoreCase = ignoreCase)
            if (index < 0) break

            while (lineScanIndex < index) {
                if (text[lineScanIndex] == '\n') line++
                lineScanIndex++
            }

            result += EditorMatch(
                start = index,
                endExclusive = index + query.length,
                line = line,
            )
            fromIndex = index + query.length.coerceAtLeast(1)
        }
        return result
    }

    fun lineCount(text: String): Int =
        if (text.isEmpty()) 1 else 1 + text.count { it == '\n' }
}
