package omega.atlas.mobile.v2.feature.terminal

enum class TerminalKey {
    ESC,
    TAB,
    ENTER,
    UP,
    DOWN,
    LEFT,
    RIGHT,
    HOME,
    END,
    PAGE_UP,
    PAGE_DOWN,
}

object TerminalKeyEncoder {
    fun encode(key: TerminalKey): ByteArray = when (key) {
        TerminalKey.ESC -> byteArrayOf(0x1B)
        TerminalKey.TAB -> byteArrayOf(0x09)
        TerminalKey.ENTER -> byteArrayOf(0x0D)
        TerminalKey.UP -> sequence("\u001B[A")
        TerminalKey.DOWN -> sequence("\u001B[B")
        TerminalKey.RIGHT -> sequence("\u001B[C")
        TerminalKey.LEFT -> sequence("\u001B[D")
        TerminalKey.HOME -> sequence("\u001B[H")
        TerminalKey.END -> sequence("\u001B[F")
        TerminalKey.PAGE_UP -> sequence("\u001B[5~")
        TerminalKey.PAGE_DOWN -> sequence("\u001B[6~")
    }

    fun ctrl(character: Char): ByteArray {
        val upper = character.uppercaseChar().code
        require(upper in 64..95) { "CTRL mapping requires ASCII @.._" }
        return byteArrayOf((upper - 64).toByte())
    }

    private fun sequence(value: String): ByteArray = value.encodeToByteArray()
}
