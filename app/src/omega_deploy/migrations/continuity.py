from __future__ import annotations
from pathlib import Path
import re

def migration_numbers(migrations_dir: str | Path) -> list[int]:
    nums=[]
    for p in Path(migrations_dir).glob("*.sql"):
        m=re.match(r"(\d{4})_",p.name)
        if m:
            nums.append(int(m.group(1)))
    return sorted(set(nums))

def migration_continuity(migrations_dir: str | Path) -> tuple[bool,dict]:
    nums=migration_numbers(migrations_dir)
    if not nums:
        return False,{"numbers":[],"missing":["ALL"]}
    expected=list(range(nums[0],nums[-1]+1))
    missing=[x for x in expected if x not in nums]
    duplicates=[]
    names=[p.name for p in Path(migrations_dir).glob("*.sql")]
    for n in nums:
        prefix=f"{n:04d}_"
        count=sum(name.startswith(prefix) for name in names)
        if count>1:
            duplicates.append(n)
    ok=not missing and not duplicates and nums[0]==1
    return ok,{"numbers":nums,"missing":missing,"duplicates":duplicates}
