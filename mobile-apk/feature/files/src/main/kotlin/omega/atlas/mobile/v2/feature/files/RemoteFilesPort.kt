package omega.atlas.mobile.v2.feature.files

import omega.atlas.mobile.v2.core.model.RemoteFileSnapshot
import omega.atlas.mobile.v2.core.result.AtlasResult

data class RemoteFileEntry(
    val path: String,
    val name: String,
    val directory: Boolean,
    val sizeBytes: Long,
    val modifiedEpochMillis: Long,
)

data class RemoteTextDocument(
    val snapshot: RemoteFileSnapshot,
    val text: String,
)

data class AtomicTextWriteRequest(
    val path: String,
    val text: String,
    val expectedSnapshot: RemoteFileSnapshot,
)

interface RemoteFilesPort {
    suspend fun list(path: String): AtlasResult<List<RemoteFileEntry>>
    suspend fun readText(path: String): AtlasResult<RemoteTextDocument>
    suspend fun writeTextAtomic(request: AtomicTextWriteRequest): AtlasResult<RemoteFileSnapshot>
}
