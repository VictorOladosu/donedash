import os
import logging
from datetime import timedelta
from flask import Flask, render_template, jsonify, request, session
from extensions import db, login_manager, csrf
from models import User
from forms import RegistrationForm, LoginForm
from flask_wtf.csrf import CSRFError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Set development mode
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    
    # Session configuration
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    
    # CSRF configuration
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from routes.admin import admin
    from routes import main as main_blueprint
    
    app.register_blueprint(admin)
    app.register_blueprint(main_blueprint)
    
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

    return app

# Create the application instance
app = create_app()