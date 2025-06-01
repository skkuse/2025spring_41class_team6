from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from api_schema import *
from database.utils import *
from common.env import ENV_API_SKIP_AUTH

USER_ID_COOKIE_KEY = "user_id"

# API_SKIP_AUTH가 설정되더라도 DB에 ID=1인 유저 정보는 필요함
DEFAULT_USER_ID = 1 # API_SKIP_AUTH 시, cookie가 없을 때 자동 선택되는 user id

def config_skip_auth():
    return ENV_API_SKIP_AUTH == "1"

def get_current_user_id(request: Request):
    user_id = request.cookies.get(USER_ID_COOKIE_KEY)
    if not user_id:
        if not config_skip_auth():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in")
        else:
            return DEFAULT_USER_ID
    return int(user_id)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserInfoResponse)
async def register_user(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    id = db_create_new_user(db, payload.email, payload.password, payload.nickname)
    if id is None:
        raise HTTPException(status_code=400, detail="User already exists")

    if payload.login == True:
      # we immdiately login here, since we have the valid ID:
      response.set_cookie(
          key=USER_ID_COOKIE_KEY,
          value=str(id),
          httponly=True
      )

    return UserInfoResponse(
        id = id,
        email = payload.email,
        nickname = payload.nickname
    )

@router.post("/login", response_model=UserInfoResponse)
async def login_user(payload: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db_find_user_with_password(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    response.set_cookie(
        key=USER_ID_COOKIE_KEY,
        value=str(user.id),
        httponly=True
    )
    return UserInfoResponse(
        id = user.id,
        email = user.email,
        nickname = user.nickname
    )

@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key=USER_ID_COOKIE_KEY)
    return {"message": "Logged out"}
