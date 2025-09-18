"""
admin.py
روت‌های مدیریتی: اضافه/حذف/لیست قواعد، export/import، وضعیت storage
(Admin endpoints: manage rules, export/import)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from ..services.storage import Storage

router = APIRouter(prefix="/admin", tags=["admin"])

class RuleCreate(BaseModel):
    username: str
    media_id: str
    patterns: list
    reply_text: str
    direct_text: str
    cooldown_seconds: int = 3600

@router.post("/rules")
async def create_rule(r: RuleCreate):
    """
    اضافه کردن یک rule جدید برای یک اکانت خاص
    (Create a new rule for a specific account)
    """
    s = Storage()
    rid = s.add_rule(r.username, r.media_id, r.patterns, r.reply_text, r.direct_text, r.cooldown_seconds)
    return {"id": rid}

@router.get("/rules")
async def list_rules(username: str = Query(..., description="Instagram username"), media_id: str = None):
    """
    لیست قوانین برای یک اکانت (و در صورت نیاز یک مدیای خاص)
    (List rules for a specific account, optionally filtered by media_id)
    """
    s = Storage()
    return s.list_rules(username, media_id)

@router.get("/export")
async def export_rules(username: str = Query(..., description="Instagram username")):
    """
    Export all rules for a given account
    """
    s = Storage()
    rules = s.list_rules(username, None)
    return {"rules": rules}

@router.post("/import")
async def import_rules(username: str, payload: dict):
    """
    Import rules for a given account
    """
    s = Storage()
    imported = 0
    for r in payload.get("rules", []):
        s.add_rule(
            username,
            r["media_id"],
            r.get("patterns", []),
            r.get("reply_text", ""),
            r.get("direct_text", ""),
            r.get("cooldown_seconds", 3600),
        )
        imported += 1
    return {"imported": imported}
