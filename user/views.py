import base64
import json
import random
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import UserProfile, WeiboUser

# Create your views here.
from django.views.generic.base import View
from dtoken.views import make_token
import redis
from .tasks import send_active_email
from tools.logging_check import logging_check
from .models import Address

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

def users(request):
    #FBV
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
    elif request.method == 'DELETE':
        pass

    return HttpResponse('--user test is ok ')

class Users(View):
    #CBV class base view
    def get(self, request):

        return JsonResponse({'code':200})
        #return HttpResponse(json.dumps({'code':200}))

    def post(self, request):
        #request.POST只能获取post表单提交数据
        #print(dict(request.POST))
        #request.body 能获取除 表单提交的其他数据
        #print(request.body)

        data = request.body
        if not data:
            result = {'code':'10101', 'error':{'message':'Please give me data'}}
            return JsonResponse(result)
        #data 字节串, json.loads是否报错
        #python 3.6.x 不报错  3.5.x版本建议decode
        json_obj = json.loads(data)
        username = json_obj.get('uname')
        email = json_obj.get('email')
        phone = json_obj.get('phone')
        password = json_obj.get('password')

        # 检查用户名是否可用
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code':'10102', 'error':'The username is existed !'}
            return JsonResponse(result)
        #生成密码哈希
        import hashlib
        m = hashlib.md5()
        m.update(password.encode())
        #创建用户
        try:
            user = UserProfile.objects.create(username=username,email=email,phone=phone,password=m.hexdigest())
        except Exception as e:
            result = {'code':'10103', 'error': 'The username is existed !'}
            return JsonResponse(result)

        #生成token
        #签发token - 官方jwt.encode()
        #{'code':200, 'username':'xxxx', 'data':{'token':xxxx}}
        token = make_token(username)
        #TODO 发激活邮件
        random_int = random.randint(1000, 9999)
        code_str = username + '_' + str(random_int)
        code_str_bs = base64.urlsafe_b64encode(code_str.encode())
        #将随机码组合 存储到redis中 可以扩展成只存储1-3天
        r.set('email_active_%s'%(username), code_str)
        active_url = 'http://127.0.0.1:7000/dadashop/templates/active.html?code=%s'%(code_str_bs.decode())
        #TODO 发邮件?
        #同步执行
        #send_active_mail(email, active_url)
        #celery异步执行
        send_active_email.delay(email, active_url)

        return JsonResponse({'code':200, 'username':username, 'data':{'token':token.decode()}})

    def delete(self, request):
        pass


def send_active_mail(email, code_url):

    subject = '达达商城用户激活邮件'
    html_message = '''
    <p>尊敬的用户 您好</p>
    <p>激活url为<a href='%s' target='blank'>点击激活</a></p>
    '''%(code_url)
    send_mail(subject, '' , '572708691@qq.com', html_message=html_message ,recipient_list=[email])


def users_active(request):
    #激活用户
    if request.method != 'GET':
        result = {'code':10104, 'error':{'message':'Please use GET !!'}}
        return JsonResponse(result)
    code = request.GET.get('code')
    if not code:
        pass
    #解析code
    try:
        code_str = base64.urlsafe_b64decode(code.encode())
        #username_9999
        new_code_str = code_str.decode()
        username, rcode = new_code_str.split('_')
    except Exception as e:
        print(e)
        result = {'code': 10105, 'error':{'message':'Your code is wrong !'}}
        return JsonResponse(result)
    old_data = r.get('email_active_%s'%(username))
    if not old_data:
        result = {'code':10106, 'error':{'message':'Your code is wrong !'}}
        return JsonResponse(result)
    if code_str != old_data:
        result = {'code':10107, 'error':{'message':'Your code is wrong !!'}}
        return JsonResponse(result)
    #激活用户
    users = UserProfile.objects.filter(username=username)
    if not users:
        pass
    user = users[0]
    user.isAcitve = True
    user.save()

    #删除redis数据
    r.delete('email_active_%s'%(username))
    result = {'code':200, 'data':{'message':'激活成功'}}
    return JsonResponse(result)


class AddressView(View):

    @logging_check
    def get(self, request, username, id):
        #获取地址
        user = request.myuser
        addressList = []
        all_add = Address.objects.filter(uid=user)
        for add in all_add:
            d = {'id':add.id,'address':add.address,'postcode': add.postcode, 'receiver_mobile':add.receiver_mobile,'receiver':add.receiver,'is_default':add.isDefault,'tag':add.tag}
            addressList.append(d)

        result = {'code':200, 'data': {'addresslist': addressList}}
        return JsonResponse(result)


    @logging_check
    def post(self, request, username, id):
        #创建新地址

        if username != request.myuser.username:
            #请求不合法
            result = {'code': 10110, 'error':{'message':'The request is illegal !'}}
            return JsonResponse(result)
        data = request.body
        json_obj = json.loads(data)
        # {"receiver":"郭小闹","address":"北京市北京市市辖区东城区海淀","receiver_phone":"13488873110","postcode":"123456","tag":"家"}
        receiver = json_obj.get('receiver')
        address = json_obj.get('address')
        receiver_phone = json_obj.get('receiver_phone')
        postcode = json_obj.get('postcode')
        tag = json_obj.get('tag')

        user = request.myuser
        #如果是第一次添加数据 则把当前数据设置为默认地址
        old_address = Address.objects.filter(uid=user)
        isDefault = False
        if not old_address:
            isDefault = True
            #此次为第一次添加地址
        Address.objects.create(receiver=receiver,address=address,tag=tag,isDefault=isDefault,receiver_mobile=receiver_phone,postcode=postcode,uid=user)

        #addressList
        addressList = []
        all_add = Address.objects.filter(uid=user)
        for add in all_add:
            d = {'id':add.id,'address':add.address,'postcode': add.postcode, 'receiver_mobile':add.receiver_mobile,'receiver':add.receiver,'is_default':add.isDefault,'tag':add.tag}
            addressList.append(d)

        result = {'code':200, 'data': {'addresslist': addressList}}
        return JsonResponse(result)


class OAuthWeiboUrlView(View):

    def get(self, request):
        #获取登录地址
        url = get_weibo_login_url()
        return JsonResponse({'code':200, 'oauth_url': url})


class OAuthWeiboView(View):

    def get(self,request):
        #获取前端传来的 微博code
        code = request.GET.get('code')
        #向微博服务器发送请求 用code换取token
        #websocket
        try:
            user_info = get_access_token(code)
        except Exception as e:
            print('----get_access_token error')
            print(e)
            result = {'code':202, 'error': {'message': 'Weibo server is busy ~'}}
            return JsonResponse(result)

        #微博用户id
        wuid = user_info.get('uid')
        access_token = user_info.get('access_token')

        #查寻weibo用户表，判断是否是第一次光临
        try:
            weibo_user = WeiboUser.objects.get(wuid=wuid)
        except Exception as e:
            print('weibouser get error')
            #该用户第一次用微博登录
            #创建数据 & 暂时不绑定UserProfile
            WeiboUser.objects.create(access_token=access_token, wuid=wuid)
            data = {'code':'201', 'uid': wuid}
            return JsonResponse(data)
        else:
            #该用户非第一次微博登录
            #检查是否进行过绑定
            uid = weibo_user.uid
            if uid:
                #之前绑定过，则认为当前为正常登陆，签发token
                username = uid.username
                token = make_token(username)
                result = {'code':200, 'username':username, 'data': {'token':token.decode()}}
                return JsonResponse(result)
            else:
                #之前微博登陆过，但是没有执行微博绑定注册
                data = {'code': '201', 'uid': wuid}
                return JsonResponse(data)

        return JsonResponse({'code':200, 'error':'test'})

    def post(self,  request):
        #绑定注册
        #json 前端将weiboid 命名为uid POST 过来
        #返回值 跟 正常注册一样
        data = json.loads(request.body)
        #获取微博的用户id
        uid = data.get('uid')
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        #TODO 检查参数 是否存在
        import hashlib
        m = hashlib.md5()
        m.update(password.encode())
        password_m = m.hexdigest()

        try:
            #注册用户  事务
            with transaction.atomic():
                user = UserProfile.objects.create(username=username,phone=phone,email=email,password=password_m)
                weibo_user = WeiboUser.objects.get(wuid=uid)
                #绑定外键
                #用类属性uid 赋值
                weibo_user.uid = user
                #用数据库字段赋值
                #weibo_user.uid_id = user.id
                weibo_user.save()

        except Exception as e:
            print('---weibo register error---')
            print(e)
            return JsonResponse({'code':10115, 'error':{'message':'The username is existed !'}})

        #签发token
        #TODO 发邮件？
        token = make_token(username)
        result = {'code':200, 'username':username, 'data':{'token':token.decode()}}
        return JsonResponse(result)






















        return JsonResponse({'code':200})









def get_access_token(code):
    #向资源授权平台 换取token
    token_url = 'https://api.weibo.com/oauth2/access_token'
    post_data = {
        'client_id': settings.WEIBO_CLIENT_ID,
        'client_secret': settings.WEIBO_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.WEIBO_REDIRECT_URI,
        'code':code
    }
    try:
        #向微博服务器发送post请求
        res = requests.post(token_url, data=post_data)
    except Exception as e:
        print('--weibo request error ')
        print(e)
        raise
    if res.status_code == 200:
        return json.loads(res.text)
    raise









def get_weibo_login_url():
    #response_type - code  代表启用授权码模式
    #scope 授权范围
    params = {'response_type': 'code' , 'client_id': settings.WEIBO_CLIENT_ID, 'redirect_uri': settings.WEIBO_REDIRECT_URI,'scope':''}
    weibo_url = 'https://api.weibo.com/oauth2/authorize?'
    url = weibo_url + urlencode(params)
    return url


































































































