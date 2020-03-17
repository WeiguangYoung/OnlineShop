# OnlineShop

**云服务地址  106.54.220.88:7000/dadashop/templates/index.html**

**前后端分离django + nginx + uwsgi，前端页面详见static文件夹**



## Requirement

celery==4.3.0

Django==1.11.8

django-cors-headers==3.0.2

django-haystack==2.8.1

django-redis==4.10.0

elasticsearch==2.4.1

elasticstack==0.4.1

haystack==0.42

PyJWT==1.7.1

PyMySQL==0.7.11

python-alipay-sdk==2.0.1

redis==3.2.1

uWSGI==2.0.18





## **部分功能实现**

基于OAuth 2.0授权码协议的微博第三方登录

基于haystack+elasticsearch的商品搜索功能

基于python-alipay-sdk的支付宝第三方支付（沙箱环境 ）

基于celery实现邮件和短信的异步发送（短信使用容联云平台）

基于django-cors-headers实现前端的跨域资源共享CORS

基于JWT生成token进行用户身份验证以及跨平台访问

基于mysql和redis的结合进行缓存的实现和数据的存储





