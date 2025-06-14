from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, Request, status
from fastapi.responses import StreamingResponse
from api_schema import *
from database.utils import *
from auth import validate_user
from sse import *
import asyncio

router = APIRouter(prefix="/api/chatrooms", tags=["chatroom"])

@router.get("", response_model=ChatRoomList)
async def get_chatrooms(user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
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


@router.post("", response_model=CreateChatroomResponse)
async def create_chatroom(payload: CreateChatroomRequest,
                          user: UserInfoInternal = Depends(validate_user),
                          db: Session = Depends(get_db)):
    from llm_layer import stream_create_character
    
    room = db_make_new_chatroom(db, user.id)
    if room is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to create chatroom")

    if not payload.character_id:
        # client wants to talk to plain AI
        chats = []
        return CreateChatroomResponse(
            id = room.id,
            title = room.title,
            chats = chats
        )
    else:
        # we create/prepare character for this chat room
        character_id = payload.character_id
        profile = db_get_character_profile_by_id(db, character_id)
        if profile is None:
            # client did something dumb
            db_delete_user_chatroom(db, room.id, user.id)
            raise HTTPException(status.HTTP_404_NOT_FOUND, "character not found")

        # now we're sure that room and character exists
        title = f"{profile.name} 님과 대화"
        db_change_chatroom_immersive(db, room.id, character_id, title)

        # since creating character takes looong time, we use SSE here
        async def event_generator():
            ccr = CreateChatroomResponse(id = room.id, title = title, chats = [])
            yield sse_to_string(make_sse(SSE_CHATROOM, ccr.model_dump()))

            async for chunk in stream_create_character(db, room.id, character_id):
                yield sse_to_string(chunk)
                await asyncio.sleep(0) # 버퍼링 방지

                if sse_type(chunk) == SSE_SIGNAL and sse_content(chunk) == SSE_CC_FAIL:
                    # something oof happened
                    db_delete_user_chatroom(db, room.id, user.id)
                    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "failed to create character")

            # finish our SSE message
            yield sse_to_string(make_sse(SSE_SIGNAL, SSE_FINISH))

        return StreamingResponse(
            event_generator(),
        )

@router.delete("", response_model=DeleteChatroomResponse)
async def delete_chatroom(payload: ChatroomIDRequest,
                          user: UserInfoInternal = Depends(validate_user),
                          db: Session = Depends(get_db)):
    if db_delete_user_chatroom(db, payload.id, user.id):
        return DeleteChatroomResponse(id=payload.id)
    else:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="db removal failed")

# ---------------------------
# /chatrooms/{room_id}/recommended
# ---------------------------
@router.get("/{room_id}/recommended", response_model=List[List[Movie]])
async def get_recommended(room_id: int, user: UserInfoInternal = Depends(validate_user), db: Session = Depends(get_db)):
    list_of_movies = db_get_recommended_movies(db, room_id)
    return [[public_movie_info(movie) for movie in movies] for movies in list_of_movies]

# ---------------------------
# /chatrooms/{room_id}/messages
# ---------------------------
@router.get("/{room_id}/messages", response_model=List[ChatHistory])
async def get_messages(room_id: int,
                       user: UserInfoInternal = Depends(validate_user),
                       db: Session = Depends(get_db)):
    chats = db_get_chat_messages(db, user.id, room_id)
    return [ChatHistory(
        user_message=chat.user_chat,
        ai_message=chat.ai_chat,
        timestamp=chat.timestamp
    ) for chat in chats]

@router.post("/{room_id}/messages", response_model=ChatHistory, response_description="""
`room_id`의 대화방에 메시지를 보낸 뒤, 그 응답을 ChatHistory의 형태로 불러옵니다.  
만약 stream=true 라면, text/event-stream 형식으로 스트리밍됩니다. 프론트에서 유의해서 작업해주세요
""")
async def post_message(room_id: int,
                       payload: MessageRequest = Body(...),
                       stream: bool = Query(False, description="true 시 SSE를 통한 스트리밍 응답"),
                       user: UserInfoInternal= Depends(validate_user),
                       db: Session = Depends(get_db)):
    from llm_layer import send_message_to_ai, stream_send_message_to_ai, get_current_summary
    import llm.tools, json
    
    room = db_get_chatroom(db, room_id)
    if not stream:
        result = await send_message_to_ai(db, user.id, room_id, payload.content)
        response = result["message"]
        result = db_append_chat_message(db, room_id, payload.content, response, get_current_summary(room))
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
            async for chunk in stream_send_message_to_ai(db, user.id, room_id, payload.content):
                t = sse_type(chunk)
                v = sse_content(chunk)
                if t == SSE_MESSAGE:
                    full_answer += cast(str, v)
                elif t == SSE_RECOMMEND:
                    recommended = cast(list[int], v)

                yield f"data: {json.dumps(chunk)}\n\n"

                # 버퍼링 방지
                await asyncio.sleep(0)

            if db_get_chatroom_name(db, room_id) == "new room":
                new_title = llm.tools.generate_chat_title(full_answer)
                if db_update_chatroom_name(db, room_id, new_title):
                    yield f"data: {json.dumps(make_sse(SSE_ROOM_TITLE, new_title))}\n\n"

            result = db_append_chat_message(db, room_id, payload.content, full_answer, get_current_summary(room))

            if result is None:
                print("something went wrong...")
            elif recommended:
                db_add_recommended_movies(db, result.id, recommended)
            yield f"data: {json.dumps(make_sse(SSE_SIGNAL, SSE_FINISH))}\n\n"

        return StreamingResponse(
            event_generator(),
        )
