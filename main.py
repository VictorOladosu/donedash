import os
from flask import Flask, render_template, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import logging
from datetime import timedelta

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

# Enhanced session configuration
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

# Enhanced CSRF configuration
app.config['WTF_CSRF_SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour expiry
app.config['WTF_CSRF_SSL_STRICT'] = False  # For development
csrf = CSRFProtect(app)

# CSRF error handler with detailed logging
@app.errorhandler(400)
def handle_csrf_error(e):
    error_msg = str(e)
    logger.error(f"CSRF error occurred: {error_msg}")
    logger.error(f"Request path: {request.path}")
    logger.error(f"Request method: {request.method}")
    return jsonify(error="CSRF token validation failed. Please try again."), 400

# Enhanced CSRF token logging
@app.after_request
def after_request(response):
    if request.method == "GET":
        token = session.get('csrf_token')
        if token:
            logger.debug(f"Generated CSRF token for path: {request.path}")
            logger.debug(f"Session ID: {session.get('_id', 'Not set')}")
    return response

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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

# Session monitoring
@app.before_request
def before_request():
    if not session.get('_fresh'):
        logger.debug(f"New session created for path: {request.path}")
    session.permanent = True
