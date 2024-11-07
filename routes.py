from flask import render_template, redirect, url_for, flash, request, jsonify, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFError
from extensions import db
from main import app, logger
from models import User, Service, Booking, Message, Review, Notification
from forms import LoginForm, RegistrationForm, ServiceForm, BookingForm, MessageForm, ReviewForm
from datetime import datetime
import os
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func, case
import json
from queue import Queue
import threading

clients = {}
lock = threading.Lock()

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
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
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
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already exists. Please choose another.', 'danger')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form)

@app.route('/services')
def services():
    category = request.args.get('category')
    search = request.args.get('search')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=int)
    available_on = request.args.get('available_on')
    location = request.args.get('location')
    sort = request.args.get('sort', 'newest')

    query = db.session.query(
        Service,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count'),
        func.count(Booking.id).label('booking_count')
    ).outerjoin(Review, Review.service_id == Service.id
    ).outerjoin(Booking, Booking.service_id == Service.id
    ).group_by(Service.id)

    if category:
        query = query.filter(Service.category == category)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Service.title.ilike(search_term),
                Service.description.ilike(search_term)
            )
        )

    if min_price is not None:
        query = query.filter(Service.rate >= min_price)
    if max_price is not None:
        query = query.filter(Service.rate <= max_price)

    if min_rating:
        query = query.having(func.avg(Review.rating) >= min_rating)

    if available_on:
        try:
            available_datetime = datetime.fromisoformat(available_on)
            pass
        except ValueError:
            flash('Invalid date format for availability filter', 'warning')

    if location:
        pass

    if sort == 'price_low':
        query = query.order_by(Service.rate.asc())
    elif sort == 'price_high':
        query = query.order_by(Service.rate.desc())
    elif sort == 'rating':
        query = query.order_by(func.avg(Review.rating).desc().nullslast())
    elif sort == 'popular':
        query = query.order_by(func.count(Booking.id).desc())
    else:
        query = query.order_by(Service.created_at.desc())

    results = query.all()
    
    services = []
    for service, avg_rating, review_count, booking_count in results:
        service.avg_rating = float(avg_rating) if avg_rating else None
        service.review_count = review_count
        service.booking_count = booking_count
        services.append(service)

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

@app.route('/stream')
@login_required
def stream():
    def event_stream():
        notifications = Notification.query.filter_by(
            user_id=current_user.id,
            read=False
        ).order_by(Notification.created_at.desc()).all()
        
        for notification in notifications:
            data = {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'type': notification.type,
                'created_at': notification.created_at.isoformat()
            }
            yield f"data: {json.dumps(data)}\n\n"
        
        queue = Queue()
        client_id = id(queue)
        
        with lock:
            clients[client_id] = queue
        
        try:
            while True:
                data = queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            with lock:
                clients.pop(client_id, None)
    
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    try:
        notifications = Notification.query.filter_by(
            user_id=current_user.id,
            read=False
        ).all()
        
        for notification in notifications:
            notification.read = True
        
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error marking notifications as read: {str(e)}")
        return jsonify({'error': 'Failed to mark notifications as read'}), 500

def send_notification(user_id, title, message, notification_type):
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type
        )
        db.session.add(notification)
        db.session.commit()
        
        data = {
            'id': notification.id,
            'title': title,
            'message': message,
            'type': notification_type,
            'created_at': notification.created_at.isoformat()
        }
        
        with lock:
            for client_queue in clients.values():
                try:
                    client_queue.put_nowait(data)
                except:
                    continue
        
        logger.info(f"Notification sent to user {user_id}: {title}")
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")

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
        
        send_notification(
            service.provider_id,
            'New Booking Request',
            f'New booking request for {service.title} on {booking.booking_date.strftime("%Y-%m-%d %H:%M")}',
            'booking_update'
        )
        
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
    
    if booking.payment_status == 'paid':
        send_notification(
            booking.provider_id,
            'Payment Received',
            f'Payment received for booking #{booking.id} - {booking.service.title}',
            'payment'
        )
    
    return render_template('services/booking_confirmation.html', booking=booking)

@app.route('/messages')
@login_required
def messages():
    conversations = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
    ).distinct(Message.sender_id, Message.receiver_id).all()
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
        
        send_notification(
            user_id,
            'New Message',
            f'You have a new message from {current_user.username}',
            'message'
        )
        
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