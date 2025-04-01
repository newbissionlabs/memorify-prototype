import base64
import os

# JWT
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.database import DBHandler
from app.models import User
from app.schemas import UserCreate as user_create_schema
from app.secrets import AES_SECRET_KEY, JWT_SECRET_KEY

router = APIRouter(prefix="/v1")


# 로그인
@router.post("/auth/login", tags=["auth"])
async def login():
    return {"로그인": False}


class JWTHandler:
    secret_key = JWT_SECRET_KEY
    encryption_key = base64.b64decode(AES_SECRET_KEY)

    # AES로 유저 ID 암호화 함수
    @classmethod
    def encrypt_user_id(cls, user_id: int) -> str:
        nonce = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(cls.encryption_key),
            modes.GCM(nonce),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(str(user_id).encode()) + encryptor.finalize()
        encrypted_data = nonce + encryptor.tag + ciphertext
        return base64.b64encode(encrypted_data).decode("utf-8")

    # AES로 암호화된 유저 ID 복호화 함수
    @classmethod
    def decrypt_user_id(cls, encrypted_data: str) -> str:
        encrypted_data = base64.b64decode(encrypted_data)
        nonce, tag, ciphertext = (
            encrypted_data[:12],
            encrypted_data[12:28],
            encrypted_data[28:],
        )
        cipher = Cipher(
            algorithms.AES(cls.encryption_key),
            modes.GCM(nonce, tag),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted.decode()

    # JWT 생성 (유저 ID 암호화하여 저장)
    @classmethod
    def create_jwt(cls, id: int) -> str:
        encrypted_user_id = cls.encrypt_user_id(id)
        print(encrypted_user_id)
        payload = {"id": encrypted_user_id}
        token = jwt.encode(payload, cls.secret_key, algorithm="HS256")
        return token


# 회원가입
@router.post(
    "/auth/signup",
    status_code=201,
    tags=["auth"],
    responses={
        400: {
            "description": "Bad Request - Duplicate entry or invalid data",
            "content": {
                "application/json": {
                    "example": {"error": {"code": 23505, "detail": "Exsists user_id"}}
                }
            },
        }
    },
)
async def signup(
    *, db: Session = Depends(DBHandler.get_session), data: user_create_schema
):
    token = JWTHandler.create_jwt(4)
    encoded_id = jwt.decode(token, JWTHandler.secret_key, algorithms=["HS256"]).get(
        "id"
    )
    decode_id = JWTHandler.decrypt_user_id(encoded_id)
    print(decode_id)
    return token
    try:
        user = User(**data.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        error = DBHandler.get_error_details(e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": error}
        )

    # 회원 가입이 완료되었으니 JWT 생성

    return user


# 단어 등록(여러 단어 한 번에 가능)
@router.post("/words", tags=["words"])
async def register_words():
    return {"단어등록": False}


# 단어상태변경(여러 단어 한 번에 가능)
@router.patch("/words/status", tags=["words"])
async def update_words_status():
    return {"단어 상태 변경": False}


# 단어장 조회
@router.get("/words", tags=["words"])
async def get_words():
    return {"단어조회": False}


# 단어 검증 필요 여부 조회
@router.get("/verifications/require", tags=["verifications"])
async def check_verification_requirement():
    return {"검증 여부": False}


# 검증 시작
@router.post("/verifications/start", tags=["verifications"])
async def start_verification():
    return {"검증 아이디": 123}


# 단어 검증 결과
@router.patch("/verifications/result", tags=["verifications"])
async def save_verification_result():
    return {"검증 결과 저장": False}


# 검증 내역 조회
@router.get("/verifications", tags=["verifications"])
async def verification_result():
    return {"검증 결과 저장": False}
