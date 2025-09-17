"""
media.py
روت‌هایی برای لیست کردن مدیاها (پست، ریلز) صاحب اکانت
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.insta_client import InstaClient
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
    """
    cfg = load_config()
    client = InstaClient(cfg)
    client.load_session()

    medias = client.get_own_recent_media(limit=50)

    result = []
    for m in medias:
        result.append(
            MediaListResp(
                id=str(m.pk),
                media_type=str(m.media_type),
                caption=(m.caption_text or ""),
                thumbnail_url=(m.thumbnail_url or ""),
            )
        )
    return result


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)
