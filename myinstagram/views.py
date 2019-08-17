#!/usr/bin/env python3
# -*-encoding:UTF-8-*-
import hashlib
import random
import json

from myinstagram import app, db
from flask import render_template, redirect, request, flash, get_flashed_messages

from myinstagram.models import Image, User, Comment
# 导入flask-login主要方法
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    # 另外的两种写法
    # images = Image.query.order_by('-id').limit(10).all()
    # images = Image.query.order_by('id desc').limit(10).all()
    return render_template('index.html', images=images)


@app.route('/image/<int:image_id>')
def image(image_id):
    image = Image.query.get(image_id)
    # 如果数据库没有对应的图片，那么就返回到首页
    if image == None:
        return redirect('/')
    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>')
@login_required  # 这句话的意思是访问这个页面是必须先要登录的
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id = user_id).paginate(page=1, per_page=3) # 一次加载3张图片
    # has_next = paginate.has_next返回给页面作为判断是否有下一页
    # print(paginate.has_next)
    return render_template('profile.html', user=user, has_next=paginate.has_next, images=paginate.items)

@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    # 参数检查
    paginate = Image.query.filter_by(user_id = user_id).paginate(page=page, per_page=per_page)

    # paginate的属性判断是否存在下一页,每页显示数量遍历出来，接在尾部
    map = {'has_next':paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id':image.id, 'url':image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


@app.route('/regloginpage/')
def regloginpage(msg=''):
    # 如果当前的用户已经被验证过就不用再登录注册，可以直接跳转到index页面
    if current_user.is_authenticated:
        return redirect('/')

    # 如果已经注册就提示重复注册了使用flash在首页进行显示
    for m in get_flashed_messages(with_categories=False, category_filter=['reglogin']):
        msg = msg + m
    # 如果已经登录的就跳到首页,同时埋藏的一个next参数在这里获得并返回
    return render_template('login.html', msg=msg, next=request.values.get('next'))


def redirect_with_msg(target, msg, categrory):
    if msg != None:
        flash(msg, category=categrory)
    return redirect(target)


@app.route('/login', methods={'post', 'get'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    # 验证数据
    if username == '' or password == '':
        return redirect_with_msg('/regloginpage', u'用户名或者密码为空！', 'reglogin')

    # 验证用户是否为空
    user = User.query.filter_by(username=username).first()

    if user == None:
        return redirect_with_msg('/regloginpage', u'用户名不存在！', 'reglogin')

    m = hashlib.md5()
    m.update((password + user.salt).encode("utf-8"))
    if m.hexdigest() != user.password:
        return redirect_with_msg('/regloginpage', u'用户名或者密码不正确！', 'reglogin')

    # 否则登录成功
    login_user(user)

    next = request.values.get('next')
    # 因为跳转到注册页面的时候如果之前浏览过页面会出现斜杠数目大于0的情况
    if next != None and next.startswith('/') > 0:
        # 直接跳转到想要点开的页面，是用户体验优化的做法之一
        return redirect(next)

    return redirect('/')

@app.route('/reg', methods={'post', 'get'})
def reg():
    # request arg
    # request form
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    # 对数据进行检验
    if username == '' or password == '':
        return redirect_with_msg('/regloginpage', u'用户名或者密码为空！', 'reglogin')
    # 如果用户名已经存在，跳转到首页显示对应的信息
    user = User.query.filter_by(username=username).first()
    if user != None:
        return redirect_with_msg('/regloginpage', u'用户名已经存在！', 'reglogin')
    # 安全加盐
    salt = ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwsyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 10))
    m = hashlib.md5()
    m.update((password + salt).encode("utf-8"))  # 使用摘要算法加盐密码, python3里面要先encode进行编码
    password = m.hexdigest()
    user = User(username, password, salt)
    # 提交数据
    db.session.add(user)
    db.session.commit()
    # 直接设置注册用户为登录状态，不必跳转到登录页面注册,使用的是flask-login的登录模块
    login_user(user)

    next = request.values.get('next')
    # 因为跳转到注册页面的时候如果之前浏览过页面会出现斜杠数目大于0的情况
    if next != None and next.startswith('/') > 0:
        return redirect(next)

    return redirect('/')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')
