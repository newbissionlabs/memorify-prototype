from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


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
