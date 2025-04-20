from flask import render_template,redirect,url_for,flash,request
from . import auth
from ..main.forms import LoginForm
from .forms import RegistrationForm,ChangePasswordForm,PasswordResetForm,PasswordResetRequestForm,ChangeEmailForm
from ..models import User
from ..email import send_email
from .. import db
from flask_login import login_required,logout_user,login_user,current_user

@auth.before_app_request
def before_request():
    # 已登录未确认，不在访问验证蓝图，也不是对静态文件的请求，则拦截
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
        and request.blueprint != 'auth' \
        and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))
    

@auth.route('/login',methods=['POST','GET'])
def login():
    form=LoginForm()
    # 是否有提交
    if form.validate_on_submit():
        # 查询
        user=User.query.filter_by(email=form.email.data).first()
        # 通过验证
        if user and user.verify_password(form.password.data):
            login_user(user)
            # 用户访问未授权的URL时会显示登录表单，原URL会保存在next参数中
            next=request.args.get('next')
            # 不存在则重定向到首页
            if not next or next.startswith('/'):
                next=url_for('main.index')
            return redirect(next)
        flash('Invalid username or password')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have logged out')
    return redirect(url_for('main.index'))


@auth.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        # 创建用户
        user=User(email=form.email.data,username=form.username.data,password=form.password.data)
        # 先提交，因为token需要用户的id
        db.session.add(user)
        db.session.commit()
        # 生成token
        token=user.generate_confirmation_token()
        # 发送确认邮件
        send_email(user.email,'Confirm you Accout','auth/email/confirm',user=user,token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)


@auth.route('/confirm/<token>')
@login_required # 需要先登录(因为允许未确认的用户访问不重要的页面)
def confirm(token):
    # 如果已经确认过了，重定向
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    # 成功确认，重定向
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account! Thanks')
    else:
        flash('The confirmation link is invlaid or has expired')
    return redirect(url_for('main.index'))

@auth.route('/confirm')
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,'Confirm you Accout','auth/email/confirm',user=current_user,token=token)
    flash('A confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if  current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/change-password',methods=['POST','GET'])
@login_required
def change_password():
    # 表单
    form=ChangePasswordForm()
    if form.validate_on_submit():
        # 如果旧密码输入正确
        if current_user.verify_password(form.old_password.data):
            # 提交修改
            current_user.password=form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template('auth/change_password.html',form=form)

@auth.route('/reset',methods=['POST','GET'])
def password_reset_request():
    # 已经登录不需要重设密码
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=PasswordResetRequestForm()
    # 填写表单
    if form.validate_on_submit():
        # 查找用户
        user=User.query.filter_by(email=form.email.data).first()
        # 存在发送验证邮件
        if user:
            token=user.generate_reset_token()
            send_email(user.email,'Reset your Password','auth/email/reset_password',user=user,token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

@auth.route('/reset/<token>',methods=['POST','GET'])
def password_reset(token):
    # 已经登录不需要重设密码
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=PasswordResetForm()
    if form.validate_on_submit():
        # token通过验证，提交修改
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            flash('Update fail ')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)

@auth.route('/change_email',methods=['POST','GET'])
@login_required
def change_email_request():
    form=ChangeEmailForm()
    # 填写表单
    if form.validate_on_submit():
        # 验证密码
        if current_user.verify_password(form.password.data):
            new_email=form.email.data
            # 生成token
            token=current_user.generate_email_change_token(new_email)
            # 发送邮件
            send_email(new_email,'Confirm your email address','auth/email/change_email',user=current_user,token=token)
            flash('An email with instructions to confirm your new email address has been sent to you.')
            return redirect(url_for('main.index'))
    else:
        flash('Invalid email or password.')
    return render_template('auth/change_email.html',form=form)


@auth.route('/change_email/<token>',methods=['POST','GET'])
@login_required
def change_email(token):
    # 验证并修改
    if current_user.change_email(token):
        db.session.commit()
        flash('You email address has been updated')
    else:
        flash('Invalid request')
    return redirect(url_for('main.index'))