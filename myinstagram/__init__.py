#!/usr/bin/env python
# -*-encoding:UTF-8-*-
# 这个文件在一开始的时候就会默认加载

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols') # 为jinja2加上一个扩展的时候就可以使用break语法
# 加载配置文件
app.config.from_pyfile('app.conf')
# 导入数据库
db = SQLAlchemy(app)

from myinstagram import views, models
