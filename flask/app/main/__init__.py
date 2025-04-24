from flask import Blueprint

# 第一个参数是蓝本的名称，第二个参数是蓝本所在的包
main=Blueprint('main',__name__)

from ..models import Permission

@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)

# 能把路由和错误处理程序与蓝本关联起来，但是要在最后导入防止循环依赖
from . import views,errors # 相对导入