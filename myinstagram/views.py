#!/usr/bin/env python3
# -*-encoding:UTF-8-*-

from myinstagram import app, db
from flask import render_template

from myinstagram.models import Image, User, Comment


@app.route('/')
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html', images=images)
