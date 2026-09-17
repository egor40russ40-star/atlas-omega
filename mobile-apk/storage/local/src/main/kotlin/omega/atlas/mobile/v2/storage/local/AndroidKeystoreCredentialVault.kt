package omega.atlas.mobile.v2.storage.local

import android.content.Context
import android.util.Base64
import java.nio.ByteBuffer
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import omega.atlas.mobile.v2.core.result.AtlasError
import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.result.ErrorDomain
import omega.atlas.mobile.v2.core.security.MutableCredentialVault
import omega.atlas.mobile.v2.core.security.SshCredential

class AndroidKeystoreCredentialVault(
    context: Context,
) : MutableCredentialVault {
    private val prefs = context.applicationContext.getSharedPreferences(
        "atlas_v2_secret_credentials",
        Context.MODE_PRIVATE,
    )

    override suspend fun loadSshCredential(connectionProfileId: String): AtlasResult<SshCredential> {
        val encoded = prefs.getString(prefKey(connectionProfileId), null)
            ?: return AtlasResult.Success(SshCredential.None)
        return try {
            val envelope = Base64.decode(encoded, Base64.NO_WRAP)
            val plaintext = decrypt(envelope)
            try {
                AtlasResult.Success(CredentialCodec.decode(plaintext))
            } finally {
                plaintext.fill(0)
                envelope.fill(0)
            }
        } catch (e: Exception) {
            failure("credential_decrypt_failed", e)
        }
    }

    override suspend fun saveSshCredential(
        connectionProfileId: String,
        credential: SshCredential,
    ): AtlasResult<Unit> = try {
        val plaintext = CredentialCodec.encode(credential)
        try {
            val envelope = encrypt(plaintext)
            try {
                val stored = Base64.encodeToString(envelope, Base64.NO_WRAP)
                prefs.edit().putString(prefKey(connectionProfileId), stored).apply()
            } finally {
                envelope.fill(0)
            }
        } finally {
            plaintext.fill(0)
        }
        AtlasResult.Success(Unit)
    } catch (e: Exception) {
        failure("credential_encrypt_failed", e)
    }

    override suspend fun removeSshCredential(connectionProfileId: String): AtlasResult<Unit> = try {
        prefs.edit().remove(prefKey(connectionProfileId)).apply()
        AtlasResult.Success(Unit)
    } catch (e: Exception) {
        failure("credential_remove_failed", e)
    }

    private fun encrypt(plaintext: ByteArray): ByteArray {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
        val ciphertext = cipher.doFinal(plaintext)
        val iv = cipher.iv
        require(iv.size <= 255)
        return ByteBuffer.allocate(2 + iv.size + ciphertext.size)
            .put(ENVELOPE_VERSION)
            .put(iv.size.toByte())
            .put(iv)
            .put(ciphertext)
            .array()
    }

    private fun decrypt(envelope: ByteArray): ByteArray {
        val input = ByteBuffer.wrap(envelope)
        require(input.get() == ENVELOPE_VERSION) { "Unsupported encrypted envelope" }
        val ivLength = input.get().toInt() and 0xFF
        require(ivLength in 12..32 && input.remaining() > ivLength) { "Invalid encrypted envelope" }
        val iv = ByteArray(ivLength)
        input.get(iv)
        val ciphertext = ByteArray(input.remaining())
        input.get(ciphertext)
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.DECRYPT_MODE, getOrCreateKey(), GCMParameterSpec(128, iv))
        return try {
            cipher.doFinal(ciphertext)
        } finally {
            ciphertext.fill(0)
            iv.fill(0)
        }
    }

    private fun getOrCreateKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (keyStore.getKey(KEY_ALIAS, null) as? SecretKey)?.let { return it }
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        generator.init(
            KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .setRandomizedEncryptionRequired(true)
                .build()
        )
        return generator.generateKey()
    }

    private fun prefKey(id: String): String = "credential::$id"

    private fun <T> failure(code: String, error: Exception): AtlasResult<T> = AtlasResult.Failure(
        AtlasError(
            code = code,
            domain = ErrorDomain.STORAGE,
            userMessageKey = "error_secure_storage",
            technicalDetail = error.javaClass.simpleName,
            retryable = false,
        )
    )

    private companion object {
        const val KEY_ALIAS = "atlas_mobile_v2_credentials"
        const val TRANSFORMATION = "AES/GCM/NoPadding"
        const val ENVELOPE_VERSION: Byte = 1
    }
}
