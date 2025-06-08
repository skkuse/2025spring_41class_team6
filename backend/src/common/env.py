import os
from dotenv import load_dotenv

assert(load_dotenv())
ENV_BACKEND_ROOT=os.getenv("BACKEND_ROOT")
ENV_OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
ENV_OPENROUTER_KEY=os.getenv("OPEN_ROUTER_KEY")
ENV_TMDB_API_KEY=os.getenv("TMDB_API_KEY")
ENV_API_SKIP_AUTH=os.getenv("API_SKIP_AUTH")
assert(ENV_BACKEND_ROOT)
assert(ENV_OPENAI_API_KEY)
assert(ENV_OPENROUTER_KEY)
assert(ENV_TMDB_API_KEY)
# API_SKIP_AUTH is optional

# ENV_OMDB_API_KEY=os.getenv("OMDB_API_KEY")
# assert(ENV_OMDB_API_KEY)
