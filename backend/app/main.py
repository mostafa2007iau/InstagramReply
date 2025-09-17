"""
main.py
ورودی اصلی سرویس FastAPI — اکنون با mount کردن روترهای auth/media/comments/admin
(Main entrypoint for FastAPI with routers)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, media, comments, admin  # relative imports
import yaml, os

app = FastAPI(title="InstagramReply Backend",
              description="Backend service that wraps instagrapi and exposes REST endpoints.",
              version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load config file presence check
cfg_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
if not os.path.exists(cfg_path):
    # copy example if exists
    example = os.path.join(os.path.dirname(__file__), "..", "..", "config.example.yaml")
    if os.path.exists(example):
        import shutil
        shutil.copy(example, cfg_path)

app.include_router(auth.router)
app.include_router(media.router)
app.include_router(comments.router)
app.include_router(admin.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
