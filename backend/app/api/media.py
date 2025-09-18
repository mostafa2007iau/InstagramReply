"""
media.py
روت‌هایی برای لیست کردن مدیاها (پست، ریلز) صاحب اکانت
"""

from fastapi import APIRouter, HTTPException, Query
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
async def list_media(username: str = Query(..., description="Instagram username")):
    """
    لیست مدیاهای صاحب اکانت
    - username را از querystring می‌گیرد
    - sessionid مربوط به همان اکانت را لود می‌کند
    """
    cfg = load_config()
    cfg["instagram"]["username"] = username
    cfg["instagram"]["sessionid_file"] = f"./sessions/sessionid_{username}.txt"

    client = InstaClient(cfg)
    try:
        client.load_session()
    except Exception as ex:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {ex}")

    medias = client.get_own_recent_media(limit=50)

    result = []
    for m in medias:
        result.append(
            MediaListResp(
                id=str(m["id"]),
                media_type=str(m["media_type"]),
                caption=(m["caption"] or ""),
                thumbnail_url=(m["thumbnail_url"] or ""),
            )
        )
    return result


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)
