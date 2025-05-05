from fastapi import HTTPException, Request, status, Depends
from app.config import constants
from app.utils import EncryptionHandler, JWTHandler
from app.schemas import User


class AuthService:
    @classmethod
    def get_user_from_jwt(cls, request: Request) -> User:
        access_token = request.cookies.get(constants.ACCESS_TOKEN_NAME)
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not found in cookies",
            )

        # 기본적으로 토큰은 암호화되어있으므로 복호화 시도
        decrypted_token = EncryptionHandler.decrypt(access_token)
        # 복호화된 토큰을 분해하기
        payload = JWTHandler.get_payload(decrypted_token)
        user = User(
            id=payload["sub"],
            role=payload.get("role"),
            permissions=payload.get("permissions"),
        )
        return user

