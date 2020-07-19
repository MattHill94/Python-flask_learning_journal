from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, DateTimeField, DateField, TimeField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email, Length, EqualTo, Regexp, ValidationError )
import datetime

from models import User
from models import Post


class JournalEntryForm(FlaskForm):
    title = StringField("Title",
                        validators=[DataRequired()])

    date = DateField("Date")

    time_from = TimeField("Time From")

    time_to = TimeField("Time to")

    what_i_learned = TextAreaField("What did you learn",
                                    validators=[DataRequired()])
    resources_to_remember = TextAreaField("Resources to remember",
                                    validators=[DataRequired()])
    submit = SubmitField("Publish post!")

def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    ) 

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
