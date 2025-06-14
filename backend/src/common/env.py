import os
from dotenv import load_dotenv

assert(load_dotenv())
ENV_BACKEND_ROOT=os.getenv("BACKEND_ROOT")
ENV_OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
ENV_OPENROUTER_KEY=os.getenv("OPEN_ROUTER_KEY")
ENV_TMDB_API_KEY=os.getenv("TMDB_API_KEY")
assert(ENV_BACKEND_ROOT)
assert(ENV_OPENAI_API_KEY)
assert(ENV_OPENROUTER_KEY)
assert(ENV_TMDB_API_KEY)
