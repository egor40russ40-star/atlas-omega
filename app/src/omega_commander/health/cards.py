from __future__ import annotations

def computer_health_ru(*,cpu_pct:float,memory_pct:float,disk_free_gb:float,temperature_c:float|None=None):
    warnings=[]
    if cpu_pct>=90: warnings.append("Высокая загрузка процессора.")
    if memory_pct>=90: warnings.append("Высокое использование памяти.")
    if disk_free_gb<20: warnings.append("Мало свободного места на диске.")
    if temperature_c is not None and temperature_c>=90: warnings.append("Высокая температура процессора.")
    status="ВНИМАНИЕ" if warnings else "НОРМА"
    return {
        "status":status,
        "cpu":f"{cpu_pct:.1f}%",
        "memory":f"{memory_pct:.1f}%",
        "disk_free":f"{disk_free_gb:.1f} ГБ",
        "temperature":None if temperature_c is None else f"{temperature_c:.1f} °C",
        "warnings":warnings,
    }
