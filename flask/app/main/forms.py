from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,SelectField,BooleanField,TextAreaField,ValidationError
from wtforms.validators import DataRequired,Email,Length,Regexp
from ..models import User,Role
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm):
    name=StringField('What is your name?', validators=[DataRequired()])
    submit=SubmitField('Submit')

class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remeber_me=BooleanField('Keep me logged in ')
    submit=SubmitField('Login in')

class EditProfileForm(FlaskForm):
    name=StringField('Real name ',validators=[Length(0,64)])
    location=StringField('Location',validators=[Length(0,64)])
    about_me=TextAreaField('About me ')
    submit=SubmitField('Submit')

class EditProfileAdminForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username=StringField('Username',validators=[DataRequired(),Length(1,64)\
            ,Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    confirmed=BooleanField('Confirmed')
    # 修改权限，权限从模型中动态获取
    role=SelectField('Role',coerce=int)
    name=StringField('Real name ',validators=[Length(0,64)])
    location=StringField('Location',validators=[Length(0,64)])
    about_me=TextAreaField('About me ')
    submit=SubmitField('Submit')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        # 动态加载role，因为role模型可能会改变
        self.role.choices=[(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user=user
    
    def validate_email(self, field):
        if field.data != self.user.email and \
        User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.') 
    
    def validate_username(self, field):
        if field.data != self.user.username and \
        User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in user')
        

class PostForm(FlaskForm):
    body=PageDownField("What's on your mind?",validators=[DataRequired()])
    submit=SubmitField('Submit')
    