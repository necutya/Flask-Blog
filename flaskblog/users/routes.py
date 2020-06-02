from flask import Blueprint
import os
from flaskblog.models import User, Post
from flask import render_template, url_for, request, flash, redirect, current_app
from flaskblog import bcrypt, db
from flaskblog.users.forms import RegisterForm, LoginForm, UpdateAccoutForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.users.utils import save_file, send_request_mail


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, password=hashed_password, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash(f'Account has been successfully created! Now, you can log in.', 'success')
            return redirect(url_for('main.home'))

    return render_template('register.html', title='Registration', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(url_for('main.home')) if not next_page else redirect(next_page)
            else:
                flash('Login unsuccessful, please check e-mail and password', 'failed')
    return render_template('login.html', title='Log in', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccoutForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.picture.data:
                path = os.path.join(current_app.root_path, 'static/profile_pictures', current_user.img)
                os.remove(path)
                picture = save_file(form.picture.data)
                current_user.img = picture
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Your account has been successfully changed", 'success')
            return redirect('account')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f'profile_pictures/{current_user.img}')
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.posted_date.desc()).paginate(per_page=5, page=page)
    return render_template('user_posts.html', posts=posts)


@users.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            if User.query.filter_by(email=email).first():
                send_request_mail(User.query.filter_by(email=email).first())
                flash("Check an email and follow the instruction to reset a password", 'success')
                return redirect(url_for("users.login"))
    return render_template('request.html', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token=token)
    print(user)
    if user is None:
        flash('That is an invalid or expired token', 'failed')
        return redirect(url_for('users.request_reset'))
    form = ResetPasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hased_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hased_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect(url_for('main.login'))
    return render_template('reset_password.html', form=form)
