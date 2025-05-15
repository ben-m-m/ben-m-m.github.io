import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "")
    SIGNING_SECRET_RAW = os.getenv("SIGNING_SECRET", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Check critical secrets on config load
    if not SECRET_KEY or not JWT_SECRET_KEY or not SIGNING_SECRET_RAW:
        print("[❌] Missing critical secrets. Please check your .env or environment variables.")
        exit(1)

    # Encoded signing secret for HMAC usage
    SIGNING_SECRET = SIGNING_SECRET_RAW.encode()

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///licenses.db")

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # Must be set in production

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
