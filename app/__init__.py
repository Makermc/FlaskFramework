from flask import Flask
from config import Config
import logging
import redis
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy

# 配置日志信息
# 设置日志的记录等级
logging.basicConfig(level=logging.ERROR)  # 线上error级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)

# redis连接对象
redis_store = None

# orm
db = SQLAlchemy()


def create_app(config_name):
    # 实例化 app实例
    app = Flask(__name__)

    # 根据配置模式的名字获取配置参数的类
    app.config.from_object(Config)

    # 注册扩展模块
    register_extensions(app)

    # 初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

    # 注册蓝图
    register_blueprints(app)
    return app


def register_extensions(app):
    """
    扩展模块初始化
    :param app:
    :return:
    """
    db.init_app(app)


def register_blueprints(app):
    """
    加载功能模块。并注册蓝图
    :param app:
    :return:
    """
    # api功能模块
    from app.api import api
    # 注册蓝图
    app.register_blueprint(api, url_prefix="/")
