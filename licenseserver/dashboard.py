from flask import Blueprint, render_template, redirect, url_for, request, flash
from licenseserver.models import db, School, Device, AuditLog
from datetime import datetime
from licenseserver.decorators import token_required  # Added import
from flask_login import login_required


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    schools = School.query.all()
    devices = Device.query.all()
    return render_template('dashboard.html', schools=schools, devices=devices)

@dashboard_bp.route('/device/<int:device_id>/update', methods=['POST'])
@token_required  # Added token_required decorator for security
def update_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        flash('Device not found', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    try:
        device.status = request.form['status']
        device.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        db.session.commit()
        flash('Device updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating device: {str(e)}', 'danger')
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/register_school', methods=['POST'])
@token_required
def register_school():
    school_id = request.form.get('school_id')
    name = request.form.get('name')

    if not school_id or not name:
        flash('School ID and Name are required', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    existing_school = School.query.filter_by(school_id=school_id).first()
    if existing_school:
        flash('School ID already exists', 'warning')
        return redirect(url_for('dashboard.dashboard'))

    new_school = School(school_id=school_id, name=name)
    db.session.add(new_school)
    db.session.commit()
    flash('School registered successfully', 'success')
    return redirect(url_for('dashboard.dashboard'))