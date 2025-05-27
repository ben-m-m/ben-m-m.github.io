from functools import wraps
from flask import request, jsonify, redirect, url_for, flash
from flask_login import current_user
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from licenseserver.models import Admin
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Authorization header missing or malformed'}), 401

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            admin_id = payload.get('admin_id')
            if not admin_id:
                return jsonify({'message': 'Token payload invalid (missing admin_id)'}), 401
            admin = Admin.query.get(admin_id)
            if not admin:
                return jsonify({'message': 'Admin not found'}), 401
        except ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated


def license_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.json.get('token')
        if not token:
            return jsonify({'message': 'Token required'}), 401
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.license_payload = payload
        except ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated


def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You need to be logged in as admin to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
