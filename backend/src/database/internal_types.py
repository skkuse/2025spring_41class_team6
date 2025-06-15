from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.inspection import inspect
from pydantic import BaseModel, ConfigDict

class UserInfoInternal(BaseModel):
  id: int
  email: str
  nickname: str
  password: str
  created_at: datetime
  model_config = ConfigDict(from_attributes=True)

class ChatRoomInfoInternal(BaseModel):
  id: int
  user_id: int
  character_id: Optional[int]
  title: str
  created_at: datetime
  model_config = ConfigDict(from_attributes=True)

class ChatHistoryInternal(BaseModel):
  id: int
  room_id: int
  user_chat: str
  ai_chat: str
  timestamp: datetime
  model_config = ConfigDict(from_attributes=True)

class PersonInfoInternal(BaseModel):
  id: int
  name: str
  profile_image_path: Optional[str]


class CharacterInfoInternal(BaseModel):
  id: int
  movie_id: int
  name: str
  tone: Optional[str] = None
  description: Optional[str] = None
  actor: Optional[PersonInfoInternal] = None
  model_config = ConfigDict(from_attributes=True)

class MovieInfoInternal(BaseModel):
  id: int
  tmdb_id: int
  title: str
  tmdb_overview: Optional[str]
  wiki_document: Optional[str]
  release_date: Optional[date]
  poster_img_url: Optional[str]
  trailer_img_url: Optional[str]
  last_update: datetime
  genres: List[str] = []
  characters: List[CharacterInfoInternal] = []
  directors: List[PersonInfoInternal] = []
  rating: Optional[int] = None
  bookmarked: Optional[bool] = None
  model_config = ConfigDict(from_attributes=True)

class ChatRoomContext(BaseModel):
  session_id: str
  summary: str