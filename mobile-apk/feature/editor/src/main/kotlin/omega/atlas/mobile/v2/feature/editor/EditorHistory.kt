package omega.atlas.mobile.v2.feature.editor

class EditorHistory(
    initialText: String,
    private val maxEntries: Int = 80,
) {
    init {
        require(maxEntries >= 2)
    }

    private val entries = mutableListOf(initialText)
    private var index = 0

    val canUndo: Boolean get() = index > 0
    val canRedo: Boolean get() = index < entries.lastIndex

    fun record(text: String) {
        if (entries[index] == text) return
        while (entries.lastIndex > index) entries.removeAt(entries.lastIndex)
        entries += text
        index = entries.lastIndex
        while (entries.size > maxEntries) {
            entries.removeAt(0)
            index--
        }
    }

    fun undo(): String? {
        if (!canUndo) return null
        index--
        return entries[index]
    }

    fun redo(): String? {
        if (!canRedo) return null
        index++
        return entries[index]
    }

    fun current(): String = entries[index]
}
