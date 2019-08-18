#!/usr/bin/env python3
# -*-encoding:UTF-8-*-
# 单元测试

import unittest
from myinstagram import app

class MyinstagramTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        print('setUp')

    def tearDown(self):
        print('teardown')
        pass

    def register(self, username, password):
        # 注册成功之后会进行重定向follow_redirects，所以会设置为True
        return self.app.post('/reg', data={"username":username, "password":password}, follow_redirects = True)

    def login(self, username, password):
        return self.app.post('/login', data={"username":username, "password":password}, follow_redirects = True)

    def logout(self):
        return self.app.get('/logout/')

    def test_reg_logout(self):
        assert self.register("hello", "world").status_code == 200
        # 如果注册成功之后，页面的title是会存在-hello这样的一个字符串的，登出之后就不存在了
        assert b'-hello' in self.app.open('/').data
        self.logout()
        assert b'-hello' not in self.app.open('/').data
        self.login("hello", "world")
        assert b'-hello' in self.app.open('/').data

    def test_profile(self):
        # 如果是没有登录的话是直接会跳转到登录注册页的，所以设置其为跳转为True
        r1 = self.app.open('/profile/3', follow_redirects = True)
        # print(dir(r1))
        assert r1.status_code == 200
        # 测试用例一定要get到最关键的那个核心的点，返回的状态值为200，但是不知道是否已经跳转，
        # 所以要到跳转到的那一页寻找该出现的点（字符串，byte字节）有没有出现
        assert b"password" in r1.data
        self.register("hello2", "world")
        # 不要漏掉data啊啊啊！需要加上http://127.0.0.1:5000，否则会找不到
        r2 = self.app.open('http://127.0.0.1:5000/profile/1', follow_redirects=True).data
        # print(r2)
        assert b"hello2" in r2













