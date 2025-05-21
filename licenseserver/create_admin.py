# licenseserver/create_admin.py

from dotenv import load_dotenv
from licenseserver.extension import db
from .models import Admin
import os

load_dotenv()

def ensure_admin():
    from licenseserver.app import app
    with app.app_context():
        username = "admin"
        password = os.getenv("ADMIN_PASSWORD")

        if not password:
            print("[❌] ADMIN_PASSWORD not set in .env or environment.")
            return

        existing = Admin.query.filter_by(username=username).first()
        if existing:
            print(f"[⚠️] Admin '{username}' already exists.")
        else:
            admin = Admin(username=username)
            admin.password = password  # uses password setter
            db.session.add(admin)
            db.session.commit()
            print(f"[✅] Admin '{username}' created.")

# Allows both import and standalone run
if __name__ == "__main__":
    ensure_admin()
