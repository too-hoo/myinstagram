#!/usr/bin/env python3
# -*-encoding:UTF-8-*-
# 启动服务器

from myinstagram import app

# 将最基础的东西分开，例如启动放在这里
if __name__ == '__main__':
    app.run(debug=True)
