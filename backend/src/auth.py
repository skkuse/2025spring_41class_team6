from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from api_schema import *
from database.utils import *

USER_ID_COOKIE_KEY = "user_id"

def check_user_id(request: Request):
    """Exception-Free User ID 추출"""
    user_id = request.cookies.get(USER_ID_COOKIE_KEY)
    if not user_id:
      return None

    return int(user_id)

def get_current_user_id(request: Request):
    """Cookie에서 User ID를 추출"""
    user_id = request.cookies.get(USER_ID_COOKIE_KEY)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in")

    return int(user_id)

def validate_user(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Cookie의 User ID를 validate 합니다"""
    user = db_find_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/user", response_model=UserInfoResponse)
async def get_user_information(user: UserInfoInternal = Depends(validate_user)):
    return UserInfoResponse(
        id = user.id,
        email=user.email,
        nickname=user.nickname
    )

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
