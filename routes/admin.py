from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from models.subscription import Subscription
from models.analytics import UserMetrics, SystemMetrics
from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    # Get system-wide metrics
    total_users = db.session.query(func.count(User.id)).scalar()
    active_subscriptions = db.session.query(func.count(Subscription.id))\
        .filter(Subscription.status == 'active').scalar()
    total_revenue = db.session.query(func.sum(UserMetrics.value))\
        .filter(UserMetrics.metric_type == 'revenue').scalar() or 0

    # Get recent metrics
    recent_metrics = SystemMetrics.query\
        .order_by(SystemMetrics.date.desc())\
        .limit(30)\
        .all()

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_subscriptions=active_subscriptions,
                         total_revenue=total_revenue,
                         recent_metrics=recent_metrics)

@admin.route('/admin/subscriptions')
@login_required
@admin_required
def subscriptions():
    subscriptions = Subscription.query\
        .join(User)\
        .order_by(Subscription.created_at.desc())\
        .all()
    return render_template('admin/subscriptions.html', subscriptions=subscriptions)

@admin.route('/admin/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)
