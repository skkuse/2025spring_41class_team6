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
import json

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

@app.get("/api/test")
async def test():
    import llm.qachat as qachat
    print(qachat.session_memories)


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
    result = await send_message_to_qachat(db, user.id, room.id, payload.initial_message)
    response = result["message"]
    recommended = result["recommendation"]
    result = db_append_chat_message(db, room.id, payload.initial_message, response, get_summary_from_qachat(room.id))
    if result is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to send message")
    else:
        db_add_recommended_movies(db, result.id, recommended)
    
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

@app.delete("/api/chatrooms", response_model=DeleteChatroomResponse)
async def delete_chatroom(payload: ChatroomIDRequest,
                          user: UserInfoInternal = Depends(find_user_by_id),
                          db: Session = Depends(get_db)):
    if db_delete_user_chatroom(db, payload.id, user.id):
        return DeleteChatroomResponse(id=payload.id)
    else:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="db removal failed")

# ---------------------------
# /chatrooms/{room_id}/recommended
# ---------------------------
@app.get("/api/chatrooms/{room_id}/recommended", response_model=List[List[Movie]])
async def get_recommended(room_id: int, user: UserInfoInternal = Depends(find_user_by_id), db: Session = Depends(get_db)):
    list_of_movies = db_get_recommended_movies(db, room_id)
    return [[public_movie_info(movie) for movie in movies] for movies in list_of_movies]

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
        result = await send_message_to_qachat(db, user.id, room_id, payload.content)
        response = result["messages"]
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
            recommended = []
            async for chunk in stream_send_message_to_qachat(db, user.id, room_id, payload.content):
                t = chunk.get("type")
                v = chunk.get("content")
                if t == "message":
                    full_answer += cast(str, v)
                elif t == "recommendation":
                    recommended = cast(list[int], v)

                yield f"data: {json.dumps(chunk)}\n\n"

                # 버퍼링 방지
                await asyncio.sleep(0)

            result = db_append_chat_message(db, room_id, payload.content, full_answer, get_summary_from_qachat(room_id))
            if result is None:
                print("something went wrong...")
            else:
              db_add_recommended_movies(db, result.id, recommended)

        return StreamingResponse(
            event_generator(),
        )



# ---------------------------
# /movies/bookmarked
# ---------------------------
@app.get("/api/movies/bookmarked", response_model=List[Movie])
async def get_bookmarked(user: UserInfoInternal = Depends(find_user_by_id), db: Session = Depends(get_db)):
    movies = db_get_bookmarked_movies(db, user.id)
    return [public_movie_info(movie) for movie in movies]

@app.post("/api/movies/bookmarked", response_model=Movie)
async def post_bookmark(payload: MovieIDRequest, user: UserInfoInternal = Depends(find_user_by_id), db: Session = Depends(get_db)):
    if db_add_bookmark(db, user.id, payload.id):
        return public_movie_info(
            cast( MovieInfoInternal, db_find_movie_by_id(db, payload.id, True) )
        )
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")


@app.delete("/api/movies/bookmarked", response_model=Movie)
async def delete_bookmark(payload: MovieIDRequest, user: UserInfoInternal = Depends(find_user_by_id), db: Session = Depends(get_db)):
    movie = db_find_movie_by_id(db, payload.id, True)

    if movie and db_rm_bookmark(db, user.id, payload.id):
        return public_movie_info(movie)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")

# ---------------------------
# /movies/archive
# ---------------------------
@app.get("/api/movies/archive", response_model=List[Movie])
async def get_archive(user: UserInfoInternal = Depends(find_user_by_id), db: Session = Depends(get_db)):
    movies = db_get_archived_movies(db, user.id)
    return [public_movie_info(movie) for movie in movies]


@app.post("/api/movies/archive", response_model=Movie)
async def post_archive(payload: ArchiveRequest, user: UserInfoInternal = Depends(find_user_by_id), db: Session = Depends(get_db)):
    if db_add_archived(db, user.id, payload.movie_id, payload.rating):
        ret = public_movie_info(
            cast( MovieInfoInternal, db_find_movie_by_id(db, payload.movie_id, True) )
        )
        ret.rating = min(5, max(0, payload.rating))
        return ret
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")


@app.put("/api/movies/archive", response_model=Movie)
async def update_archive(payload: ArchiveRequest, user: UserInfoInternal = Depends(find_user_by_id), db: Session = Depends(get_db)):
    if db_update_archived(db, user.id, payload.movie_id, payload.rating):
        ret = public_movie_info(
            cast( MovieInfoInternal, db_find_movie_by_id(db, payload.movie_id, True) )
        )
        ret.rating = min(5, max(0, payload.rating))
        return ret
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")


@app.delete("/api/movies/archive", response_model=Movie)
async def delete_archive(payload: MovieIDRequest, user: UserInfoInternal = Depends(find_user_by_id), db: Session = Depends(get_db)):
    movie = db_find_movie_by_id(db, payload.id, True)
    if movie and db_rm_archived(db, user.id, payload.id):
        return public_movie_info(movie)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="bad request")


# ---------------------------
# /movies/{id}
# ---------------------------
@app.get("/api/movies/{id}", response_model=Movie)
async def get_movie(id: int = Path(...), verbose: bool = Query(True), db: Session = Depends(get_db)):
    movie = db_find_movie_by_id(db, id, verbose)
    if movie is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="영화가 없습니다.")

    return public_movie_info(movie)


def public_movie_info(internal: MovieInfoInternal) -> Movie:
    movie = internal

    return Movie(
        id=movie.id,
        title=movie.title,
        overview=movie.tmdb_overview                             if movie.tmdb_overview else "[TMDB 줄거리 없음]",
        wiki_document=movie.wiki_document                        if movie.wiki_document else "[WIKIPEDIA 정보 없음]",
        release_date=str(movie.release_date)                     if movie.release_date else "[방영일 정보 없음]",
        poster_img_url=tmdb_full_image_path(movie.poster_img_url, ImgType.POSTER, None)  if movie.poster_img_url  else "",
        trailer_img_url=tmdb_full_image_path(movie.trailer_img_url, ImgType.STILL, None) if movie.trailer_img_url else "",
        rating = movie.rating                                                            if movie.rating else 0,
        ordering = 0,
        genres = movie.genres,
        characters = [public_character_info(chara) for chara in movie.characters],
        directors = [public_person_info(crew) for crew in movie.directors]
    )

def public_person_info(internal: PersonInfoInternal) -> Person:
    return Person(
        id = internal.id,
        name = internal.name,
        profile_image = tmdb_full_image_path(
            internal.profile_image_path,
            ImgType.PROFILE,
            None) if internal.profile_image_path else ""
    )


def public_character_info(internal: CharacterInfoInternal) -> Character:
    return Character(
        id = internal.id,
        name = internal.name,
        actor = public_person_info(internal.actor) if internal.actor else None
    )
