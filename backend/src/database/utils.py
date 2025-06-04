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
  name: str
  tone: str
  description: str
  actor: Optional[PersonInfoInternal] = None

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
  ranking: Optional[int] = None
  model_config = ConfigDict(from_attributes=True)

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

def db_find_user(db: Session, email: str) -> UserInfoInternal|None:
  """email을 key로 DB에서 user 정보 불러옴"""
  stmt = sql.select(m.User).where(m.User.email == email)
  res = db.execute(stmt).scalar_one_or_none()
  if res is not None:
    return UserInfoInternal.model_validate(res)
    # return UserInfoInternal(
    #   id = res.id,              
    #   email=email,
    #   nickname=res.nickname,    
    #   password=res.password,    
    #   created_at=res.created_at 
    # )
  return None

def db_find_user_by_id(db: Session, id: int) -> UserInfoInternal|None:
  """id를 key로 DB에서 user 정보 불러옴"""
  stmt = sql.select(m.User).where(m.User.id == id)
  res = db.execute(stmt).scalar_one_or_none()
  if res is not None:
    return UserInfoInternal.model_validate(res)
    # return UserInfoInternal(
    #   id = res.id,              
    #   email=res.email,          
    #   nickname=res.nickname,    
    #   password=res.password,    
    #   created_at=res.created_at 
    # )

def db_find_user_with_password(db: Session, email: str, password: str) -> UserInfoInternal|None:
  """email을 key로 DB에서 user 정보를 불러옴 + pw 검사"""
  res = db_find_user(db, email)
  if res is None or res.password != password:
    return None
  return res

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
      id = doc.id, 
      user_id = doc.user_id, 
      character_id = doc.character_id, 
      title= doc.title, 
      created_at=doc.created_at, 
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
    id           = room.id, 
    user_id      = room.user_id, 
    character_id = room.character_id, 
    title        = room.title, 
    created_at   = room.created_at 
  ) for room in rooms]

def db_delete_user_chatroom(db: Session, room_id: int, user_id: int) -> bool:
  """
  delete user chatroom from the database
  the `user_id` must own the `room_id`.  
  Otherwise, this function fails. (it does nothing when it fails)
  """
  stmt = (
    sql.delete(m.ChatRoom)
    .where(m.ChatRoom.user_id == user_id)
    .where(m.ChatRoom.id == room_id)
  )

  db.execute(stmt)
  try:
    db.commit()
    return True
  except:
    db.rollback()
    return False


def db_get_chat_messages(db: Session, user_id: int, room_id: int) -> List[ChatHistoryInternal]:
  """
  get all chat histories in ChatRoom `room_id`. If the owner does not match the user information,
  it returns an empty list.
  """
  stmt = (
    sql.select(m.ChatHistory)
    .join(m.ChatRoom, m.ChatHistory.room_id == m.ChatRoom.id)
    .where(m.ChatHistory.room_id == room_id)
    .where(m.ChatRoom.user_id == user_id)
  )
  result = db.execute(stmt).scalars().all()
  return [ChatHistoryInternal(
    id = chat.id,
    room_id = chat.room_id,
    user_chat = chat.user_chat,
    ai_chat = chat.ai_chat,
    timestamp = chat.timestamp
  ) for chat in result]



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

def db_get_bookmarked_movies(db: Session):
  raise NotImplementedError

def db_add_bookmark(db: Session, id: int):
  raise NotImplementedError

def db_rm_bookmark(db: Session, id: int):
  raise NotImplementedError

def db_find_movie_by_id(db: Session, id: int, verbose: bool = True) -> MovieInfoInternal|None:
  stmt = sql.select(m.Movie).where(m.Movie.id == id)
  movie = db.execute(stmt).scalar_one_or_none()
  if movie is None:
    return None
  
  genres = []
  directors = []
  characters = []
  if verbose:
    stmt_genre = sql.select(m.Genre).join(m.MovieGenre, m.Genre.id == m.MovieGenre.genre_id).where(m.MovieGenre.movie_id == id)
    stmt_director = sql.select(m.Director).join(m.MovieDirector, m.Director.id == m.MovieDirector.director_id).where(m.MovieDirector.movie_id == id)
    stmt_chara = sql.select(m.CharacterProfile, m.Actor).where(m.CharacterProfile.movie_id == id).outerjoin(m.Actor, m.CharacterProfile.actor_id == m.Actor.id)

    genres = [i.name for i in db.scalars(stmt_genre).all()]
    directors = [PersonInfoInternal(id = i.id, name = i.name, profile_image_path=i.profile_path) for i in db.scalars(stmt_director).all()]
    characters = [CharacterInfoInternal(
      id = character.id,
      name = character.name,
      tone = character.tone,
      description = character.description,
      actor = PersonInfoInternal(id = actor.id, name = actor.name, profile_image_path = actor.profile_path) if actor is not None else None
    ) for character, actor in db.execute(stmt_chara).all()]

  return MovieInfoInternal(
    id=movie.id,
    tmdb_id=cast(int, movie.tmdb_id),
    title=movie.title,
    tmdb_overview=movie.tmdb_overview,
    wiki_document=movie.wiki_document,
    release_date=movie.release_date,
    poster_img_url=movie.poster_img_url,
    trailer_img_url=movie.trailer_img_url,
    last_update=movie.last_update,
    genres=genres,
    directors=directors,
    characters=characters
  )

def db_find_movie_by_tmdb_id(db: Session, tmdb_id: int):
  stmt = sql.select(m.Movie).where(m.Movie.tmdb_id == tmdb_id)
  movie = db.execute(stmt).scalar_one_or_none()
  return orm_to_dict(movie)

def db_find_movies_by_tmdb_title(db: Session, title: str):
  stmt = sql.select(m.Movie).where(m.Movie.title == title)
  movies = db.execute(stmt).scalars().all()
  return [orm_to_dict(m) for m in movies]

def db_find_movies_by_alias(db: Session, title: str) -> List[MovieInfoInternal]:
  stmt1= sql.select(m.Movie)\
    .join(m.MovieAlias, m.Movie.id == m.MovieAlias.movie_id)\
    .where(m.MovieAlias.aliased_name == title)
  stmt2 = sql.select(m.Movie).where(m.Movie.title == title)

  union_cte = stmt1.union(stmt2).cte("movie_union")
  stmt = sql.select(m.Movie).join(union_cte, m.Movie.id == union_cte.c.id)

  movies = db.scalars(stmt).all()
  return [MovieInfoInternal.model_validate(movie) for movie in movies]

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
  stmt = sql.select(m.Director).where(m.Director.tmdb_id == director.person_id)
  result = db.execute(stmt).scalar_one_or_none()
  if result:
    return result
  
  doc = m.Director(
    tmdb_id = director.person_id,
    name = director.name,
    original_name = director.original_name,
    profile_path = director.profile_path
  )
  db.add(doc)
  return doc

def _upsert_actor(db: Session, actor: ActorInfo):
  stmt = sql.select(m.Actor).where(m.Actor.tmdb_id == actor.person_id)
  result = db.execute(stmt).scalar_one_or_none()
  if result:
    return result
  
  doc = m.Actor(
    tmdb_id = actor.person_id,
    name = actor.name,
    original_name = actor.original_name,
    profile_path = actor.profile_path
  )
  db.add(doc)
  return doc

def _upsert_platform(db: Session, platform: PlatformInfo):
  stmt = sql.select(m.Platform).where(m.Platform.tmdb_id == platform.tmdb_id)
  result = db.execute(stmt).scalar_one_or_none()
  if result:
    return result

  doc = m.Platform(
    tmdb_id = platform.tmdb_id,
    name = platform.name,
    logo_path = platform.logo_path,
  )
  db.add(doc)
  return doc

def upsert_movie_with_tmdb(db: Session, tmdb_data: TmdbRequestResult):
  """
  TMDB에서 불러온 영화 정보를 MovieChat DB에 반영합니다  
  DB 반영 실패시 None이 반환되며, 성공시 해당 영화 정보가 반환됩니다.
  """
  tmdb_id = tmdb_data.id
  stmt0 = sql.select(m.Movie).where(m.Movie.tmdb_id == tmdb_id)
  result = db.execute(stmt0).scalar_one_or_none()
  if result:
    print("updating")
    result.title          = tmdb_data.title
    result.tmdb_overview  = tmdb_data.overview
    result.release_date   = tmdb_data.release_date
    result.poster_img_url = tmdb_data.poster_path
    db.commit()
    
    stmt1 = sql.delete(m.MovieGenre).where(m.MovieGenre.movie_id == result.id)
    stmt2 = sql.delete(m.MovieDirector).where(m.MovieDirector.movie_id == result.id)
    stmt3 = sql.delete(m.MoviePlatform).where(m.MoviePlatform.movie_id == result.id)
    stmt4 = sql.delete(m.MovieActor).where(m.MovieActor.movie_id == result.id)
    db.execute(stmt1)
    db.execute(stmt2)
    db.execute(stmt3)
    db.execute(stmt4)
    doc = result
    
  else:
    print("inserting")
    doc = m.Movie(
      tmdb_id=tmdb_id,
      title=tmdb_data.title,
      tmdb_overview=tmdb_data.overview,
      release_date=tmdb_data.release_date,
      poster_img_url=tmdb_data.poster_path,
    )
    db.add(doc)

  pending_genres = [_upsert_genre(db, i) for i in tmdb_data.genres]
  pending_directors = [_upsert_director(db, i) for i in tmdb_data.directors]
  pending_platforms = [_upsert_platform(db, i) for i in tmdb_data.platforms]
  
  pending_actors = [(_upsert_actor(db, i), idx) for idx, i in enumerate(tmdb_data.casts)]
  db.flush()

  # 캐릭터를 추가함 (begin)
  for a, i in pending_actors:
    cast_info = tmdb_data.casts[i]
    ch = m.CharacterProfile(
      movie_id = doc.id,
      name = cast_info.character,
      description = "",
      tone = "",
      actor_id = a.id
    )
    db.add(ch)
  # 캐릭터를 추가함 (end)

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
  for a, _ in pending_actors:
    rel = m.MovieActor(actor_id=a.id, movie_id=movie_id)
    db.add(rel)

  try:
    db.commit()
    return MovieInfoInternal.model_validate(doc)
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
  if len(res) == 0:
    return None

  return upsert_movie_with_tmdb(db, res[0])

def update_movie_by_tmdb_search(db: Session, search: TmdbSearchMovieArgs, lang: str = "ko"):
  """
  TMDB의 영화 정보를 MovieChat DB에 반영합니다.  
  db 반영에 성공한 영화 정보들의 list를 반환합니다.
  query로 들어온 영화 제목이 '정식' title과 일치하지 않으면 alias로 등록됩니다.
  """
  datas : List[MovieInfoInternal]= []

  res = tmdb_request_movie_bulk(identifier={"search": search, "lang": lang})
  if len(res) == 0:
    print(f"[update_movie_by_tmdb_search] {search}에 대한 영화를 TMDB에서 찾을 수 없음")
    return datas
  
  for movie in res:
    data = upsert_movie_with_tmdb(db, movie)
    if data is None:
      continue
    
    datas.append(data)

    possible_alias = search["query"]
    if possible_alias != movie.title:
      print(f"[update_movie_by_tmdb_search] {movie.title}의 다른 이름 {possible_alias}(을)를 추가합니다")

      doc = m.MovieAlias(movie_id=data.id, aliased_name=possible_alias)
      db.add(doc)
      try:
        db.commit()
      except IntegrityError as e:
        # 동시 다발적으로 동일한 alias를 추가하는 상황에서 발생할 수도 있는데,
        # 이 경우는 단순히 rollback 해주면 됨.
        print(f"[update_movie_by_tmdb_search] 경고: IntegrityError {e}")
        db.rollback()
    
  return datas

def db_update_wikipedia_data(db: Session, id: int, wiki_data: str):
  stmt = (
    sql.update(m.Movie).where(m.Movie.id == id)
    .values(wiki_document=wiki_data)
  )
  db.execute(stmt)
  try:
    db.commit()
    return True
  except:
    db.rollback()
    return False

def db_get_movie_reviews(db: Session, id: int, limit: int|None) -> list[str]:
  if limit:
    stmt = (
      sql.select(m.MovieReview.text)
      .where(m.MovieReview.id == id)
      .limit(limit)
    )
  else:
    stmt = (
      sql.select(m.MovieReview.text)
      .where(m.MovieReview.id == id)
    )

  return [i for i in db.execute(stmt).scalars().all()]

def db_add_movie_reviews(db: Session, id: int, reviews: list[str]):
  for i in reviews:
    doc = m.MovieReview(movie_id = id, text = i)
    db.add(doc)
  
  try:
    db.commit()
    return True
  except:
    db.rollback()
    return False

# asdf = m.SessionLocal()
# update_movie_by_tmdb_search(asdf, { "query": "기생충" })
# update_movie_by_tmdb_search(asdf, { "query": "마인크래프트 무비" })
# update_movie_by_tmdb_search(asdf, { "query": "마인크래프트" })
# update_movie_by_tmdb_search(asdf, { "query": "아이언맨 3" })
# print(find_movies_by_alias(asdf, "기생충"))
# asdf.close()

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