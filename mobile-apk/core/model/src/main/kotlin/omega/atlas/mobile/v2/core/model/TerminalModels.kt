package omega.atlas.mobile.v2.core.model

enum class TerminalLifecycleState {
    DISCONNECTED,
    CONNECTING,
    AUTHENTICATING,
    OPENING_PTY,
    ATTACHING_TMUX,
    READY,
    RECONNECTING,
    BLOCKED,
    ERROR,
}

data class TerminalSessionDescriptor(
    val id: String,
    val workspaceId: String,
    val connectionProfileId: String,
    val tmuxSessionName: String,
    val title: String,
    val state: TerminalLifecycleState = TerminalLifecycleState.DISCONNECTED,
)

enum class ModifierState {
    OFF,
    NEXT_KEY,
    LOCKED,
}

data class TerminalModifierState(
    val ctrl: ModifierState = ModifierState.OFF,
    val alt: ModifierState = ModifierState.OFF,
    val shift: ModifierState = ModifierState.OFF,
)
