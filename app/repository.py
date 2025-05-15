from fastapi import Depends
from sqlmodel import Session, select
from app.database import DBHandler
from app.models import User, Word, UserWord


class BaseRepository:
    def __init__(self, session: Session = Depends(DBHandler.get_session)):
        self.session = session


class WordRepository(BaseRepository):
    def get_or_create(self, word: Word) -> Word:
        statement = select(Word).where(Word.word == word.word)
        result = self.session.exec(statement).first()

        if result:
            return result

        return self.create(word)

    def create(self, word: Word) -> Word:
        self.session.add(instance=word)
        self.session.commit()
        self.session.refresh(instance=word)
        return word


class UserWordRepository(BaseRepository):
    def create(self, user: User, word: Word) -> UserWord:
        """
        단일 User와 Word 관계 추가
        """
        existing = self.session.exec(
            select(UserWord).where(UserWord.user == user.id, UserWord.word == word.id)
        ).first()
        if existing:
            raise ValueError(
                f"UserWord relation for user {user.id} and word {word.id} already exists"
            )

        user_word = UserWord(user=user.id, word=word.id)
        self.session.add(user_word)
        self.session.commit()
        self.session.refresh(user_word)
        return user_word

    def create_multiple(self, user: User, words: list[Word]) -> list[UserWord]:
        """
        유저 한 명과 여러 단어의 관계를 한 번에 추가
        """
        created_user_words = []

        # 기존 관계 확인
        existing_relations = self.session.exec(
            select(UserWord).where(
                UserWord.user == user.id, UserWord.word.in_([word.id for word in words])
            )
        ).all()
        existing_word_ids = {uw.word for uw in existing_relations}

        # 새로운 관계만 추가
        for word in words:
            if word.id not in existing_word_ids:
                user_word = UserWord(
                    user=user.id,
                    word=word.id,
                )
                self.session.add(user_word)
                created_user_words.append(user_word)

        # 벌크 커밋
        self.session.commit()

        # 생성된 객체들 리프레시
        for user_word in created_user_words:
            self.session.refresh(user_word)

        return created_user_words
