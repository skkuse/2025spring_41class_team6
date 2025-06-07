from typing import cast, Optional
from sqlalchemy import event, ForeignKey, Integer, String, Date, DateTime, create_engine
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import expression
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from datetime import date, datetime, timezone
from sqlalchemy.orm.attributes import flag_modified
from common.env import ENV_BACKEND_ROOT

# SQLite 경로 지정 (상대경로 or 전복로)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{ENV_BACKEND_ROOT}/src/database/moviechat.db"

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

# TABLE 이름(요구사항 명세서_6조.pdf p. 18 참고)
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
TABLE_MOVIE_REVIEW      = "movie_reviews"
TABLE_RECOMMENDED_MOVIE = "recommended_movies"
REL_MOVIE_GENRE         = "rel_movie_genres"
REL_MOVIE_ACTOR         = "rel_movie_actors"
REL_MOVIE_PLATFORM      = "rel_movie_platforms"
REL_MOVIE_DIRECTOR      = "rel_movie_directors"

def fk(tablename: str) -> str: return f"{tablename}.id"

class User(Base):
    __tablename__ = TABLE_USER
    id         : Mapped[int]      = mapped_column(primary_key=True, index=True, autoincrement=True)
    email      : Mapped[str]      = mapped_column(nullable=False,   unique=True)
    password   : Mapped[str]      = mapped_column(nullable=False)
    nickname   : Mapped[str]      = mapped_column(nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=current_time)

class Movie(Base):
    __tablename__ = TABLE_MOVIE
    id              : Mapped[int]           = mapped_column(primary_key=True, index=True, autoincrement=True)
    tmdb_id         : Mapped[Optional[int]] = mapped_column(unique=True, nullable=True)
    title           : Mapped[str]           = mapped_column(nullable=False)
    tmdb_overview   : Mapped[Optional[str]]
    wiki_document   : Mapped[Optional[str]]
    release_date    : Mapped[Optional[date]]
    poster_img_url  : Mapped[Optional[str]]
    trailer_img_url : Mapped[Optional[str]]
    last_update     : Mapped[datetime]      = mapped_column(DateTime(timezone=True), nullable=False, default=current_time)

class MovieReview(Base):
    """쿼리 성능 최적화를 위해 별도 분리"""
    __tablename__ = TABLE_MOVIE_REVIEW
    id       : Mapped[int] = mapped_column(primary_key=True)
    movie_id : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_MOVIE), ondelete="CASCADE"), nullable=False)
    text     : Mapped[str] = mapped_column(nullable=False)

class RecommendedMovie(Base):
    __tablename__ = TABLE_RECOMMENDED_MOVIE
    chat_id : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_CHAT_HISTORY), ondelete="CASCADE"), primary_key=True, nullable=False)
    movie_id : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_MOVIE), ondelete="CASCADE"), primary_key=True, nullable=False)

@event.listens_for(Movie, "before_update", propagate=True)
def auto_update_last_modified(mapper, connection, target: Movie):
    target.last_update = current_time()
    flag_modified(target, "last_update")

class BookmarkedMovie(Base):
    __tablename__ = TABLE_BOOKMARKED_MOVIE
    movie_id   : Mapped[int]      = mapped_column(ForeignKey(fk(TABLE_MOVIE), ondelete="CASCADE"), primary_key=True)
    user_id    : Mapped[int]      = mapped_column(ForeignKey(fk(TABLE_USER), ondelete="CASCADE"),  primary_key=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=current_time)

class ArchivedMovie(Base):
    __tablename__ = TABLE_ARCHIVED_MOVIE
    movie_id   : Mapped[int]      = mapped_column(ForeignKey(fk(TABLE_MOVIE), ondelete="CASCADE"), primary_key=True)
    user_id    : Mapped[int]      = mapped_column(ForeignKey(fk(TABLE_USER), ondelete="CASCADE"),  primary_key=True)
    rating     : Mapped[int]      = mapped_column(nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_time)

class Director(Base):
    __tablename__ = TABLE_DIRECTOR
    id            : Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    tmdb_id       : Mapped[int]  = mapped_column(unique=True, nullable=False)
    name          : Mapped[str]  = mapped_column(nullable=False)
    original_name : Mapped[str]  = mapped_column(nullable=False)
    profile_path  : Mapped[Optional[str]]

class ChatRoom(Base):
    __tablename__ = TABLE_CHAT_ROOM
    id           : Mapped[int]      = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id      : Mapped[int]      = mapped_column(ForeignKey(fk(TABLE_USER), ondelete="CASCADE"), nullable=False)
    character_id : Mapped[Optional[int]] = mapped_column(ForeignKey(fk(TABLE_CHARACTER_PROFILE), ondelete="SET NULL"))
    title        : Mapped[str]      = mapped_column(nullable=False)
    summary      : Mapped[str]      = mapped_column(nullable=False, default="")
    created_at   : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_time)

class ChatHistory(Base):
    __tablename__ = TABLE_CHAT_HISTORY
    id        : Mapped[int]      = mapped_column(primary_key=True, index=True, autoincrement=True)
    room_id   : Mapped[int]      = mapped_column(ForeignKey(fk(TABLE_CHAT_ROOM), ondelete="CASCADE"))
    ai_chat   : Mapped[str]      = mapped_column(nullable=False)
    user_chat : Mapped[str]      = mapped_column(nullable=False)
    timestamp : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=current_time)

class CharacterProfile(Base):
    __tablename__ = TABLE_CHARACTER_PROFILE
    id             : Mapped[int]      = mapped_column(primary_key=True, index=True, autoincrement=True)
    movie_id       : Mapped[int]      = mapped_column(ForeignKey(fk(TABLE_MOVIE), ondelete="CASCADE"), nullable=False)
    name           : Mapped[str]      = mapped_column(nullable=False)
    description    : Mapped[str]      = mapped_column(nullable=False)
    tone           : Mapped[str]      = mapped_column(nullable=False)
    other_features : Mapped[Optional[str]]
    actor_id       : Mapped[Optional[int]] = mapped_column(ForeignKey(fk(TABLE_ACTOR), ondelete="SET NULL"))

class Genre(Base):
    __tablename__ = TABLE_GENRE
    id   : Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    name : Mapped[str]  = mapped_column(unique=True, nullable=False)

class Actor(Base):
    __tablename__ = TABLE_ACTOR
    id            : Mapped[int]  = mapped_column(primary_key=True)
    tmdb_id       : Mapped[int]  = mapped_column(unique=True, nullable=False)
    name          : Mapped[str]  = mapped_column(nullable=False)
    original_name : Mapped[str]  = mapped_column(nullable=False)
    profile_path  : Mapped[Optional[str]]

class Platform(Base):
    __tablename__ = TABLE_PLATFORM
    id         : Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    tmdb_id    : Mapped[int]  = mapped_column(unique=True, nullable=False)
    name       : Mapped[str]  = mapped_column(nullable=False)
    logo_path  : Mapped[Optional[str]]

class MovieAlias(Base):
    __tablename__ = TABLE_MOVIE_ALIAS
    movie_id     : Mapped[int]  = mapped_column(ForeignKey(fk(TABLE_MOVIE), ondelete="CASCADE"), nullable=False, primary_key=True)
    aliased_name : Mapped[str]  = mapped_column(nullable=False, primary_key=True)

class MovieGenre(Base):
    __tablename__ = REL_MOVIE_GENRE
    movie_id : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_MOVIE), ondelete="CASCADE"), primary_key=True, nullable=False)
    genre_id : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_GENRE), ondelete="CASCADE"), primary_key=True, nullable=False)

class MovieActor(Base):
    __tablename__ = REL_MOVIE_ACTOR
    movie_id : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_MOVIE), ondelete="CASCADE"), primary_key=True, nullable=False)
    actor_id : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_ACTOR), ondelete="CASCADE"), primary_key=True, nullable=False)

class MoviePlatform(Base):
    __tablename__ = REL_MOVIE_PLATFORM
    movie_id    : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_MOVIE),    ondelete="CASCADE"),    primary_key=True, nullable=False)
    platform_id : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_PLATFORM), ondelete="CASCADE"), primary_key=True, nullable=False)

class MovieDirector(Base):
    __tablename__ = REL_MOVIE_DIRECTOR
    movie_id    : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_MOVIE),    ondelete="CASCADE"), primary_key=True, nullable=False)
    director_id : Mapped[int] = mapped_column(ForeignKey(fk(TABLE_DIRECTOR), ondelete="CASCADE"), primary_key=True, nullable=False)

Base.metadata.create_all(bind=engine)