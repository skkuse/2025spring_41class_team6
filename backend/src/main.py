import asyncio
from fastapi import FastAPI, Path, Body, Query, Response, Request, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from datetime import datetime
from api_schema import *
from llm_layer import get_summary_from_qachat, send_message_to_qachat, stream_send_message_to_qachat
from database.utils import *
from common.env import *
import auth
from typing import cast
import llm.qachat as qa

app = FastAPI()

app.include_router(auth.router)

# auth.get_current_user_id를 오버라이드해서 login을 skip할 수 있음
#
# app.dependency_overrides[auth.get_current_user_id] = lambda req: 1
# => 항상 ID=1 로 로그인됨
# 또는 find_user_by_id 자체를 오버라이드해서 원하는 유저로 자동 login할 수 있음
def find_user_by_id(user_id: int = Depends(auth.get_current_user_id), db: Session = Depends(get_db)):
    user = db_find_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/user", response_model=UserInfoResponse)
async def get_user_information(user: UserInfoInternal = Depends(find_user_by_id)):
    return UserInfoResponse(
        id = user.id,
        email=user.email,
        nickname=user.nickname
    )

# ---------------------------
# /chatrooms
# ---------------------------
@app.get("/api/chatrooms", response_model=ChatRoomList)
async def get_chatrooms(user: UserInfoInternal = Depends(find_user_by_id), db: Session = Depends(get_db)):
    rooms = db_get_user_chatrooms(db, user.id)
    
    return {
        "normal": [
            ChatRoom(id=room.id, title=room.title)
            for room in rooms if room.character_id is None
        ],
        "immersive": [
            ChatRoom(id=room.id, title=room.title)
            for room in rooms if room.character_id is not None
        ]
    }


@app.post("/api/chatrooms", response_model=CreateChatroomResponse)
async def create_chatroom(payload: CreateChatroomRequest,
                          user: UserInfoInternal = Depends(find_user_by_id),
                          db: Session = Depends(get_db)):
    room = db_make_new_chatroom(db, user.id)
    if room is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to create chatroom")

    chats = []
    if not payload.initial_message:
        return CreateChatroomResponse(
            id = room.id,
            title = room.title,
            chats = chats
        )

    # 초기 메시지가 있었다면 메시지를 AI에게 보내고 응답을 chats에 append하여 반환
    response = await send_message_to_qachat(db, user.id, room.id, payload.initial_message)
    result = db_append_chat_message(db, room.id, payload.initial_message, response, get_summary_from_qachat(room.id))
    if result is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to send message")
    
    chats.append(ChatHistory(
        user_message=result.user_chat,
        ai_message=result.ai_chat,
        timestamp=result.timestamp
    ))
    
    return CreateChatroomResponse(
        id = room.id,
        title = room.title,
        chats = chats
    )

# ---------------------------
# /chatrooms/{room_id}/messages
# ---------------------------
@app.get("/api/chatrooms/{room_id}/messages", response_model=List[ChatHistory])
async def get_messages(room_id: int,
                       user: UserInfoInternal = Depends(find_user_by_id),
                       db: Session = Depends(get_db)):
    chats = db_get_chat_messages(db, user.id, room_id)
    return [ChatHistory(
        user_message=chat.user_chat,
        ai_message=chat.ai_chat,
        timestamp=chat.timestamp
    ) for chat in chats]

@app.post("/api/chatrooms/{room_id}/messages", response_model=ChatHistory, response_description="""
`room_id`의 대화방에 메시지를 보낸 뒤, 그 응답을 ChatHistory의 형태로 불러옵니다.  
만약 stream=true 라면, text/event-stream 형식으로 스트리밍됩니다. 프론트에서 유의해서 작업해주세요
""")
async def post_message(room_id: int,
                       payload: MessageRequest = Body(...),
                       stream: bool = Query(False, description="true 시 SSE를 통한 스트리밍 응답"),
                       user: UserInfoInternal= Depends(find_user_by_id),
                       db: Session = Depends(get_db)):
    
    if not stream:
        response = await send_message_to_qachat(db, user.id, room_id, payload.content)
        result = db_append_chat_message(db, room_id, payload.content, response, get_summary_from_qachat(room_id))
        if result is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to send message")

        return ChatHistory(
            user_message=result.user_chat,
            ai_message=result.ai_chat,
            timestamp=result.timestamp
        )
    else:
        async def event_generator():
            full_answer = ""
            async for chunk in stream_send_message_to_qachat(db, user.id, room_id, payload.content):
                full_answer += chunk
                yield f"data: {chunk}\n\n"
        
            result = db_append_chat_message(db, room_id, payload.content, full_answer, get_summary_from_qachat(room_id))
            if result is None:
                print("something went wrong...")
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
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
