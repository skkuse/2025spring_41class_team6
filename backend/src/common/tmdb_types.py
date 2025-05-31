from pydantic import BaseModel
from datetime import date

import sys
if sys.version_info < (3, 11):
  from typing_extensions import TypedDict, Required, NotRequired
else:
  from typing import TypedDict, Required, NotRequired

from typing import Optional, List

# see: https://developer.themoviedb.org/reference/search-movie
TmdbSearchMovieArgs = TypedDict(
  "TmdbSearchMovieArgs", {
    "query"                  : str,
    "include_adult"          : NotRequired[bool],
    "language"               : NotRequired[str],
    "primary_release_year"   : NotRequired[str],
    "page"                   : NotRequired[int],
    "region"                 : NotRequired[str],
    "year"                   : NotRequired[str],
  }
)

TmdbSearchOpt = TypedDict(
  "TmdbSearchOpt", {
    "movie_id" : NotRequired[int],
    "search"   : NotRequired[TmdbSearchMovieArgs],
    "lang"     : NotRequired[str],
  }
)

class ActorInfo(BaseModel):
    credit_id: str
    person_id: int
    character: str
    name: str
    original_name: str
    profile_path: Optional[str]
    order: int

class DirectorInfo(BaseModel):
    credit_id: str
    person_id: int
    name: str
    original_name: str
    profile_path: Optional[str]

class PlatformInfo(BaseModel):
    tmdb_id: int
    name: str
    logo_path: Optional[str]

class ExternalIdInfo(BaseModel):
   imdb: str
   wikidata: str

class TmdbRequestResult(BaseModel):
    id: int
    title: str
    overview: str
    poster_path: str
    release_date: date
    genres: List[str]
    casts: List[ActorInfo]
    directors: List[DirectorInfo]
    platforms: List[PlatformInfo]
    external_ids: ExternalIdInfo
