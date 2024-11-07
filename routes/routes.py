from flask import render_template, redirect, url_for, flash, request, jsonify, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFError
from extensions import db
from models import User, Service, Booking, Message, Review, Notification
from forms import LoginForm, RegistrationForm, ServiceForm, BookingForm, MessageForm, ReviewForm
from datetime import datetime
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func
import json
from queue import Queue
import threading
from . import main
from main import logger

# Rest of the routes.py content remains the same, just change 'app' to 'main'
# For example: @app.route('/') becomes @main.route('/')
