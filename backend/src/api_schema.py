from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 채팅방 관련 모델
class ChatRoom(BaseModel):
    id: int
    title: str

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
