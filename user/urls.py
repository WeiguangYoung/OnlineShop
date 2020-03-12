from django.conf.urls import url
from . import views


urlpatterns = [
    #http://127.0.0.1:8000/v1/users
    #url(r'^$', views.users)
    url(r'^$', views.Users.as_view()),
    #http://127.0.0.1:8000/v1/users/activation?code=eGlhb25hbzZfMzEyNQ==
    url(r'^/activation$', views.users_active),
    #http://127.0.0.1:8000/v1/users/xiaonao9/address/0
    url(r'^/(?P<username>\w+)/address/(?P<id>\d+)$', views.AddressView.as_view()),
    #用于前端获取 微博登录地址
    url(r'^/weibo/authorization$', views.OAuthWeiboUrlView.as_view())




]

# v1/tokens  POST  创建token - 登录
# v1/authorization  POST 创建校验- 登录









