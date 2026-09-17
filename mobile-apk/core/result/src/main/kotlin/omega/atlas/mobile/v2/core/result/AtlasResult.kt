package omega.atlas.mobile.v2.core.result

sealed interface AtlasResult<out T> {
    data class Success<T>(val value: T) : AtlasResult<T>
    data class Failure(val error: AtlasError) : AtlasResult<Nothing>
}

inline fun <T, R> AtlasResult<T>.map(transform: (T) -> R): AtlasResult<R> = when (this) {
    is AtlasResult.Success -> AtlasResult.Success(transform(value))
    is AtlasResult.Failure -> this
}
