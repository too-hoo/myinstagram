#!/usr/bin/env python3
# -*-encoding:UTF-8-*-
from datetime import datetime

from myinstagram import db
import random


class Comment(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.INTEGER, db.ForeignKey('image.id'))
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    status = db.Column(db.INTEGER, default=0)  # 正常情况是0，否则是1
    user = db.relationship('User')

    def __init__(self, content, image_id, user_id):
        """
        status 是不用初始化的，因为默认是0了
        :param content:
        :param image_id:
        :param user_id:
        """
        self.content = content
        self.image_id = image_id
        self.user_id = user_id

    def __repr__(self):
        # 默认的输出方法
        return '<Comment: %d %d>' % (self.id, self.status)


class Image(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    url = db.Column(db.String(512))
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    created_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.created_date = datetime.now()  # 设置创建的时间为现在，否则会解析不出来,初始化的时候要设置为现在的时间点

    def __repr__(self):
        # 默认的输出方法
        return '<Image: %d %s>' % (self.id, self.url)


class User(db.Model):
    __tablename__ = 'user' # 设置数据库的表名，默认的是使用类的小写的

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(32))
    head_url = db.Column(db.String(256)) # 这个是头像的信息
    # 这个人是和图片有关联的意思 ,想要知道一张照片对应的是那个用户使用反向引用
    images = db.relationship('Image', backref='user', lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        # 注意这里的头像是不同于主要的大图的，是t.png
        self.head_url = 'https://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 't.png'

    def __repr__(self):
        # 默认的输出方法
        return '<User: %d %s>' % (self.id, self.username)
