# Create your views here.
import hashlib
import random
import base64
import json

from urllib.parse import unquote
from celery_tasks.user_tasks import send_verify
from .models import UserProfile, Address, WeiboUser
from django_redis import get_redis_connection
from django.views.generic import View
from django.http import JsonResponse
from django.db import transaction
from django.conf import settings
from dtoken.views import make_token
from .weiboapi import OAuthWeibo
from utils.loging_decorator import logging_check,get_username_by_request,get_user_by_request

# Create your views here.


class BaseUserView(View):
    """
    此类是用来公共调用，有两个功能：
    1.获取生成用户地址列表
    2.检查传递的参数
    """
    def get_address_list(self,alladdress):
        """
        对用户的地址进行序列化
        params : 返回所有地址query_set,进行遍历
        return : 地址列表，元素为每一条合法的地址
        """
        addressList = []
        for values in alladdress:
            each_address = {}
            each_address['id'] = values.id
            each_address['address'] = values.address
            each_address['receiver'] = values.receiver
            each_address['receiver_mobile'] = values.receiver_mobile
            each_address['tag'] = values.tag
            each_address['is_default'] = values.default_address
            addressList.append(each_address)
        return addressList

    def check_args(self,data):
        """
        用来检查用户传递的数据。是否为空。
        params : 前端传递的数据，格式为字典。
        return : 返回检查之后的数据
        """
        for key,value in data.items():
            if not value:
                return key
        return data


class ModifyPasswordView(BaseUserView):
    """
    用户登陆状态下 修改密码：
    http://127.0.0.1:8000/v1/user/<username>/password
    """
    @logging_check
    def post(self, request, username):
        """
        :param request:请求对象
        :return:返回修改密码之后的状态，
        """
        data = json.loads(request.body)
        if len(data) != 3:
            return JsonResponse({'code': 10123, 'error': 'Missing parameters'})
        checked_data = self.check_args(data)
        if type(checked_data) == str:
            return JsonResponse({'code': 10123, 'error': 'Missing %s parameters'%checked_data}) 
        oldpassword = data.get('oldpassword')
        password1 = data.get('password1')
        password2 = data.get('password2')
        if oldpassword == password1 or oldpassword == password2:
            return JsonResponse({'code': 10109, 'error': 'Please Use Different Password!'})
        # 判断两次密码是否一致
        if password1 != password2:
            return JsonResponse({'code': 10102, 'error': 'Inconsistent passwords!'})
        try:
            user = UserProfile.objects.get(username=username)
        except Exception as e:
            return JsonResponse({'code': 10104, 'error': 'User query error'})
        real_password = user.password
        m = hashlib.md5()
        m.update(oldpassword.encode())
        if m.hexdigest() != real_password:
            return JsonResponse({'code': 10103, 'error': 'Old password error!'})
        new = hashlib.md5()
        new.update(password1.encode())
        user.password = new.hexdigest()
        user.save()
        return JsonResponse({'code': 200, 'data': 'OK'})


class SendSmsCodeView(BaseUserView):
    """
    用户找回密码视图处理函数：
    分为三步：
    1.验证邮箱，并且发送邮件验证码
    2.验证邮件验证码，
    3.验证码验证成功，修改密码
    """

    def post(self, request):
        data = json.loads(request.body)
        if len(data) != 1:
            return JsonResponse({'code': 10123, 'error':'Missing parameters'})
        check_data = self.check_args(data)
        if type(check_data) == str:
            return JsonResponse({'code': 10123, 'error': 'Missing %s parameters'%checked_data}) 
        # 验证用户是否是已经注册用户
        email = data.get('email')
        try:
            user = UserProfile.objects.get(email=email)
        except Exception as e:
            return JsonResponse({'code': 10104, 'error':'User query error'})
        # 先去查询该用户是否在时效时间内发送过验证码
        redis_conn = get_redis_connection('verify_email')
        try:
            email_code = redis_conn.get('email_code_%s'%email)
        except Exception as e:
            return JsonResponse({'code': 10132, 'error': 'Verify Code Error'})
        if email_code:
            return JsonResponse({'code': 202, 'error': 'please enter your code!'})

        email_code = "%06d" % random.randint(0, 999999)
        try:
            redis_conn.setex("email_code_%s" % email, 10 * 60, email_code)
        except Exception as e:
            return JsonResponse({'code': 10105, 'error': 'Storage authentication code failed'})
        send_verify.delay(email=email, email_code=email_code, sendtype=0)
        return JsonResponse({'code': 200, 'data':'OK'})


class VerifyCodeView(BaseUserView):
    """
    第二步 验证发送邮箱的验证码
    """
    def post(self, request):
        """
        验证用户邮箱验证码
        :param request:
        :param username: 用户名
        :return:
        """
        data = json.loads(request.body)
        if len(data) != 2:
            return JsonResponse({'code': 10123, 'error': 'Missing parameters'})
        checked_data = self.check_args(data)
        if type(checked_data) == str:
            return JsonResponse({'code': 10123, 'error': 'Missing %s parameters'%checked_data}) 
        email = data.get('email')
        code = data.get('code')
        # 验证用户是否匹配
        redis_conn = get_redis_connection('verify_email')
        try:
            email_code = redis_conn.get('email_code_%s' % email)
        except Exception as e:
            return JsonResponse({'code': 10106,'error': 'invalid validation. Resend it.'})
        redis_code = email_code.decode()
        print(redis_code)
        if redis_code == code:
            return JsonResponse({'code': 200, 'data': 'OK', 'email': email})
        return JsonResponse({'code': 10124, 'error':'code is wrong!'})
        

class ModifyPwdView(BaseUserView):
    """
    最后一步验证邮箱，修改密码
    """

    def post(self, request):
        data = json.loads(request.body)
        if len(data) != 3:
            return JsonResponse({'code': 10123, 'error': 'Missing parameters'})
        checked_data = self.check_args(data)
        if type(checked_data) == str:
            return JsonResponse({'code': 10123, 'error': 'Missing %s parameters'%checked_data}) 
        password1 = data.get('password1')
        password2 = data.get('password2')
        email = data.get('email')
        if password1 != password2:
            return JsonResponse({'code': 10110, 'error': 'Password Inconsistencies!'})
        try:
            user = UserProfile.objects.get(email=email)
        except Exception as e:
            return JsonResponse({'code': 10104, 'error': 'User query error!'})
        # 读取旧密码
        new = hashlib.md5()
        new.update(password1.encode())
        user.password = new.hexdigest()
        user.save()
        return JsonResponse({'code': 200, 'data': 'OK'})


class ActiveView(View):
    """
    # 用户发送邮件激活
    # GET http://127.0.0.1:8000/v1/user/active?code=xxxxx&username=xxx
    """
    def get(self, request):
        """
        由于没有设置激活链接的参数的redis中的有效时间。
        在用户激活之后删除redis中缓存的激活链接
        """
        code = request.GET.get('code', None)
        if not code:
            return JsonResponse({'code': 10113, 'error':'Error activating link parameters'})
        # 反解激活验证链接
        verify_code = base64.urlsafe_b64decode(code.encode('utf-8')).decode()
        random_code, username = verify_code.split('/')
        redis_conn = get_redis_connection('verify_email')
        result = redis_conn.get('email_active_%s' % email).decode()
        if not result:
            return JsonResponse({'code': 10112, 'error': 'Link is invalid and resend it!'})
        # 验证前端传来的激活链接和redis中是否一致
        if code != result:
            return JsonResponse({'code': 10112, 'error': 'Link is invalid and resend it!'})
        try:
            user = UserProfile.objects.get(username=username)
        except Exception as e:
            return JsonResponse({'code': 10104, 'error': 'User query error!'})
        user_email = user.email
        # 判断code中的用户信息和数据库中信息是否一致
        if user_email != email:
            return JsonResponse({'code': 10112, 'error': 'Link is invalid and resend it!'})
        user.isActive = True
        user.save()
        redis_conn.delete('email_active_%s'%email)
        return JsonResponse({'code': 200, 'data': 'OK'})


class AddressView(BaseUserView):
    """
    get: 获取用户的绑定的收获地址
    post: 新增用户绑定的收获地址
    delete：实现用户删除地址功能
    put: 实现用户修改地址功能
    """
    @logging_check
    def get(self, request, username):
        """
        返回用户关联的地址页面，以及地址
        :param request:
        :return: addressAdmin.html & addresslist
        """
        try:
            user = UserProfile.objects.get(username=username)
        except Exception as e:
            return JsonResponse({'code': 10104, 'error': 'User query error'})
        # 获取用户的id
        userId = user.id
        # 返回当前用户所有地址，
        try:
            all_address = Address.objects.filter(uid=userId, is_alive=True)
            # 获取用户地址，然后用json的地址返回查询后根据querySet 返回相应的字符串。
        except Address.DoesNotExist as e:
            return JsonResponse({'code': 10114, 'error': 'Error in Address Query!'})
        addressList = self.get_address_list(all_address)
        result = {
            'code': 200,
            'data': {
                'addresslist': addressList
            }
        }
        return JsonResponse(result)

    @logging_check
    def post(self, request, username):
        """
        用来提交保存用户的收获地址
        1.先获取相应的用户，然后根据用户的id来绑定地址
        :param request:
        :return:返回保存后的地址以及地址的id
        """
        data = json.loads(request.body)
        if not data:
            return JsonResponse({'code': 10100, 'error': 'Submit invalid parameters'})
        if len(data) != 5:
            return JsonResponse({'code': 10123, 'error': 'Missing parameters'})
        checked_data = self.check_args(data)
        if type(checked_data) == str:
            return JsonResponse({'code': 10123, 'error': 'Missing %s parameters'%checked_data}) 
        receiver = data.get('receiver')
        address = data.get('address')
        receiver_phone = data.get('receiver_phone')
        postcode = data.get('postcode')
        tag = data.get('tag')
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist as e:
            return JsonResponse({'code': 10104, 'error': 'User query error'})
        # 先查询当前用户有没有保存的地址。
        # 如果有则需要将default_address 设置为False
        # 如果没有则需要default_address 设置为True
        query_address = Address.objects.filter(uid=user.id)
        if not query_address:
            try:
                Address.objects.create(
                    uid=user,
                    receiver=receiver,
                    address=address,
                    default_address=True,
                    receiver_mobile=receiver_phone,
                    is_alive=True,
                    postcode=postcode,
                    tag=tag,
                )
            except Exception as e:
                return JsonResponse({'code': 10120, 'error': 'Address storage exception'})
            try:
                all_address = Address.objects.filter(uid=user, is_alive=True)
            except Exception as e:
                return JsonResponse({'code': 10121, 'error': 'Address storage exception'})
            addressList =self.get_address_list(all_address)
            result = {
                'code': 200,
                'data': {
                    'addresslist': addressList
                }
            }
            return JsonResponse(result)
        else:
            try:
                Address.objects.create(
                    uid=user,
                    receiver=receiver,
                    address=address,
                    default_address=False,
                    receiver_mobile=receiver_phone,
                    is_alive=True,
                    postcode=postcode,
                    tag=tag,
                )
            except Exception as e:
                return JsonResponse({'code': 10120, 'error': 'Address storage exception'})
            try:
                all_address = Address.objects.filter(uid=user, is_alive=True)
            except Exception as e:
                return JsonResponse({'code': 10121, 'error': 'Get address exception'})
            addressList =self.get_address_list(all_address)     
            result = {
                'code': 200,
                'data': {
                    'addresslist': addressList
                }
            }
            return JsonResponse(result)

    @logging_check
    def delete(self, request, username, id=None):
        """
         删除用户的提交的地址
         :param request: 提交的body中为用户的地址的id
         :param username:
         :return: 删除后用户的所有的收货地址
        """
        # 根据用户发来的地址的id来直接删除用户地址
        if not id:
            return JsonResponse({'code': 10122, 'error': 'Get address id error'})
        try:
            address = Address.objects.get(id=id)
        except Address.DoesNotExist as e:
            # 此刻应该写个日志
            return JsonResponse({'code': 10121, 'error': 'Get address exception'})
        address.is_alive = False
        address.save()
        # 获取用户的id，然后根据用户的id来返回用户绑定的所有的未删除的地址
        uid = address.uid
        # 将包含用户的uid的以及用户的可以用的地址删选出来
        try:
            all_address = Address.objects.filter(uid=uid, is_alive=True)
        except Address.DoesNotExist as e:
            return JsonResponse({'code': 10121, 'error': 'Get address exception'})
        addressList = self.get_address_list(all_address)
        result = {
            'code': 200,
            'data': {
                'addresslist': addressList
            }
        }
        return JsonResponse(result)

    @logging_check
    def put(self, request, username, id=None):
        """
        根据用户传递过来的收货地址来修改相应的内容
        :param request: 用户请求的对象
        :param address_id:用户地址id
        :return: 返回修改之后的地址的全部内容
        """
        if not id:
            return JsonResponse({'code': 10122, 'error': 'Get address id error'})
        data = json.loads(request.body)
        if len(data) != 5:
            return JsonResponse({'code': 10123, 'error': 'Error in address modification parameters!'})
        checked_data = self.check_args(data)
        if type(checked_data) == str:
            return JsonResponse({'code': 10123, 'error': 'Missing %s parameters'%checked_data}) 
        address = data.get('address')
        receiver = data.get('receiver')
        tag = data.get('tag')
        receiver_mobile = data.get('receiver_mobile')
        data_id = data.get('id')
        if int(id) != data_id:
            print(type(id),type(data_id))
            return JsonResponse({'code':12345,'error':'ID error'})
        # 1  根据地址的id筛选出那一条记录
        try:
            filter_address = Address.objects.filter(id=id)[0]
        except Exception as e:
            return JsonResponse({'code': 10122, 'error': 'Get address exception!'})
        # 要修改的地址
        # 修改内容：
        filter_address.receiver = receiver
        filter_address.receiver_mobile =receiver_mobile
        filter_address.address = address
        filter_address.tag = tag
        filter_address.save()
        # 将所有的地址都筛选出来，返回
        uid = filter_address.uid
        try:
            all_address = Address.objects.filter(uid=uid, is_alive=True)
        except Address.DoesNotExist as e:
            return JsonResponse({'code': 10121, 'error': 'Get address exception'})
        addressList = self.get_address_list(all_address)
        result = {
            'code': 200,
            'data': {
                'addresslist': addressList
            }
        }
        return JsonResponse(result)


class DefaultAddressView(BaseUserView):
    """
    用来修改默认地址
    """
    @logging_check
    def post(self, request, username):
        """
        用来修改默认地址
        :param request:用户请求对象
        :param address_id:用户修改地址的id
        :return:
        """
        # 先根据address_id 来匹配出用户的id
        # 找到用户的id之后选出所有的用户地址。
        # 在将用户地址id为address_id 设为默认
        data = json.loads(request.body)
        if len(data) != 1:
            return JsonResponse({'code': 10123, 'error':  'Miss parameters!'})
        checked_data = self.check_args(data)
        if type(data) == str:
            return JsonResponse({'code': 10123, 'error': 'Missing %s parameters'%checked_data}) 
        address_id = data.get('id')
        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            return JsonResponse({'code': 10121, 'error': 'Get address exception!'})
        # 用户ID
        uid = address.uid
        user_address = Address.objects.filter(uid=uid, is_alive=True)
        for single_address in user_address:
            if single_address.id == address_id:
                single_address.default_address = True
                single_address.save()
            else:
                single_address.default_address = False
                single_address.save()
        # 返回用户所有地址
        try:
            all_address = Address.objects.filter(uid=uid, is_alive=True)
        except Address.DoesNotExist as e:
            return JsonResponse({'code': 10121, 'error':'Get address exception!'})
        addressList = self.get_address_list(all_address)
        result = {
            'code': 200,
            'data': {
                'addresslist': addressList
            }
        }
        return JsonResponse(result)


class OAuthWeiboUrlView(View):
    def get(self, request):
        """
        用来获取微博第三方登陆的url
        :param request:
        :param username:
        :return:
        """
        try:
            oauth_weibo = OAuthWeibo()
            oauth_weibo_url = oauth_weibo.get_weibo_login_code()
        except Exception as e:
            return JsonResponse({'code': 10124, 'error': 'Cant get weibo login page'})
        return JsonResponse({'code': 200, 'oauth_url': oauth_weibo_url})


class OAuthWeiboView(View):
    def get(self, request):
        """
        获取用户的code,以及用户的token
        :param request:
        :return:
        """
        # 首先获取两个参数code 和state
        code = request.GET.get('code', None)
        if not code:
            return JsonResponse({'code': 10100, 'error':  'Invalid parameters'})
        try:
            oauth_weibo = OAuthWeibo()
        except Exception as e:
            return JsonResponse({'code': 10125, 'error': 'Unable to get weibo token'})
        # 返回用户的绑定信息
        # 信息格式为
        """
        data = {
            # 用户令牌，可以使用此作为用户的凭证
            "access_token": "2.00aJsRWFn2EsVE440573fbeaF8vtaE",
            "remind_in": "157679999",             # 过期时间
            "expires_in": 157679999,
            "uid": "5057766658",
            "isRealName": "true"
        }
        """
        try:
            userInfo = oauth_weibo.get_access_token_uid(code)
        except Exception as e:
            print(e)
            return JsonResponse({'code':10142,'error':'cant reach weibo server'})
        # 将用户weibo的uid传入到前端
        # OAuth 2.0 中授权码模式下 如果错误的请求，响应中会字典中会有error键
        if userInfo.get('error'):
            return JsonResponse({'code':12345,'error':'unable get token'})
        weibo_uid = userInfo.get('uid', None)
        access_token = userInfo.get('access_token', None)
        try:
            weibo_user = WeiboUser.objects.get(uid=uid)
        except Exception as e:
            # 如果查不到相关的token 则说明没用绑定相关的用户
            # 没有绑定微博用户则说明用户表中也没有创建用户信息。此时返回access_token,
            # 并且让跳转到 绑定用户的页面，填充用户信息，提交 绑定微博信息
            if not WeiboUser.objects.filter(uid=weibo_uid):
                WeiboUser.objects.create(access_token=access_token, uid=weibo_uid)
            data = {
                'code': '201',
                'uid': weibo_uid 
            }
            return JsonResponse(data)
        else:
            # 如果查询到相关用户绑定的uid
            # 此时正常登陆。然后返回jwt_token
            user_id = weibo_user.uid
            str_user_id = str(user_id)
            try:
                user = UserProfile.objects.get(id=int(str_user_id))
            except Exception as e:
                return JsonResponse({'code':10134,'error':'Cant get User'})
            username = user.username
            token = make_token(username)
            result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
            return JsonResponse(result)

    def post(self, request):
        """
        此时用户提交了关于个人信息以及uid
        创建用户，并且创建绑定微博关系
        :param requset:
        :return:
        """
        data = json.loads(request.body)
        uid = data.get('uid', None)
        username = data.get('username', None)
        password = data.get('password', None)
        phone = data.get('phone', None)
        email = data.get('email', None)
        if not username:
            return JsonResponse({'code': 201, 'error': 'Invalid username!'})
        if not password:
            return JsonResponse({'code': 10108, 'error': 'Invalid password!'})
        if not email:
            return JsonResponse({'code': 10126, 'error': 'Invalid email'})
        if not phone:
            return JsonResponse({'code': 10117, 'error': 'Invalid phone number!'})
        if not uid:
            return JsonResponse({'code': 10130, 'error': 'Invalid access token!'})
        # 创建用户表
        m = hashlib.md5()
        m.update(password.encode())
        # 创建用户以及微博用户表
        try:
            with transaction.atomic():
                user = UserProfile.objects.create(username=username, password=m.hexdigest(),
                                       email=email, phone=phone)
                weibo_user = WeiboUser.objects.get(uid=uid) 
                weibo_user.username = user
                weibo_user.save()
        except Exception as e:
            return JsonResponse({'code': 10128, 'error':'create user failed!'})
        # 创建成功返回用户信息
        token = make_token(username)
        result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
        return JsonResponse(result)


class Users(BaseUserView):
    def get(self, request, username=None):
        pass

    def post(self, request):
        """
        Cautions： verify_url :此处发送前端的地址。
        """
        data = json.loads(request.body)
        if len(data) != 4:
            return JsonResponse({'code': 10123, 'error':  'Miss parameters!'})
        checked_data = self.check_args(data)  
        if type(checked_data) == str:
            return JsonResponse({'code': 10123, 'error':  'Missing %s parameters'%checked_data}) 
        username = data.get('uname')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        # 优先查询当前用户名是否已存在
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 206, 'error': 'Your username is already existed'}
            return JsonResponse(result)
        m = hashlib.md5()
        m.update(password.encode())
        try:
            UserProfile.objects.create(username=username, password=m.hexdigest(),
                                       email=email, phone=phone)
        except Exception as e:
            return JsonResponse({'code': 208, 'error': 'Server is busy'})
        # 发送用户激活链接
        # 此链接是通过用户名和邮箱中间拼接了/
        code = "%d" % random.randint(1000, 9999)
        code_str = code + '/' + username
        # 生成激活链接：
        active_code = base64.urlsafe_b64encode(code_str.encode(encoding='utf-8')).decode('utf-8')
        redis_conn = get_redis_connection('verify_email')
        # TODO : 用户激活链接永久有效，可以根据自己的喜好去设置。
        redis_conn.set("email_active_%s" % email, active_code)
        verify_url = settings.ACTIVE_HOST + '/html/templates/active.html?code=%s' % (active_code)
        token = make_token(username)
        result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
        send_verify.delay(email=email, verify_url=verify_url, sendtype=1)
        return JsonResponse(result)


class SmScodeView(View):
    """
    实现短信验证码功能
    """
    def post(self, request):
        """
        短信测试：
        :param request:
        :return:
        """
        data = json.loads(request.body)
        if not data:
            return JsonResponse({'code': 10131, 'error':'Invalid phone number!'})
        phone = data.get('phone', None)
        code = "%06d" % random.randint(0, 999999)
        try:
            redis_conn = get_redis_connection('verify_email')
            redis_conn.setex("sms_code_%s" % phone, 3 * 60, code)
        except Exception as e:
            return JsonResponse({'code': 10105, 'error': 'Storage authentication code failed'})
        send_verify.delay(phone=phone, code=code, sendtype=2)
        return JsonResponse({'code': 200, 'data': 'OK'})