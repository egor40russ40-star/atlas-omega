package omega.atlas.mobile.v2.app

import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import omega.atlas.mobile.v2.core.ui.AtlasTheme
import org.connectbot.terminal.TerminalEmulator
import org.connectbot.terminal.TerminalEmulatorFactory

class MainActivity : ComponentActivity() {
    private lateinit var emulator: TerminalEmulator
    private lateinit var runtime: AtlasTerminalRuntime
    private var keyPassphraseForImport: String? = null

    private val keyPicker = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        if (uri == null) return@registerForActivityResult
        runCatching {
            val text = contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
                ?: error("Не удалось прочитать SSH-ключ")
            require(text.contains("PRIVATE KEY")) { "Выбранный файл не похож на приватный SSH-ключ" }
            runtime.savePrivateKey(text, keyPassphraseForImport)
        }.onFailure {
            // Detailed errors stay local; no secret content is logged.
        }.also {
            keyPassphraseForImport = null
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        emulator = TerminalEmulatorFactory.create(
            initialRows = 24,
            initialCols = 80,
            onKeyboardInput = { bytes ->
                if (::runtime.isInitialized) runtime.send(bytes)
            },
            autoDetectUrls = true,
            boldAsBright = true,
        )
        runtime = AtlasTerminalRuntime(this, emulator)

        setContent {
            AtlasTheme {
                AtlasMobileV2Shell(
                    emulator = emulator,
                    runtime = runtime,
                    onImportPrivateKey = { passphrase ->
                        keyPassphraseForImport = passphrase
                        keyPicker.launch(arrayOf("text/*", "application/octet-stream", "*/*"))
                    },
                )
            }
        }
    }

    override fun onDestroy() {
        if (::runtime.isInitialized) runtime.close()
        super.onDestroy()
    }
}
