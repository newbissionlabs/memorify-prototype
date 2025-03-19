from fastapi import APIRouter

router = APIRouter()


# 로그인
@router.post("/auth/login", tags=["auth"])
async def login():
    return {"로그인": False}


# 회원가입
@router.post("/auth/signup", tags=["auth"])
async def signup():
    return {"회원가입": False}


# 단어 등록(여러 단어 한 번에 가능)
@router.post("/words", tags=["words"])
async def register_words():
    return {"단어등록": False}


# 단어상태변경(여러 단어 한 번에 가능)
@router.patch("/words/status", tags=["words"])
async def update_words_status():
    return {"단어 상태 변경": False}


# 단어장 조회
@router.get("/words", tags=["words"])
async def get_words():
    return {"단어조회": False}


# 단어 검증 필요 여부 조회
@router.get("/verifications/require", tags=["verifications"])
async def check_verification_requirement():
    return {"검증 여부": False}


# 검증 시작
@router.post("/verifications/start", tags=["verifications"])
async def start_verification():
    return {"검증 아이디": 123}


# 단어 검증 결과
@router.patch("/verifications/result", tags=["verifications"])
async def save_verification_result():
    return {"검증 결과 저장": False}


# 검증 내역 조회
@router.get("/verifications", tags=["verifications"])
async def verification_result():
    return {"검증 결과 저장": False}
