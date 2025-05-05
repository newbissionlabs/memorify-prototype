from sqlmodel import Field, SQLModel


class UserRead(SQLModel):
    id: int
    name: str


class UserLogin(SQLModel):
    user_id: str = Field(..., max_length=20, index=True)
    password: str = Field(..., max_length=20)


class UserCreate(UserLogin):
    name: str | None = Field(default=None, max_length=20)


class User(SQLModel):
    id: int
    role: str | None
    permissions: list[str] | None


"""WORD"""


# 개인이 생성한 단어일 수 있으므로 뜻, 발음기호도 같이 넣을 수 있음
class Word(SQLModel):
    word: str
    meaning: str | None
    pronunciation: str | None


class AddWordsRequest(SQLModel):
    words: list[Word]
