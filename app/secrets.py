import os

from dotenv import load_dotenv

load_dotenv()

DEBUG_MODE_STR = "DEBUG_MODE"

DOCS_PREFIX = os.getenv("DOCS_PREFIX")
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", DEBUG_MODE_STR)
AES_SECRET_KEY = os.getenv("AES_SECRET_KEY")
FERNET_KEY: str = os.getenv("FERNET_KEY", DEBUG_MODE_STR)
