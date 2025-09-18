"""
comments.py
روت‌هایی برای polling کامنت‌ها، و اجرای عملیات reply + send DM با رعایت rules
(Endpoints to trigger polling and process comments)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from ..services.insta_client import InstaClient
from ..services.storage import Storage
from ..services.rules import RulesEngine
import yaml, os, random, asyncio

router = APIRouter(prefix="/comments", tags=["comments"])

class PollRequest(BaseModel):
    media_id: str

@router.post("/poll")
async def poll_comments(req: PollRequest, username: str = Query(..., description="Instagram username")):
    """
    Poll comments for a specific media and process them according to rules.
    - این endpoint برای فراخوانی worker یا از UI استفاده می‌شود تا کامنت‌های جدید را بررسی کند.
    - الان بر اساس username هر اکانت sessionid جدا لود می‌شود.
    """
    cfg = load_config()
    cfg["instagram"]["username"] = username
    cfg["instagram"]["sessionid_file"] = f"./sessions/sessionid_{username}.txt"

    client = InstaClient(cfg)
    try:
        client.load_session()
    except Exception as ex:
        raise HTTPException(status_code=401, detail=f"Authentication failed for {username}: {ex}")

    storage = Storage()
    rules_engine = RulesEngine(storage)

    comments = client.get_comments(int(req.media_id), amount=100)
    actions = []
    for c in comments:
        if storage.is_comment_processed(username, c["id"]):
            continue
        rule = rules_engine.match(c["text"], req.media_id, username=username)
        if rule:
            # respect cooldown per-user and per-rule (simple check via storage processed comments)
            success_reply = client.reply_comment(c["id"], rule.reply_text)
            await asyncio.sleep(random.uniform(
                cfg.get("poller", {}).get("random_delay_min_ms", 8000) / 1000.0,
                cfg.get("poller", {}).get("random_delay_max_ms", 15000) / 1000.0
            ))
            success_dm = client.send_direct(c["username"], rule.direct_text)
            storage.mark_comment_processed(username, c["id"], req.media_id)
            actions.append({
                "comment_id": c["id"],
                "reply": success_reply,
                "dm": success_dm
            })
    return {"processed": len(actions), "details": actions}

def load_config():
    with open(os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")) as f:
        return yaml.safe_load(f)
