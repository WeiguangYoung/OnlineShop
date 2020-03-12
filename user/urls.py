from django.conf.urls import url
from . import views


urlpatterns = [
    #http://127.0.0.1:8000/v1/users
    #url(r'^$', views.users)
    url(r'^$', views.Users.as_view())

]

# v1/tokens  POST  创建token - 登录
# v1/authorization  POST 创建校验- 登录









