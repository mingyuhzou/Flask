from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_pagedown import PageDown



bootstrap=Bootstrap()
mail=Mail()
moment=Moment()
db=SQLAlchemy()
# migrate=Migrate()
csrf = CSRFProtect()
login_manager=LoginManager()
login_manager.login_view='auth.login'
pagedown=PageDown()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    # migrate.init_app(app,db)
    csrf.init_app(app) 
    login_manager.init_app(app)
    pagedown.init_app(app)
    
    '''
    添加路由和自定义的错误页面
    '''
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')
    return app 