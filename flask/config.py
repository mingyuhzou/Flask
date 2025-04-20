import os 

basedir=os.path.abspath(os.path.dirname(__file__))

# 配置基类
class Config:
    SECRET_KEY = 'nndjxh'# 设置密钥
    SQLALCHEMY_TRACK_MODIFICATIONS = False                     # 不追踪数据库修改


    '''邮件设置 以QQ邮件服务器为例'''
    MAIL_SERVER='smtp.qq.com'   # SMTP服务器
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME')  # 凑够环境变量中取得 '2228632512@qq.com'
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')  # "jdilyngiczeadhha"
    MAIL_DEFAULT_SENDER = '2228632512@qq.com'   # 默认发送者
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]' # 前缀
    FLASKY_MAIL_SENDER = 'Flasky Admin <2228632512@qq.com>' # 发送者
    FLASKY_ADMIN=set(['mingyuhzou@gmail.com','22286325612@qq.com'])
    FLASKY_POSTS_PER_PAGE=FLASKY_FOLLOWERS_PER_PAGE=20                                 # 每页的帖子数
    FLASKY_COMMENTS_PER_PAGE=10
    '''数据库设置'''
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'data.sqlite')

    # 
    @staticmethod
    def init_app(app):
        """可选：在应用创建后执行额外的初始化"""
        pass  # 默认不执行任何操作
# 下面是几个子类

'''
开发环境，启用调试模式
'''
class DevelopmentConfig(Config):
    DEBUG = True  # 开启调试模式

'''
测试环境，使用内容数据库
'''
class TestingConfig(Config):
    TESTING = True  # 启用测试模式
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 使用内存数据库


'''
生产环境，关闭调试模式
'''
class ProductionConfig(Config):
    DEBUG = False  # 关闭调试模式

# 配置字典
config = {
 'development': DevelopmentConfig,
 'testing': TestingConfig,
 'production': ProductionConfig,
 'default': DevelopmentConfig
}