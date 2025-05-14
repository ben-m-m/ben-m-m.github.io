from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(256), nullable=False)
    school_id = db.Column(db.String(100), db.ForeignKey('school.school_id'), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=30))
    status = db.Column(db.String(50), nullable=False, default='Active')
    last_checked = db.Column(db.DateTime, nullable=True)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    action = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
