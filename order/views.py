import os
from alipay import AliPay
from django.views import View
from django import http
from django.shortcuts import redirect,HttpResponse
from django_redis import get_redis_connection
from goods.models import SKU, SPU, SPUSaleAttr, SaleAttrValue
import json
from .models import OrderInfo, OrderGoods
from user.models import UserProfile, Address
from django.db import transaction
import datetime
import time
from utils.loging_decorator import logging_check,get_user_by_request
from dadashop.settings import IP_URL,PIC_URL

class OrderProcessingnView(View):
    # 组织数据方法
    def get_address(self,request):
        """
        :param request:
        :return: address_list(地址列表)
        """
        user = get_user_by_request(request)
        addresses = Address.objects.filter(is_alive=True, uid=user)
        addresses_list = []
        for address in addresses:
            if address.default_address == False:
                addresses_list.append({
                    "id": address.id,
                    "name": address.receiver,
                    "mobile": address.receiver_mobile,
                    "title": address.tag,
                    "address": address.address
                })
            else:
                addresses_list.insert(0, {
                    "id": address.id,
                    "name": address.receiver,
                    "mobile": address.receiver_mobile,
                    "title": address.tag,
                    "address": address.address
                })
        return addresses_list

    # 组织数据方法
    def get_cart_dict(self,request):
        """
        :param request:
        :return: cart_list(购物车中的商品)
        """
        user = get_user_by_request(request)
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%d' % user.id)
        cart_dict = {}
        for sku_id, status in redis_cart.items():
            cart_dict[int(sku_id.decode())] = {
                'state': json.loads(status.decode()),
            }
        return cart_dict

    # 组织数据方法
    def get_sku_list(self, sku, cart_dict=None,s_count=None):
        """
        :param sku:
        :param cart_dict:
        :return: sku_sale_attr_names(销售属性名)
        :return: sku_sale_attr_vals(销售属性值)
        :return: count(购买数量)
        """
        sku_sale_attr_names = []
        sku_sale_attr_val = []
        if cart_dict != None:
            selected = int(cart_dict[sku.id]['state']['selected'])
            if selected == 0:
                return None
            s_count = int(cart_dict[sku.id]['state']['count'])

        saleattr_vals = SaleAttrValue.objects.filter(sku_id=sku.id)
        for saleattr_val in saleattr_vals:
            #属性值
            sku_sale_attr_val.append(saleattr_val.sale_attr_value_name)
            saleattrname = SPUSaleAttr.objects.filter(saleattrvalue=saleattr_val)[0]
            #属性名称
            sku_sale_attr_names.append(saleattrname.sale_attr_name)

        # 销售属性名
        # spu = SPU.objects.filter(sku=sku)[0]
        # sku_sale_attr_name = spu.spusaleattr_set.all()
        # for salerattr in sku_sale_attr_name:
        #     sku_sale_attr_names.append(salerattr.sale_attr_name)
        # # sku销售属性
        # sku_sale_attr_val = sku.skusaleattrvalue_set.all()
        # for sale_attr_val in sku_sale_attr_val:
        #     saleattrval = SaleAttrValue.objects.filter(skusaleattrvalue=sale_attr_val)[0]
        #     sku_sale_attr_vals.append(saleattrval.sale_attr_value_name)
        return sku_sale_attr_names, sku_sale_attr_val, s_count

    # 组织数据方法
    def get_order_list(self,skus,cart_dict=None,s_count=None):
        """
        :param skus:
        :param cart_dict:
        :return: sku_list(sku列表)
        :return: total_count(总数量)
        :return: total_amount(总价格)
        :return: payment_amount(实付款)
        """
        sku_list = []
        total_count = 0
        total_amount = 0
        for sku in skus:
            # 判断商品是否为选中状态
            if cart_dict != None:
                if self.get_sku_list(sku, cart_dict) == None:
                    continue
            # 获取sku的销售属性、销售属性值和购买数量.
            sku_sale_attr_names, sku_sale_attr_vals, count = self.get_sku_list(sku, cart_dict,s_count)
            # sku商品入列表准备数据
            print(count)
            sku_list.append({
                'id': sku.id,
                'default_image_url': str(sku.default_image_url),
                'name': sku.name,
                'price': sku.price,
                'count': count,
                'total_amount': sku.price * int(count),
                "sku_sale_attr_names": sku_sale_attr_names,
                "sku_sale_attr_vals": sku_sale_attr_vals,
            })
            # 计算总数量
            total_count += int(count)
            # 计算总金额
            total_amount += sku.price * int(count)
        # 3.运费
        transit = 10
        # 4.实付款(总金额+运费)
        payment_amount = total_amount + transit
        return sku_list,total_count,total_amount,transit,payment_amount
    # 组织订单信息字符串
    def get_order_string(self,order_id,total_amount,sku_goods):
        """
        :param order_id:
        :param total_amount:
        :return: order_string
        """
        trade_name = []
        for sku_good in sku_goods:
            trade_name.append(sku_good.sku.name + "(" + sku_good.sku.caption + ")")
        alipay = AliPay(
            appid="2016100200644279",
            app_notify_url=None,  # 默认回调url-　阿里与商户后台交互
            # 使用的文件读取方式,载入支付秘钥
            app_private_key_path=os.path.join(os.getcwd(), "utils/key_file/s7_private_key.pem"),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            # 使用文件读取的方式,载入支付报公钥
            alipay_public_key_path=os.path.join(os.getcwd(), "utils/key_file/alipay_public_key.pem"),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        # 测试方式此为支付宝沙箱环境
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=int(total_amount),
            subject=("\n".join(trade_name)),
            # 回转url,　支付宝与买家业务处理完毕(支付成功)将玩家重定向到此路由,带着交易的参数返回
            # return_url="http://" + IP_URL + ":8000/v1/orders/success/",
            return_url = "http://127.0.0.1/dadashop/templates/pay_success.html",
            notify_url="http://" + IP_URL + ":8000/v1/orders/success/"  # 可选, 不填则使用默认notify url
        )
        return order_string
    @logging_check
    def get(self, request):
        """
        处理业务确认订单和展示订单
        状态码0 -- 处理确认订单业务
        状态码1 -- 处理展示订单业务
        状态码2 -- 处理确认收货业务
        :param request:
        :return:
        """
        status = int(request.GET.get("status"))
        user = get_user_by_request(request)
        # 确认订单业务
        if status == 0:
            # 1.获取收货地址列表
            addresses_list = self.get_address(request)
            # 2.组织商品数据
            settlement = int(request.GET.get('settlement_type'))
            # 购物车结算
            if settlement == 0:
            # 获取购买购物车商品列表
                cart_dict = self.get_cart_dict(request) #从redis中获取购物车中的商品id
                skus = SKU.objects.filter(id__in=cart_dict.keys())
                # 3.获取商品列表，总数量,总价格,运费,实付款(总价格+运费)
                sku_list, total_count, total_amount, transit, payment_amount = self.get_order_list(skus, cart_dict)
            # 直接购买结算
            elif settlement == 1:
                sku_id = request.GET.get('sku_id')
                count = request.GET.get('buy_num')
                skus = SKU.objects.filter(id=sku_id)
                cart_dict = None
                # 获取商品列表，总数量,总价格,运费,实付款(总价格+运费)
                sku_list, total_count, total_amount, transit, payment_amount = self.get_order_list(skus,cart_dict,count)
            # 3.组织数据
            data = {
                'addresses': addresses_list,
                'sku_list': sku_list,
                'total_count': total_count,
                'total_amount': total_amount,
                'transit': transit,
                'payment_amount': payment_amount
            }
            return http.JsonResponse({'code':200, 'data':data, 'base_url':PIC_URL})
        # 查询用户订单数据
        elif status == 1:
            # 获取状态码为依据返回制定状态的订单.
            order_status = request.GET.get("order_status")
            if order_status == '0':
                order_list = OrderInfo.objects.filter(user=user)
            else:
                order_list = OrderInfo.objects.filter(user=user,status=order_status)
            orders_lists = []
            for order in order_list:
                good_skus = OrderGoods.objects.filter(order=order)
                sku_list = []
                # 1.组织订单中sku数据
                for good_sku in good_skus:
                    sku = good_sku.sku
                    sku_sale_attr_names, sku_sale_attr_vals,_ = self.get_sku_list(sku)
                    sku_list.append({
                        'id': sku.id,
                        'default_image_url': str(sku.default_image_url),
                        'name': sku.name,
                        'price': sku.price,
                        'count': good_sku.count,
                        'total_amount': sku.price * good_sku.count,
                        "sku_sale_attr_names": sku_sale_attr_names,
                        "sku_sale_attr_vals": sku_sale_attr_vals,
                    })
                # 2.组织订单信息
                orders_lists.append({
                    "order_id": order.order_id,
                    "order_total_count": order.total_count,
                    "order_total_amount": order.total_amount,
                    "order_freight": order.freight,
                    "address": {
                        "title": order.address.tag,
                        "address": order.address.address,
                        "mobile": order.address.receiver_mobile,
                        "receiver": order.address.receiver
                    },
                    "status": order.status,
                    "order_sku": sku_list,
                    "order_time": str(order.created_time)[0:19]
                })
            data = {
                'orders_list': orders_lists,
            }
            return http.JsonResponse({"code": 200,"data": data, 'base_url':PIC_URL})
        # 买家确认收货业务
        elif status == 2:
            order_id = request.GET.get("order_id")
            order = OrderInfo.objects.filter(order_id=order_id)[0]
            order.status = 4
            order.save()
            return http.JsonResponse({"code": 200, 'base_url':PIC_URL})
    @logging_check
    def post(self, request):
        """
        处理业务生成订单,跳转订单支付,响应支付成功
        状态码0 -- 生成订单
        状态码1 -- 跳转订单支付
        状态码2 -- 跳转立即购买
        :param request:
        :return:
        """
        status = json.loads(request.body).get("status")
        user = get_user_by_request(request)
        # 处理生成订单业务
        if status == 0:
            address_id = json.loads(request.body).get("address_id")
            settlement_type = json.loads(request.body).get("settlement_type")
            try:
                address = Address.objects.get(id=address_id, is_alive=True)
            except:
                return http.JsonResponse({'code': 50102, 'errmsg': '收货地址无效'})
            now = datetime.datetime.now()
            with transaction.atomic():  # 禁止自动提交
                # 开启事务
                sid = transaction.savepoint()
                # 1.创建订单基本对象
                order_id = '%s%02d' % (now.strftime('%Y%m%d%H%M%S'), user.id)
                total_count = 0
                total_amount = 0
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user_id=user.id,
                    address_id=address_id,
                    total_count=0,
                    total_amount=0,
                    freight=1,
                    pay_method=1,
                    status=1
                )


                # 2.数据库中修改商品的数量
                cart_dict = self.get_cart_dict(request) # 从redis中获取订单商品的信息.
                skus = SKU.objects.filter(id__in=cart_dict.keys())
                # 用以存储购物车中选中的商品,用作订单生成后删除redis中的商品.
                sku_ids = []
                for sku in skus:
                    selected = int(cart_dict[sku.id]['state']['selected'])
                    if selected == 0:
                        continue
                    cart_count = int(cart_dict[sku.id]['state']['count'])
                    sku_ids.append(sku.id)
                    # 判断库存，不足则提示,如果足够则继续执行
                    if sku.stock < cart_count:
                        # 回滚事务
                        transaction.savepoint_rollback(sid)
                        sku_ids.remove(sku.id)
                        # 给出提示
                        return http.JsonResponse({'code': 50103, 'errmsg': '商品[%d]库存不足' % sku.id})
                    # 使用乐观锁进行修改
                    # 使用乐观锁修改商品数量
                    version_old = sku.version
                    result = SKU.objects.filter(pk=sku.id, version=version_old).update(stock=sku.stock - cart_count, sales=sku.sales + cart_count,version=version_old+1)
                    # result表示sql语句修改数据的个数
                    if result == 0:
                        # 库存发生变化，未成功购买
                        transaction.savepoint_rollback(sid)
                        sku_ids.remove(sku.id)
                        return http.JsonResponse({'code': 50104, 'errmsg': '操作太快了,请稍后重试'})
                    # 创建订单商品对象
                    order_sku = OrderGoods.objects.create(
                        order_id=order_id,
                        sku_id=sku.id,
                        count=cart_count,
                        price=sku.price
                    )
                    #　计算总金额、总数量
                    total_count += cart_count
                    total_amount += sku.price * cart_count
                # 5.修改订单对象的总金额、总数量
                order.total_count = total_count
                order.total_amount = total_amount
                order.freight = 10
                order.save()

                # 提交
                transaction.savepoint_commit(sid)

            # 3.从redis中删除所有已经加入了订单的商品
            redis_cli = get_redis_connection('cart')
            for sku_id in sku_ids:
                redis_cli.hdel('cart_%d' % user.id, sku_id)
            # 4.生成支付宝支付链接
            sku_goods = OrderGoods.objects.filter(order=order_id)
            order_string = self.get_order_string(order.order_id,order.total_amount+10,sku_goods)
            # 构建让用户跳转的支付链接
            pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string
            # 5.组织数据
            data = {
                'saller': '达达商城',
                'total_amount': order.total_amount+order.freight,
                'order_id': order_id,
                'pay_url': pay_url
            }
            # 响应
            return http.JsonResponse({'code': 200, 'data': data})
        # 跳转订单支付
        elif status == 1:
            order_id = json.loads(request.body).get("order_id")
            order = OrderInfo.objects.filter(order_id=order_id)[0]
            # 1.生成支付链接
            sku_goods = OrderGoods.objects.filter(order=order_id)
            order_string = self.get_order_string(order.order_id,order.total_amount,sku_goods)
            # 构建让用户跳转的支付链接
            pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string
            # 2.组织数据
            data = {
                'saller': '达达商城',
                'total_amount': order.total_amount+10,
                'order_id': order_id,
                'pay_url': pay_url
            }
            # 响应
            return http.JsonResponse({'code': 200, 'data': data})
            # 立即购买功能
class AlipayResultView(View):
    # 获取参数字典和验签结果
    def get_sdict_ali_verify(self,request,method):
        """
        :param request:
        :param method: 请求方式
        :return: success_dict,ali_verufy,alipay
        """
        success_dict = {}
        if method == 1:
            for key,val in request.GET.items():
                success_dict[key] = val
        if method == 2:
            for key,val in request.POST.items():
                success_dict[key] = val
        # 1.剔除掉sign做验签准备
        sign = success_dict.pop("sign",None)
        # 2.生成alipay对象
        alipay = AliPay(
                appid = "2016100200644279",
                app_notify_url=None,
                app_private_key_path=os.path.join(os.getcwd(), "utils/key_file/s7_private_key.pem"),
                alipay_public_key_path=os.path.join(os.getcwd(), "utils/key_file/alipay_public_key.pem"),
                debug=True
                )
        # 3.使用支付宝接口进行验签
        ali_verify = alipay.verify(success_dict,sign)
        return success_dict,ali_verify,alipay
    # 重定向接口
    def get(self,request):
        # 1.获取参数字典,验签结果,alipay对象
        success_dict,ali_verify,alipay = self.get_sdict_ali_verify(request,1)
        # 2.根据验证结果进行业务处理
        if ali_verify is True:
            order_id = success_dict.get('out_trade_no',None)
            order = OrderInfo.objects.filter(order_id=order_id)[0]
            total_amount = success_dict.get('total_amount', None)
            if order.status == 2:
                data = {
                    "order_id": order_id,
                    "total_amount": total_amount
                }
                return http.JsonResponse({"code": 200, "data": data})
            # 主动查询
            else:
                result = alipay.api_alipay_trade_query(out_trade_no=order_id)
                print("主动查询")
                if result.get("trade_status","") == "TRADE_SUCCESS":
                    order = OrderInfo.objects.filter(order_id=order_id)[0]
                    order.status = 2
                    order.save()
                    data = {
                        "order_id": order_id,
                        "total_amount": total_amount
                    }
                    return http.JsonResponse({"code": 200, "data": data})
                else:
                    data = {
                        "order_id": order_id,
                        "total_amount": total_amount
                    }
                    return http.JsonResponse({"code": 50105, "data": data})
        else:
            return HttpResponse("非法访问")
    # 回调接口
    def post(self,request):
        """
        处理支付宝的付款回调业务
        :param request:
        :return:
        """
        # 1.获取参数字典,验签结果,alipay对象
        success_dict, ali_verify, alipay = self.get_sdict_ali_verify(request, 2)
        # 2.根据验证结果进行业务处理
        if ali_verify is True:
            trade_status = success_dict.get('trade_status',None)
            if trade_status == "TRADE_SUCCESS":
                order_id = success_dict.get('out_trade_no',None)
                order = OrderInfo.objects.filter(order_id=order_id)[0]
                order.status = 2
                order.save()
                return HttpResponse("seccess")
        else:
            return HttpResponse("非法访问")