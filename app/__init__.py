from flask import Flask
from config import config_map
import redis
import logging
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler

# 数据库
db = SQLAlchemy()

# redis连接对象
redis_store = None

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


def create_app(config_name):
    app = Flask(__name__)

    # 根据配置模式的名字获取配置参数的类
    config_class = config_map(config_name)
    app.config.from_object(config_class)

    # 使用app初始化db
    db.init_app(app)

    # 初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 利用flask-session，将session数据保存到redis中
    # Session 修改了app中session中的设置
    Session(app)

    # 为flask补充csrf防护
    CSRFProtect(app)
    # 注册蓝图
    register_blueprints(app)
    return app


def register_blueprints(app):
    from app.api import api
    app.register_blueprint(api, url_prefix="/")
