from __future__ import annotations
from typing import Protocol, Iterable, Any
from pathlib import Path

class ParquetArchivePort(Protocol):
    def write_rows(self, path: Path, rows: Iterable[dict[str, Any]], *, compression: str = "zstd") -> int:
        ...

class ResearchQueryPort(Protocol):
    def query_parquet(self, glob_path: str, sql: str):
        ...
