import os
from dotenv import load_dotenv

assert(load_dotenv())
ENV_PROJECT_ROOT=os.getenv("PROJECT_ROOT")
ENV_OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
ENV_TMDB_API_KEY=os.getenv("TMDB_API_KEY")
ENV_OMDB_API_KEY=os.getenv("OMDB_API_KEY")
assert(ENV_PROJECT_ROOT)
assert(ENV_OPENAI_API_KEY)
assert(ENV_TMDB_API_KEY)
assert(ENV_OMDB_API_KEY)