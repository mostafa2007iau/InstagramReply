"""
admin.py
روت‌های مدیریتی: اضافه/حذف/لیست قواعد، export/import، وضعیت storage
(Admin endpoints: manage rules, export/import)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.storage import Storage
import json

router = APIRouter(prefix="/admin", tags=["admin"])

class RuleCreate(BaseModel):
    media_id: str
    patterns: list
    reply_text: str
    direct_text: str
    cooldown_seconds: int = 3600

@router.post("/rules")
async def create_rule(r: RuleCreate):
    """
    اضافه کردن یک rule جدید
    (Create a new rule)
    """
    s = Storage()
    rid = s.add_rule(r.media_id, r.patterns, r.reply_text, r.direct_text, r.cooldown_seconds)
    return {"id": rid}

@router.get("/rules")
async def list_rules(media_id: str = None):
    s = Storage()
    return s.list_rules(media_id)

@router.get("/export")
async def export_rules():
    s = Storage()
    rules = s.list_rules(None)
    return {"rules": rules}

@router.post("/import")
async def import_rules(payload: dict):
    s = Storage()
    imported = 0
    for r in payload.get("rules", []):
        s.add_rule(r["media_id"], r.get("patterns", []), r.get("reply_text", ""), r.get("direct_text", ""), r.get("cooldown_seconds", 3600))
        imported += 1
    return {"imported": imported}
