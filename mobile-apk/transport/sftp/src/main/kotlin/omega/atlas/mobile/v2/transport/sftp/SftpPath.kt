package omega.atlas.mobile.v2.transport.sftp

internal object SftpPath {
    fun child(parent: String, name: String): String {
        val base = parent.ifBlank { "." }
        return when {
            base == "/" -> "/$name"
            base.endsWith("/") -> base + name
            else -> "$base/$name"
        }
    }

    fun temporaryFor(path: String, nonce: String): String {
        val slash = path.lastIndexOf('/')
        val dir = if (slash >= 0) path.substring(0, slash + 1) else ""
        val name = if (slash >= 0) path.substring(slash + 1) else path
        require(name.isNotBlank()) { "Path must reference a file" }
        val safeNonce = nonce.filter { it.isLetterOrDigit() }.take(20)
        require(safeNonce.isNotBlank()) { "Nonce is invalid" }
        return "$dir.$name.atlas-$safeNonce.tmp"
    }
}
