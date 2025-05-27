from fastapi import FastAPI, Path, Body, Response, Request, HTTPException, status, Depends
from datetime import datetime
from api_schema import *

app = FastAPI()

# 모의 유저 DB
mock_user_db = {
    "test@example.com": {"id": 1, "email": "test@example.com", "password": "1234"},
    "user2@example.com": {"id": 2, "email": "user2@example.com", "password": "abcd"},
}

def get_current_user_id(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in")
    return int(user_id)

@app.get("/api/")
async def root():
    return {"test": "HTTP 418: I'm a teapot"}

@app.post("/api/register")
async def register_user(payload: RegisterRequest):
    if payload.email in mock_user_db:
        raise HTTPException(status_code=400, detail="User already exists")
    new_id = max([u["id"] for u in mock_user_db.values()]) + 1
    mock_user_db[payload.email] = {
          "id": new_id,
          "email": payload.email,
          "password": payload.password,
          "nickname": payload.nickname,
      }
    return {"message": "User registered", "user_id": new_id}

@app.post("/api/login")
async def login_user(payload: RegisterRequest, response: Response):
    user = mock_user_db.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    response.set_cookie(
        key="user_id",
        value=str(user["id"]),
        httponly=True
    )
    return {"message": "Login successful", "user_id": user["id"]}


@app.post("/api/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="user_id")
    return {"message": "Logged out"}

from typing import cast

@app.get("/api/user", response_model=UserInfoResponse)
async def get_user_information(user_id: int = Depends(get_current_user_id)):
    user_info = mock_user_db.get("user_id")
    user_info = cast(dict, user_info)
    return UserInfoResponse(
        id = user_id,
        email = user_info["email"],
        nickname = user_info["nickname"]
    )

# ---------------------------
# /chatrooms
# ---------------------------
@app.get("/api/chatrooms")
async def get_chatrooms():
    return {
        "normal": [
            ChatRoom(id=1234, title="채팅방 이름"),
            ChatRoom(id=356, title="채팅방 #2")
        ],
        "immersive": [
            ChatRoom(id=534566000, title="몰입형 대화 #1")
        ]
    }


@app.post("/api/chatrooms", response_model=CreateChatroomResponse)
async def create_chatroom(payload: CreateChatroomRequest):
    chats = []
    if payload.initial_message:
        chats.append(ChatHistory(
            user_message=payload.initial_message,
            ai_message="AI 응답 예시",
            timestamp=datetime.now()
        ))
    return CreateChatroomResponse(
        id=1234,
        title="채팅방 이름",
        chats=chats
    )


# ---------------------------
# /chatrooms/{room_id}/messages
# ---------------------------
@app.get("/api/chatrooms/{room_id}/messages", response_model=List[ChatHistory])
async def get_messages(room_id: int = Path(...)):
    return [
        ChatHistory(user_message="안녕", ai_message="안녕하세요!", timestamp=datetime.now()),
        ChatHistory(user_message="이 영화 어때?", ai_message="추천할게요!", timestamp=datetime.now())
    ]


@app.post("/api/chatrooms/{room_id}/messages", response_model=ChatHistory)
async def post_message(room_id: int, payload: MessageRequest):
    return ChatHistory(
        user_message=payload.content,
        ai_message="AI 응답",
        timestamp=datetime.now()
    )


# ---------------------------
# /movies/{id}
# ---------------------------
@app.get("/api/movies/{id}", response_model=Movie)
async def get_movie(id: int):
    return Movie(
        id=id,
        title="영화 제목(TMDB-ko 기준)",
        overview="영화 줄거리 요약",
        wiki_document="wiki 줄거리",
        release_date="2000-00-00 00:00:00",
        poster_img_url="https://poster.example.com",
        trailer_img_url="https://trailer.example.com",
        rating=0,
        ordering=0
    )


# ---------------------------
# /movies/bookmarked
# ---------------------------
@app.get("/api/movies/bookmarked", response_model=List[Movie])
async def get_bookmarked():
    return [
        Movie(id=1, title="Bookmark Movie #1", overview="...", wiki_document="...", release_date="2020-01-01 00:00:00",
              poster_img_url="https://...", trailer_img_url="https://...", ordering=1),
        Movie(id=2, title="Bookmark Movie #2", overview="...", wiki_document="...", release_date="2020-01-01 00:00:00",
              poster_img_url="https://...", trailer_img_url="https://...", ordering=2)
    ]


@app.post("/api/movies/bookmarked", response_model=Movie)
async def post_bookmark(payload: MovieIDRequest):
    return Movie(
        id=payload.id,
        title="Bookmarked!",
        overview="...",
        wiki_document="...",
        release_date="2000-00-00 00:00:00",
        poster_img_url="https://poster.example.com",
        trailer_img_url="https://trailer.example.com",
        ordering=1
    )


@app.delete("/api/movies/bookmarked", response_model=Movie)
async def delete_bookmark(payload: MovieIDRequest):
    return Movie(
        id=payload.id,
        title="Bookmark Removed",
        overview="...",
        wiki_document="...",
        release_date="2000-00-00 00:00:00",
        poster_img_url="https://poster.example.com",
        trailer_img_url="https://trailer.example.com",
        ordering=1
    )


# ---------------------------
# /movies/archive
# ---------------------------
@app.get("/api/movies/archive", response_model=List[Movie])
async def get_archive():
    return [
        Movie(id=1, title="Archived Movie #1", overview="...", wiki_document="...", release_date="2020-01-01 00:00:00",
              poster_img_url="https://...", trailer_img_url="https://...", ordering=1, ranking=5),
        Movie(id=2, title="Archived Movie #2", overview="...", wiki_document="...", release_date="2020-01-01 00:00:00",
              poster_img_url="https://...", trailer_img_url="https://...", ordering=2, ranking=3)
    ]


@app.post("/api/movies/archive", response_model=Movie)
async def post_archive(payload: ArchiveRequest):
    return Movie(
        id=payload.id,
        title="Archived!",
        overview="...",
        wiki_document="...",
        release_date="2000-00-00 00:00:00",
        poster_img_url="https://poster.example.com",
        trailer_img_url="https://trailer.example.com",
        ordering=1,
        ranking=payload.ranking
    )


@app.delete("/api/movies/archive", response_model=Movie)
async def delete_archive(payload: MovieIDRequest):
    return Movie(
        id=payload.id,
        title="Archive Removed",
        overview="...",
        wiki_document="...",
        release_date="2000-00-00 00:00:00",
        poster_img_url="https://poster.example.com",
        trailer_img_url="https://trailer.example.com",
        ordering=1,
        ranking=3
    )
