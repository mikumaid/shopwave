from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    MultipleFileField, TextAreaField, IntegerField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from shopwave.models import User

USERNAME_LENGTH = dict(min=3, max=25, message='Username must be between 3 and 25 characters.')
IMAGE_FORMATS = ['jpg', 'png', 'jpeg']
IMAGE_ALLOWED = FileAllowed(IMAGE_FORMATS, 'Images only!')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(**USERNAME_LENGTH)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    admin_key = PasswordField('Admin Key')
    submit = SubmitField('Register')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError(f'Username {username.data} is already taken. Please choose a different one.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError(f'Email {email.data} is already registered. Please use a different email.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(**USERNAME_LENGTH)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(IMAGE_FORMATS)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError(f'Username {username.data} is already taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError(f'Email {email.data} is already registered. Please use a different email.')

class BaseProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    price = IntegerField('Price', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=2000)])
    detail = TextAreaField('Detail', validators=[DataRequired(), Length(max=2000)])
    images = MultipleFileField('Product Images', validators=[IMAGE_ALLOWED])

class ProductForm(BaseProductForm):
    submit = SubmitField('Add Product')

class EditProductForm(BaseProductForm):
    submit = SubmitField('Update Product')
