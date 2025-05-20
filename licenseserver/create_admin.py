from dotenv import load_dotenv
from extension import db
from models import Admin
from app import app
import os

load_dotenv()

with app.app_context():
    username = "admin"
    password = os.getenv("ADMIN_PASSWORD")

    if not password:
        print("[❌] ADMIN_PASSWORD not set in .env or environment.")
        exit(1)

    existing = Admin.query.filter_by(username=username).first()
    if existing:
        print(f"[⚠️] Admin '{username}' already exists.")
    else:
        admin = Admin(username=username)
        admin.password = password  # Setter will hash it
        db.session.add(admin)
        db.session.commit()
        print(f"[✅] Admin '{username}' created.")
