import database.models as m
from common.tmdb_utils import * 
import sqlalchemy as sql
from sqlalchemy import Column
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import wikipedia
import sqlalchemy.dialects.sqlite as sqlite
from typing import List, Optional, cast
from datetime import date, datetime
from sqlalchemy.inspection import inspect
from pydantic import BaseModel

class ChatRoomContext(BaseModel):
  session_id: str
  summary: str

def orm_to_dict(obj):
    if obj is None: return None
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

def get_db():
  """DB Session을 불러옴"""
  db = m.SessionLocal()
  try:
    yield db
  finally:
    db.close()

def update_moviechat_db(data):
  raise NotImplementedError

def db_create_new_user(db: Session, email: str, password: str, nickname: str):
  stmt = sql.select(m.User).where(m.User.email == email)
  res = db.execute(stmt).scalar_one_or_none()
  if res:
    return cast(int, res.id)

  doc = m.User(email=email, password=password, nickname=nickname)
  db.add(doc)
  try:
    db.commit()
    return cast(int, doc.id)
  except:
    db.rollback()
    return None

class UserInfoInternal(BaseModel):
  id: int
  email: str
  nickname: str
  password: str
  created_at: datetime

def db_find_user(db: Session, email: str) -> UserInfoInternal|None:
  """email을 key로 DB에서 user 정보 불러옴"""
  stmt = sql.select(m.User).where(m.User.email == email)
  res = db.execute(stmt).scalar_one_or_none()
  if res is not None:
    # (type: ignore)는 pylance type 검사가 Column[T] -> T로 추론하는 것을 못해서 넣음
    # cast()를 직접적으로 해주는 것에 대한 이득도 딱히 없고 이게 나은 듯
    return UserInfoInternal(
      id = res.id,              # type: ignore
      email=email,
      nickname=res.nickname,    # type: ignore
      password=res.password,    # type: ignore
      created_at=res.created_at # type: ignore
    )
  return None

def db_find_user_by_id(db: Session, id: int) -> UserInfoInternal|None:
  """id를 key로 DB에서 user 정보 불러옴"""
  stmt = sql.select(m.User).where(m.User.id == id)
  res = db.execute(stmt).scalar_one_or_none()
  if res is not None:
    # (type: ignore)는 pylance type 검사가 Column[T] -> T로 추론하는 것을 못해서 넣음
    # cast()를 직접적으로 해주는 것에 대한 이득도 딱히 없고 이게 나은 듯
    return UserInfoInternal(
      id = res.id,              # type: ignore
      email=res.email,          # type: ignore
      nickname=res.nickname,    # type: ignore
      password=res.password,    # type: ignore
      created_at=res.created_at # type: ignore
    )

def db_find_user_with_password(db: Session, email: str, password: str) -> UserInfoInternal|None:
  """email을 key로 DB에서 user 정보를 불러옴 + pw 검사"""
  res = db_find_user(db, email)
  if res is None or res.password != password:
    return None
  return res

class ChatRoomInfoInternal(BaseModel):
  id: int
  user_id: int
  character_id: Optional[int]
  title: str
  created_at: datetime

def db_make_new_chatroom(db: Session, user_id: int) -> ChatRoomInfoInternal | None:
  doc = m.ChatRoom(
    user_id=user_id,
    character_id=None,
    title="new room"
  )
  db.add(doc)
  try:
    db.commit()
    return ChatRoomInfoInternal(
      id = doc.id, # type: ignore
      user_id = doc.user_id, # type: ignore
      character_id = doc.character_id, # type: ignore
      title= doc.title, # type: ignore
      created_at=doc.created_at, # type: ignore
    )
  except:
    db.rollback()
    return None

def db_get_user_chatrooms(db: Session, user_id: int) -> List[ChatRoomInfoInternal]:
  """
  get all chat room information owned by `user_id`.  
  the `user_id` must be valid, since this does not check its validity
  """
  stmt = sql.select(m.ChatRoom).where(m.ChatRoom.user_id == user_id)
  rooms = db.scalars(stmt).all()
  return [ChatRoomInfoInternal(
    id           = room.id, # type: ignore
    user_id      = room.user_id, # type: ignore
    character_id = room.character_id, # type: ignore
    title        = room.title, # type: ignore
    created_at   = room.created_at # type: ignore
  ) for room in rooms]

class ChatHistoryInternal(BaseModel):
  id: int
  room_id: int
  user_chat: str
  ai_chat: str
  timestamp: datetime

def db_append_chat_message(db: Session, room_id: int, usr_msg: str, ai_msg: str, summary: dict) -> ChatHistoryInternal|None:
  import json

  doc = m.ChatHistory(
    room_id=room_id,
    user_chat=usr_msg,
    ai_chat=ai_msg,
  )
  db.add(doc)
  
  print(f"[db_append_chat_message] summary:\n{summary}\n\n")
  try:
    stmt = sql.update(m.ChatRoom).where(m.ChatRoom.id == room_id).values(summary=json.dumps(summary))
    db.execute(stmt)
    db.commit()
    return ChatHistoryInternal(
      id=doc.id,
      room_id=doc.room_id,
      user_chat=doc.user_chat,
      ai_chat=doc.ai_chat,
      timestamp=doc.timestamp
    )
  except:
    db.rollback()
    return None

def db_get_chatroom_context(db: Session, room_id: int) -> ChatRoomContext:
  stmt = sql.select(m.ChatRoom.summary).where(m.ChatRoom.id == room_id)
  result = db.execute(stmt).scalar_one()
  return ChatRoomContext(
    session_id=str(room_id),
    summary=result
  )

def db_update_chatroom_context(db: Session, response: dict, cxt: ChatRoomContext):
  raise NotImplementedError

def db_get_chatroom_history(db: Session, room_id: int):
  raise NotImplementedError

def db_get_bookmarked_movies(db: Session):
  raise NotImplementedError

def db_add_bookmark(db: Session, id: int):
  raise NotImplementedError

def db_rm_bookmark(db: Session, id: int):
  raise NotImplementedError

def db_find_movie_by_id(db: Session, id: int):
  stmt = sql.select(m.Movie).where(m.Movie.id == id)
  movie = db.execute(stmt).scalar_one_or_none()
  return orm_to_dict(movie)

def db_find_movie_by_tmdb_id(db: Session, tmdb_id: int):
  stmt = sql.select(m.Movie).where(m.Movie.tmdb_id == tmdb_id)
  movie = db.execute(stmt).scalar_one_or_none()
  return orm_to_dict(movie)

def db_find_movies_by_tmdb_title(db: Session, title: str):
  stmt = sql.select(m.Movie).where(m.Movie.title == title)
  movies = db.execute(stmt).scalars().all()
  return [orm_to_dict(m) for m in movies]

def db_find_movies_by_alias(db: Session, title: str):
  stmt1= sql.select(m.Movie)\
    .join(m.MovieAlias, m.Movie.id == m.MovieAlias.movie_id)\
    .where(m.MovieAlias.aliased_name == title)
  stmt2 = sql.select(m.Movie).where(m.Movie.title == title)

  union_cte = stmt1.union(stmt2).cte("movie_union")
  stmt = sql.select(m.Movie).join(union_cte, m.Movie.id == union_cte.c.id)

  movies = db.scalars(stmt).all()
  return [orm_to_dict(m) for m in movies]

# flush, commit 안 함
def _upsert_genre(db: Session, genre: str):
  stmt = sql.select(m.Genre).where(m.Genre.name == genre)
  result = db.execute(stmt).scalar_one_or_none()
  if result:
    return result

  doc = m.Genre(name=genre)
  db.add(doc)
  return doc

def _upsert_director(db: Session, director: DirectorInfo):
  stmt = sql.select(m.Director).where(m.Director.tmdb_id == director["person_id"])
  result = db.execute(stmt).scalar_one_or_none()
  if result:
    return result
  
  doc = m.Director(
    tmdb_id = director["person_id"],
    name = director["name"],
    original_name = director["original_name"],
    profile_path = director["profile_path"]
  )
  db.add(doc)
  return doc

def _upsert_platform(db: Session, platform: PlatformInfo):
  stmt = sql.select(m.Platform).where(m.Platform.tmdb_id == platform["tmdb_id"])
  result = db.execute(stmt).scalar_one_or_none()
  if result:
    return result

  doc = m.Platform(
    tmdb_id = platform["tmdb_id"],
    name = platform["name"],
    logo_path = platform["logo_path"]
  )
  db.add(doc)
  return doc

def upsert_movie_with_tmdb(db: Session, tmdb_data: TmdbRequestResult):
  """
  TMDB에서 불러온 영화 정보를 MovieChat DB에 반영합니다  
  DB 반영 실패시 None이 반환되며, 성공시 해당 id가 반환됩니다.
  """
  tmdb_id = tmdb_data["id"]
  stmt0 = sql.select(m.Movie).where(m.Movie.tmdb_id == tmdb_id)
  result = db.execute(stmt0).scalar_one_or_none()
  if result:
    print("updating")
    result.title          = cast(Column[str], tmdb_data["title"])
    result.tmdb_overview  = cast(Column[str], tmdb_data["overview"])
    result.release_date   = cast(Column[date], tmdb_data["release_date"])
    result.poster_img_url = cast(Column[str], tmdb_data["poster_path"])
    db.commit()
    
    stmt1 = sql.delete(m.MovieGenre).where(m.MovieGenre.movie_id == result.id)
    stmt2 = sql.delete(m.MovieDirector).where(m.MovieDirector.movie_id == result.id)
    stmt3 = sql.delete(m.MoviePlatform).where(m.MoviePlatform.movie_id == result.id)
    db.execute(stmt1)
    db.execute(stmt2)
    db.execute(stmt3)
    doc = result
    
  else:
    print("inserting")
    doc = m.Movie(
      tmdb_id=tmdb_id,
      title=tmdb_data["title"],
      tmdb_overview=tmdb_data["overview"],
      release_date=tmdb_data["release_date"],
      poster_img_url=tmdb_data["poster_path"],
    )
    db.add(doc)

  pending_genres = [_upsert_genre(db, i) for i in tmdb_data["genres"]]
  pending_directors = [_upsert_director(db, i) for i in tmdb_data["directors"]]
  pending_platforms = [_upsert_platform(db, i) for i in tmdb_data["platforms"]]
  db.flush()

  movie_id = doc.id
  for g in pending_genres:
    rel = m.MovieGenre(genre_id=g.id, movie_id=movie_id)
    db.add(rel)
  for d in pending_directors:
    rel = m.MovieDirector(director_id=d.id, movie_id=movie_id)
    db.add(rel)
  for p in pending_platforms:
    rel = m.MoviePlatform(platform_id=p.id, movie_id=movie_id)
    db.add(rel)

  try:
    db.commit()
    return movie_id 
  except IntegrityError as e:
    db.rollback()
    print(e)
    return None

def update_movie_by_tmdb_id(db: Session, tmdb_id: int, lang: str = "ko"):
  """
  TMDB의 영화 정보를 MovieChat DB에 반영합니다.  
  성공 시 해당 id를 반환합니다.  
  존재하지 않거나, 실패 시 `None`을 반환합니다
  """
  res = tmdb_request_movie_bulk(identifier={"movie_id": tmdb_id, "lang": lang})
  if res is None:
    return None

  return upsert_movie_with_tmdb(db, res)

def update_movie_by_tmdb_search(db: Session, search: TmdbSearchMovieArgs, lang: str = "ko"):
  """
  TMDB의 영화 정보를 MovieChat DB에 반영합니다.  
  성공 시 해당 id를 반환합니다.  
  존재하지 않거나, 실패 시 `None`을 반환합니다
  """
  res = tmdb_request_movie_bulk(identifier={"search": search, "lang": lang})
  if res is None:
    print("못 찾음...")
    return None
  
  id = upsert_movie_with_tmdb(db, res)
  
  if not (id is None) and search["query"] != res["title"]:
    print(f"[update_movie_by_tmdb_search] alias {search['query']}를 추가합니다")

    doc = m.MovieAlias(movie_id=id, aliased_name=search["query"])
    db.add(doc)
    try:
      db.commit()
    except IntegrityError:
      db.rollback()
    
  return cast(int, id)

# asdf = m.SessionLocal()
# update_movie_by_tmdb_search(asdf, { "query": "기생충" })
# update_movie_by_tmdb_search(asdf, { "query": "마인크래프트 무비" })
# update_movie_by_tmdb_search(asdf, { "query": "마인크래프트" })
# update_movie_by_tmdb_search(asdf, { "query": "아이언맨 3" })
# print(find_movies_by_alias(asdf, "기생충"))
# asdf.close()


def try_find_movies_by_alias(db: Session, fuzzy_title: str):
  # search = tmdb.Search().movie(query=fuzzy_title)
  pass

# 북마킹 기능들
def find_user_bookmarked(db: Session, user_id: int):
  raise NotImplementedError

def bookmark_user_movies(db: Session, user_id: int, movie_id: int):
  doc = m.BookmarkedMovie(movie_id=movie_id, user_id=user_id)
  db.add(doc)
  try:
    db.commit()
    print("log - bookmark_user_movies: success")
    return True
  except IntegrityError as e:
    db.rollback()
    msg = str(e.orig).lower()
    print("error - bookmark_user_movies: IntegrityError")
    print(msg)
    return False
  except Exception:
    db.rollback()
    print("error - bookmark_user_movies: other")
    raise

# 아카이빙 기능들
def find_user_archived(user_id: int):
  raise NotImplementedError

def archive_user_movies(user_id: int, movie_id: int, rating: int):
  raise NotImplementedError