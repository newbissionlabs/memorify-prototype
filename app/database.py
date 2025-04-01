from psycopg2.errors import Error as pgerror
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, create_engine

# from app.models import User  # User 모델을 임포트
from app.secrets import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)


class DBHandler:
    @classmethod
    def get_error_details(cls, error: IntegrityError):
        code = None
        if isinstance(error, IntegrityError):
            error = error.orig
        if isinstance(error, pgerror):
            code = error.pgcode
            if isinstance(error, UniqueViolation):
                detail = "Exsists user_id"

        return {"code": code, "detail": detail}

    @classmethod
    def get_session(cls):
        with Session(engine) as session:
            yield session
