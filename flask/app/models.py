from flask import current_app,request
from . import db
from  werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime,timezone
import hashlib
from markdown import markdown
import bleach

class Permission:
    FOLLOW=1
    COMMENT=2
    WRITE=4
    MODERATE=8
    ADMIN=16
class Role(db.Model):
    __tablename__='roles' # 表名
    id=db.Column(db.Integer,primary_key=True) # 属性
    name=db.Column(db.String(64),unique=True)
    # 是否是默认角色
    default=db.Column(db.Boolean,default=False,index=True)
    # 在定义时设置默认值，只有在添加到数据库后才会设置值，不方便做计算
    permissions=db.Column(db.Integer)
    # 建立一对多关系 backref指定在User表中添加role对象
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __init__(self,**kwargs):
        # 父类的构造函数
        super(Role,self).__init__(**kwargs)
        # 将权限的初始话放到构造函数中
        if not self.permissions:
            self.permissions=0
    # 用于表示对象的字符串方法
    def __repr__(self):
        return '<Role %r>'%self.name
    
    def has_permission(self,perm):
        return self.permissions&perm==perm

    def add_permission(self,perm):
        if not self.has_permission(perm):
            self.permissions+=perm
    def remove_permission(self,perm):
        if self.has_permission(perm):
            self.permissions-=perm
    def reset_permission(self):
        self.permissions=0

    # 将预定义的角色及其权限写入到数据库，模型出现改动后，调用该方法更新橘色
    @staticmethod
    def insert_roles():
        roles={'User':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE ],
               'Moderator':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE,Permission.MODERATE],
               'Administrator':[Permission.FOLLOW,Permission.COMMENT,Permission.WRITE,Permission.MODERATE,Permission.ADMIN],
               }
        default_role='User'
        for r in roles:
            role=Role.query.filter_by(name=r).first()
            # 不存在则新建
            if not role:
                role=Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default=(role.name==default_role)
            db.session.add(role)
        db.session.commit()
class Follow(db.Model):
    __tablename__='follows'
    follower_id=db.Column(db.Integer,db.ForeignKey('Users.id'),primary_key=True) # 关注者
    followed_id=db.Column(db.Integer,db.ForeignKey('Users.id'),primary_key=True) # 被关注的人
    timestamp=db.Column(db.DateTime,default=datetime.now(timezone.utc))

class User(db.Model,UserMixin):
    __tablename__='Users' # 表名
    id=db.Column(db.Integer,primary_key=True) # 属性
    email=db.Column(db.String(64),unique=True,index=True)
    username=db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    # 创建外键引用 roles指的是表名
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))

    avatar_hash=db.Column(db.String(32))

    posts=db.relationship('Post',backref='author',lazy='dynamic')

    confirmed=db.Column(db.Boolean,default=False)
    location=db.Column(db.String(64))
    name = db.Column(db.String(64))
    about_me=db.Column(db.Text())
    member_since=db.Column(db.DateTime(),default=datetime.now(timezone.utc))
    last_seen=db.Column(db.DateTime(),default=datetime.now(timezone.utc))

    '''
    foreign_key 特定指定外键，确保模型知道用哪个字段作为外键来建立表之间的关联
    db.backref是为了设置joined字段———在查询FOLLOW时一并把User查出来
    cascade='all, delete-orpan' 级联删除，当follow不与User关联时，会被自动删除
    '''

    followed=db.relationship('Follow',foreign_keys=[Follow.follower_id],backref=db.backref('follower',lazy='joined'),
                             lazy='dynamic',cascade='all, delete-orphan')# 被我关注的人的ID 从User到关系表，就转换为了关注者(follower_id)
    followers=db.relationship('Follow',foreign_keys=[Follow.followed_id],backref=db.backref('followed',lazy='joined'),
                             lazy='dynamic',cascade='all, delete-orphan')# 关注我的人的ID 从User到关系表，就转换为被关注者()
    
    comments=db.relationship('Comment',backref='author',lazy='dynamic')


    # 用于表示对象的字符串方法
    def __repr__(self):
        return '<User %r>'%self.username
    
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email in current_app.config['FLASKY_ADMIN']:
                self.role=Role.query.filter_by(name='Administrator').first()
            else:
                self.role=Role.query.filter_by(default=True).first()
        if self.email and not self.avatar_hash:
            self.avatar_hash=self.gravatar_hash()

    def ping(self):
        self.last_seen=datetime.now(timezone.utc)
        db.session.add(self)
        db.session.commit()

    '''
    @property装饰器将方法伪装为属性，当有人访问password时，会
    触发异常
    '''
    @property
    def password(self):
        raise AttributeError("password is not a readabel attribute")
    
    '''@password.setter与@property需成对出现 当有人设置password时调用此方法加密'''
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def generate_confirmation_token(self):
        '''
        Serializer用于生成和验证加密令牌 第一个参数是密钥，第二个是过期时间
        '''
        s=Serializer(current_app.config["SECRET_KEY"],'confirmation')
        # dumps方法传入想要加密的数据，把用户的ID放到加密数据中，转换为字符串
        return s.dumps({'confirm':self.id})
    

    def generate_reset_token(self):
        s=Serializer(current_app.config["SECRET_KEY"],'confirmation')
        return s.dumps({'reset':self.id})
    def generate_email_change_token(self,new_email):
        s=Serializer(current_app.config["SECRET_KEY"],'confirmation')
        return s.dumps({'change_email':self.id,'new_email':new_email})
    
    # 静态方法不依赖类的实例
    @staticmethod
    def reset_password(token,new_password,max_age=3600):
        s=Serializer(current_app.config["SECRET_KEY"],'confirmation')
        try:
            data=s.loads(token.encode('utf-8'),max_age=max_age)
        except:
            return False
        # get根据主键查找对象实例
        user=User.query.get(data.get('reset'))
        if not user:
            return False
        user.password=new_password
        db.session.add(user)
        return True 

    def confirm(self,token,max_age=3600):
        s=Serializer(current_app.config["SECRET_KEY"],'confirmation')
        print('enter')
        try:
            # loads方法传入令牌解密并检验令牌的有效性
            data=s.loads(token.encode('utf-8'),max_age=max_age)
        except Exception as e:
            print(e)
            return False
        # 不匹配
        print(data.get('confirm'))
        if data.get('confirm')!=self.id:
            return False
        self.confirmed=True
        db.session.add(self)
        return True 
    
    def change_email(self,token):
        s=Serializer(current_app.config["SECRET_KEY"],'confirmation')
        try:
            data=s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('change_email')!=self.id:
            return False
        new_email=data.get('new_email')
        if not new_email:return False

        if self.query.filter_by(email=new_email).first():return False

        self.email=new_email
        self.avatar_hash=self.gravatar_hash()
        db.session.add(self)
        return True

    def can(self,perm):
        return self.role and self.role.has_permission(perm)
    def is_administrator(self):
        return self.can(Permission.ADMIN)
    
        
    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
    
    def gravatar(self,size=100,default='identicon',rating='g'):
        # https和http请求不同的网址
        if request.is_secure:
            url='https://secure.gravatar.com/avatar'
        else:
            url='http://www.gravatar.com/avatar'

        # 如果没有哈希值则生成
        hash=self.avatar_hash or self.gravatar_hash()
        return f'{url}/{hash}?s={size}&d={default}&r={rating}'
    
    # 辅助方法，关注别人
    def follow(self,user):
        if not self.is_following(user):
            f=Follow(follower=self,followed=user)
            db.session.add(f)
    # 取消关注
    def unfollow(self,user):
        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    # 是否关注
    def is_following(self,user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None 
    # 是否被关注
    def is_followed_by(self,user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


class Post(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True) # 属性
    body=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True ,default=datetime.now(timezone.utc))
    author_id=db.Column(db.Integer,db.ForeignKey('Users.id'))
    body_html=db.Column(db.Text)

    comments=db.relationship('Comment',backref='post',lazy='dynamic')

    @staticmethod
    def on_change_body(target,value,oldvalue,initiator):
        # HTML中允许出现的标签
        allowed_tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        '''markdown()将markdown内容转换为html
            bleach.clean()清理HTML内容，过滤和清晰不安全的HTML，strip控制是否完全删除不允许的标签和其内容
            bleach.linkify()将文本中的URL自动转换为<a>标签
        '''
        target.body_html=bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),tags=allowed_tags,strip=True
        )) 
        
# 注册了一个事件监听器，监听set操作，如果修改了body内容则触发on_change_body
db.event.listen(Post.body,'set',Post.on_change_body)

class Comment(db.Model):
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True ,default=datetime.now(timezone.utc))
    author_id=db.Column(db.Integer,db.ForeignKey('Users.id'))
    body_html=db.Column(db.Text)
    disabled=db.Column(db.Boolean)
    author_id=db.Column(db.Integer,db.ForeignKey('Users.id'))
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))
    @staticmethod
    def on_change_body(target,value,oldvalue,initiator):
        # HTML中允许出现的标签
        allowed_tags=['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i','strong']
        '''markdown()将markdown内容转换为html
            bleach.clean()清理HTML内容，过滤和清晰不安全的HTML，strip控制是否完全删除不允许的标签和其内容
            bleach.linkify()将文本中的URL自动转换为<a>标签
        '''
        target.body_html=bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),tags=allowed_tags,strip=True
        )) 
db.event.listen(Comment.body,'set',Comment.on_change_body)

class AnonymousUser(AnonymousUserMixin):
    def can(self,perm):
        return False
    def is_administrator(self):
        return False
    
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.anonymous_user=AnonymousUser