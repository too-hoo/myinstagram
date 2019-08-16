#!/usr/bin/env python3
# -*-encoding:UTF-8-*-

from myinstagram import app, db
from flask import render_template, redirect

from myinstagram.models import Image, User, Comment


@app.route('/')
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html', images=images)


@app.route('/image/<int:image_id>')
def image(image_id):
    image = Image.query.get(image_id)
    # 如果数据库没有对应的图片，那么就返回到首页
    if image == None:
        return redirect('/')
    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')
    return render_template('profile.html', user=user)
