#!/usr/bin/env python3
# -*-encoding:UTF-8-*-
import hashlib
import os
import random
import json
import uuid

from myinstagram import app, db
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory

from myinstagram.models import Image, User, Comment
# 导入flask-login主要方法
from flask_login import login_user, logout_user, current_user, login_required

# 导入七牛的上传的方法
from myinstagram.qiniusdk import qiniu_upload_file

# 默认是使用get请求的
@app.route('/index/images/<int:page>/<int:per_page>/')
def index_image(page, per_page):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next':paginate.has_next}
    images = []
    for image in paginate.items:
        comments = []
        # 限定首页的评论数为最小的2条
        for i in range(0, min(2, len(image.comments))):
            comment = image.comments[i]
            comments.append({'username':comment.user.username,
                             'user_id':comment.user_id,
                             'content':comment.content})
        # 首页的每一个块可以看做是一个对象，将每一个对象拼接在一起，返回
        imgvo = {'id':image.id,
                 'url':image.url,
                 'comment_count':len(image.comments),
                 'user_id':image.user_id,
                 'head_url':image.user.head_url,
                 'created_date':str(image.created_date),
                 'commemts':comments}
        images.append(imgvo)

    map['images'] = images
    # 将把python的类型转化成为json字符串，返回
    return json.dumps(map)

@app.route('/')
def index():
    images = Image.query.order_by(db.desc(Image.id)).paginate(page=1, per_page=10, error_out=False)
    # 另外的两种写法
    # images = Image.query.order_by('-id').limit(10).all()
    # images = Image.query.order_by('id desc').limit(10).all()
    print(images.has_next)
    return render_template('index.html',has_next=images.has_next,  images=images.items)


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
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3)  # 一次加载3张图片
    # has_next = paginate.has_next返回给页面作为判断是否有下一页
    # print(paginate.has_next)
    return render_template('profile.html', user=user, has_next=paginate.has_next, images=paginate.items)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    # 参数检查
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)

    # paginate的属性判断是否存在下一页,每页显示数量遍历出来，接在尾部
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments)}
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


@app.route('/image/<image_name>')
def view_image(image_name):
    # 查看上传的图片，flask已经将图片封装好了直接使用send_from_directory就可以了
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


# 下面的是两种方式的查看图片的方法
def save_to_qiniu(file, file_name):
    return qiniu_upload_file(file, file_name)


def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name


@app.route('/upload/', methods={"post"})  # 图片上传使用的方法都是使用post方法的
@login_required  # 需要登录之后才能上传照片
def upload():
    # print(type(request.files)) # ImmutableMultiDict包含的是所有上传文件的一些基本信息
    file = request.files['file']  # http请求是可以通过多文件上传的
    # dir(file) # 可以使用这个函数对文件的一些方法进行列举
    # https://werkzeug-docs-cn.readthedocs.io/zh_CN/latest/
    # 需要对文件进行裁剪等操作
    file_ext = ''
    if file.filename.find('.') > 0:
        # 截取上传的图片的后缀名rsplit找右侧的第一个.，设置成为新图片的后缀名
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        # print(file_name)
        # 保存到本地
        url = save_to_local(file, file_name)
        # url = qiniu_upload_file(file, file_name)
        if url != None:
            # 如果URL不空，保存链接地址和当前用户的id
            db.session.add(Image(url, current_user.id))
            db.session.commit()
    return redirect('/profile/%d' % current_user.id)


@app.route('/addcomment/', methods={'post'})
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content'].strip()
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code":0, "id":comment.id,
                       "content":content,
                       "username":comment.user.username,
                       "user_id":comment.user.id})











