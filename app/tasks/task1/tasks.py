# coding:utf-8

from app.tasks.main import celery_app


@celery_app.task
def send_email():
    print("邮件发送成功！")
