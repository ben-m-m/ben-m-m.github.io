from flask import Flask, jsonify, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import School, Device, AuditLog
from extension import db
from decorators import token_required, license_required
from utils import device_status
from config import SECRET_KEY
from dashboard import dashboard_bp
import webbrowser
from models import Admin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from auth import auth_bp



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///licenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = SECRET_KEY

# Initialize SQLAlchemy
db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Register dashboard blueprint
app.register_blueprint(dashboard_bp)

app.register_blueprint(auth_bp)

# Ensure tables are created once at startup (Flask 3.x fix)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# ---------------------- API Endpoints ----------------------

@app.route('/api/schools', methods=['GET'])
@token_required
def get_schools():
    schools = School.query.all()
    result = [{'school_id': s.school_id, 'name': s.name} for s in schools]
    return jsonify(result), 200

@app.route('/api/devices', methods=['GET'])
@token_required
def get_devices():
    devices = Device.query.all()
    result = []
    for d in devices:
        result.append({
            'id': d.id,
            'machine_id': d.machine_id,
            'school_id': d.school_id,
            'status': device_status(d),
            'expiry_date': d.expiry_date.strftime('%Y-%m-%d'),
            'last_checked': d.last_checked.strftime('%Y-%m-%d %H:%M:%S') if d.last_checked else None
        })
    return jsonify(result), 200

@app.route('/api/device/check', methods=['POST'])
@license_required
def check_device():
    payload = request.license_payload
    machine_id = payload.get('machine_id')
    school_id = payload.get('school_id')

    device = Device.query.filter_by(machine_id=machine_id, school_id=school_id).first()
    if not device:
        return jsonify({'error': 'Device not registered'}), 404

    device.last_checked = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'machine_id': device.machine_id,
        'status': device_status(device),
        'expiry_date': device.expiry_date.strftime('%Y-%m-%d')
    }), 200

@app.route('/audit-logs')
def audit_logs():
    school_id = request.args.get('school_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = AuditLog.query
    if school_id:
        query = query.filter(AuditLog.school_id == school_id)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)

    audit_logs = query.order_by(AuditLog.timestamp.desc()).all()
    schools = School.query.all()

    return render_template('audit_logs.html', audit_logs=audit_logs, schools=schools)

@app.route('/devices')
def devices():
    search = request.args.get('search', '')
    status = request.args.get('status', '')

    query = Device.query
    if search:
        query = query.filter(
            Device.machine_id.contains(search) | Device.school_id.contains(search)
        )
    if status:
        if status == 'Expired':
            query = query.filter(Device.expiry_date < datetime.utcnow())
        else:
            query = query.filter(Device.status == status)

    devices = query.order_by(Device.id.desc()).all()
    return render_template('devices.html', devices=devices)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password == password:  # Ideally hash+check password
            login_user(admin)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    # Redirect to dashboard home page
    return redirect(url_for('dashboard.dashboard'))

# ---------------------- Run ----------------------
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password == password:  # Ideally hash+check password
            login_user(admin)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))"""

if __name__ == '__main__':
    webbrowser.open_new('http://127.0.0.1:5000/dashboard')
    app.run(debug=True, port=5000)
