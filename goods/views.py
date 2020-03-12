from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from haystack.query import EmptySearchQuerySet
from haystack.forms import  ModelSearchForm
from django_redis import get_redis_connection
import json
from dadashop.settings import PIC_URL

from .models import *



class GoodsIndexView(View):
    def get(self, request):
        """
        首页商品及分类项展示

        商城默认有三个品类：
        名称         id
        拉杆箱        101
        背包         102
        手提包       103
        :param result:
        :return:
        """
        # 127.0.0.1:8000/v1/goods/index
        # 0. 获取所有品类
        catalog_list = Catalog.objects.all()
        # 1. 获取各个catalog下的三条sku数据，首页每个品类下面默认显示三个sku
        index_data = []
        # 从redis中获取所有数据
        redis_conn = get_redis_connection('goods')
        redis_index  = redis_conn.get('index_cache')
        if redis_index is None:
            print("未使用缓存")
            for cata in catalog_list:
                catalog_dic = {}
                catalog_dic["catalog_id"] = cata.id
                catalog_dic["catalog_name"] = cata.name
                # 1.1 获取拉杆箱sku
                spu_ids = SPU.objects.filter(catalog=cata.id).values("id")
                sku_list = SKU.objects.filter(SPU_ID__in=spu_ids, is_launched=True)[:3]
                catalog_dic["sku"] = []
                for sku in sku_list:
                    sku_dict = dict()
                    sku_dict['skuid'] = sku.id
                    sku_dict['caption'] = sku.caption
                    sku_dict['name'] = sku.name
                    sku_dict['price'] = str(sku.price)
                    sku_dict['image'] = str(sku.default_image_url)
                    catalog_dic["sku"].append(sku_dict)
                index_data.append(catalog_dic)
                # 写入缓存
            redis_conn.set("index_cache", json.dumps(index_data))
        else:
            print("使用缓存")
            index_data = json.loads(redis_index)
        result = {"code": 200, "data": index_data, "base_url": PIC_URL}

        return JsonResponse(result)


class GoodsListView(View):
    def get(self, request, catalog_id):
        """
        获取列表页内容
        :param request:
        :param catalog_id: 分类id
        :param page_num: 第几页
        :param page_size: 每页显示多少项
        :return:
        """
        # 127.0.0.1:8000/v1/goods/catalogs/1/?launched=true&page=1
        # 0. 获取url传递参数值
        launched = bool(request.GET.get('launched', True))
        page_num = request.GET.get('page', 1)
        # 1.获取分类下的sku列表
        spu_list_ids = SPU.objects.filter(catalog=catalog_id).values("id")
        sku_list = SKU.objects.filter(SPU_ID__in=spu_list_ids, is_launched=launched).order_by("id")
        # 2.分页
        # 创建分页对象，指定列表、页大小
        page_num = int(page_num)
        page_size = 9
        try:
            paginator = Paginator(sku_list, page_size)
            # 获取指定页码的数据
            page_skus = paginator.page(page_num)
            page_skus_json = []
            for sku in page_skus:
                sku_dict = dict()
                sku_dict['skuid'] = sku.id
                sku_dict['name'] = sku.name
                sku_dict['price'] = str(sku.price)
                sku_dict['image'] = str(sku.default_image_url)
                page_skus_json.append(sku_dict)
        except:
            result = {'code': 40200, 'error': '页数有误，小于0或者大于总页数'}
            return JsonResponse(result)
        result = {'code': 200, 'data': page_skus_json, 'paginator':{'pagesize':page_size, 'total': len(sku_list)}, 'base_url': PIC_URL}
        return JsonResponse(result)


class GoodsDetailView(View):
    def get(self, request, sku_id):
        """
        获取sku详情页信息，获取图片暂未完成
        :param request:
        :param sku_id: sku的id
        :return:
        """
        # 127.0.0.1:8000/v1/goods/detail/401/
        # 1. 获取sku实例
        sku_details = {}
        # 从redis中获取所有数据
        redis_conn = get_redis_connection('goods')
        redis_detail = redis_conn.get('goods_%s' % sku_id)
        if redis_detail is None:
            print("未使用缓存")
            try:
                sku_item = SKU.objects.get(id=sku_id)
            except:
                # 1.1 判断是否有当前sku
                result = {'code': 40300, 'error': "Such sku doesn' exist", }
                return JsonResponse(result)
            sku_catalog = sku_item.SPU_ID.catalog
            sku_details['image'] = str(sku_item.default_image_url)
            sku_details["spu"] = sku_item.SPU_ID.id
            sku_details["name"] = sku_item.name
            sku_details["caption"] = sku_item.caption
            sku_details["price"] = str(sku_item.price)
            sku_details["catalog_id"] = sku_catalog.id
            sku_details["catalog_name"] = sku_catalog.name

            # 详情图片
            sku_image = SKUImage.objects.filter(sku_id=sku_item.id)
            if sku_image:
                sku_details['detail_image'] = str(sku_image[0].image)
            else:
                sku_details['detail_image'] = ""

            # 2. 获取sku销售属性名称和sku销售属性值
            sku_sale_attrs_val_lists = SaleAttrValue.objects.filter(sku=sku_id)
            sku_sale_attr_val_names = [] # 保存sku销售属性值名称的list
            sku_sale_attr_val_id = []
            sku_sale_attr_names = [] # 保存sku销售属性名称的list
            sku_sale_attr_id = []
            sku_all_sale_attr_vals_name = {}
            sku_all_sale_attr_vals_id = {}

            # 传递sku销售属性id和名称  以及  sku销售属性值id和名称
            for sku_sale_attrs_val in sku_sale_attrs_val_lists:
                sku_sale_attr_val_names.append(sku_sale_attrs_val.sale_attr_value_name)
                sku_sale_attr_val_id.append(sku_sale_attrs_val.id)
                sku_sale_attr_names.append(sku_sale_attrs_val.sale_attr_id.sale_attr_name)
                sku_sale_attr_id.append(sku_sale_attrs_val.sale_attr_id.id)
                # 该销售属性下的所有属性值，供·页面选择使用
                # SPU销售属性：颜色，容量
                # 页面显示：
                # 颜色： 红色，蓝色
                # 容量：100ml，200ml
                # 返回数据包含：
                #   1. spu销售属性id，即颜色，容量两个属性的id
                #   2. spu销售属性名称
                #   3. 销售属性值id，即 红色id为1，蓝色id为2，100ml的id为3，200ml的id为4
                #   4. 销售属性值名称
                #   5. sku销售属性值id及名称
                attr = SPUSaleAttr.objects.get(id=sku_sale_attrs_val.sale_attr_id.id)
                sku_all_sale_attr_vals_id[attr.id] = []
                sku_all_sale_attr_vals_name[attr.id] = []
                vals = SaleAttrValue.objects.filter(sale_attr_id=attr.id)
                for val in vals:
                    print("attr.id:", attr.id)
                    print("val.id:", val.id, val.sale_attr_value_name)
                    sku_all_sale_attr_vals_name[int(attr.id)].append(val.sale_attr_value_name)
                    sku_all_sale_attr_vals_id[int(attr.id)].append(val.id)
                    print(sku_all_sale_attr_vals_name,sku_all_sale_attr_vals_id )
            sku_details['sku_sale_attr_id'] = sku_sale_attr_id
            sku_details['sku_sale_attr_names'] = sku_sale_attr_names
            sku_details['sku_sale_attr_val_id'] = sku_sale_attr_val_id
            sku_details['sku_sale_attr_val_names'] = sku_sale_attr_val_names
            sku_details['sku_all_sale_attr_vals_id'] = sku_all_sale_attr_vals_id
            sku_details['sku_all_sale_attr_vals_name'] = sku_all_sale_attr_vals_name

            # sku规格部分
            # 用于存放规格相关数据，格式：{规格名称1: 规格值1, 规格名称2: 规格值2, ...}
            spec = dict()
            sku_spec_values = SKUSpecValue.objects.filter(sku=sku_id)
            if not sku_spec_values:
                sku_details['spec'] = dict()
            else:
                for sku_spec_value in sku_spec_values:
                    spec[sku_spec_value.spu_spec.spec_name] = sku_spec_value.name
                sku_details['spec'] = spec

            # 写入缓存
            redis_conn.setex("goods_%s" % sku_id, 60*60*24, json.dumps(sku_details))
        else:
            print("使用缓存")
            sku_details = json.loads(redis_detail)

        result = {'code': 200, 'data': sku_details, 'base_url': PIC_URL}
        return JsonResponse(result)


# class GoodsSearchView(View):
#     def post(self, request):
#         """
#         首页查询功能
#         :param request:
#         :return:
#         """
#         # 127.0.0.1:8000/v1/goods/search/

#         # 获取分页的页码
#         if request.method == "POST":
#             page_num = int(request.POST.get('page', '1'))
#             page_size = 9
#             search_msg = request.POST.get('searchbox')
#             # 字符串转码
#             spu_query_list = SPU.objects.filter(name__contains=search_msg.encode('utf-8').decode("unicode_escape"))
#             if spu_query_list.count() == 0:
#                 result = {'code': 40202, 'error': '您所查询的商品不存在', }
#                 return JsonResponse(result)
#             sku_list = []
#             for spu_query in spu_query_list:
#                 skus = SKU.objects.filter(SPU_ID=spu_query.id, is_launched=True)[:]
#                 for sku in skus:
#                     sku_list.append(sku)

#             paginator = Paginator(sku_list, page_size)
#             # 2.3获取指定页码的数据
#             page_skus = paginator.page(page_num)
#             page_skus_list = []
#             try:
#                 for sku in page_skus:
#                     sku_dict = dict()
#                     sku_dict['skuid'] = sku.id
#                     sku_dict['name'] = sku.name
#                     sku_dict['price'] = str(sku.price)
#                     sku_image_count = SKUImage.objects.filter(sku_id=sku.id).count()
#                     # 如果该sku没有指定图片，则选取默认图片进行展示
#                     if sku_image_count == 0:
#                         sku_image = str(sku.default_image_url)
#                     else:
#                         sku_image = str(SKUImage.objects.get(sku_id=sku.id).image)
#                     sku_dict['image'] = sku_image
#                     page_skus_list.append(sku_dict)
#                 print(len(page_skus_list))
#             except:
#                 result = {'code': 40200, 'data': '页数有误，小于0或者大于总页数'}
#                 return JsonResponse(result)
#             result = {'code': 200, 'data':  page_skus_list, 'paginator':{'pagesize':page_size, 'total': len(sku_list)}}
#             return JsonResponse(result)


class GoodsSearchView(View):
    def post(self,request, load_all=True, searchqueryset=None):
        """
        首页查询功能
        :param request:
        :return:
        """
        # 127.0.0.1:8000/v1/goods/search/
        from dadashop.settings import HAYSTACK_SEARCH_RESULTS_PER_PAGE
        query = ''
        page_size = HAYSTACK_SEARCH_RESULTS_PER_PAGE
        results = EmptySearchQuerySet()
        if request.POST.get('q'):
            form = ModelSearchForm(request.POST, searchqueryset=searchqueryset, load_all=load_all)
            if form.is_valid():
                query = form.cleaned_data['q']
                results = form.search()
        else:
            form = ModelSearchForm(searchqueryset=searchqueryset, load_all=load_all)

        paginator = Paginator(results, page_size)
        try:
            page = paginator.page(int(request.POST.get('page', 1)))
        except:
            result = {'code': 40200, 'error': '页数有误，小于0或者大于总页数'}
            return JsonResponse(result)

        # 记录查询信息
        context = {
            'form': form,
            'page': page,
            'paginator': paginator,
            'query': query,
        }

        sku_list = []
        # print(len(page.object_list))
        for result in page.object_list:
            sku = {
                'skuid': result.object.id,
                'name': result.object.name,
                'price': result.object.price,
            }
            # 获取图片
            sku_image = str(result.object.default_image_url)
            sku['image'] = sku_image
            sku_list.append(sku)
        result = {"code": 200, "data": sku_list, 'paginator': {'pagesize': page_size, 'total': len(results)}, 'base_url': PIC_URL}
        return JsonResponse(result)


class GoodsChangeSkuView(View):
    def post(self, request):
        data = json.loads(request.body)
        # 将前端传来的销售属性值id放入列表
        sku_vals = []
        result = {}
        for k in data:
            if 'spuid' != k:
                sku_vals.append(data[k])
        sku_list = SKU.objects.filter(SPU_ID=data['spuid'])

        for sku in sku_list:
            sku_details = dict()
            sku_details['sku_id'] = sku.id
            # 获取sku销售属性值id
            sale_attrs_val_lists = SaleAttrValue.objects.filter(sku=sku.id)
            sale_attr_val_id = []

            for sale_attrs_val in sale_attrs_val_lists:
                sale_attr_val_id.append(sale_attrs_val.id)

            if sku_vals == sale_attr_val_id:
                result = {"code": 200, "data": sku.id,}
        if len(result) == 0:
            result = {"code": 40050, "error": "no such sku",}
        return JsonResponse(result)


