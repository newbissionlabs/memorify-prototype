from sqlmodel import SQLModel, Field


class UserRead(SQLModel):
    id: int
    name: str


class UserLogin(SQLModel):
    user_id: str = Field(..., max_length=20, index=True)
    password: str = Field(..., max_length=20)


class UserCreate(UserLogin):
    name: str | None = Field(default=None, max_length=20)
