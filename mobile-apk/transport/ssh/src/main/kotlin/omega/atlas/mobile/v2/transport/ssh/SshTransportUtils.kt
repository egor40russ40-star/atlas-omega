package omega.atlas.mobile.v2.transport.ssh

import java.security.MessageDigest
import java.util.Base64

object SshTransportUtils {
    private val safeTmuxName = Regex("[A-Za-z0-9._-]{1,80}")

    fun fingerprint(serverHostKey: ByteArray): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(serverHostKey)
        return "SHA256:" + Base64.getEncoder().withoutPadding().encodeToString(digest)
    }

    fun requireSafeTmuxSessionName(value: String): String {
        require(safeTmuxName.matches(value)) { "Unsafe tmux session name" }
        return value
    }
}
