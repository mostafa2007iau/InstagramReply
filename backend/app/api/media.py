"""
media.py
روت‌هایی برای لیست کردن مدیاها (پست، ریلز) صاحب اکانت
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.insta_client import InstaClient
import yaml, os

router = APIRouter(prefix="/media", tags=["media"])

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
SESS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "sessions")

class MediaListResp(BaseModel):
    id: str
    media_type: str
    caption: str
    thumbnail_url: str

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"instagram_accounts": []}
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {"instagram_accounts": []}

def ensure_sessions_dir():
    os.makedirs(SESS_DIR, exist_ok=True)

def build_session_path(username: str) -> str:
    ensure_sessions_dir()
    return os.path.join(SESS_DIR, f"sessionid_{username}.txt")

@router.get("/list")
async def list_media(username: str = Query(..., description="Instagram username")):
    """
    لیست مدیاهای صاحب اکانت
    - username را از querystring می‌گیرد
    - sessionid مربوط به همان اکانت را لود می‌کند
    """
    cfg = load_config()

    # پیدا کردن حساب کاربری مطابق با username
    accounts = cfg.get("instagram_accounts", [])
    account = next((a for a in accounts if a.get("username") == username), None)
    if not account:
        # اگر اکانت در config نبود، حداقل باید مسیر سشن داشته باشه؛
        # (رمز عبور لازم است اگر سشن وجود نداشته باشد.)
        account = {
            "username": username,
            "password": "",  # اگر لازم است لاگین با پسورد انجام شود، باید از قبل ست شود
            "sessionid_file": build_session_path(username),
            "use_proxy": False,
            "proxy": None,
        }

    # InstaClient شما انتظار دارد config به شکل {"instagram": {...}} باشد
    client = InstaClient({"instagram": account})

    try:
        client.load_session()  # تلاش می‌کند از sessionid وارد شود و در صورت نیاز با پسورد
    except Exception as ex:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {ex}")

    medias = client.get_own_recent_media(limit=50)

    result = [
        MediaListResp(
            id=str(m.get("id", "")),
            media_type=str(m.get("media_type", "")),
            caption=(m.get("caption") or ""),
            thumbnail_url=(m.get("thumbnail_url") or ""),
        )
        for m in medias
    ]
    return result
