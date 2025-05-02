from fastapi import FastAPI

from app.middlewares import JWTMiddleware
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

# jwt 인증의 경우 필요한 엔드포인트에서 Depends로 처리하는 것으로 변경
# app.add_middleware(JWTMiddleware)