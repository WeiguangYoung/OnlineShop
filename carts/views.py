import json

from django.http import JsonResponse
from django.shortcuts import render
# Create your views here.
from django.views import View
from tools.logging_check import logging_check
from django_redis import get_redis_connection
from goods.models import *

class CartView(View):

    def get(self, request, username):

        pass

    @logging_check
    def post(self, request, username):
        #购物车数据  加入到  redis  hashmap
        #key  , hashmap field[sku_id]  value -> count selected
        # {sku_id: {'count':1, 'selected': 1}}
        data = request.body
        json_obj = json.loads(data)
        #{ "sku_id":2,"count":"1"}
        sku_id = json_obj.get('sku_id')
        count = json_obj.get('count')
        if count:
            count = int(count)

        #检查 sku_id
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            print('--cart get sku error ')
            result = {'code':10301,  'error':'Your sku_id is error'}
            return JsonResponse(result)
        #检查库存和添加数量
        if int(count) > sku.stock:
            result = {'code': 10302, 'error': 'Your count is error'}
            return JsonResponse(result)

        user = request.myuser
        uid = user.id
        #生成 redis的 存储key
        cache_key = 'cart_%s'%(uid)

        #第一次存数据
        r = get_redis_connection('carts')
        all_carts = r.hgetall(cache_key)

        if not all_carts:
            #初始化购物车数据 默认添加购物车时， 选中状态为 1 【1-选中 0未选中】
            status = {'count':count,'selected':1}
            r.hset(cache_key, sku_id, json.dumps(status))
        else:
            #redis有这个用户的购物车数据
            cart_sku = r.hget(cache_key, sku_id)
            if not cart_sku:
                #第一次存储该sku商品
                status = {'count': count, 'selected': 1}
                r.hset(cache_key, sku_id, json.dumps(status))
            else:
                #购物车中有此次添加的sku商品
                cart_sku_data = json.loads(cart_sku)
                old_count = cart_sku_data['count']
                new_count = int(old_count) + count
                #检查当前购物车 该sku商品的数量是否已经超过库存
                if new_count > sku.stock:
                    result = {'code':10302, 'error':'The count is error'}
                    return JsonResponse(result)

                status = {'count': new_count, 'selected':1}
                r.hset(cache_key, sku_id, json.dumps(status))

        #购物车 redis数据添加完毕
        #如何返回  全量 or 增量

        #{'sku_id':{'count':1,'select':1} }
        new_all_carts = r.hgetall(cache_key)
        all_carts_sku = SKU.objects.filter(id__in=new_all_carts.keys())
        #filter 查询谓词 查询int型字段  接受 字符 类型
        #get 查询 int型字段  接受字符类型
        #redis返回值中若出现字符类型，均为字节串，在结合redis数据进行 django orm查询时， 查询条件可直接输入，无需转换
        skus_list = []
        for cs in all_carts_sku:
            d = {}
            d['id'] = cs.id
            d['name'] = cs.name
            d['price'] = cs.price
            #ImageField 的值是一个image对象
            d['default_image_url'] = str(cs.default_image_url)
            #{b'1': b'{"count": 1, "selected": 1}'}
            d_j = json.loads(new_all_carts[str(cs.id).encode()])
            d['count'] = d_j['count']
            d['selected'] = d_j['selected']
            #['尺寸', '颜色']
            sku_sale_attr_name = []
            #['15寸', '蓝色']
            sku_sale_attr_val = []

            sale_attr_vals = SaleAttrValue.objects.filter(sku_id=cs.id)
            for sv in  sale_attr_vals:
                sku_sale_attr_val.append(sv.sale_attr_value_name)
                s_name =  sv.sale_attr_id.sale_attr_name
                sku_sale_attr_name.append(s_name)
            d['sku_sale_attr_val'] = sku_sale_attr_val
            d['sku_sale_attr_name'] = sku_sale_attr_name
            skus_list.append(d)

        return JsonResponse({'code':200, 'data': skus_list})



























































































        pass





