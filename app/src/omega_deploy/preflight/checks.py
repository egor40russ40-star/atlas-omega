from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from omega_deploy.domain.models import PreflightCheck, PreflightReport, CheckState
from omega_deploy.preflight.environment import detect_environment
from omega_deploy.migrations.continuity import migration_continuity

def run_preflight(
    repo_root: str | Path,
    *,
    minimum_disk_free_gb: float = 5.0,
    minimum_memory_gb: float = 4.0,
) -> PreflightReport:
    repo=Path(repo_root)
    env=detect_environment(repo)
    checks=[]

    checks.append(PreflightCheck(
        "python",
        CheckState.PASS if env.python_ok else CheckState.FAIL,
        f"Python {env.python_version}: {'подходит' if env.python_ok else 'нужен Python 3.12+'}.",
        () if env.python_ok else ("DEPLOY_PYTHON_TOO_OLD",),
    ))

    disk_gb=env.disk_free_bytes/1024**3
    checks.append(PreflightCheck(
        "disk",
        CheckState.PASS if disk_gb>=minimum_disk_free_gb else CheckState.FAIL,
        f"Свободно на диске: {disk_gb:.1f} ГБ.",
        () if disk_gb>=minimum_disk_free_gb else ("DEPLOY_DISK_INSUFFICIENT",),
        {"disk_free_gb":disk_gb},
    ))

    if env.memory_total_bytes is None:
        checks.append(PreflightCheck(
            "memory",CheckState.WARNING,
            "Объём RAM не удалось определить переносимым способом.",
            ("DEPLOY_MEMORY_UNKNOWN",),
        ))
    else:
        mem_gb=env.memory_total_bytes/1024**3
        checks.append(PreflightCheck(
            "memory",
            CheckState.PASS if mem_gb>=minimum_memory_gb else CheckState.FAIL,
            f"Оперативная память: {mem_gb:.1f} ГБ.",
            () if mem_gb>=minimum_memory_gb else ("DEPLOY_MEMORY_INSUFFICIENT",),
            {"memory_gb":mem_gb},
        ))

    ok,details=migration_continuity(repo/"migrations")
    checks.append(PreflightCheck(
        "migrations",CheckState.PASS if ok else CheckState.FAIL,
        "Цепочка миграций непрерывна." if ok else "Нарушена цепочка миграций.",
        () if ok else ("DEPLOY_MIGRATION_GAP",),
        details,
    ))

    writable=repo.exists() and os_writable(repo)
    checks.append(PreflightCheck(
        "write",CheckState.PASS if writable else CheckState.FAIL,
        "Каталог доступен для runtime-файлов." if writable else "Нет права записи в каталог.",
        () if writable else ("DEPLOY_RUNTIME_NOT_WRITABLE",),
    ))

    blocking=tuple(sorted({
        code
        for c in checks if c.state is CheckState.FAIL
        for code in c.reason_codes
    }))
    return PreflightReport(
        datetime.now(timezone.utc),tuple(checks),not blocking,blocking
    )

def os_writable(path: Path) -> bool:
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(dir=path,delete=True):
            return True
    except Exception:
        return False
