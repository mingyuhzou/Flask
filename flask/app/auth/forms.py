from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Email,Length,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User

class RegistrationForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username=StringField('Username',validators=[DataRequired(),Regexp('^[A-Za-z][A-Za-z._]*$',0,'Usernames must have only letters, numbers, \
                                                dots or underscores')])
    password=PasswordField('Password',validators=[DataRequired(),EqualTo('password2',\
        message='Passwords must match')])
    password2=PasswordField('Password2',validators=[DataRequired(),])
    submit=SubmitField('Register')

    # def validate_email(self,field):
    #     if User.query.filter_by(email=field.data).first():
    #         raise ValidationError('Email already registered')
    
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

class ChangePasswordForm(FlaskForm):
    old_password=PasswordField('Old password',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired(),EqualTo('password2',\
        message='Passwords must match')])
    password2=PasswordField('Password2',validators=[DataRequired(),])
    submit=SubmitField('Update password')

class PasswordResetRequestForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    submit = SubmitField('Reset Password')
class PasswordResetForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired(),EqualTo('password2',\
        message='Passwords must match')])
    password2=PasswordField('Password2',validators=[DataRequired(),])
    submit=SubmitField('Reset Password')

class ChangeEmailForm(FlaskForm):
    email=StringField('New Email',validators=[DataRequired(),Length(1,64),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Update Email Addressrd')

    def Validata_email(self,field):
        if User.query.filter_by(email=field.email.data).first():
            raise ValidationError('Email already registered.')