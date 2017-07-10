from flask import Flask, request, redirect, render_template, session, flash, make_response
import cgi
from app import app, db
from models import User, Movie

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged In')
            return redirect('/blog')
        else:
            flash('User password incorrect or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if password != verify:
            flash("""Your passwords don't match. Please try again""")
            return redirect('/register')

        elif email in User.query.filter_by(email='email'):
            flash("""Your email is previously registered. Please sign in.""")
            return redirect('/register')

        else:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/blog')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')

@app.route('/blog')
def index():
    owner = User.query.filter_by(email=session['email']).first()
    posts = BlogPost.query.filter_by(deleted=False, owner=owner).all()
    diff = request.args.get('id')

    if diff:
        post = BlogPost.query.filter_by(id=diff).first()
        return render_template('individ_post.html', post=post)

    return render_template('blog.html', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    if request.method == 'POST':
        owner = User.query.filter_by(email=session['email']).first()
        blog_name = request.form['title']
        post_body = request.form['post']

        if blog_name == '':
            error = 'Please fill in the title.'
            return render_template('post.html', post=post_body, error=error)
        if post_body == '':
            error2 = 'Please fill in the body.'
            return render_template('post.html', title=blog_name, error2=error2)

        new_post = BlogPost(blog_name, post_body, owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id=' + str(new_post.id))

    return render_template('post.html')


@app.route('/delete-post', methods=['POST'])
def delete_post():
    post_id = int(request.form['post-id'])
    post = BlogPost.query.get(post_id)
    post.deleted = True
    db.session.add(post)
    db.session.commit()

    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

if __name__ == '__main__':
    app.run()
