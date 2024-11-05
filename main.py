import os
from flask import Flask, render_template, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import logging
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = True  # Enable in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

# CSRF configuration
app.config['WTF_CSRF_SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']  # Use same secret key
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour expiry
csrf = CSRFProtect(app)

# CSRF error handler
@app.errorhandler(400)
def handle_csrf_error(e):
    logger.error(f"CSRF error occurred: {str(e)}")
    return jsonify(error="CSRF token validation failed. Please try again."), 400

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Log all form validation errors
@app.after_request
def log_validation_errors(response):
    if response.status_code == 200 and request.method == "POST":
        form_errors = session.get('_form_errors')
        if form_errors:
            logger.debug(f"Form validation errors: {form_errors}")
            session.pop('_form_errors', None)
    return response
