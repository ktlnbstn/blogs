from flask import Flask, request, redirect, render_template, session, flash, make_response
import cgi
from app import app, db
from models import *
from hashutils import check_pw_hash

@app.route('/login', methods=['POST', 'GET'])
def login():
    # when logging in, check password against stored password
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash('Logged In')
            return redirect('/newpost')
        else:
            flash('User password incorrect or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # if the user forgot to enter a username/passwrod/verification, notify
        if len(username) == 0 or len(password) == 0 or len(verify) == 0:
            flash("""One or more fields are invalid.""")
            return redirect('/signup')

        # if the user uses an invalid username, tell them the error
        if len(username) < 3 or len(username) > 20 or ' ' in username:
            flash("""Invalid username. Must be 3-20 characters without spaces.""")
            return redirect('/signup')

        # if the user typed an invalid passowrd, tell them the error
        if len(password) < 3 or len(password) > 20 or ' ' in password:
            flash("""Invlaid password. Must be 3-20 characters without spaces.""")
            return redirect('/signup')

        # if the password and second copy of password don't match, notify
        if password != verify:
            flash("""Your passwords don't match. Please try again""")
            return redirect('/signup')

        # if the user attempts to register a previously registered username, notify
        if username in User.query.filter_by(username='username'):
            flash("""Your username is previously registered. Please sign in.""")
            return redirect('/signup')

        # if everything checks out, commit a user object
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/blog')

@app.route('/blog')
def index():
    # only display the logged in user's posts
    owner = User.query.filter_by(username=session['username']).first()
    posts = BlogPost.query.filter_by(deleted=False, owner=owner).all()
    diff = request.args.get('id')

    if diff:
        post = BlogPost.query.filter_by(id=diff).first()
        return render_template('individ_post.html', post=post)

    return render_template('blog.html', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    # assign a newpost to the correct user
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        blog_name = request.form['title']
        post_body = request.form['post']

        # if the title is empty, notify
        if blog_name == '':
            error = 'Please fill in the title.'
            return render_template('post.html', post=post_body, error=error)

        # if the body is empty, notify
        if post_body == '':
            error2 = 'Please fill in the body.'
            return render_template('post.html', title=blog_name, error2=error2)

        # if everything checks out, create a new post object and redirect
        new_post = BlogPost(blog_name, post_body, owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id=' + str(new_post.id))

    return render_template('post.html')


@app.route('/delete-post', methods=['POST'])
def delete_post():
    # allow users to delete their posts
    post_id = int(request.form['post-id'])
    post = BlogPost.query.get(post_id)
    post.deleted = True
    db.session.add(post)
    db.session.commit()

    return redirect('/blog')

@app.before_request
def require_login():
    # require a login to create a blog
    allowed_routes = ['login', 'index', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

if __name__ == '__main__':
    app.run()
