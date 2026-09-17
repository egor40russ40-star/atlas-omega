package omega.atlas.mobile.v2.feature.editor

import omega.atlas.mobile.v2.core.model.EditorLocation
import omega.atlas.mobile.v2.core.model.RemoteFileSnapshot

data class EditorDocumentState(
    val location: EditorLocation,
    val snapshot: RemoteFileSnapshot,
    val text: String,
    val originalText: String,
) {
    val dirty: Boolean get() = text != originalText
}

enum class CodeToTerminalAction {
    INSERT,
    RUN,
}
