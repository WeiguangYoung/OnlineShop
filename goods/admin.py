from django.contrib import admin
from .models import *
from django_redis import get_redis_connection


redis_conn = get_redis_connection("goods")


class BaseModel(admin.ModelAdmin):
    """
    继承admin.ModelAdmin
    重写save_model / delete_model 方法
    """
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 删除首页缓存
        redis_conn.delete('index_cache')
        print("保存数据时，首页缓存删除")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # 删除首页缓存
        redis_conn.delete('index_cache')
        print("删除数据时，首页缓存删除")


@admin.register(Brand)
class BrandAdmin(BaseModel):
    list_display = ['id', 'name']

    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20

    # ordering设置默认排序字段，创建时间降序排序
    ordering = ('create_time',)


@admin.register(Catalog)
class CatalogAdmin(BaseModel):
    list_display = ['id', 'name']

    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20

    # ordering设置默认排序字段，创建时间降序排序
    ordering = ('create_time',)


@admin.register(SPU)
class SPUAdmin(BaseModel):

    list_display = ['id', 'name', 'catalog']

    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20

    # ordering设置默认排序字段，创建时间降序排序
    ordering = ('create_time',)

    # fk_fields 设置显示外键字段
    fk_fields = ('catalog',)

    search_fields = ('name', )  # 搜索字段


@admin.register(SPUSaleAttr)
class SPUSaleAttrAdmin(BaseModel):

    list_display = ['id', 'SPU_id', 'sale_attr_name']

    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20

    # ordering设置默认排序字段，创建时间降序排序
    ordering = ('create_time',)

    # fk_fields 设置显示外键字段
    fk_fields = ('SPU_id',)

    search_fields = ('sale_attr_name',)  # 搜索字段


@admin.register(SKU)
class SKUAdmin(BaseModel):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        redis_conn.delete('index_cache')
        redis_conn.delete("goods_%s" % obj.id)
        print("保存数据时，首页缓存删除，详情页缓存删除")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # 删除首页缓存
        redis_conn.delete('index_cache')
        redis_conn.delete("goods_%s" % obj.id)
        print("保存数据时，首页缓存删除，详情页缓存删除")

    list_display = ['id', 'name', 'SPU_ID', 'is_launched',]
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20

    # ordering设置默认排序字段，创建时间降序排序
    ordering = ('create_time',)

    # fk_fields 设置显示外键字段
    fk_fields = ('SPU_id',)

    search_fields = ('name',)  # 搜索字段


@admin.register(SaleAttrValue)
class SaleAttrValueAdmin(BaseModel):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 删除详情页缓存
        redis_conn.delete("goods_%s" % obj.sku.id)
        print("sku.id", obj.sku.id)
        print("保存数据时，详情页缓存清除")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # 删除详情页缓存
        redis_conn.delete("goods_%s" % obj.sku.id)
        print("保存数据时，详情页缓存清除")

    list_display = ['id', 'sku', 'sale_attr_value_name', 'sale_attr_id',]
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20

    # ordering设置默认排序字段，创建时间降序排序
    ordering = ('create_time',)

    # fk_fields 设置显示外键字段
    fk_fields = ('sale_attr_id', 'sku')

    search_fields = ('sale_attr_value_name',)  # 搜索字段

@admin.register(SKUImage)
class SKUImageAdmin(BaseModel):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 删除详情页缓存
        redis_conn.delete("goods_%s" % obj.sku_id.id)
        print("sku.id", obj.sku_id.id)
        print("保存数据时，详情页缓存清除")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # 删除详情页缓存
        redis_conn.delete("goods_%s" % obj.sku_id.id)
        print("保存数据时，详情页缓存清除")

    list_display = ['id', 'sku_id', 'image',]
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20

    # ordering设置默认排序字段，创建时间降序排序
    ordering = ('create_time',)

    # fk_fields 设置显示外键字段
    fk_fields = ('sku_id',)


@admin.register(SPUSpec)
class SPUSpecAdmin(BaseModel):

    list_display = ['id', 'spu', 'spec_name']

    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20

    # ordering设置默认排序字段，创建时间降序排序
    ordering = ('create_time',)

    # fk_fields 设置显示外键字段
    fk_fields = ('spu',)

    search_fields = ('spec_name',)  # 搜索字段


@admin.register(SKUSpecValue)
class SKUSpecValueAdmin(BaseModel):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 删除详情页缓存
        redis_conn.delete("goods_%s" % obj.sku.id)
        print("sku.id", obj.sku.id)
        print("保存数据时，详情页缓存清除")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # 删除详情页缓存
        redis_conn.delete("goods_%s" % obj.sku.id)
        print("保存数据时，详情页缓存清除")

    list_display = ['id', 'sku', 'spu_spec', 'name']

    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20

    # ordering设置默认排序字段，创建时间降序排序
    ordering = ('create_time',)

    # fk_fields 设置显示外键字段
    fk_fields = ('sku', 'spu_spec')

    search_fields = ('spec_name',)  # 搜索字段
