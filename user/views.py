import base64
import json
import random

from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import UserProfile

# Create your views here.
from django.views.generic.base import View
from dtoken.views import make_token
import redis

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
        # try:
        #     user = UserProfile.objects.create(username=username,email=email,phone=phone,password=m.hexdigest())
        # except Exception as e:
        #     result = {'code':'10103', 'error': 'The username is existed !'}
        #     return JsonResponse(result)

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
        send_active_mail(email, active_url)
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
























