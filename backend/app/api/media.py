"""
media.py
روت‌هایی برای لیست کردن مدیاها (پست، ریلز) صاحب اکانت و جزئیات آنها
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
    لیست مدیاهای صاحب اکانت (Returns list of own recent media)
    """
    cfg = load_config()
    client = InstaClient(cfg)
    client.load_session()

    # گرفتن user_id از username
    username = cfg.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="username not set in config.yaml")

    user_id = client.cl.user_id_from_username(username)

    # استفاده از user_medias_v1 (پایدارتر از get_own_recent_media)
    medias = client.cl.user_medias_v1(user_id, amount=50)

    # تبدیل به خروجی ساده
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
