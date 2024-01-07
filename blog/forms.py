from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField , SubmitField , TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from blog.models import User



class RegisterationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    email = StringField('Email Address',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=8,message='Minimum 8 Character'),EqualTo('confirm_password',message='Passwords are not matched!')])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),Length(min=8,message='Minimum 8 Character')])
    submit = SubmitField('Register')

    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("The Username is already taken!")
        

    def validate_email(self,email):
        email=User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("Someone already registered with this email before.")
        



class LoginForm(FlaskForm):
    email = StringField('Email Address',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=8,message='Minimum 8 Character')])
    submit = SubmitField('Login')


    
class UpdateForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    email = StringField('Email Address',validators=[DataRequired(),Email()])
    pp = FileField('Photo Update',validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user=User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("The Username is already taken!")
        

    def validate_email(self,email):
        if email.data != current_user.email:
            email=User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError("Someone already registered with this email before.")
            
class AddPostForm(FlaskForm):
    title = StringField('Title of Post',validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class PasswordResetReq(FlaskForm):
    email = StringField('Email Address',validators=[DataRequired(),Email()])
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('This email is not registered. Would you like to register first?')

class ResetPassword(FlaskForm):
    password = PasswordField('Your New Password',validators=[DataRequired(),Length(min=8,message='Minimum 8 Character'),EqualTo('confirm_password',message='Passwords are not matched!')])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),Length(min=8,message='Minimum 8 Character')])
    submit = SubmitField('Reset')