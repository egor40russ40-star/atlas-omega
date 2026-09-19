package omega.atlas.mobile.v2.feature.terminal

/**
 * Deterministic text-to-PTY encoding.
 *
 * Paste and run are deliberately separate operations. [paste] never adds a
 * newline. [run] appends exactly one terminal ENTER byte (CR) after UTF-8 text.
 */
object TerminalInputEncoder {
    fun paste(text: String): ByteArray = text.encodeToByteArray()

    fun run(text: String): ByteArray =
        paste(text) + TerminalKeyEncoder.encode(TerminalKey.ENTER)
}
