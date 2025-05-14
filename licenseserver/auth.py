import jwt
from flask import request, jsonify
from config import JWT_SECRET

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token.split()[1], JWT_SECRET, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated
