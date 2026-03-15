from fastapi import FastAPI

from .core.cache import lifespan
from .router import api_router

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
