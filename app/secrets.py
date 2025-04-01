import os

from dotenv import load_dotenv

load_dotenv()


DOCS_PREFIX = os.getenv("DOCS_PREFIX")
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
AES_SECRET_KEY = os.getenv("AES_SECRET_KEY")
