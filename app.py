from flask import (Flask, g, render_template, flash, redirect, url_for, abort, )
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user, current_user, login_required)

import forms
import models
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
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
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

@app.route('/')
def index():
    """Index page is also a list of posts"""
    posts = models.Post.select().limit(8)
    display_posts = []
    for post in posts:
        post_tags = set((models.Tags.select()
                          .join(models.PostTags)
                          .where(models.PostTags.post == post)))
        display_posts.append([post, post_tags])
    if current_user.is_authenticated is False:
                return redirect(url_for('register'))
    return render_template('index.html', posts=display_posts)

@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def create_new():
    """Create a new journal entry."""
    form = forms.JournalEntryForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user.get_id(),
                            title=form.title.data.strip(),
                            date=form.date.data,
                            time_spent=form.time_spent.data,
                            what_i_learned=form.what_i_learned.data.strip(),
                            resources_to_remember=form.resources_to_remember.data.strip()
                            )
        flash("Entry created", "success")
        models.PostTags.tag_new_post(models.Post.get(title=form.title.data.strip()))
        return redirect(url_for('view_posts'))
    return render_template('new.html', form=form)

@app.route('/entries/<int:id>')
@login_required
def view_post(id):
    """View a journal entry with detail."""
    try:
        current_post = models.Post.get_by_id(id)
    except models.DoesNotExist:
        abort(404)
    else:
        post_tags = set((models.Tags.select()
                          .join(models.PostTags)
                          .where(models.PostTags.post == current_post)))
        return render_template('detail.html', post=current_post, tags=post_tags)

@app.route('/entries')
def view_posts():
    """Page to view a list of entries.  More entries are viewed"""
    posts = models.Post.select().limit(24)
    display_posts = []
    for post in posts:
        post_tags = set((models.Tags.select()
                          .join(models.PostTags)
                          .where(models.PostTags.post == post)))
        display_posts.append([post, post_tags])
    return render_template('index.html', posts=display_posts)

@app.route('/entries/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete_post(id):
    """Delete a journal entry"""
    try:
        post = models.Post.get_by_id(id)
        try:
            tag_association = models.PostTags.get(post=post)
            tag_association.delete_instance()
        except models.DoesNotExist:
            pass
    except models.DoesNotExist:
        abort(404)
    else:
        post.delete_instance()
        flash("Entry has been deleted", "success")
        return redirect(url_for('view_posts'))

@app.route('/entries/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_post(id):
    """Edit a journal entry"""
    try:
        post = models.Post.get_by_id(id)
    except models.DoesNotExist:
        abort(404)
    else:
        form = forms.EditForm(
            title=post.title,
            date=post.date,
            time_spent=post.time_spent,
            what_i_learned=post.what_i_learned,
            resources_to_remember=post.resources_to_remember
        )
        if form.validate_on_submit():
            post.title = form.title.data.strip()
            post.date_created = form.date.data
            post.time_spent = form.time_spent.data
            post.what_i_learned = form.what_i_learned.data.strip()
            post.resources_to_remember = form.resources_to_remember.data.strip()
            post.save()
            flash("Entry has been updated", "success")
            models.PostTags.tag_new_post(models.Post.get(title=form.title.data.strip()))
            models.PostTags.remove_existing_tag(models.Post.get(title=form.title.data.strip()))
            return redirect(url_for('view_posts'))
        return render_template('edit.html', form=form, post=post)

@app.route("/Register", methods=('GET', 'POST'))
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        flash("Woooo", "Success")
        models.User.create_user(
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

@app.route('/new_tag', methods=('GET', 'POST'))
@login_required
def create_tag():
    """create a tag to organize your journal entries."""
    form = forms.TagForm()
    if form.validate_on_submit():
        models.Tags.create(tag=form.tag.data.strip())
        flash('Tag Created', 'success')
        models.PostTags.tag_current_posts(models.Tags.get(tag=form.tag.data.strip()))
        return redirect(url_for('view_posts'))
    return render_template('create_tag.html', form=form)

@app.route('/entries/<tag>')
@login_required
def posts_by_tag(tag):
    """Shows all entries with a selected tag."""
    display_posts = []
    try:
        tagged_posts = set((models.Post
                              .select()
                              .join(models.PostTags)
                              .join(models.Tags)
                              .where(models.Tags.tag == tag)
                              .order_by(models.Post.date.desc())))
    except models.DoesNotExist:
        redirect(url_for('view_posts'))
    else:
        for post in tagged_posts:
            post_tags = set((models.Tags.select()
                              .join(models.PostTags)
                              .where(models.PostTags.post == post)))
            display_posts.append([post, post_tags])
    return render_template('index.html', posts=display_posts)

@app.route('/tags/<tag>', methods=('GET', 'POST'))
@login_required
def delete_tag(tag):
    """Delete an unused tag"""
    try:
        unwanted_tag = models.Tags.get(tag=tag)
        tag_association = models.PostTags.get(tag=unwanted_tag)
    except models.DoesNotExist:
        abort(404)
    else:
        tag_association.delete_instance()
        unwanted_tag.delete_instance()
        flash("Tag has been deleted", "success")
        return redirect(url_for('view_posts'))

@app.route('/tags')
@login_required
def view_tags():
    """View all existing tags to find post associated with them."""
    tags = set(models.Tags.select())
    return render_template('tags.html', tags=tags)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    models.initialize()
    try:
        with models.db.transaction():
            models.User.create_user(
                email='example@email.co.uk',
                password='password1',
            )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)