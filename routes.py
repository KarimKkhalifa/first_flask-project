from flask import render_template, request, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from init import app, db, login_manager
from models import User, Posts


@app.route('/register', methods=['POST', 'GET'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if request.method == 'POST':
        if not login or not password or not password2:
            flash('fill all fields')
            return redirect('/register')
        elif password != password2:
            flash('passwords are not equal')
            return redirect('/register')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password_hash=hash_pwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect('/posts_page')
        else:
            flash('Login or password is not correct')
    else:
        flash('fill login and password fields')
    return render_template('login.html')


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/user', methods=['POST', 'GET'])
@login_required
def user_page():
    user = current_user
    if request.method == 'POST':
        logout_user()
        return redirect('/')
    else:

        return render_template('user_page.html', user=user)


@app.route('/user/delete')
def user_delete():
    user = current_user
    db.session.delete(user)
    db.session.commit()
    return redirect('/')


@app.route('/')
def home_page():
    user = current_user
    return render_template('home_page.html', user=user)


@app.route('/posts_page', methods=['POST', 'GET'])
def posts_page():
    newest = request.form.get('newest')
    oldest = request.form.get('oldest')
    post = Posts.query.all()
    if request.method == 'POST' and newest:
        post = Posts.query.all()
        post = post[::-1]
    return render_template('posts_page.html', data=post)


@app.route('/posts_page/<int:id>')
def posts_detail(id):
    post = Posts.query.get(id)
    user_id = current_user.id
    return render_template('post_detail.html', data=post, user_id=user_id)


@app.route('/posts_page/<int:id>/delete')
def posts_delete(id):
    post = Posts.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts_page')


@app.route('/posts_page/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    posts = Posts.query.get(id)
    if request.method == 'POST':
        posts.title = request.form['title']
        posts.text = request.form['text']
        db.session.commit()
        return redirect('/posts_page')
    else:
        return render_template('post_update.html', post=posts)


@app.route('/create', methods=['POST', 'GET'])
@login_required
def posts_create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        user_id = current_user.id
        posts = Posts(title=title, text=text, user_id=user_id)
        db.session.add(posts)
        db.session.commit()
        return redirect('/posts_page')

    else:
        return render_template('create.html')


@app.template_filter('date')
def date_form(value, format='%B'):
    return value.strftime(format)
