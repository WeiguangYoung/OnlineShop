# -*- coding:utf-8 -*-
from django.db import models
from utils.models import BaseModel


# Create your models here.



class Address(BaseModel):
    """
    用户收货地址表：
    uid: 用户ID
    receiver: 收件人
    address: 用户地址
    default_address:是否为默认地址
    is_alive: 地址是否删除，如果地址被用户删除的话，则为False，有效的地址为True
    postcode：邮政编码
    receiver_mobile: 收件人的联系电话
    tag: 地址标签 例如：家 公司等
    """
    uid = models.ForeignKey('UserProfile', verbose_name=u'用户id',
                            related_name='address')
    receiver = models.CharField(verbose_name=u'收件人', max_length=10)
    address = models.CharField(max_length=100, verbose_name='用户地址')
    default_address = models.BooleanField(verbose_name=u'默认地址',default=False)
    # 是否用户已经删除这条地址，如果删除地址改为False，如果没删除则为True
    is_alive = models.BooleanField(verbose_name=u'是否删除', default=True)
    postcode = models.CharField(verbose_name=u'邮政编码', max_length=7)
    receiver_mobile = models.CharField(verbose_name=u'电话', max_length=11)
    tag = models.CharField(verbose_name=u'标签', max_length=10, default=None)

    class Meta:
        db_table = 'address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s,%s,%s,%s,%s,%s" % (
        str(self.id), self.receiver, self.address, self.default_address, self.postcode, self.receiver_mobile)


# Create your models here.
class UserProfile(BaseModel):
    username = models.CharField(max_length=11, verbose_name='用户名', unique=True)
    password = models.CharField(max_length=32)
    email = models.CharField(max_length=50, verbose_name='邮箱')
    phone = models.CharField(max_length=11, verbose_name='手机')
    isActive = models.BooleanField(default=False, verbose_name='激活状态')

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return str(self.id)

class WeiboUser(BaseModel):
    """
    用户微博表：
    uid: 外健关联用户表，为用户的ID
    weibo_token:调用微博API，返回用户的唯一令牌。即下面的access_token
    {
        # 用户令牌，可以使用此作为用户的凭证
        "access_token": "2.00aJsRWFn2EsVE440573fbeaF8vtaE",
        "remind_in": "157679999",             # 过期时间
        "expires_in": 157679999,
        "uid": "5057766658",
        "isRealName": "true"
    }
    """
    username = models.OneToOneField(UserProfile, verbose_name=u'用户id', null=True)
    uid = models.CharField(verbose_name=u'微博uid', max_length=10, db_index=True, unique=True)
    access_token = models.CharField(verbose_name=u'微博授权密钥', max_length=32, db_index=True)

    class Meta:
        db_table = 'weibouser'
        verbose_name = '微博用户表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.weibo_id