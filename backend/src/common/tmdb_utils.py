import tmdbsimple as tmdb
from datetime import date
from enum import Enum
from urllib.parse import urljoin
from typing import cast

from common.tmdb_types import *
from common.env import ENV_TMDB_API_KEY

tmdb.API_KEY = ENV_TMDB_API_KEY

class ImgType(Enum):
  LOGO="logo"
  POSTER="poster"
  PROFILE="profile"
  STILL="still"
  BACKDROP="backdrop"

_cached_tmbd_configuration: dict|None = None

def tmdb_get_configuration() -> dict|None:
  """TMDB configuration을 불러옵니다"""
  global _cached_tmbd_configuration
  if _cached_tmbd_configuration is None:
    _cached_tmbd_configuration = tmdb.Configuration().info()
  return _cached_tmbd_configuration

# TMDB에서는 주요인물만 가져올 수 있는 방법이 딱히 없기 때문에 order 상위 N명으로 추려냅니다
def tmdb_parse_casts(credits: dict, max_ordering: int) -> List[ActorInfo]:
  tmp = credits["cast"]
  return [ActorInfo(
    credit_id = i["credit_id"],
    person_id = i["id"],
    character = i["character"],
    name = i["name"],
    original_name = i["original_name"],
    profile_path = i["profile_path"],
    order = i["order"],
  ) for i in tmp if i["order"] < max_ordering]

def tmdb_parse_directors(credits: dict) -> List[DirectorInfo]:
  tmp = credits["crew"]
  return [DirectorInfo(
    credit_id = i["credit_id"],
    person_id = i["id"],
    name = i["name"],
    original_name = i["original_name"],
    profile_path = i["profile_path"],
  ) for i in tmp if i["job"] == "Director"]

def tmdb_parse_platforms(kr_providers: dict) -> List[PlatformInfo]:
  if kr_providers is None:
    return []
  print(kr_providers)
  tmp = kr_providers.get("flatrate")
  if tmp is None:
    tmp = kr_providers.get("free") # 여기 실제론 TMDB API 문서와 다르게 반환하는 요소가 있는 것 같음
  if tmp is None:
    return []

  return [PlatformInfo(
    tmdb_id = i["provider_id"],
    name = i["provider_name"],
    logo_path = i["logo_path"],
  ) for i in tmp]

def tmdb_request_movie_bulk(identifier: TmdbSearchOpt, max_casts: int= 15) -> List[TmdbRequestResult]:
  """
  TMDB에서 영화를 찾습니다.  
  Args:
    identifier:
      * ID로 찾고 싶다면 `movie_id`에 id값 세팅
      * query로 찾고 싶다면: `search`에 dictionary 형태로 `query`, `page` 등의 값 세팅  
        참고: https://developer.themoviedb.org/reference/search-movie
  Returns:
    TMDB에서 찾은 영화 정보들을 모두 반환합니다
  """
  id = identifier.get("movie_id")
  search = identifier.get("search")
  lang = identifier.get("lang")
  # 일단은 korean으로 설정함
  if lang is None:
    lang = "ko"

  if id is not None:
    ids = [id]
  elif search and search["query"]:
    tmdb.Search().movie()
    movies = tmdb.Search().movie(**search)["results"]
    ids = [movie["id"] for movie in movies]
  else:
    return []

  movie_data: List[TmdbRequestResult] = []
  for id in ids:
    movie = tmdb.Movies(id)

    response = movie.info(append_to_response="credits,watch/providers,external_ids", language=lang)
    credits = response["credits"]
    kr_providers = response["watch/providers"]["results"].get('KR')
    externals = response["external_ids"]

    data = TmdbRequestResult(
      id = id,
      title = response["title"],
      overview = response["overview"],
      poster_path = response["poster_path"],
      release_date = tmdb_parse_release_date(response),
      genres = tmdb_parse_genres(response),
      casts = tmdb_parse_casts(credits, max_casts),
      directors = tmdb_parse_directors(credits),
      platforms = tmdb_parse_platforms(kr_providers),
      external_ids = ExternalIdInfo(
        imdb = externals.get("imdb_id"),
        wikidata = externals.get("wikidata_id")
      )
    )
    movie_data.append(data)

  return movie_data


def tmdb_full_image_path(path: str, type: ImgType, size_max: int|None=None, secure=True):
  """
  TMDB image path(ex: /asdfasdf.jpg)에서 full path를 생성합니다  
  (ex: https://base_url/w500/asdfasdf.jpg).
  Args:
    path:
      TMDB에서 가져온 image path:
      - logo_path
      - poster_path
      - profile_path
      - still_path
      - backdrop_path
    type:
      TMDB 이미지 타입  
      ex) poster_path 링크라면 ImgType.POSTER
    size_max:
      (optional) width 기준 최대 사이즈 지정.  
      TMDB에서 지원하는 이미지 사이즈 중 size_max보다 작거나 같은
      이미지 링크를 반환합니다.  
      지정하지 않으면 원본 이미지 사이즈 링크로 반환됩니다.
    secure:
      (optional) 이미지 출처로 HTTPS를 사용.  
      기본값은 True입니다.
  Returns:
    img src태그에 바로 사용할 수 있는 링크가 반환됩니다.
  """
  config = tmdb_get_configuration()
  assert(config is not None)
  config = config["images"]

  base_url: str= config["secure_base_url" if secure else "base_url"]
  base_url = cast(str, base_url.strip('/'))
  path = path.strip('/')
  
  sizes = "original"

  if size_max is not None:
    def _resolution_of(s: str) -> int: return int(s[1:])

    config_size: list[str] = config[f"{type.value}_sizes"]
    config_size = [i for i in config_size if i.startswith('w')]

    config_size = sorted(config_size, key=_resolution_of, reverse=True)

    for i in config_size:
      if _resolution_of(i) <= size_max:
        sizes = i
        break

  return "/".join([base_url, sizes, path])

# added NULL safety
def tmdb_parse_title(info: dict) -> str|None:
  return info.get("title")

def tmdb_parse_overview(info: dict) -> str|None:
  return info.get("overview")

def tmdb_parse_poster_path(info: dict) -> str|None:
  return info.get("poster_path")

def tmdb_parse_release_date(info: dict) -> date|None:
  d = info.get("release_date")
  return date.fromisoformat(d) if d else None

def tmdb_parse_genres(info: dict) -> list[str]:
  tmp = info.get("genres")
  if not tmp:
    return []

  return [i["name"] for i in tmp if i.get("name")]
