from fastapi import Depends
from sqlmodel import Session, select
from app.database import DBHandler
from app.models import Word


class WordRepository:
    def __init__(self, session: Session = Depends(DBHandler.get_session)):
        self.session = session

    def get_or_create(self, word: Word):
        statement = select(Word).where(Word.word == word.word)
        result = self.session.exec(statement).first()

        if result:
            return result

        self.session.add(instance=word)
        self.session.commit()
        self.session.refresh(instance=word)
        return word

    def create_word(self, word: Word):
        self.session.add(instance=word)
        self.session.commit()
        self.session.refresh(instance=word)
        return word
