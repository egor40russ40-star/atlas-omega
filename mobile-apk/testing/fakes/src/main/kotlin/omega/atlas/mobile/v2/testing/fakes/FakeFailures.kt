package omega.atlas.mobile.v2.testing.fakes

import omega.atlas.mobile.v2.core.result.AtlasError
import omega.atlas.mobile.v2.core.result.ErrorDomain

object FakeFailures {
    val hostKeyChanged = AtlasError(
        code = "ssh_host_key_changed",
        domain = ErrorDomain.TRUST,
        userMessageKey = "error_ssh_host_key_changed",
        technicalDetail = "Remote host identity no longer matches the pinned fingerprint.",
        retryable = false,
    )

    val ambiguousCommandDelivery = AtlasError(
        code = "terminal_delivery_unknown",
        domain = ErrorDomain.PTY,
        userMessageKey = "error_terminal_delivery_unknown",
        technicalDetail = "Connection dropped after write began; command will not be re-sent automatically.",
        retryable = false,
    )

    val fileConflict = AtlasError(
        code = "remote_file_changed",
        domain = ErrorDomain.FILE_CONFLICT,
        userMessageKey = "error_remote_file_changed",
        technicalDetail = "Remote metadata changed since editor snapshot.",
        retryable = false,
    )
}
