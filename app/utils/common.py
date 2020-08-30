from flask import jsonify, request, current_app, g
from app.utils.response_code import RET
from app import redis_store
from config import Config
import datetime
import functools
import jwt


def create_access_token(account, login_ip):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'iss': 'michael',
        'data': {
            'account': account,
            'login_ip': login_ip,
        },
    }
    access_token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return access_token


def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 获取用户传来的access_token
        access_token = request.headers.get('Authorization')
        # 发起请求的ip
        current_login_ip = request.remote_addr
        if (access_token):
            try:
                # jwt解码
                payload = jwt.decode(access_token, Config.SECRET_KEY, issuer='michael', algorithms=['HS256'])
                # 获取登录信息
                data = payload.get('data')
                account = data.get('account')
                login_ip = data.get('login_ip')
                # 验证ip，防止token泄露
                if login_ip != current_login_ip:
                    return jsonify(errno=RET.NODATA, errmag="无效token")
                # 从redis中取出account对应的token
                # 当token泄露，并且hacker伪造请求ip，可以手动删除redis保存的token，让其失效
                try:
                    token = redis_store.get("token_%s" % account)
                except Exception as e:
                    current_app.logger.error(e)
                    return jsonify(errno=RET.DBERR, errmag="redis读取token异常")
                if token is None:
                    return jsonify(errno=RET.NODATA, errmag="无效token")
                g.account = account
                return view_func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify(errno=RET.TOKENERR, errmsg="token已过期")
            except jwt.InvalidTokenError:
                return jsonify(errno=RET.TOKENERR, errmsg="无效token")
        else:
            return jsonify(errno=RET.TOKENERR, errmsg="没有提供认证token")

    return wrapper
