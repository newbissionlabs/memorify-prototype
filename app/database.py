from sqlmodel import Session, create_engine

# from app.models import User  # User 모델을 임포트
from app.secrets import DATABASE_URL
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session