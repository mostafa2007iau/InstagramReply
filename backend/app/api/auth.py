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

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    """
    Login endpoint
    - بار اول: لاگین با username/password و ذخیره sessionid
    - دفعات بعد: فقط از sessionid استفاده می‌کند
    """
    cfg = load_config()
    # تزریق username/password به config
    cfg["instagram"]["username"] = req.username
    cfg["instagram"]["password"] = req.password
    cfg["instagram"]["sessionid_file"] = f"./sessions/sessionid_{req.username}.txt"

    client = InstaClient(cfg)
    try:
        client.load_session()
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
    cfg["instagram"]["username"] = username
    cfg["instagram"]["sessionid_file"] = f"./sessions/sessionid_{username}.txt"

    client = InstaClient(cfg)
    try:
        client.load_session()
        return {"is_authenticated": client.client.authenticated}
    except Exception:
        return {"is_authenticated": False}

def load_config():
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")) as f:
        return yaml.safe_load(f)
