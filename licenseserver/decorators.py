import os
import jwt
import hmac
import hashlib
import base64
from flask import request, jsonify
from functools import wraps
from licenseserver.config import config

env = os.getenv("FLASK_ENV", "default")
JWT_SECRET_KEY = config[env].JWT_SECRET_KEY
SIGNING_SECRET = config[env].SIGNING_SECRET
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token.split()[1], JWT_SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated

def sign_license_data(data: str) -> str:
    # SIGNING_SECRET is bytes, so no need to encode again
    signature = hmac.new(SIGNING_SECRET, data.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode()

def verify_signature(token: str, provided_signature: str) -> bool:
    expected_signature = hmac.new(SIGNING_SECRET, token.encode(), hashlib.sha256).digest()
    expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode()
    return hmac.compare_digest(expected_signature_b64, provided_signature)

def verify_license_token(token: str, signature: str) -> dict | None:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        if not verify_signature(token, signature):
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def license_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-License-Token')
        signature = request.headers.get('X-License-Signature')

        if not token or not signature:
            return jsonify({'error': 'Missing license token or signature.'}), 401

        payload = verify_license_token(token, signature)
        if not payload:
            return jsonify({'error': 'Invalid or expired license.'}), 401

        request.license_payload = payload
        return f(*args, **kwargs)
    return decorated_function
