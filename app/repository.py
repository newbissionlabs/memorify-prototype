from fastapi import Depends
from sqlmodel import Session, select
from app.database import DBHandler
from app.models import User, Word, UserWord
from app.schemas import UpdateWord
from app.config import WordStatusEnum


class BaseRepository:
    def __init__(self, session: Session = Depends(DBHandler.get_session)):
        self.session = session


class WordRepository(BaseRepository):
    def get_by_id(self, id: int) -> Word:
        return self.session.exec(select(Word).where(Word.id == id)).one()
    
    def get_all_by_id(self, ids: list[int]) -> list[Word]:
        return self.session.exec(select(Word).where(Word.id.in_(ids))).all()
    
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
    def get(self, id: int) -> UserWord | None:
        user_word = None
        try:
            user_word = self.session.exec(
                select(UserWord).where(UserWord.id == id)
            ).one()
        except:
            pass

        return user_word

    def get_all(self, ids: list[int]) -> list[UserWord]:
        user_words = []
        for id in ids:
            print(id)
            user_word = self.get(id)
            # 넘겨받은 id 중에 없는 것도 존재할 수 있음
            if user_word:
                user_words.append(user_word)

        return user_words

    def get_users_words(self, user: User) -> list[UserWord]:
        return self.session.exec(select(UserWord).where(UserWord.user == user.id)).all()

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

    def update(self, user_word: UserWord, status: WordStatusEnum) -> None:
        user_word.status = status

        # user_word가 이미 get 과정에서 가져온 객체이므로 굳이 add 안해도 됨
        # self.session.add(user_word)
        self.session.commit()

        # 현재 프로그램상 refresh 객체를 사용하지 않음
        # self.session.refresh(user_word)
