# -*- coding:utf-8 -*-
from celery_tasks.main import celery_app
from django.core.mail import send_mail
from django.conf import settings
from utils.SendTemplateSMS import send_template_SMS


@celery_app.task(name='send_verify')
def send_verify(email=None, code=None, email_code=None, phone=None, verify_url=None, sendtype=None):
    """
    发送邮件
    :param receiver : 收件人，code 邮箱验证码
    :return:None
    发送类型为0：  则发送邮箱验证码。
    发送类型为1：  则发送邮箱激活链接
    发送类型为2：  则发送短信验证码
    """
    if sendtype == 0:
        # 发送
        subject = '达达商城密码找回邮件'
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>欢迎注册使用达达商城。</p>' \
                       '<p>您的邮箱为：%s，您的邮箱验证码为：</p>' \
                       '<b>%s</b><p>10分钟之内有效。</p>' % (email, email_code)
        send_mail(subject, '', settings.EMAIL_FROM, [email], html_message=html_message)
    elif sendtype == 1:
        # 发送邮箱激活链接
        subject = '达达商城激活邮件'
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>欢迎注册使用达达商城。</p>' \
                       '<p>您的邮箱为：%s，请点击此链接激活您的邮箱(30分钟有效)：</p>' \
                       '<p><a href="%s" target="_blank"><b>请点击激活</b></a></p>' % (email, verify_url)
        send_mail(subject, '', settings.EMAIL_FROM, [email], html_message=html_message)
    elif sendtype == 2:
        # 发送短信验证码
        try:
            send_template_SMS(phone, {3, code}, 1)
        except Exception as e:
            print(e)