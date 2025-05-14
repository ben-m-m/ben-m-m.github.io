from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import db, School, Device
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    schools = School.query.all()
    devices = Device.query.all()
    return render_template('dashboard.html', schools=schools, devices=devices)

@dashboard_bp.route('/device/<int:device_id>/update', methods=['POST'])
def update_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        flash('Device not found')
        return redirect(url_for('dashboard.dashboard'))
    device.status = request.form['status']
    device.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
    db.session.commit()
    flash('Device updated successfully')
    return redirect(url_for('dashboard.dashboard'))
