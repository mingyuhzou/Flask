from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User,Post

def user(count=100):
    fake=Faker()
    i=0
    while i<count:
        u=User(email=fake.email(),
               username=fake.user_name(),
               password='password',
               confirmed=True,
               name=fake.name(),
               location=fake.city(),
               about_me=fake.text(),
               member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i+=1
        except IntegrityError: # 违反了数据库的约束，因为邮件和用户名是随机生成的有可能的重复
            # 撤销更改
            db.session.rollback()

def posts(count=100):
    fake=Faker()
    user_count=User.query.count()
    for i in range(count):
        # offset跳过多少条记录，与randint一起使用相等于随机选择用户
        u=User.query.offset(randint(0,user_count-1)).first()
        p=Post(body=fake.text(),timestamp=fake.past_date(),author=u)
        db.session.add(p)
    db.session.commit()