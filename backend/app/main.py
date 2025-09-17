"""
main.py
ورودی اصلی سرویس FastAPI
(Main entrypoint for the FastAPI service)
"""

# pip: install uvicorn fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# از ماژول‌های داخلی سرویس استفاده خواهد شد (در پیام‌های بعدی اضافه می‌شوند)
# (Internal service modules will be added in subsequent messages)

app = FastAPI(title="InstagramReply Backend",
              description="Backend service that wraps instagrapi and exposes REST endpoints (It will handle login, media listing, comment polling and actions).",
              version="0.1.0")

# CORS policy برای ارتباط با کلاینت MAUI در زمان توسعه
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در production محدودش کن
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """
    Health endpoint
    بازگشت وضعیت سالم بودن سرویس
    (Return service health status)
    """
    return {"status": "ok"}

# Routers و لود سرویس‌ها در فایل‌های بعدی اضافه خواهد شد
# (Routers and service wiring will be added in subsequent messages)
