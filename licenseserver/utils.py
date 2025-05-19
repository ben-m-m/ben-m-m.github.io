import os
from datetime import datetime
import hmac, hashlib, base64
from config import config

env = os.getenv("FLASK_ENV", "default")
SIGNING_SECRET = config[env].SIGNING_SECRET_RAW
SECRET_KEY = config[env].SECRET_KEY
def is_expired(expiry_date):
    return datetime.utcnow() > expiry_date

def device_status(device):
    if device.status != 'Active':
        return device.status
    if is_expired(device.expiry_date):
        return 'Expired'
    return 'Active'

def sign_response(data: dict):
    message = str(data).encode()
    signature = hmac.new(SIGNING_SECRET, message, hashlib.sha256).digest()
    return base64.b64encode(signature).decode()
