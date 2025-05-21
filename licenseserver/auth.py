import jwt
import hmac
import hashlib
import base64
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from functools import wraps
from flask import request, jsonify,Blueprint, render_template, redirect, url_for, flash
from licenseserver.models import db, Admin
from flask_login import login_required

# Load secrets from .env
load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
SIGNING_SECRET = os.getenv('SIGNING_SECRET')

if not JWT_SECRET or not SIGNING_SECRET:
    print("[❌] Missing secrets. Please check your .env file.")
    exit(1)

# -------------------- License Token Functions -------------------- #

def sign_license_data(data: str) -> str:
    signature = hmac.new(SIGNING_SECRET.encode(), data.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode()

def generate_license_token(school_id: str, machine_id: str, validity_days: int = 30) -> dict:
    payload = {
        'school_id': school_id,
        'machine_id': machine_id,
        'exp': datetime.utcnow() + timedelta(days=validity_days),
        'iat': datetime.utcnow(),
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    license_signature = sign_license_data(token)
    return {
        'token': token,
        'signature': license_signature
    }


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token.split()[1], JWT_SECRET, algorithms=["HS256"])
        except Exception:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register_admin', methods=['GET', 'POST'])
@login_required
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if Admin.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
        else:
            new_admin = Admin(username=username, password=password)
            db.session.add(new_admin)
            db.session.commit()
            flash('Admin registered successfully!', 'success')
            return redirect(url_for('dashboard.dashboard'))

    return render_template('register_admin.html')