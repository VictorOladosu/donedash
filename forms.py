from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, ValidationError, NumberRange
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('provider', 'Service Provider')])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class ServiceForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    rate = FloatField('Hourly Rate', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('cleaning', 'Cleaning'),
        ('handyman', 'Handyman'),
        ('moving', 'Moving'),
        ('gardening', 'Gardening'),
        ('other', 'Other')
    ])

class BookingForm(FlaskForm):
    booking_date = DateTimeField('Booking Date', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    hours = FloatField('Number of Hours', validators=[DataRequired(), NumberRange(min=1, max=24)], default=1.0)
    message = TextAreaField('Message to Provider')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(str(i), str(i)) for i in range(1, 6)], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
