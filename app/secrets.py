from dotenv import load_dotenv

load_dotenv()

import os

DOCS_PREFIX = os.getenv("DOCS_PREFIX")
DATABASE_URL = os.getenv("DATABASE_URL")