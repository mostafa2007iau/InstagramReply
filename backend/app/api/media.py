"""
media.py
روت‌هایی برای لیست کردن مدیاها (پست، ریلز) صاحب اکانت و جزئیات آنها
(Endpoints to list account medias)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.insta_client import InstaClient
import yaml, os

router = APIRouter(prefix="/media", tags=["media"])

class MediaListResp(BaseModel):
    id: str
    media_type: str
    caption: str
    thumbnail_url: str

@router.get("/list")
async def list_media():
    """
    لیست مدیاهای صاحب اکانت
    (Returns list of own recent media)
    """
    cfg = load_config()
    client = InstaClient(cfg)
    client.load_session()
    medias = client.get_own_recent_media(limit=50)
    return medias

def load_config():
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")) as f:
        return yaml.safe_load(f)
