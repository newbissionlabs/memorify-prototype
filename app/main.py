from fastapi import FastAPI

from app.routers import router
from app.secrets import DOCS_PREFIX

app = FastAPI(
    docs_url=DOCS_PREFIX + "/docs",
    redoc_url=DOCS_PREFIX + "/redoc",
    openapi_url=DOCS_PREFIX + "/json",
    debug=False,
)


@app.get("/")
def root_handler():
    return {"ping": "pong"}


app.include_router(router)
