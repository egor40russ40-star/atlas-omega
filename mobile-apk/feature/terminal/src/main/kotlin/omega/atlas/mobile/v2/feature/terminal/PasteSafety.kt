package omega.atlas.mobile.v2.feature.terminal

enum class PasteRisk {
    SINGLE_LINE,
    MULTI_LINE,
}

object PasteSafety {
    fun classify(text: String): PasteRisk =
        if (text.contains('\n') || text.contains('\r')) PasteRisk.MULTI_LINE else PasteRisk.SINGLE_LINE

    fun requiresConfirmation(text: String): Boolean = classify(text) == PasteRisk.MULTI_LINE
}
