from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from models import db, School, Device, AuditLog
from utils import device_status, sign_response
from auth import token_required
from dashboard import dashboard_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = config.SECRET_KEY
db.init_app(app)

limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])

app.register_blueprint(dashboard_bp)

@app.before_request
def create_tables():
    db.create_all()

# Helper to log actions
def log_action(device_id, action, details=''):
    log = AuditLog(device_id=device_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()

# API Endpoints
@app.route('/register_school', methods=['POST'])
@token_required
def register_school():
    data = request.json
    if School.query.filter_by(school_id=data['school_id']).first():
        return jsonify({'message': 'School already exists'}), 400
    school = School(school_id=data['school_id'], name=data['name'])
    db.session.add(school)
    db.session.commit()
    return jsonify({'message': 'School registered successfully'})

@app.route('/register_device', methods=['POST'])
@token_required
def register_device():
    data = request.json
    school = School.query.filter_by(school_id=data['school_id']).first()
    if not school:
        return jsonify({'message': 'Invalid School ID'}), 404
    device = Device(machine_id=data['machine_id'], school_id=data['school_id'],
                    expiry_date=datetime.utcnow() + timedelta(days=data.get('validity_days', 30)))
    db.session.add(device)
    db.session.commit()
    log_action(device.id, 'Device Registered', f'Validity: {device.expiry_date}')
    return jsonify({'message': 'Device registered successfully'})

@app.route('/check_status', methods=['POST'])
@limiter.limit("10 per minute")
@token_required
def check_status():
    data = request.json
    device = Device.query.filter_by(machine_id=data['machine_id'], school_id=data['school_id']).first()
    if not device:
        return jsonify({'status': 'Unregistered'}), 404
    device.last_checked = datetime.utcnow()
    db.session.commit()
    log_action(device.id, 'Status Check', f'Status: {device_status(device)}')
    response_data = {'status': device_status(device), 'expiry_date': device.expiry_date.strftime('%Y-%m-%d')}
    response_data['signature'] = sign_response(response_data)
    return jsonify(response_data)

@app.route('/update_device', methods=['POST'])
@token_required
def update_device():
    data = request.json
    device = Device.query.filter_by(machine_id=data['machine_id'], school_id=data['school_id']).first()
    if not device:
        return jsonify({'message': 'Device not found'}), 404
    if 'status' in data:
        device.status = data['status']
    if 'expiry_date' in data:
        device.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
    db.session.commit()
    log_action(device.id, 'Device Updated', f"Status: {device.status}, Expiry: {device.expiry_date}")
    return jsonify({'message': 'Device updated successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
