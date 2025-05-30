from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

import sys
if sys.version_info < (3, 11):
  from typing_extensions import TypedDict, Required, NotRequired
else:
  from typing import TypedDict, Required, NotRequired

# 사용자 관련 모델
class RegisterRequest(BaseModel):
    email: str
    password: str
    nickname: str
    login: Optional[bool] = Field(default=False, description="true로 설정하면 User 생성 후 바로 login 됩니다")

class UserInfoResponse(BaseModel):
    id: int
    email: str
    nickname: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

# 채팅방 관련 모델
class ChatRoom(BaseModel):
    id: int
    title: str

class ChatRoomList(BaseModel):
    normal: List[ChatRoom]
    immersive: List[ChatRoom]

class ChatHistory(BaseModel):
    user_message: str
    ai_message: str
    timestamp: datetime

class CreateChatroomRequest(BaseModel):
    initial_message: Optional[str] = ""

class CreateChatroomResponse(BaseModel):
    id: int
    title: str
    chats: List[ChatHistory]

class MessageRequest(BaseModel):
    content: str

# 영화 관련 모델
class Movie(BaseModel):
    id: int
    title: str
    overview: str
    wiki_document: str
    release_date: str
    poster_img_url: str
    trailer_img_url: str
    rating: int = 0
    ordering: int = 0
    ranking: Optional[int] = None  # archive 용

class MovieIDRequest(BaseModel):
    id: int

class ArchiveRequest(MovieIDRequest):
    ranking: int
