from dataclasses import dataclass
from enum import Enum

TIMEZONE = "Asia/Seoul"


@dataclass(frozen=True)
class _Constant:
    ACCESS_TOKEN_NAME: str = "MMFYAT"
    REFRESH_TOKEN_NAME: str = "MMFYRT"
    JWT_SKIP_PATHS: tuple[str] = ("/v1/auth/login", "/v1/auth/signup")
    VERIFICATION_CODE_LENGTH: int = 5


constants = _Constant()


class WordStatusEnum(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    AMBIGUOUS = "ambiguous"
    
class VerificationStatusEnum(str, Enum):
    PENDING = "pending"
    DONE = "done"
    IN_PROGRESS = "in_progress"
    READY = "ready"