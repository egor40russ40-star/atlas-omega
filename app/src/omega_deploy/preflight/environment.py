from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os, platform, shutil, sys

@dataclass(frozen=True, slots=True)
class EnvironmentSnapshot:
    os_name: str
    os_release: str
    machine: str
    python_version: str
    python_ok: bool
    cpu_count: int
    memory_total_bytes: int | None
    disk_free_bytes: int
    cwd: str

def _memory_total() -> int | None:
    # Linux
    try:
        if Path("/proc/meminfo").exists():
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemTotal:"):
                    return int(line.split()[1])*1024
    except Exception:
        pass
    # Windows best effort via ctypes.
    if os.name=="nt":
        try:
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_=[
                    ("dwLength",ctypes.c_ulong),
                    ("dwMemoryLoad",ctypes.c_ulong),
                    ("ullTotalPhys",ctypes.c_ulonglong),
                    ("ullAvailPhys",ctypes.c_ulonglong),
                    ("ullTotalPageFile",ctypes.c_ulonglong),
                    ("ullAvailPageFile",ctypes.c_ulonglong),
                    ("ullTotalVirtual",ctypes.c_ulonglong),
                    ("ullAvailVirtual",ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual",ctypes.c_ulonglong),
                ]
            x=MEMORYSTATUSEX(); x.dwLength=ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(x))
            return int(x.ullTotalPhys)
        except Exception:
            pass
    return None

def detect_environment(path: str | Path=".") -> EnvironmentSnapshot:
    usage=shutil.disk_usage(Path(path).resolve())
    py_ok=sys.version_info >= (3,12)
    return EnvironmentSnapshot(
        platform.system() or "UNKNOWN",
        platform.release() or "UNKNOWN",
        platform.machine() or "UNKNOWN",
        platform.python_version(),
        py_ok,
        os.cpu_count() or 1,
        _memory_total(),
        usage.free,
        str(Path.cwd()),
    )
