package omega.atlas.mobile.v2.core.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val AtlasDarkColors = darkColorScheme(
    primary = Color(0xFF8CC8FF),
    onPrimary = Color(0xFF002A43),
    secondary = Color(0xFFB9C7FF),
    onSecondary = Color(0xFF18224A),
    tertiary = Color(0xFF83E6C0),
    background = Color(0xFF0B0F14),
    onBackground = Color(0xFFE6EDF3),
    surface = Color(0xFF111820),
    onSurface = Color(0xFFE6EDF3),
    surfaceVariant = Color(0xFF18222D),
    onSurfaceVariant = Color(0xFFB7C4D1),
    error = Color(0xFFFFB4AB),
    onError = Color(0xFF690005),
)

@Composable
fun AtlasTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = AtlasDarkColors,
        typography = Typography(),
        content = content,
    )
}
