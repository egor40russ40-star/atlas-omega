package omega.atlas.mobile.v2.feature.git

object GitPorcelainParser {
    fun parseStatus(raw: String): GitSnapshot {
        val records = raw.split('\u0000').filter { it.isNotEmpty() }
        var branch = "(detached)"
        var ahead = 0
        var behind = 0
        val changes = mutableListOf<GitFileChange>()

        var index = 0
        if (records.firstOrNull()?.startsWith("## ") == true) {
            val header = records.first().removePrefix("## ")
            branch = header.substringBefore("...").substringBefore(" [").ifBlank { "(detached)" }
            val meta = header.substringAfter(" [", "").removeSuffix("]")
            Regex("ahead (\\d+)").find(meta)?.groupValues?.getOrNull(1)?.toIntOrNull()?.let { ahead = it }
            Regex("behind (\\d+)").find(meta)?.groupValues?.getOrNull(1)?.toIntOrNull()?.let { behind = it }
            index = 1
        }

        while (index < records.size) {
            val record = records[index]
            if (record.length < 3) {
                index++
                continue
            }
            val x = record[0]
            val y = record[1]
            val path = record.substring(3)
            val conflict = setOf("DD", "AU", "UD", "UA", "DU", "AA", "UU").contains("$x$y")
            val kind = when {
                conflict -> GitChangeKind.CONFLICT
                x == '?' && y == '?' -> GitChangeKind.UNTRACKED
                x == 'R' || y == 'R' || x == 'C' || y == 'C' -> GitChangeKind.RENAMED
                x == 'D' || y == 'D' -> GitChangeKind.DELETED
                x == 'A' || y == 'A' -> GitChangeKind.ADDED
                else -> GitChangeKind.MODIFIED
            }
            val staged = x != ' ' && x != '?'
            changes += GitFileChange(
                path = path,
                kind = kind,
                staged = staged,
            )

            // Porcelain v1 -z emits one extra pathname after rename/copy entries.
            index += if ((x == 'R' || y == 'R' || x == 'C' || y == 'C') && index + 1 < records.size) 2 else 1
        }

        return GitSnapshot(
            branch = branch,
            ahead = ahead,
            behind = behind,
            changes = changes,
        )
    }
}
