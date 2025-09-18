"""
insta_client.py
Wrapper ساده دور instagrapi برای لاگین، لیست مدیا، گرفتن کامنت و ارسال reply و DM.
(Simple wrapper around instagrapi for login, list media, get comments, reply and send DM.)
"""

from typing import List, Dict
import os
import asyncio
import random
import logging

from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired

logger = logging.getLogger("insta_client")
logger.setLevel(logging.INFO)


class InstaClient:
    """
    InstaClient
    - یک wrapper برای مدیریت اتصال به اینستاگرام با instagrapi
    - Provides: login, session persistence (via sessionid), list media, fetch comments, reply comment, send dm
    """

    def __init__(self, config: Dict):
        self.config = config
        self.client = Client()

        ig = config.get("instagram", {})
        self.username = ig.get("username")
        self.password = ig.get("password")
        self.use_proxy = ig.get("use_proxy", False)
        self.proxy = ig.get("proxy")
        self.sessionid_file = ig.get("sessionid_file", f"./sessions/sessionid_{self.username}.txt")

        if self.use_proxy and self.proxy:
            self.client.set_proxy(self.proxy)

    # ---------------- Session Management ----------------

    def load_session(self):
        """
        Load session automatically:
        - If sessionid file exists, login_by_sessionid
        - Otherwise, login with username/password and save sessionid
        """
        if os.path.exists(self.sessionid_file):
            try:
                with open(self.sessionid_file, "r", encoding="utf-8") as f:
                    sessionid = f.read().strip()
                self.client.login_by_sessionid(sessionid)
                logger.info("✅ Logged in via saved sessionid.")
                return
            except Exception as ex:
                logger.warning(f"⚠️ Failed login by sessionid, retrying with password: {ex}")

        # fallback: login with password
        self.login_with_password()

    def login_with_password(self):
        """Login with username/password and save sessionid."""
        try:
            self.client.login(self.username, self.password)
            sessionid = self.client.sessionid
            os.makedirs(os.path.dirname(self.sessionid_file), exist_ok=True)
            with open(self.sessionid_file, "w", encoding="utf-8") as f:
                f.write(sessionid)
            logger.info("✅ Logged in with password and sessionid saved.")
        except TwoFactorRequired as t2:
            logger.warning("TwoFactor required: %s", t2)
            raise
        except ChallengeRequired as ch:
            logger.warning("Challenge required: %s", ch)
            raise
        except Exception as ex:
            logger.error("❌ Login failed: %s", ex)
            raise

    # ---------------- Media ----------------

    def get_own_recent_media(self, limit: int = 20) -> List[Dict]:
        """Get recent media of logged-in account."""
        medias = []
        try:
            user_id = self.client.user_id_from_username(self.username)
            items = self.client.user_medias(user_id, amount=limit)
            for m in items:
                medias.append({
                    "id": str(m.pk),
                    "pk": m.pk,
                    "media_type": getattr(m, "media_type_name", str(m.media_type)),
                    "caption": m.caption_text or "",
                    "thumbnail_url": getattr(m, "thumbnail_url", None) or
                                     getattr(m, "thumbnail_resources", [None])[0]
                })
        except Exception as ex:
            logger.error("Failed to list medias: %s", ex)
        return medias

    # ---------------- Comments ----------------

    def get_comments(self, media_pk: int, amount: int = 50) -> List[Dict]:
        """Get comments for a given media."""
        out = []
        try:
            comments = self.client.media_comments(media_pk, amount=amount)
            for c in comments:
                out.append({
                    "id": str(c.pk),
                    "text": c.text,
                    "user_id": c.user.pk,
                    "username": c.user.username,
                    "created_at": c.created_at
                })
        except Exception as ex:
            logger.error("Failed to fetch comments: %s", ex)
        return out

    def reply_comment(self, comment_id: str, text: str) -> bool:
        """Reply to a comment."""
        try:
            self.client.comment_reply(comment_id, text)
            return True
        except Exception as ex:
            logger.error("Reply comment failed: %s", ex)
            return False

    def send_direct(self, username: str, text: str) -> bool:
        """Send direct message (DM) to a username."""
        try:
            user = self.client.user_id_from_username(username)
            self.client.direct_send(text, [user])
            return True
        except Exception as ex:
            logger.error("Send direct failed: %s", ex)
            return False

    # ---------------- Utility ----------------

    def random_delay(self, min_ms: int, max_ms: int):
        """Random human-like delay."""
        ms = random.randint(min_ms, max_ms)
        logger.info("Sleeping for %d ms", ms)
        asyncio.sleep(ms / 1000.0)
