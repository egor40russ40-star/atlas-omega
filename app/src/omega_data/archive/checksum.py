from __future__ import annotations
from pathlib import Path
import hashlib

def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def verify_sha256(path: str | Path, expected: str) -> bool:
    return sha256_file(path) == expected
