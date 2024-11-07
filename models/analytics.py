from extensions import db
from datetime import datetime

class UserMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # 'booking_count', 'revenue', 'rating_avg'
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='metrics')

class SystemMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False)  # 'total_users', 'total_revenue', 'active_subscriptions'
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
