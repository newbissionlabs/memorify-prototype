import base64
import os

# JWT
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.config import constants, WordStatusEnum
from app.database import DBHandler
from app.models import User, Word
from app.schemas import (
    UserCreate as user_create_schema,
    UserLogin as user_login_schema,
    User as user_schema,
    AddWordsRequest,
    # UpdateWord,
    # UpdateWordsRequest,
)
from app.utils import JWTHandler as jwthandler
from app.services import AuthService
from app.repository import WordRepository, UserWordRepository

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
        ).one()
    except IntegrityError as e:
        print("@@@@@@@@@@@@@@@@fail@@@@@@@@@@@@@@")
        db.rollback()
        error = DBHandler.get_error_details(e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": error}
        )

    if user is None or user.id is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": "No User"}
        )
    # 로그인에 성공했으니 JWT 생성
    tokens = jwthandler.get_new_tokens(user.id)
    response = JSONResponse(content=tokens)
    response.set_cookie(
        key=constants.ACCESS_TOKEN_NAME, value=tokens.get("access_token")
    )
    response.set_cookie(
        key=constants.REFRESH_TOKEN_NAME, value=tokens.get("refresh_token")
    )
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
    tokens = jwthandler.get_new_tokens(user.id)

    return tokens


# 단어 등록(여러 단어 한 번에 가능)
@router.post("/words", tags=["words"])
async def register_words(
    *,
    user: user_schema = Depends(AuthService.get_user_from_jwt),
    request: AddWordsRequest,
    word_repo: WordRepository = Depends(WordRepository),
    user_word_repo: UserWordRepository = Depends(UserWordRepository),
):
    """
    data: JSON [word, word, word, ....]
    """
    # 1. 단어마다 db에 있는지 조회 (get_or_create)
    words: list[Word] = Word.create_bulk(request.words)
    registed_words = []
    for word in words:
        registed_word = word_repo.get_or_create(word)
        registed_words.append(registed_word)
    # 2. user_word에 추가하기
    result = user_word_repo.create_multiple(user=user, words=registed_words)
    print(result)
    # 3. 하나라도 삑사리나면 rollback?

    return Response(content=None, status_code=status.HTTP_201_CREATED)


# 단어상태변경(여러 단어 한 번에 가능)
@router.patch("/words/status", tags=["words"])
async def update_words_status(
    *,
    _: user_schema = Depends(AuthService.get_user_from_jwt),
    request: dict[int, WordStatusEnum],
    user_word_repo: UserWordRepository = Depends(UserWordRepository),
):
    # update_words = [
    #     UpdateWord(id=word_id, status=status)
    #     for word_id, status in request.__root__.items()
    # ]

    result = user_word_repo.get_all(request.keys())
    if not result:
        return JSONResponse(
            content={"error": "일치하는 단어 없음"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    for user_word in result:
        user_word_repo.update(user_word, request[user_word.id])

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# 단어장 조회
@router.get("/words", tags=["words"])
async def get_words(
    *,
    user: user_schema = Depends(AuthService.get_user_from_jwt),
    word_repo: WordRepository = Depends(WordRepository),
    user_word_repo: UserWordRepository = Depends(UserWordRepository),
):
    # user_words에서 user가 등록한 단어목록 가져오기
    user_words = user_word_repo.get_users_words(user=user)
    # Word에서 단어 상세정보 가져오기
    words = word_repo.get_all_by_id([user_word.id for user_word in user_words])
    result = []
    for user_word, word in zip(user_words, words):
        result.append(
            {
                "id": user_word.id,
                "created": user_word.created_at,
                "word": word.word,
                "meaning": word.meaning,
                "pronunciation": word.pronunciation,
                "status": user_word.status,
            }
        )
    return result


# 단어 검증 필요 여부 조회
@router.get("/verifications/require", tags=["verifications"])
async def check_verification_requirement(
    *,
    user: user_schema = Depends(AuthService.get_user_from_jwt),
):
    # TODO: 유저별로 단어 시험 체크하는 테이블 만들어야 할듯?
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
async def verification_result(
    *,
    user: user_schema = Depends(AuthService.get_user_from_jwt),
):
    return {"검증 결과 저장": False}
