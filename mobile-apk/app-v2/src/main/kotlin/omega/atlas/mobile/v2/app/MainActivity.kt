package omega.atlas.mobile.v2.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import omega.atlas.mobile.v2.core.ui.AtlasTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AtlasTheme {
                AtlasMobileV2Shell()
            }
        }
    }
}
