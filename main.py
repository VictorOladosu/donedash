import os
from flask import Flask, render_template, jsonify, request, session
import logging
from datetime import timedelta
from extensions import db, login_manager, csrf
from flask_wtf.csrf import CSRFError
from models import User
from forms import RegistrationForm, LoginForm

# Configure logging with more verbose format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set development mode
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

# Enhanced session configuration for development
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Extended session lifetime
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Enhanced CSRF configuration
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour expiry

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# CSRF error handler with detailed logging
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    logger.error(f"CSRF error occurred: {str(e)}")
    logger.error(f"Request path: {request.path}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Request headers: {dict(request.headers)}")
    
    # Create appropriate form based on the route
    if 'login' in request.path:
        form = LoginForm()
        template = 'auth/login.html'
    else:
        form = RegistrationForm()
        template = 'auth/register.html'
    
    return render_template(template, 
                         form=form,
                         csrf_error="Security token has expired. Please try again."), 400

# Enhanced form validation error logging
@app.after_request
def log_validation_errors(response):
    if request.method == "POST":
        form_errors = session.get('_form_errors')
        if form_errors:
            logger.error(f"Form validation errors for {request.path}:")
            for field, errors in form_errors.items():
                logger.error(f"Field '{field}': {errors}")
            session.pop('_form_errors', None)
    return response

# Session initialization and monitoring
@app.before_request
def before_request():
    session.permanent = True
    if not request.is_secure and app.config['ENV'] == 'production':
        logger.warning(f"Insecure request received for path: {request.path}")
    
    # Initialize session if needed
    if '_fresh' not in session:
        session['_fresh'] = True
        logger.debug(f"New session created for path: {request.path}")
        logger.debug(f"Session ID: {session.get('_id', 'Not set')}")
    
    # Log request details for debugging
    if app.debug:
        logger.debug(f"Request headers: {dict(request.headers)}")
