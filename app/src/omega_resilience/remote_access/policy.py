ALLOWED_MODES={"LOCAL_ONLY","LAN_ONLY","VPN_ONLY","REMOTE_DISABLED"}

def validate_remote_mode(mode: str, *, public_internet_exposed: bool) -> tuple[str,...]:
    if mode not in ALLOWED_MODES:
        raise ValueError("unknown remote mode")
    if public_internet_exposed:
        return ("RES_REMOTE_PUBLIC_FORBIDDEN",)
    return ()
