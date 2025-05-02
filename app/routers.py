import base64
import os

# JWT
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.config import constants
from app.database import DBHandler
from app.models import User
from app.schemas import UserCreate as user_create_schema
from app.schemas import UserLogin as user_login_schema
from app.utils import JWTHandler as jwthandler

router = APIRouter(prefix="/v1")

# TODO: JWT 검증하는 미들웨어 만들어야할 거같음 일단은 Depends로 쓰게 함수로다가....


# 로그인
@router.post("/auth/login", tags=["auth"])
async def login(
    *, db: Session = Depends(DBHandler.get_session), data: user_login_schema
):
    try:
        user = db.exec(
            select(User).where(
                User.user_id == data.user_id, User.password == data.password
            )
        ).first()
    except IntegrityError as e:
        print("@@@@@@@@@@@@@@@@fail@@@@@@@@@@@@@@")
        db.rollback()
        error = DBHandler.get_error_details(e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": error}
        )

    # 로그인에 성공했으니 JWT 생성
    payload = {"id": user.id}
    tokens = jwthandler.get_new_tokens(payload)
    response = JSONResponse(content=tokens)
    response.set_cookie(key=constants.ACCESS_TOKEN_NAME, value=tokens.get("access_token"))
    response.set_cookie(key=constants.REFRESH_TOKEN_NAME, value=tokens.get("refresh_token"))
    return response


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
    payload = {"sub": user.id}
    tokens = jwthandler.get_new_tokens(payload)

    return tokens


# 단어 등록(여러 단어 한 번에 가능)
@router.post("/words", tags=["words"])
async def register_words(
    *, db: Session = Depends(DBHandler.get_session), data: list[str]
):
    """
    data: JSON [word, word, word, ....]
    """
    # 1. 단어마다 db에 있는지 조회 (get_or_create)
    for word in data:
        print(word)
    # 2. user_word에 추가하기
    # 3. 하나라도 삑사리나면 rollback?

    return {"단어등록": data}


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
