package omega.atlas.mobile.v2.feature.files

import omega.atlas.mobile.v2.core.model.RemoteFileSnapshot

enum class FileConflictDecision {
    SAFE_TO_WRITE,
    REMOTE_CHANGED,
}

object FileConflictGuard {
    fun compare(
        expected: RemoteFileSnapshot,
        current: RemoteFileSnapshot,
    ): FileConflictDecision {
        if (expected.path != current.path) return FileConflictDecision.REMOTE_CHANGED

        val expectedHash = expected.contentHash
        val currentHash = current.contentHash
        if (expectedHash != null && currentHash != null) {
            return if (expectedHash == currentHash) {
                FileConflictDecision.SAFE_TO_WRITE
            } else {
                FileConflictDecision.REMOTE_CHANGED
            }
        }

        return if (
            expected.sizeBytes == current.sizeBytes &&
            expected.modifiedEpochMillis == current.modifiedEpochMillis
        ) {
            FileConflictDecision.SAFE_TO_WRITE
        } else {
            FileConflictDecision.REMOTE_CHANGED
        }
    }
}
