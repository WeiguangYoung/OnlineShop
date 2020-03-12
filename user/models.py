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








