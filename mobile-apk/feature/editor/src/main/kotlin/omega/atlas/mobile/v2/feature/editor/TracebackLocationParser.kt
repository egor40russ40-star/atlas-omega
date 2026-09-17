package omega.atlas.mobile.v2.feature.editor

import omega.atlas.mobile.v2.core.model.EditorLocation

object TracebackLocationParser {
    private val python = Regex("File \\\"([^\\\"]+)\\\", line ([0-9]+)")
    private val generic = Regex("(^|\\s)([^\\s:]+\\.[A-Za-z0-9_]+):([0-9]+)(?::([0-9]+))?")

    fun firstLocation(text: String): EditorLocation? {
        python.find(text)?.let { match ->
            return EditorLocation(
                path = match.groupValues[1],
                line = match.groupValues[2].toIntOrNull(),
            )
        }
        generic.find(text)?.let { match ->
            return EditorLocation(
                path = match.groupValues[2],
                line = match.groupValues[3].toIntOrNull(),
                column = match.groupValues.getOrNull(4)?.takeIf { it.isNotBlank() }?.toIntOrNull(),
            )
        }
        return null
    }
}
