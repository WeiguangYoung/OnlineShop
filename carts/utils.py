import pickle
import base64
import json
from django_redis import get_redis_connection
from django.http import JsonResponse
#from utils.loging_decorator import logging_check
# from dtoken.views import *


def merge_cart(user,token,cart_data):
    cart_cookie = cart_data
    print(cart_cookie)
    user = user
    #判断如果未登录购物车为空
    if not cart_cookie:
        cart_dict = get_redis_connection('cart')
        cart_len = cart_dict.hlen('cart_%d' % user.id)
        response = {'code': 200, 'username': user.username, 'data': {'token': token.decode(), 'len': cart_len}}
        return JsonResponse(response)

    for c_dic in cart_cookie:
        sku_id= c_dic['id']
        print(sku_id)
        c_count = int(c_dic['count'])
        print(c_count)
        redis_cli = get_redis_connection('cart')
        skuid = redis_cli.hgetall('cart_%d'%user.id)
        print('((()))',skuid)
        if sku_id.encode() in skuid.keys():
            print(skuid.keys())
            print('==========================',sku_id)
            status = redis_cli.hget('cart_%d'%user.id,sku_id)
            count = int(json.loads(status.decode())['count'])
            count = max(c_count,count)
            status = json.dumps({'count':count,'selected':1})
            redis_cli.hset('cart_%d' % user.id, sku_id,status)
            print('合并1完成')
        else:
            status = json.dumps({'count':c_count, 'selected': 1})
            redis_cli.hset('cart_%d' % user.id, sku_id, status)
            print("合并2完成")

    cart_dict = get_redis_connection('cart')
    cart_len = cart_dict.hlen('cart_%d' % user.id)
    response = {'code': 200, 'username': user.username, 'data': {'token': token.decode(),'len':cart_len}}
    # 返回响应对象，最终返回给浏览器
    return JsonResponse(response)



