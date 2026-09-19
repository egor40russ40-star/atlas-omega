package omega.atlas.mobile.v2.feature.files

/**
 * Lexical workspace boundary used by mobile navigation.
 *
 * SFTP transport performs a second server-side canonical-path check so symlinks
 * cannot be used to escape this boundary.
 */
object WorkspacePathPolicy {
    fun resolve(root: String, candidate: String): String {
        val normalizedRoot = normalizeAbsolute(root)
        val raw = candidate.trim()
        val absolute = when {
            raw.isBlank() -> normalizedRoot
            raw.startsWith("/") -> normalizeAbsolute(raw)
            normalizedRoot == "/" -> normalizeAbsolute("/$raw")
            else -> normalizeAbsolute("$normalizedRoot/$raw")
        }
        require(isWithinNormalized(normalizedRoot, absolute)) {
            "Path is outside workspace root"
        }
        return absolute
    }

    fun isWithin(root: String, candidate: String): Boolean =
        runCatching { resolve(root, candidate) }.isSuccess

    fun parent(root: String, current: String): String {
        val normalizedRoot = normalizeAbsolute(root)
        val safeCurrent = resolve(normalizedRoot, current)
        if (safeCurrent == normalizedRoot) return normalizedRoot
        val parent = safeCurrent.substringBeforeLast('/', missingDelimiterValue = "/").ifBlank { "/" }
        return if (isWithinNormalized(normalizedRoot, parent)) parent else normalizedRoot
    }

    private fun isWithinNormalized(root: String, path: String): Boolean =
        root == "/" || path == root || path.startsWith("$root/")

    private fun normalizeAbsolute(value: String): String {
        require(value.trim().startsWith('/')) { "Path must be absolute" }
        val stack = ArrayDeque<String>()
        value.trim().split('/').forEach { segment ->
            when (segment) {
                "", "." -> Unit
                ".." -> if (stack.isNotEmpty()) stack.removeLast()
                else -> stack.addLast(segment)
            }
        }
        return if (stack.isEmpty()) "/" else "/" + stack.joinToString("/")
    }
}
