from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes import anon, draw, groups, members

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groups.router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(draw.router, prefix="/api")
app.include_router(anon.router, prefix="/api")


@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}
