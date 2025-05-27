from typing import cast
from sqlalchemy import event, Column, ForeignKey, Integer, String, Date, DateTime, create_engine
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import expression
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from sqlalchemy.orm.attributes import flag_modified
from common.env import ENV_PROJECT_ROOT

# SQLite 경로 지정 (상대경로 or 절대경로)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{ENV_PROJECT_ROOT}/backend/database/moviechat.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

@event.listens_for(Engine, "connect")
def enable_sqlite_fk_constraints(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def current_time():
    return datetime.now(timezone.utc)

# TABLE 이름(요구사항 명세서_6조.pdf p. 18 참조)
TABLE_USER              = "users"
TABLE_MOVIE             = "movies"
TABLE_BOOKMARKED_MOVIE  = "bookmarked_movies"
TABLE_ARCHIVED_MOVIE    = "archived_movies"
TABLE_CHAT_ROOM         = "chat_rooms"
TABLE_CHAT_HISTORY      = "chat_history"
TABLE_CHARACTER_PROFILE = "character_profiles"
TABLE_DIRECTOR          = "directors"
TABLE_GENRE             = "genres"
TABLE_ACTOR             = "actors"
TABLE_PLATFORM          = "platforms"
TABLE_MOVIE_ALIAS       = "movie_aliases"
REL_MOVIE_GENRE         = "rel_movie_genres"
REL_MOVIE_ACTOR         = "rel_movie_actors"
REL_MOVIE_PLATFORM      = "rel_movie_platforms"
REL_MOVIE_DIRECTOR      = "rel_movie_directors"

def fk(tablename: str) -> str: return f"{tablename}.id"

class User(Base):
    __tablename__ = TABLE_USER
    id         = Column(Integer,  primary_key=True, index=True, autoincrement=True)
    email      = Column(String,   nullable=False,   unique=True)
    password   = Column(String,   nullable=False)
    nickname   = Column(String,   nullable=False)
    created_at = Column(DateTime(timezone=True), default=current_time)

class Movie(Base):
    __tablename__ = TABLE_MOVIE
    id              = Column(Integer,  primary_key=True, index=True, autoincrement=True)
    tmdb_id         = Column(Integer,  unique=True, nullable=True)
    title           = Column(String,   nullable=False)
    tmdb_overview   = Column(String,   nullable=True)
    wiki_document   = Column(String,   nullable=True)
    release_date    = Column(Date)
    poster_img_url  = Column(String)
    trailer_img_url = Column(String)

    # 업데이트 시각(자동 갱신됨)
    last_update = Column(DateTime(timezone=True), default=current_time, nullable=False)

@event.listens_for(Movie, "before_update", propagate=True)
def auto_update_last_modified(mapper, connection, target: Movie):
    target.last_update = current_time()
    flag_modified(target, "last_update")

class BookmarkedMovie(Base):
    """
    Args:
      movie_id: int  
        DB 상의 Movie ID
        (TMDBID 아님)
      user_id: int  
        DB 상의 User ID  
        (email 아님)
    """
    __tablename__ = TABLE_BOOKMARKED_MOVIE
    movie_id      = Column(Integer, ForeignKey(fk(TABLE_MOVIE)), primary_key=True)
    user_id       = Column(Integer, ForeignKey(fk(TABLE_USER)),  primary_key=True)
    created_at    = Column(DateTime(timezone=True), default=current_time)
    
class ArchivedMovie(Base):
    __tablename__ = TABLE_ARCHIVED_MOVIE
    movie_id      = Column(Integer, ForeignKey(fk(TABLE_MOVIE)), primary_key=True)
    user_id       = Column(Integer, ForeignKey(fk(TABLE_USER)),  primary_key=True)
    rating        = Column(Integer, nullable=False)
    created_at    = Column(DateTime(timezone=True), default=current_time)
    
class Director(Base):
    __tablename__ = TABLE_DIRECTOR
    id   = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_id = Column(Integer, unique=True, nullable=False)
    name = Column(String,  nullable=False)
    original_name = Column(String, nullable=False)
    profile_path = Column(String)
    
class ChatRoom(Base):
    __tablename__ = TABLE_CHAT_ROOM
    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey(fk(TABLE_USER)), nullable=False)
    character_id  = Column(Integer, ForeignKey(fk(TABLE_CHARACTER_PROFILE)))
    title         = Column(String, nullable=False)
    created_at    = Column(DateTime(timezone=True), default=current_time)
    
class ChatHistory(Base):
    __tablename__ = TABLE_CHAT_HISTORY
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id   = Column(Integer, ForeignKey(fk(TABLE_CHAT_ROOM)))
    ai_chat   = Column(String, nullable=False) # message => ai_chat   ; refactored. AI 응답과 user 요청을 하나로 두는게 더 simple하다
    user_chat = Column(String, nullable=False) # message => user_chat ;
    timestamp = Column(DateTime(timezone=True), nullable=False, default=current_time)
    
class CharacterProfile(Base):
    __tablename__ = TABLE_CHARACTER_PROFILE
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movie_id       = Column(Integer, ForeignKey(fk(TABLE_MOVIE)), nullable=False)
    name           = Column(String, nullable=False)
    description    = Column(String, nullable=False)
    tone           = Column(String, nullable=False)
    other_features = Column(String, nullable=True)
    
class Genre(Base):
    __tablename__ = TABLE_GENRE
    id   = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    
class Actor(Base):
    __tablename__ = TABLE_ACTOR
    id   = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Platform(Base):
    __tablename__ = TABLE_PLATFORM
    id   = Column(Integer, primary_key=True, autoincrement=True)
    tmdb_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    logo_path = Column(String)

class MovieAlias(Base):
    __tablename__ = TABLE_MOVIE_ALIAS
    movie_id = Column(Integer, ForeignKey(fk(TABLE_MOVIE)), nullable=False, primary_key=True)
    aliased_name = Column(String, nullable=False, primary_key=True)

class MovieGenre(Base):
    __tablename__ = REL_MOVIE_GENRE
    movie_id = Column(Integer, ForeignKey(fk(TABLE_MOVIE)), primary_key=True, nullable=False)
    genre_id = Column(Integer, ForeignKey(fk(TABLE_GENRE)), primary_key=True, nullable=False)

class MovieActor(Base):
    __tablename__ = REL_MOVIE_ACTOR
    movie_id = Column(Integer, ForeignKey(fk(TABLE_MOVIE)), primary_key=True, nullable=False)
    actor_id = Column(Integer, ForeignKey(fk(TABLE_ACTOR)), primary_key=True, nullable=False)

class MoviePlatform(Base):
    __tablename__ = REL_MOVIE_PLATFORM
    movie_id    = Column(Integer, ForeignKey(fk(TABLE_MOVIE)),    primary_key=True, nullable=False)
    platform_id = Column(Integer, ForeignKey(fk(TABLE_PLATFORM)), primary_key=True, nullable=False)

class MovieDirector(Base):
    __tablename__ = REL_MOVIE_DIRECTOR
    movie_id    = Column(Integer, ForeignKey(fk(TABLE_MOVIE)),    primary_key=True, nullable=False)
    director_id = Column(Integer, ForeignKey(fk(TABLE_DIRECTOR)), primary_key=True, nullable=False)

Base.metadata.create_all(bind=engine)
