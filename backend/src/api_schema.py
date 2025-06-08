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
    character_id: Optional[int] = None

class CreateChatroomResponse(BaseModel):
    id: int
    title: str
    chats: List[ChatHistory]

class ChatroomIDRequest(BaseModel):
    id: int

class DeleteChatroomResponse(BaseModel):
    id: int

class MessageRequest(BaseModel):
    content: str

# 영화 관련 모델
class Person(BaseModel):
    id: int
    name: str
    profile_image: str

class Character(BaseModel):
    id: int
    name: str
    actor: Optional[Person]

class Movie(BaseModel):
    id: int
    title: str
    overview: str
    wiki_document: str
    release_date: str
    poster_img_url: str
    trailer_img_url: str
    rating: Optional[int] = None # 유저 필드
    bookmarked: bool = False # 유저 필드
    ordering: int = 0
    genres: List[str] = []
    characters: List[Character] = []
    directors: List[Person] = []

class MovieIDRequest(BaseModel):
    id: int

class ArchiveRequest(BaseModel):
    movie_id: int
    rating: int

from database.utils import MovieInfoInternal, PersonInfoInternal, CharacterInfoInternal
def public_movie_info(internal: MovieInfoInternal) -> Movie:
    from common.tmdb_utils import tmdb_full_image_path, ImgType

    movie = internal

    return Movie(
        id=movie.id,
        title=movie.title,
        overview=movie.tmdb_overview                             if movie.tmdb_overview else "[TMDB 줄거리 없음]",
        wiki_document=movie.wiki_document                        if movie.wiki_document else "[WIKIPEDIA 정보 없음]",
        release_date=str(movie.release_date)                     if movie.release_date else "[방영일 정보 없음]",
        poster_img_url=tmdb_full_image_path(movie.poster_img_url, ImgType.POSTER, None)  if movie.poster_img_url  else "",
        trailer_img_url=tmdb_full_image_path(movie.trailer_img_url, ImgType.STILL, None) if movie.trailer_img_url else "",
        bookmarked=movie.bookmarked                                                      if movie.bookmarked is not None else False,
        rating = movie.rating,
        ordering = 0,
        genres = movie.genres,
        characters = [public_character_info(chara) for chara in movie.characters],
        directors = [public_person_info(crew) for crew in movie.directors]
    )

def public_person_info(internal: PersonInfoInternal) -> Person:
    from common.tmdb_utils import tmdb_full_image_path, ImgType

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