#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# @TIME  :2020/8/29 0:36
# @Author:Michael.ma

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Menu(db.Model):
    """菜单表"""

    __tablename__ = "tb_menu"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    url = db.Column(db.String(128), nullable=False)
    icon = db.Column(db.String(32))
    visible = db.Column(db.BOOLEAN)
    pid = db.Column(db.Integer)


class Organization(db.Model):
    """机构表"""

    __tablename__ = "tb_organization"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    pid = db.Column(db.Integer)

    def to_dict(self):
        """将对象转换为字典"""
        org_dict = {
            "org_id": self.id,
            "name": self.name,
            "pid": self.pid
        }
        return org_dict


role_menu = db.Table(
    "tb_role_menu",
    db.Column("role_id", db.Integer, db.ForeignKey("tb_role.id"), primary_key=True),
    db.Column("menu_id", db.Integer, db.ForeignKey("tb_menu.id"), primary_key=True),
)


class Role(db.Model):
    """角色表"""

    __tablename__ = "tb_role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey("tb_organization.id"), nullable=False)


# role_user = db.Table(
#     "tb_role_user",
#     db.Column("role_id", db.Integer, db.ForeignKey("tb_role.id"), primary_key=True),
#     db.Column("user_id", db.Integer, db.ForeignKey("tb_user.id"), primary_key=True),
# )


class User(db.Model):
    """用户表
       继承基类，记录注册时间以及最后登录时间
    """

    __tablename__ = "tb_user"

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    login_ip = db.Column(db.String(32))
    login_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    org_id = db.Column(db.Integer, db.ForeignKey("tb_organization.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("tb_role.id"), nullable=False)

    # 加上property装饰器后，会把函数变为属性，属性名即为函数名
    @property
    def password(self):
        """读取属性的函数行为"""
        raise AttributeError("这个属性只能设置，不可读取！")

    # 使用这个装饰器,对应设置属性操作
    @password.setter
    def password(self, val):
        """
        设置属性 user.password = "xxxxx"
        :param val: 原始明文密码
        :return:
        """
        self.password_hash = generate_password_hash(val)

    def check_password(self, password):
        """
        校验登录密码
        :param password: 用户登录时填写的原始密码
        :return: 如果正确返回True,否则返回False
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """将对象转换为字典"""
        user_dict = {
            "user_id": self.id,
            "account": self.account,
            "name": self.name,
            "login_ip": self.login_ip,
            "login_time": self.login_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_dict
