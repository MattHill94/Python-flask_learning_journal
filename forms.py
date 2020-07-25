from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, ValidationError, Email, Length, EqualTo
from wtforms.fields.html5 import IntegerField, DateField

from models import User
from models import Post
import datetime

def email_exists(form, field):
    """Custom validator to ensure no duplicate users"""
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('A user with that E-mail already exists.')

def title_exists(form, field):
    """Make sure entered title does not already exist"""
    if Post.select().where(Post.title ** field.data).exists():
        raise ValidationError('That title is already in use.')

def tag_exists(form, field):
    """Make sure a duplicate tag is not created"""
    if Tags.select().where(Tags.tag ** field.data).exists():
        raise ValidationError('That tag already exists.')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(),
        Email(),
        email_exists
    ])
    password = PasswordField('Password', validators=[
        InputRequired(),
        Length(min=2),
    ])



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(message='You must enter and email address'),
        Email()
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message='You must enter your password')
    ])


class JournalEntryForm(FlaskForm):
    title = StringField('Title', validators=[
        InputRequired(message='You must give your entry a title'),
        title_exists
    ])

    date = DateField('Date', validators=[
        InputRequired(message='Please enter a date')
    ])

    what_i_learned = TextAreaField('What I Learned', validators=[
        InputRequired(message='You must have learned something')
    ])

    resources_to_remember = TextAreaField('Resources to Remember')


class EditForm(FlaskForm):
    title = StringField('Title', validators=[
        InputRequired(message='You must give your entry a title'),
    ])
    date = DateField('Date')
    what_i_learned = TextAreaField('What I Learned', validators=[
        InputRequired(message='You must have learned something')
    ])
    resources_to_remember = TextAreaField('Resources to Remember')
