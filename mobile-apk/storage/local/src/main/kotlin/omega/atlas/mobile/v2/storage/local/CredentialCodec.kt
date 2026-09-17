package omega.atlas.mobile.v2.storage.local

import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.DataInputStream
import java.io.DataOutputStream
import java.nio.ByteBuffer
import java.nio.CharBuffer
import java.nio.charset.StandardCharsets
import omega.atlas.mobile.v2.core.security.SshCredential

internal object CredentialCodec {
    private const val VERSION = 1
    private const val TYPE_NONE = 0
    private const val TYPE_PASSWORD = 1
    private const val TYPE_PRIVATE_KEY = 2
    private const val MAX_SECRET_BYTES = 8 * 1024 * 1024

    fun encode(credential: SshCredential): ByteArray {
        val buffer = ByteArrayOutputStream()
        DataOutputStream(buffer).use { out ->
            out.writeByte(VERSION)
            when (credential) {
                SshCredential.None -> out.writeByte(TYPE_NONE)
                is SshCredential.Password -> {
                    out.writeByte(TYPE_PASSWORD)
                    writeChars(out, credential.value)
                }
                is SshCredential.PrivateKey -> {
                    out.writeByte(TYPE_PRIVATE_KEY)
                    writeChars(out, credential.pem)
                    writeNullableChars(out, credential.passphrase)
                }
            }
        }
        return buffer.toByteArray()
    }

    fun decode(bytes: ByteArray): SshCredential {
        DataInputStream(ByteArrayInputStream(bytes)).use { input ->
            require(input.readUnsignedByte() == VERSION) { "Unsupported credential envelope" }
            return when (input.readUnsignedByte()) {
                TYPE_NONE -> SshCredential.None
                TYPE_PASSWORD -> SshCredential.Password(readChars(input))
                TYPE_PRIVATE_KEY -> SshCredential.PrivateKey(
                    pem = readChars(input),
                    passphrase = readNullableChars(input),
                )
                else -> error("Unknown credential type")
            }
        }
    }

    private fun writeNullableChars(out: DataOutputStream, value: CharArray?) {
        if (value == null) {
            out.writeInt(-1)
        } else {
            writeChars(out, value)
        }
    }

    private fun readNullableChars(input: DataInputStream): CharArray? {
        val length = input.readInt()
        if (length == -1) return null
        return readCharsWithKnownLength(input, length)
    }

    private fun writeChars(out: DataOutputStream, value: CharArray) {
        val bytes = charsToUtf8(value)
        try {
            out.writeInt(bytes.size)
            out.write(bytes)
        } finally {
            bytes.fill(0)
        }
    }

    private fun readChars(input: DataInputStream): CharArray =
        readCharsWithKnownLength(input, input.readInt())

    private fun readCharsWithKnownLength(input: DataInputStream, length: Int): CharArray {
        require(length in 0..MAX_SECRET_BYTES) { "Invalid credential field length" }
        val bytes = ByteArray(length)
        input.readFully(bytes)
        return try {
            utf8ToChars(bytes)
        } finally {
            bytes.fill(0)
        }
    }

    private fun charsToUtf8(value: CharArray): ByteArray {
        val encoded: ByteBuffer = StandardCharsets.UTF_8.encode(CharBuffer.wrap(value))
        return ByteArray(encoded.remaining()).also(encoded::get)
    }

    private fun utf8ToChars(bytes: ByteArray): CharArray {
        val decoded = StandardCharsets.UTF_8.decode(ByteBuffer.wrap(bytes))
        return CharArray(decoded.remaining()).also(decoded::get)
    }
}
