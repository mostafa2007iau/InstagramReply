# InstagramReply

این مخزن شامل دو بخش است: یک سرویس بک‌اند با Python (instagrapi) و یک کلاینت .NET MAUI 9 برای ویندوز و اندروید.
(This repository contains two parts: a Python backend service using instagrapi and a .NET MAUI 9 client for Windows and Android.)

در این مرحله اولیه فایل‌های پایه backend را قرار داده‌ام؛ در پیام‌های بعدی کلاینت MAUI و بقیه فایل‌ها ارسال خواهد شد.
(Initial backend skeleton provided here; MAUI client and remaining files will be sent in subsequent messages.)

مراحل سریع راه‌اندازی محلی برای بخش backend:
(Quick local setup steps for backend:)

1. وارد پوشه backend شو:
   cd backend

2. ایجاد و فعال‌سازی virtualenv (پیشنهاد شده):
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\Activate.ps1  # Windows PowerShell

3. نصب وابستگی‌ها:
   pip install -r requirements.txt

4. اجرای محلی:
   python -m app.main

توضیحات بیشتر و اجرای Docker و کلاینت MAUI در پیام‌های بعدی خواهد آمد.
(More details and Docker/MAUI instructions will follow.)
