package omega.atlas.mobile

import java.net.URI

object AtlasConfig {
    const val DEFAULT_GATEWAY = "https://tinvest-robot.tailf87948.ts.net"
    const val DEFAULT_SSH_HOST = "atlas-omega-nucbox.tailf87948.ts.net"
    const val DEFAULT_SSH_USER = "test4"
    const val DEFAULT_SSH_PORT = 22
    const val VERSION = "0.2.0-alpha1"
    const val LIVE_TRADING_ENABLED = false
    const val RESEARCH_ONLY = true

    fun normalizeGateway(raw: String): String = raw.trim().trimEnd('/')

    fun isAllowedGateway(raw: String): Boolean {
        return try {
            val u = URI(normalizeGateway(raw))
            u.scheme.equals("https", ignoreCase = true) && !u.host.isNullOrBlank()
        } catch (_: Exception) {
            false
        }
    }
}

object TerminalKeys {
    val esc = byteArrayOf(0x1b)
    val tab = byteArrayOf(0x09)
    val enter = byteArrayOf(0x0d)
    val up = "\u001b[A".toByteArray()
    val down = "\u001b[B".toByteArray()
    val right = "\u001b[C".toByteArray()
    val left = "\u001b[D".toByteArray()

    fun ctrl(letter: Char): ByteArray {
        val c = letter.uppercaseChar()
        require(c in 'A'..'Z')
        return byteArrayOf((c.code - 'A'.code + 1).toByte())
    }

    fun text(value: String): ByteArray = value.toByteArray(Charsets.UTF_8)
}
