"""
insta_client.py
Wrapper ساده دور instagrapi برای لاگین، لیست مدیا، گرفتن کامنت و ارسال reply و DM.

(Simple wrapper around instagrapi for login, list media, get comments, reply and send DM.)
"""

# نصب کتابخانه:
# pip install instagrapi
from typing import List, Dict, Optional
import os
import asyncio
import random
import json
import logging

from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired

logger = logging.getLogger("insta_client")
logger.setLevel(logging.INFO)

class InstaClient:
    """
    InstaClient
    - یک wrapper برای مدیریت اتصال به اینستاگرام با instagrapi
    - Provides: login, session persistence, list media, fetch comments, reply comment, send dm

    پارامترها (Parameters):
    - config (dict): دیکشنری پیکربندی از فایل yaml (config dict)
    """
    def __init__(self, config: Dict):
        self.config = config
        self.client = Client()
        self.session_file = config.get("instagram", {}).get("session_file", "./session.json")
        self.use_proxy = config.get("instagram", {}).get("use_proxy", False)
        self.proxy = config.get("instagram", {}).get("proxy", None)
        if self.use_proxy and self.proxy:
            self.client.set_proxy(self.proxy)

    def load_session(self):
        """بارگزاری session از فایل اگر وجود دارد (Load session from file if exists)."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                self.client.set_settings(state.get("settings", {}))
                self.client.set_device(state.get("device", {}))
                self.client.relogin()  # try relogin using stored settings
                logger.info("Session loaded and relogin attempted.")
            except Exception as ex:
                logger.warning(f"Failed to load session: {ex}")

    def save_session(self):
        """ذخیره session به فایل جهت reuse (Persist session to file)."""
        try:
            settings = self.client.get_settings()
            device = self.client.get_device()
            state = {"settings": settings, "device": device}
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info("Session saved to %s", self.session_file)
        except Exception as ex:
            logger.warning(f"Failed saving session: {ex}")

    def login(self, username: str, password: str):
        """
        Login to Instagram (synchronous)
        - در صورت مواجهه با challenge یا 2FA استثنا پرتاب می‌شود تا بالادست UI بتواند آن را هندل کند.
        (Raises ChallengeRequired or TwoFactorRequired to be handled by upper layer.)
        """
        if self.use_proxy and self.proxy:
            self.client.set_proxy(self.proxy)
        try:
            self.client.login(username, password)
            self.save_session()
            return True
        except TwoFactorRequired as t2:
            logger.warning("TwoFactor required: %s", t2)
            raise
        except ChallengeRequired as ch:
            logger.warning("Challenge required: %s", ch)
            raise
        except Exception as ex:
            logger.error("Login failed: %s", ex)
            raise

    def get_own_recent_media(self, limit: int = 20) -> List[Dict]:
        """
        Get recent media of logged-in account
        - بازگرداندن لیست مدیاها به صورت دیکشنری شامل id، pk، upload_date و caption
        (Returns list of media dicts with id, pk, upload_date, caption)
        """
        medias = []
        try:
            user_id = self.client.user_id
            items = self.client.user_medias(user_id, amount=limit)
            for m in items:
                medias.append({
                    "id": str(m.pk),
                    "pk": m.pk,
                    "media_type": m.media_type_name,
                    "caption": m.caption_text,
                    "thumbnail_url": m.thumbnail_url or getattr(m, "thumbnail_resources", None)
                })
        except Exception as ex:
            logger.error("Failed to list medias: %s", ex)
        return medias

    def get_comments(self, media_pk: int, amount: int = 50) -> List[Dict]:
        """
        Get comments for a given media
        - برمی‌گرداند لیست کامنت‌ها به همراه id، text، user_id، username و create_time
        (Returns list of comments with id, text, user_id, username, create_time)
        """
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
        """
        Reply to a comment (post a reply comment)
        - ارسال پاسخ به یک کامنت مشخص
        (Posts a reply comment)
        """
        try:
            self.client.comment_reply(comment_id, text)
            return True
        except Exception as ex:
            logger.error("Reply comment failed: %s", ex)
            return False

    def send_direct(self, username: str, text: str) -> bool:
        """
        Send direct message (DM) to a username
        - ارسال دایرکت به username مشخص (با توجه به محدودیت‌های اینستاگرام ممکن است ناکام باشد)
        (Sends DM to a username; may fail due to IG restrictions)
        """
        try:
            user = self.client.user_id_from_username(username)
            self.client.direct_send(text, [user])
            return True
        except Exception as ex:
            logger.error("Send direct failed: %s", ex)
            return False

    def random_delay(self, min_ms: int, max_ms: int):
        """تاخیر تصادفی بین عملیات برای رفتار انسان‌نما (Random human-like delay)."""
        ms = random.randint(min_ms, max_ms)
        logger.info("Sleeping for %d ms", ms)
        asyncio.sleep(ms / 1000.0)
