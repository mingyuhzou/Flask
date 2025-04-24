import os
from app import create_app,db
from app.models import *
import click 
from flask_migrate import Migrate,upgrade
from werkzeug.middleware.profiler import ProfilerMiddleware

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db,User=User,Role=Role)

if app.config['FLASKY_PROFILE_ENABLED']:
    app.wsgi_app=ProfilerMiddleware(
        app.wsgi_app,
        restrictions=[app.config['FLASKY_PROFILE_LENGTH']],
        profile_dir=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'profile_data')
    )

from sqlalchemy import inspect

@app.cli.command()
def deploy():
    print("开始部署！")

    # 输出当前数据库中的所有表名
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("1数据库中的表名有：")
    for table in tables:
        print(f" - {table}")
        
    # 执行数据库迁移
    upgrade()

    # 输出当前数据库中的所有表名
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("2数据库中的表名有：")
    for table in tables:
        print(f" - {table}")

    # 插入角色
    print("插入角色...")
    Role.insert_roles()

    User.add_self_follows()



