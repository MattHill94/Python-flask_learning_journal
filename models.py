import datetime
from peewee import *
from flask_login import UserMixin
from flask import Flask
from flask_bcrypt import generate_password_hash

db = SqliteDatabase('journal.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    def get_posts(self):
        return Post.select().where(Post.user == self)
    
    def get_stream(self):
        return Post.select().where(
            (Post.user == self)
        )
        
    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with db.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

    class Meta:
        database = db
        oder_by = ('joined_at' , )

class Post(Model):
    user = ForeignKeyField(
        rel_model=User,
        related_name='posts'
    )
    title = CharField(max_length=100)
    date = DateField()
    time_from = TimeField()
    time_to = TimeField()
    what_i_learned = CharField(max_length=250)
    resources_to_remember = CharField(max_length=250)

    class Meta:
        database = db

    @classmethod
    def create_post(cls, title, date, time_from, time_to, what_i_learned, resources_to_remember):
        try:
            cls.create(
                title=title,
                date=date,
                time_from=time_from,
                time_to=time_to,
                what_i_learned=what_i_learned,
                resources_to_remember=resources_to_remember,
            )
        except IntegrityError:
            raise ValueError("something happened")


def initialize():
    db.connect()
    db.create_tables([Post, User], safe=True)
    db.close()     