from dataclasses import dataclass

TIMEZONE = "Asia/Seoul"


@dataclass(frozen=True)
class _Constant:
    access_token: str = "MMFYAT"
    refresh_token: str = "MMFYRT"


constants = _Constant()
