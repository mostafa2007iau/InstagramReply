"""
rules.py
یک مدیریت ساده برای rules (قواعد)
- Rules در دیتابیس SQLite ذخیره می‌شوند (فایل storage ساده در services/storage.py).
(Simple rules manager. Rules stored via storage module.)
"""

from typing import List, Dict, Optional
import re
import logging

logger = logging.getLogger("rules")

class Rule:
    """
    Rule model
    - id: شناسه (identifier)
    - media_id: شناسه پست (related media id)
    - patterns: لیست regex یا کلمات برای تطبیق (list of patterns)
    - reply_text: متن پاسخ به کامنت (reply comment text)
    - direct_text: متن دایرکت برای ارسال (direct message text)
    - cooldown_seconds: cooldown برای این rule (cooldown)
    """
    def __init__(self, id: int, media_id: str, patterns: List[str], reply_text: str, direct_text: str, cooldown_seconds: int = 3600):
        self.id = id
        self.media_id = media_id
        self.patterns = patterns
        self.reply_text = reply_text
        self.direct_text = direct_text
        self.cooldown_seconds = cooldown_seconds

class RulesEngine:
    """
    RulesEngine
    - بارگذاری قواعد از storage
    - تطبیق متن با قواعد (match)
    """
    def __init__(self, storage):
        self.storage = storage

    def get_rules_for_media(self, media_id: str) -> List[Rule]:
        """بازگرداندن لیست قوانینی که به یک media خاص مربوط‌اند (Return rules for a media)."""
        raw = self.storage.list_rules(media_id)
        rules = []
        for r in raw:
            rules.append(Rule(r["id"], r["media_id"], r["patterns"], r["reply_text"], r["direct_text"], r.get("cooldown_seconds", 3600)))
        return rules

    def match(self, text: str, media_id: str) -> Optional[Rule]:
        """بررسی متن در برابر قوانین media و بازگشت rule اول matchشده (Return first matching rule)."""
        rules = self.get_rules_for_media(media_id)
        for r in rules:
            for p in r.patterns:
                try:
                    if re.search(p, text, re.IGNORECASE):
                        logger.info("Matched rule %s for media %s", r.id, media_id)
                        return r
                except re.error:
                    # treat pattern as plain substring if regex invalid
                    if p.lower() in text.lower():
                        logger.info("Matched substring rule %s for media %s", r.id, media_id)
                        return r
        return None
