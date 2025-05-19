from dataclasses import dataclass
from enum import Enum

TIMEZONE = "Asia/Seoul"


@dataclass(frozen=True)
class _Constant:
    ACCESS_TOKEN_NAME: str = "MMFYAT"
    REFRESH_TOKEN_NAME: str = "MMFYRT"
    JWT_SKIP_PATHS: tuple[str] = ("/v1/auth/login", "/v1/auth/signup")


constants = _Constant()


class WordStatusEnum(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    AMBIGUOUS = "ambiguous"