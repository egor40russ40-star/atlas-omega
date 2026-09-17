package omega.atlas.mobile.v2.feature.sessions

object TmuxSessionCommands {
    private val safeName = Regex("[A-Za-z0-9._-]{1,80}")

    fun requireSafeName(value: String): String {
        require(safeName.matches(value)) { "Unsafe tmux session name" }
        return value
    }

    fun attachOrCreate(sessionName: String): ByteArray {
        val safe = requireSafeName(sessionName)
        return "exec tmux new-session -A -s $safe\r".encodeToByteArray()
    }
}
