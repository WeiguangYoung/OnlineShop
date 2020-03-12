from django.db import models

# Create your models here.
class UserProfile(models.Model):

    username = models.CharField(max_length=11, verbose_name='用户名', unique=True)
    password = models.CharField(max_length=32, verbose_name='密码')
    email = models.EmailField()
    isAcitve = models.BooleanField(default=False,verbose_name='是否激活')
    #创建时间
    created_time = models.DateTimeField(auto_now_add=True)
    #修改时间
    updated_time = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=11,verbose_name='手机号', default='')

    class Meta:
        db_table = 'user_profile'


    def __str__(self):
        return 'id:%s username:%s'%(self.id, self.username)


class Address(models.Model):

    receiver = models.CharField(max_length=20, verbose_name='收件人')
    address = models.CharField(max_length=100,verbose_name='收件地址')
    isDefault = models.BooleanField(default=False,verbose_name='是否为默认地址')
    postcode = models.CharField(max_length=6, verbose_name='邮编')
    receiver_mobile = models.CharField(max_length=11,verbose_name='联系人电话')
    tag = models.CharField(max_length=10, verbose_name='标签')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    uid = models.ForeignKey(UserProfile)


    class Meta:
        db_table = 'address'

    def __str__(self):

        return '%s_%s_%s_%s'%(self.id, self.receiver, self.address, self.receiver_mobile)



class WeiboUser(models.Model):
    #微博用户表
    uid = models.OneToOneField(UserProfile, null=True)
    wuid = models.CharField(max_length=50, db_index=True, verbose_name='微博用户id')
    access_token = models.CharField(max_length=100, verbose_name='授权令牌')

    class Meta:
        db_table = 'weibo_user'

    def __str__(self):

        return '%s_%s' %(self.wuid, self.uid)























































