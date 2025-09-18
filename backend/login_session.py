# login_session.py
# اجرای دستی برای ساخت session.json معتبر

from instagrapi import Client
import getpass

def main():
    print("🔐 Instagram Login")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    cl = Client()
    try:
        cl.login(username, password)
        cl.dump_settings("session.json")
        print("✅ Session saved to session.json")
    except Exception as ex:
        print(f"❌ Login failed: {ex}")

if __name__ == "__main__":
    main()
