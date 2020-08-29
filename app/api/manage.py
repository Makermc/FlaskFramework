#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @TIME  :2020/8/29 12:32
# @Author:Michael.ma
from . import api
from flask import request, jsonify, current_app
from app import redis_store, db, constants
from app.utils.response_code import RET
from app.models.manage import User
from sqlalchemy.exc import IntegrityError


@api.route("/users", methods=["POST"])
def register():
    """注册
    请求参数：账号，密码，昵称，机构
    参数格式：json
    """
    req_dict = request.get_json()
    account = req_dict.get("account")
    password = req_dict.get("password")
    name = req_dict.get("name")
    org_id = req_dict.get("org_id")
    # 校验参数
    if not all([account, password, name, org_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断登录账号是否注册过
    try:
        user = User.query.filter_by(account=account).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    else:
        if user is not None:
            return jsonify(errno=RET.DATAERR, errmsg="账号已存在")
    user = User(account=account, name=name, org_id=org_id)
    user.password = password  # 设置属性
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="账号已存在")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="查询数据库异常")
    # 将token与账号保存到redis中,设置有效期
    try:
        redis_store.setex("token_%s" % account, constants.TOKEN_CODE_REDIS_EXPIRES, "token")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存token失败")
    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


@api.route("/tokens", methods=["POST"])
def login():
    """用户登录"""
    # 获取参数
    req_dict = request.get_json()
    account = req_dict.get('account')
    password = req_dict.get('password')

    # 校验参数
    # 参数完整的校验
    if not all([account, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 判断错误次数是否超过限制，如果超过限制，则返回
    # redis记录："access_nums_请求的ip": 次数
    user_ip = request.remote_addr
    print(user_ip)
    try:
        access_nums = redis_store.get("access_nums_%s" % user_ip)
        print(access_nums)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="错误次数过多，请稍后重试")
    # 从数据库中根据手机号查询数据的数据对象
    try:
        user = User.query.filter_by(account=account).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")
    # 用数据库的密码与用户填写的密码进行对比校验

    if user is None or user.check_password(password) is False:
        # 如果验证失败，记录错误次数，返回信息
        try:
            # 创建redis管道对象，可以一次执行多个语句
            pipeline = redis_store.pipeline()
            pipeline.multi()
            pipeline.incr("access_nums_%s" % user_ip)
            pipeline.expire("access_nums_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
            pipeline.excute()
            # redis_store.incr("access_nums_%s" % user_ip)
            # if access_nums == 4:
            # redis_store.expire("access_nums_%s" % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")

    # 将token与账号保存到redis中,设置有效期
    try:
        redis_store.setex("token_%s" % account, constants.TOKEN_CODE_REDIS_EXPIRES, "token")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存token失败")
    return jsonify(errno=RET.OK, errmsg="登录成功", token="token")
