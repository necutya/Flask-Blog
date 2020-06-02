from flask import Blueprint
from flaskblog.models import Post
from flask import render_template, url_for, request, flash, redirect, abort
from flaskblog import db
from flaskblog.posts.forms import PostForm
from flask_login import current_user, login_required

posts = Blueprint('posts', __name__)


@posts.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash("New post has been successfully created!", 'success')
            return redirect(url_for("main.home"))
    return render_template('newpost.html', title='New post', form=form, legend="New post")


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post, title=post.title)


@posts.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author.username != current_user.username:
        abort(403)
    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash("Post has been successfully edited!", 'success')
            return redirect(url_for("posts.post", post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html', title='Edit post', form=form, legend="Edit post")


@posts.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author.username != current_user.username:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))
