from flask import Flask, g, render_template, flash, redirect, url_for, abort, request
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user, 
                        login_required, current_user)

import forms 
import models
from models import User
from models import Post
import datetime

DEBUG = True
PORT = 8000
HOST = "0.0.0.0"

app = Flask(__name__)
app.secret_key = "khewhoifj43kfnierkskje6667384fkldehjkdjhfje"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.db
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

@app.route("/")
@login_required
def index():
    	template = "index.html"
    	stream = models.Post
    	return render_template("index.html", stream=stream)

@app.route('/stream')
@app.route('/stream/<username>')
@login_required
def stream(username=None):
    template = 'user_stream.html'
    if username and username != current_user.username:
        try:
            user = models.User.select().where(
                models.User.username**username).get()
        except models.DoesNotExist:
            abort(404)
        else:
            stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'stream.html'
    return render_template(template, stream=stream, user=user)













@app.route("/entries/new", methods=('GET', 'POST'))
@login_required
def entry():
    form = forms.JournalEntryForm()
    if form.validate_on_submit():
        flash("Woooo", "Success")
        models.Post.create_post(
            title=form.title.data,
            date=form.date.data,
            time_from=form.time_from.data,
            time_to=form.time_to.data,
            what_i_learned=form.what_i_learned.data,
            resources_to_remember=form.resources_to_remember.data
        )                
        return redirect(url_for('entry'))
    return render_template("new.html", form=form)

"""@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.JournalEntryForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user.id,
                           content=form.content.data.strip())
        flash("Message posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('post.html', form=form)"""


@app.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html', stream=posts)

@app.route("/Register", methods=('GET', 'POST'))
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        flash("Woooo", "Success")
        models.User.create_user(
            username = form.username.data,
            email = form.email.data,
            password = form.password.data
        )
        return redirect(url_for('index'))
    return render_template('registraition.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ =='__main__':
    models.initialize()  
    app.run(debug=DEBUG, host=HOST, port=PORT)