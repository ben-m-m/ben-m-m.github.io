import jwt
import hmac
import hashlib
import base64
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from functools import wraps
from flask import request, jsonify, Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from licenseserver.models import db, Admin

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
        'admin_id': 1  # Optional: used for traceability
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    signature = sign_license_data(token)
    return {'token': token, 'signature': signature}

# -------------------- Token Decorators -------------------- #

# Decorator for routes requiring token with admin privileges
def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Authorization header missing or malformed'}), 401

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if not payload.get('admin_id'):
                return jsonify({'message': 'Token missing admin_id'}), 403
            admin = Admin.query.get(payload['admin_id'])
            if not admin:
                return jsonify({'message': 'Admin not found'}), 404
        except ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated

# Decorator for license check token (school_id + machine_id)
def license_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Authorization header missing or malformed'}), 401

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if not payload.get('school_id') or not payload.get('machine_id'):
                return jsonify({'message': 'Token missing device identifiers'}), 403
        except ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        request.license_payload = payload
        return f(*args, **kwargs)
    return decorated

# -------------------- Auth Blueprint -------------------- #

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
