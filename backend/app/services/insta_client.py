"""
insta_client.py
مدیریت ارتباط با Instagram از طریق instagrapi
"""

from instagrapi import Client
import os

class InstaClient:
    def __init__(self, cfg):
        self.cl = Client()
        self.username = cfg["username"]
        self.password = cfg["password"]
        self.session_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "session.json"
        )

    def load_session(self):
        """
        تلاش برای بارگذاری سشن از فایل.
        اگر معتبر نبود، لاگین جدید انجام می‌دهد.
        """
        if os.path.exists(self.session_path):
            try:
                self.cl.load_settings(self.session_path)
                # تست اعتبار
                self.cl.get_timeline_feed()
                return
            except Exception:
                print("⚠️ Session invalid, re-login required")
                self.login_and_save()
        else:
            self.login_and_save()

    def login_and_save(self):
        """
        لاگین با یوزرنیم/پسورد و ذخیره سشن
        """
        self.cl.login(self.username, self.password)
        self.cl.dump_settings(self.session_path)

    def get_own_recent_media(self, limit=20):
        """
        گرفتن مدیاهای اخیر اکانت لاگین‌شده
        """
        user_id = self.cl.user_id_from_username(self.username)
        return self.cl.user_medias(user_id, limit)
