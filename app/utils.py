# crypto_handler.py
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from cryptography.fernet import Fernet

from app.config import constants
from app.secrets import FERNET_KEY, JWT_SECRET_KEY

# TODO: key값들 secret에 저장된 값들로 바꿔놓기
# TODO: 생성된 refresh_token의 jti를 whitelist에 추가할것
# TODO: 기기별(브라우저별)) 로그인을 관리하기 위해 id 부여하고 요청헤더 또는 쿠키에 같이 전송될 수 있도록 관리

# TODO: jwt 디코딩해서 payload 넘기는 함수 만들기

class EncryptionHandler:
    # __fernet_key = Fernet.generate_key()
    __fernet_key = FERNET_KEY.encode()
    __fernet = Fernet(__fernet_key)

    @classmethod
    def encrypt(cls, data: str) -> str:
        return cls.__fernet.encrypt(data.encode()).decode()

    @classmethod
    def decrypt(cls, token: str) -> str:
        return cls.__fernet.decrypt(token.encode()).decode()

    @classmethod
    def key(cls):
        return cls.__fernet_key


class JWTHandler:
    # __secret_key = Fernet.generate_key()
    __secret_key = JWT_SECRET_KEY

    @classmethod
    def get_new_tokens(cls, payload: dict) -> dict:
        refresh_token = cls.create_refresh_token(payload)
        access_token = cls.create_access_token(refresh_token)
        encrypted_refresh_token = EncryptionHandler.encrypt(refresh_token)
        encrypted_access_token = EncryptionHandler.encrypt(access_token)

        return {
            "refresh_token": encrypted_refresh_token,
            "access_token": encrypted_access_token,
        }

    @classmethod
    def create_jti(cls, id):
        return f"{id}-{uuid4()}"

    @classmethod
    def create_refresh_token(cls, payload: str) -> str:
        """
        payload에 필요한 정보를 추가후 refresh 토큰 생성

        - jti: 토큰 식별 id
        - token_type(type): refresh 고정
        - iat: 토큰 생성 시간
        - exp: 토큰 만료 시간
        """
        now_utc: datetime = datetime.now(timezone.utc)

        refresh_payload = {
            **payload,
            "type": "refresh",
            "jti": cls.create_jti(payload["id"]),
            "iat": int(now_utc.timestamp()),
            "exp": int((now_utc + timedelta(days=7)).timestamp()),
        }

        token = jwt.encode(refresh_payload, cls.__secret_key, algorithm="HS256")
        return token

    @classmethod
    def create_access_token(cls, refresh_token: str) -> str:
        try:
            # 1. 디코드 (유효성 검사 포함)
            payload = jwt.decode(refresh_token, cls.__secret_key, algorithms=["HS256"])

            # 2. refresh 타입인지 확인
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")

            # 3. 새 payload로 access token 생성
            now_utc = datetime.now(timezone.utc)
            access_payload = {
                **payload,
                "type": "access",
                "jti": cls.create_jti(payload["id"]),
                "iat": int(now_utc.timestamp()),
                "exp": int((now_utc + timedelta(minutes=15)).timestamp()),
            }

            access_token = jwt.encode(
                access_payload, cls.__secret_key, algorithm="HS256"
            )
            return access_token

        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid refresh token")

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> str:
        decrypted_refresh_token = EncryptionHandler.decrypt(refresh_token)
        new_access_token = cls.create_access_token(decrypted_refresh_token)
        return EncryptionHandler.encrypt(new_access_token)
