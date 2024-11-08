from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False)  # 'provider' or 'customer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Provider specific fields
    hourly_rate = db.Column(db.Float)
    description = db.Column(db.Text)
    skills = db.Column(db.String(500))
    
    # Location fields
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(200))
    
    # Notifications relationship
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Service availability
    availability_start = db.Column(db.Time)
    availability_end = db.Column(db.Time)
    availability_days = db.Column(db.String(50))  # Comma-separated list of available days
    
    # Location information
    service_area = db.Column(db.Float)  # Service area radius in miles
    location_flexible = db.Column(db.Boolean, default=False)
    
    # Additional service details
    experience_years = db.Column(db.Integer)
    qualifications = db.Column(db.Text)
    languages = db.Column(db.String(200))  # Comma-separated list of languages
    
    # Search optimization fields
    tags = db.Column(db.String(500))  # Comma-separated tags for better search
    featured = db.Column(db.Boolean, default=False)
    
    # Relationships
    provider = db.relationship('User', backref='services')
    reviews = db.relationship('Review', backref='service', lazy='dynamic')
    bookings = db.relationship('Booking', backref='service', lazy='dynamic')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    booking_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    hours = db.Column(db.Float, nullable=False, default=1.0)  # Number of hours booked
    total_amount = db.Column(db.Float, nullable=False)  # Total amount to be paid
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid
    payment_intent_id = db.Column(db.String(100))  # Stripe payment intent ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # booking_update, payment, message
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
