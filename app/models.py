from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

# from app.schemas import Word as word_schema, AddWordsRequest
from app.schemas import AddWordsRequest
from app.config import WordStatusEnum


class BaseModel(SQLModel):
    """
    모든 모델(테이블)에 `create_at`, `update_at` 칼럼을 추가해주기 위함
    """

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class User(BaseModel, table=True):
    """
    유저의 기본 모델 `password`는 프로토타입이라 해쉬화 안했음
    id: int | auto increment
    user_id: str | required,  max_length=20
    password: str | required, max_length=20 -> 해쉬화 할 경우 255
    name: str | default="anonymous", max_length=20
    """

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(..., max_length=20, unique=True, index=True)
    password: str = Field(..., max_length=20)
    name: str = Field(default="anonymous", max_length=20)

    words: list["UserWord"] = Relationship(back_populates="users")


class Word(BaseModel, table=True):
    """
    현재는 프로토타입이므로 English Only로 만듦
    """

    id: int | None = Field(default=None, primary_key=True)
    word: str = Field(..., index=True, unique=True)
    meaning: str | None = Field(default=None)
    pronunciation: str | None = Field(default=None)

    users: list["UserWord"] = Relationship(back_populates="words")

    # 현재 Word 스키마를 없앤 상태 <<< Word를 단순히 word만 포함해서 딱히 필요없어졌음
    # @classmethod
    # def create(cls, request: word_schema) -> "Word":
    #     return cls(
    #         word=request.word,
    #         meaning=request.meaning,
    #         pronunciation=request.pronunciation,
    #     )
    @classmethod
    def create(cls, word: str) -> str:
        return cls(word=word)

    @classmethod
    def create_bulk(cls, request: AddWordsRequest) -> list["Word"]:
        return [cls.create(word) for word in request]


class UserWord(BaseModel, table=True):
    """
    유저별로 등록한 단어 관계 테이블
    """

    id: int | None = Field(default=None, primary_key=True)
    user: int = Field(foreign_key="user.id")
    word: int = Field(foreign_key="word.id")
    status: WordStatusEnum = Field(default=WordStatusEnum.PENDING)

    users: User = Relationship(back_populates="words")
    words: Word = Relationship(back_populates="users")
