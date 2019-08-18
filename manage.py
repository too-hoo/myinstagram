#!/usr/bin/env python3
# -*-encoding:UTF-8-*-
# 脚本数据文件
import random
import unittest

from myinstagram import app
from flask_script import Manager
from myinstagram import db
from myinstagram.models import User, Image, Comment

# sql的ORM操作
from sqlalchemy import or_, and_, not_

manager = Manager(app)

@manager.command
def run_test():
    # 注意在跑测试之前先要将数据库清空之后再创建一个新的
    db.drop_all()
    db.create_all()
    # 默认是会自己去寻找当前的目录下面的test.py文件
    tests = unittest.TestLoader().discover('./')
    # 找到之后就可以跑单元测试
    unittest.TextTestRunner().run(tests)
    pass

def get_image_url():
    """
    随机生成图片的地址
    :return:
    """
    return 'https://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'


@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 100):
        db.session.add(User('User' + str(i+1), 'a' + str(i))) # str(i+1)让id从1开始
        for j in range(0, 3):
            # 每个人生成三张图片
            db.session.add(Image(get_image_url(), i+1))
            for k in range(0, 3):
                # 每张图片有三条评论(评论,image_id, user_id),那么一个用户就有9条评论，图片id为：1 + 3*i+j
                db.session.add(Comment('This is a comment' + str(k), 1 + 3*i+j, i+1))
    db.session.commit()

# 单个查询：
    print(1, User.query.all())  # 使用默认的方法__repr__返回所有的user
    print(2, User.query.get(3)) # 使用get方法查询第3个用户,输出的结果为2 <User: 3 User3>
    print(3, User.query.filter_by(id=5).first()) # 也可以使用filter的方法将第5个用户查询出来
    print(4, User.query.filter_by(id=5)) # 如果不加first()的话，输出的是查询的sql语句：
    '''
    4 SELECT user.id AS user_id, user.username AS user_username, user.password AS user_password, user.head_url AS user_head_url 
    FROM user 
    WHERE user.id = %s
    '''
    print(5, User.query.order_by(User.id.desc()).offset(1).limit(2).all()) # 使用order_by降序查询，偏移一位，查询两个，打印所有
    '''5 [<User: 99 User99>, <User: 98 User98>]'''
    print(6, User.query.filter(User.username.endswith('0')).limit(3).all()) # 使用filter将结尾的为0的数据打印出来，只是打印3个,类似与纯的sql中的like
    '''6 [<User: 10 User10>, <User: 20 User20>, <User: 30 User30>]'''
    # 使得查询复杂点，导入or_,and_, not_等的使用
    print(7, User.query.filter(or_(User.id == 88, User.id == 99)).all()) # 使用or_将User的id为88和99查询出来,去掉all之后会一样打印出sql
    '''7 [<User: 88 User88>, <User: 99 User99>]'''
    print(8, User.query.filter(and_(User.id > 88, User.id < 94)).all()) # 使用and_将区间内的数据查询出来
    print(9, User.query.filter(and_(User.id > 88, User.id < 93)).first_or_404())  # 打印出区间内的第一个数据否则返回404 Not Found
    '''
    8 [<User: 89 User89>, <User: 90 User90>, <User: 91 User91>, <User: 92 User92>, <User: 93 User93>]
    9 <User: 89 User89>
    '''
    # 分页查询, 条件是可以组合的例如逆序排序然后再分页
    print(10, User.query.paginate(page=1, per_page=10).items)  # 正序列查询
    print(11, User.query.order_by(User.id.desc()).paginate(page=1, per_page=10).items)  # 逆序查询
    '''
    10 [<User: 1 User1>, <User: 2 User2>, <User: 3 User3>, <User: 4 User4>, <User: 5 User5>, <User: 6 User6>, <User: 7 User7>, <User: 8 User8>, <User: 9 User9>, <User: 10 User10>]
    11 [<User: 100 User100>, <User: 99 User99>, <User: 98 User98>, <User: 97 User97>, <User: 96 User96>, <User: 95 User95>, <User: 94 User94>, <User: 93 User93>, <User: 92 User92>, <User: 91 User91>]
    '''
# 关联查询：
    user = User.query.get(1)
    print(12, user.images.all()) # 将用户的id为1的图片查询出来
    '''
    12 [<Image: 1 https://images.nowcoder.com/head/205m.png>, <Image: 2 https://images.nowcoder.com/head/360m.png>, <Image: 3 https://images.nowcoder.com/head/928m.png>]
    '''
    # 反过来知道一张图片想要知道他的用户,需要在model里面设置反向引用，否则会报错：AttributeError: 'Image' object has no attribute 'user'
    # 需要加上：images = db.relationship('Image', backref='user', lazy='dynamic')
    image = Image.query.get(1)
    print(13, image, image.user)
    '''13 <Image: 1 https://images.nowcoder.com/head/918m.png> <User: 1 User1>'''

# 数据更新的两种方式
    # 批量方式：查出数据更新
    for i in range(50, 100, 2): # 更新用户名,50之后的偶数的步长更新
        user = User.query.get(i)
        user.username = "[New1]" + user.username

    # 单个数据进行更新
    # 注意filter和filter_by的区别
    User.query.filter_by(id = 51).update({'username': '[New2]'}) # 这里是找到id为51的用户的信息进行更新
    db.session.commit()

# 数据删除
    for i in range(50, 100, 2): # 将评论50之后的id奇数的删除
        comment = Comment.query.get(i + 1)
        db.session.delete(comment) # 是直接删除就可以的了

    db.session.commit() # 最后进行数据库的session提交更新






if __name__ == '__main__':
    manager.run()












