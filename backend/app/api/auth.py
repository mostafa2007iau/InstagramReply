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
    - تلاش برای لاگین و در صورت موفقیت session را ذخیره می‌کند
    (Attempts login; on success session is persisted)
    """
    cfg = load_config()
    client = InstaClient(cfg)
    try:
        client.login(req.username, req.password)
        return {"ok": True}
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.get("/status")
async def status():
    """برمی‌گرداند که آیا session وجود دارد یا خیر (Return whether session exists)."""
    cfg = load_config()
    client = InstaClient(cfg)
    client.load_session()
    return {"is_authenticated": client.client.authenticated}

def load_config():
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")) as f:
        return yaml.safe_load(f)
