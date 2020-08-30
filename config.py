# coding:utf-8

class Config(object):
    """配置信息"""

    SECRET_KEY = "ADSFE5*va8413b52s4175yh12bz"

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:1234567@127.0.0.1:3306/flask"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379