from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFError
from extensions import db
from main import app, logger
from models import User, Service, Booking, Message, Review
from forms import LoginForm, RegistrationForm, ServiceForm, BookingForm, MessageForm, ReviewForm
from datetime import datetime
import os
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError

@app.route('/')
def index():
    services = Service.query.order_by(Service.created_at.desc()).limit(6).all()
    return render_template('index.html', services=services)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                session.permanent = True  # Use permanent session
                logger.info(f"User {user.email} logged in successfully")
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('index'))
            
            logger.warning(f"Failed login attempt for email: {form.email.data}")
            flash('Invalid email or password. Please try again.', 'danger')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
    
    if form.errors:
        logger.debug(f"Login form validation errors: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.title()}: {error}', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists. Please choose another.', 'danger')
                return render_template('auth/register.html', form=form)
            
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered. Please use a different email.', 'danger')
                return render_template('auth/register.html', form=form)
            
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form)

@app.route('/services')
def services():
    category = request.args.get('category')
    query = Service.query
    if category:
        query = query.filter_by(category=category)
    services = query.order_by(Service.created_at.desc()).all()
    return render_template('services/list.html', services=services)

@app.route('/service/<int:id>')
def service_detail(id):
    service = Service.query.get_or_404(id)
    reviews = Review.query.filter_by(service_id=id).all()
    booking_form = BookingForm()
    review_form = ReviewForm()
    return render_template('services/detail.html', service=service, reviews=reviews,
                         booking_form=booking_form, review_form=review_form)

@app.route('/service/create', methods=['GET', 'POST'])
@login_required
def create_service():
    if current_user.role != 'provider':
        flash('Only service providers can create services', 'danger')
        return redirect(url_for('index'))
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            provider_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            rate=form.rate.data,
            category=form.category.data
        )
        db.session.add(service)
        db.session.commit()
        flash('Service created successfully!', 'success')
        return redirect(url_for('services'))
    return render_template('services/create.html', form=form)

@app.route('/booking/create/<int:service_id>', methods=['POST'])
@login_required
def create_booking(service_id):
    if current_user.role != 'customer':
        flash('Only customers can make bookings', 'danger')
        return redirect(url_for('services'))
    
    form = BookingForm()
    if form.validate_on_submit():
        service = Service.query.get_or_404(service_id)
        hours = form.hours.data
        total_amount = service.rate * hours
        
        booking = Booking(
            service_id=service_id,
            customer_id=current_user.id,
            provider_id=service.provider_id,
            booking_date=form.booking_date.data,
            hours=hours,
            total_amount=total_amount,
            status='pending'
        )
        db.session.add(booking)
        db.session.commit()
        
        return redirect(url_for('payment', booking_id=booking.id))
    return redirect(url_for('service_detail', id=service_id))

@app.route('/payment/<int:booking_id>')
@login_required
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    if booking.payment_status == 'paid':
        flash('This booking has already been paid for', 'info')
        return redirect(url_for('booking_confirmation', booking_id=booking_id))
    
    return render_template(
        'services/payment.html',
        booking=booking,
        stripe_publishable_key=os.environ['STRIPE_PUBLISHABLE_KEY']
    )

@app.route('/booking-confirmation/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
    return render_template('services/booking_confirmation.html', booking=booking)

@app.route('/messages')
@login_required
def messages():
    conversations = db.session.query(Message.sender_id, Message.receiver_id).distinct().all()
    return render_template('messages/chat.html', conversations=conversations)

@app.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            receiver_id=user_id,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('chat', user_id=user_id))
    
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at).all()
    return render_template('messages/chat.html', messages=messages, form=form, other_user_id=user_id)

@app.route('/bookings')
@login_required
def bookings():
    if current_user.role == 'customer':
        bookings = Booking.query.filter_by(customer_id=current_user.id).all()
    else:
        bookings = Booking.query.filter_by(provider_id=current_user.id).all()
    return render_template('bookings.html', bookings=bookings)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
