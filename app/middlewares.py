from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastapi.responses import JSONResponse
from app.config import constants
from fastapi import status
from app.utils import JWTHandler


class JWTMiddleware(BaseHTTPMiddleware):
    """
    ### 토큰 검증 미들웨어
    401: 토큰 없음, 만료, 유효하지 않음
    403: 
    """
    async def dispatch(self, request: Request, call_next):
        # JWT_SKIP_PATHS에 있으면 return 하려고 했으나 
        # 후처리가 필요할 수 있어서 없는경우를 하기로 결정
        if request.url.path not in constants.JWT_SKIP_PATHS:
            token = request.cookies.get(constants.ACCESS_TOKEN_NAME)
            if not token:
                return JSONResponse({"error": "401 unauth"}, 401)
        # TODO: JWT 확인
        response = await call_next(request)
        print("jwt middleware stop")
        return response


middleware = [Middleware(JWTMiddleware, exclude_paths=["/api/v1/auth/*"])]
