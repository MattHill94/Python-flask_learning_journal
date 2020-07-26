import datetime
import re

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

db = SqliteDatabase('journal.db')

class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField()

    class Meta:
        database = db

    @classmethod
    def create_user(cls, email, password):
        try:
            with db.transaction():
                cls.create(
                    email=email,
                    password=generate_password_hash(password))
        except IntegrityError:
            raise ValueError('User already exists')

class BaseModel(Model):
    class Meta:
        database = db

class Post(BaseModel):
    user = ForeignKeyField(
        User,
        related_name='posts')
    title = CharField(unique=True)
    date = DateField(default=datetime.datetime.now())
    time_spent = TimeField()
    what_i_learned = TextField()
    resources_to_remember = TextField()

class Tags(BaseModel):
    tag = CharField()

class PostTags(Model):
    post = ForeignKeyField(Post)
    tag = ForeignKeyField(Tags)

    class Meta:
        database = db
        indexes = (
            (('post', 'tag'), True),
        )

    @classmethod
    def tag_current_posts(cls, tag):
        try:
            tag_posts = Post.select().where(Post.what_i_learned.contains(tag.tag))
        except DoesNotExist:
            pass
        else:
            try:
                for post in tag_posts:
                    cls.create(
                        post=post,
                        tag=tag)
            except IntegrityError:
                pass

    @classmethod
    def tag_new_post(cls, post):
        try:
            associated_tags = Tags.select().where(Tags.tag.in_(re.findall(r"[\w']+|[.,!?;]", post.what_i_learned)))
        except DoesNotExist:
            pass
        else:
            try:
                for tag in associated_tags:
                    cls.create(
                        post=post,
                        tag=tag)
            except IntegrityError:
                pass

    @classmethod
    def remove_existing_tag(cls, post):
        try:
            associated_tags = Tags.select().where(Tags.tag.not_in(re.findall(r"[\w']+|[.,!?;]", post.what_i_learned)))
        except DoesNotExist:
            pass
        else:
            for tag in associated_tags:
                try:
                    unwanted_association = cls.get(tag=tag, post=post)
                except DoesNotExist:
                    pass
                else:
                    unwanted_association.delete_instance()

def initialize():
    db.connect()
    db.create_tables([User, Tags, Post, PostTags], safe=True)
    db.close()

