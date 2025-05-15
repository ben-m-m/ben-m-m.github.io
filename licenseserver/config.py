import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "")
SIGNING_SECRET = os.getenv("SIGNING_SECRET", "")

if not SECRET_KEY or not JWT_SECRET or not SIGNING_SECRET:
    print("[❌] Missing critical secrets. Please check your .env or environment variables.")
    exit(1)

# Encode SIGNING_SECRET for HMAC usage:
SIGNING_SECRET = SIGNING_SECRET.encode()
