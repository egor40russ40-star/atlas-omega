package omega.atlas.mobile.v2.app

import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.result.AtlasError
import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.result.ErrorDomain
import omega.atlas.mobile.v2.feature.git.GitActionPolicy
import omega.atlas.mobile.v2.feature.git.GitDiff
import omega.atlas.mobile.v2.feature.git.GitPorcelainParser
import omega.atlas.mobile.v2.feature.git.GitRepository
import omega.atlas.mobile.v2.feature.git.GitSnapshot
import omega.atlas.mobile.v2.transport.ssh.TrileadCommandRunner

class SshGitRepository(
    private val profileProvider: () -> ConnectionProfile,
    private val runner: TrileadCommandRunner,
) : GitRepository {

    override suspend fun status(workspacePath: String): AtlasResult<GitSnapshot> =
        mapCommand(
            command = "git -C ${q(workspacePath)} status --porcelain=v1 -z --branch",
        ) { GitPorcelainParser.parseStatus(it.stdout) }

    override suspend fun diff(workspacePath: String, path: String): AtlasResult<GitDiff> =
        mapCommand(
            command = buildString {
                append("git -C ${q(workspacePath)} diff --no-ext-diff -- ${q(path)}")
                append("; printf '\\n--- STAGED ---\\n'")
                append("; git -C ${q(workspacePath)} diff --cached --no-ext-diff -- ${q(path)}")
            },
            allowExitCodes = setOf(0, 1),
        ) { GitDiff(path, it.stdout) }

    override suspend fun stage(workspacePath: String, path: String): AtlasResult<Unit> =
        mapCommand("git -C ${q(workspacePath)} add -- ${q(path)}") { Unit }

    override suspend fun unstage(workspacePath: String, path: String): AtlasResult<Unit> =
        mapCommand("git -C ${q(workspacePath)} restore --staged -- ${q(path)}") { Unit }

    override suspend fun commit(workspacePath: String, message: String): AtlasResult<String> {
        val safeMessage = try {
            GitActionPolicy.requireCommitMessage(message)
        } catch (e: IllegalArgumentException) {
            return failure("git_commit_message_invalid", e.message)
        }
        return mapCommand(
            "git -C ${q(workspacePath)} commit -m ${q(safeMessage)} && git -C ${q(workspacePath)} rev-parse HEAD"
        ) { it.stdout.trim().lineSequence().lastOrNull().orEmpty() }
    }

    private suspend fun <T> mapCommand(
        command: String,
        allowExitCodes: Set<Int> = setOf(0),
        transform: (omega.atlas.mobile.v2.transport.ssh.SshCommandResult) -> T,
    ): AtlasResult<T> {
        return when (val result = runner.run(profileProvider(), command)) {
            is AtlasResult.Failure -> result
            is AtlasResult.Success -> {
                val value = result.value
                when {
                    value.outputTruncated -> failure("git_output_too_large", "Git output exceeded mobile limit")
                    value.exitCode !in allowExitCodes -> failure(
                        "git_command_failed",
                        value.stderr.ifBlank { "exit=${value.exitCode}" },
                    )
                    else -> AtlasResult.Success(transform(value))
                }
            }
        }
    }

    private fun q(value: String): String =
        "'" + value.replace("'", "'\"'\"'") + "'"

    private fun <T> failure(code: String, detail: String?): AtlasResult<T> = AtlasResult.Failure(
        AtlasError(
            code = code,
            domain = ErrorDomain.VALIDATION,
            userMessageKey = "error_git_operation",
            technicalDetail = detail,
            retryable = false,
        )
    )
}
