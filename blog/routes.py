import os
import secrets
from PIL import Image
from flask import render_template,url_for,flash,redirect,request,abort
from blog import app , bcrypt , db , mail
from blog.forms import RegisterationForm,LoginForm,UpdateForm,AddPostForm , ResetPassword , PasswordResetReq
from blog.models import User , Post 
from flask_login import login_user , current_user,logout_user,login_required
from flask_mail import Message


@app.route("/")
def index():
    page = request.args.get('page',1,type=int)
    post=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('index.html',post=post)

@app.route('/about')
def about():
    return render_template('about.html',title='About')

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Login successfull! Welcome: {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'failed')
    return render_template('login.html',title='Login',form=form)

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterationForm()
    if form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=pw_hash)
        db.session.add(user)
        db.session.commit()
        print(f"User added to database with : {user}") # For us to see who registered.
        flash(f'Account created for:{form.username.data} successfully!','success') # For UI to show who registered.
        return redirect(url_for('index'))
    return render_template('register.html',title='Register',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('register'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (168, 168)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/profile' , methods=['GET', 'POST'])
@login_required 
def profile():
    form = UpdateForm()
    if form.validate_on_submit():
        if form.pp.data:
            picture_file = save_picture(form.pp.data)
            current_user.image_file = picture_file 
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash(f'Successfully Updated!','success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html',title='Profile',
                            image_file=image_file,form=form)
# Crud Methods Routing
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def add_new_post():
    form = AddPostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f'New Post added!','success')
        return redirect(url_for('index'))
    return render_template('add-post.html',title='Add Post',form=form,titleUp='Add Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',title=post.title,post=post)

@app.route("/post/<int:post_id>/update" , methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = AddPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash(f'Post Updated!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('add-post.html',title='Update'
                           ,form=form,titleUp='Update Post')
    

@app.route("/post/<int:post_id>/delete" , methods=['GET','POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash(f'Post deleted!','failed')
    return redirect(url_for('index'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('users_posts.html', post=post, user=user)


def send_reset_email(user):
    token = user.get_reset_token() 
    msg = Message()
    msg.subject = "Password Reset Request"
    msg.recipients = ['user.email']
    msg.sender = 'hamzaunsal@freemail.hu'
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request just ignore this mail.
'''
    mail.send(msg)

@app.route("/reset_password" , methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PasswordResetReq()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPassword()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
