"""
auth.py
روت‌های مربوط به لاگین، وضعیت session و حل challenge/2fa
(Auth endpoints: login, session status, handle challenge)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yaml
import os
from ..services.insta_client import InstaClient

router = APIRouter(prefix="/auth", tags=["auth"])

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")

class LoginRequest(BaseModel):
    username: str
    password: str

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(cfg, f)

@router.post("/login")
async def login(req: LoginRequest):
    """
    Login endpoint
    - بار اول: لاگین با username/password و ذخیره sessionid
    - دفعات بعد: فقط از sessionid استفاده می‌کند
    """
    cfg = load_config()

    # اطمینان از وجود لیست اکانت‌ها
    if "instagram_accounts" not in cfg:
        cfg["instagram_accounts"] = []

    # بررسی اینکه آیا اکانت قبلاً وجود دارد
    account = next((a for a in cfg["instagram_accounts"] if a["username"] == req.username), None)

    if not account:
        # اگر اکانت جدید است، اضافه‌اش کن
        account = {
            "username": req.username,
            "password": req.password,
            "sessionid_file": f"./sessions/sessionid_{req.username}.txt",
            "use_proxy": False,
            "proxy": None
        }
        cfg["instagram_accounts"].append(account)
    else:
        # اگر قبلاً وجود دارد، اطلاعاتش را به‌روزرسانی کن
        account["password"] = req.password
        account["sessionid_file"] = f"./sessions/sessionid_{req.username}.txt"

    save_config(cfg)

    client = InstaClient(account)
    try:
        client.login()
        return {"ok": True, "message": "Login successful, session ready."}
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get("/status")
async def status(username: str):
    """
    بررسی وضعیت لاگین برای یک اکانت خاص
    (Check if session exists and is authenticated for given username)
    """
    cfg = load_config()

    account = next((a for a in cfg.get("instagram_accounts", []) if a["username"] == username), None)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    session_file = account.get("sessionid_file")
    if not session_file or not os.path.exists(session_file):
        return {"is_authenticated": False}

    try:
        client = InstaClient(account)
        client.load_session()
        return {"is_authenticated": client.client.authenticated}
    except Exception:
        return {"is_authenticated": False}
