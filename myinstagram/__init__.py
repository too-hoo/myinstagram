#!/usr/bin/env python
# -*-encoding:UTF-8-*-
# 这个文件在一开始的时候就会默认加载

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols') # 为jinja2加上一个扩展的时候就可以使用break语法
# 加载配置文件
app.config.from_pyfile('app.conf')
# 导入数据库
db = SQLAlchemy(app)
app.secret_key = 'toohoo' # 初始化的时候添加验证是否是同一个用户，否则使用同一个账户注册的时候会报错提示重复
# 为flask-login进行初始化
login_manager = LoginManager(app)
# 处理未登录的时候查看需要登录的信息页面，帮助跳转到登录页面
login_manager.login_view = '/regloginpage/'


from myinstagram import views, models
