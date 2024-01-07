import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config['SECRET_KEY']='691D430F5BFABF14'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view ='login'
login_manager.login_message_category ='info'
app.config['MAIL_SERVER'] = 'imap.freemail.hu'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = "YOUR EMAIL"
app.config['MAIL_PASSWORD'] = "YOUR PASSWORD"
mail = Mail(app)


with app.app_context():
    db.create_all()

from blog import routes