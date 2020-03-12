from django.db import models


class Catalog(models.Model):
    """
    商品类别
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    name = models.CharField(max_length=10, verbose_name='类别名称')

    class Meta:
        db_table = 'DDSC_GOODS_CATALOG'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Brand(models.Model):
    """
    品牌
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    name = models.CharField(max_length=20, verbose_name='商品名称')
    logo = models.ImageField(verbose_name='Logo图片')
    first_letter = models.CharField(max_length=1, verbose_name='品牌首字母')

    class Meta:
        db_table = 'DDSC_BRAND'
        verbose_name = '品牌'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SPU(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    name = models.CharField(max_length=50, verbose_name='名称')
    sales = models.IntegerField(default=0, verbose_name='商品销量')
    comments = models.IntegerField(default=0, verbose_name='评价数量')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name='品牌')
    catalog = models.ForeignKey(Catalog, on_delete=models.PROTECT, related_name='catalog_goods', verbose_name='商品类别')

    class Meta:
        db_table = 'DDSC_SPU'
        verbose_name = 'SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SPUSaleAttr(models.Model):
    """
    SPU销售属性表
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    SPU_id = models.ForeignKey(SPU, on_delete=models.CASCADE, verbose_name='SPU')
    # sale_attr_value_name = models.CharField(max_length=20, verbose_name='SPU属性值名称')
    # sale_attr_id = models.IntegerField(default=0, verbose_name='SPU销售属性ID')
    sale_attr_name = models.CharField(max_length=20, verbose_name='SPU属性名称')

    class Meta:
        db_table = 'DDSC_SPU_SALE_ATTR'
        verbose_name = 'SPU销售属性'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % (self.sale_attr_name)



class SKU(models.Model):
    """
    SKU
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    name = models.CharField(max_length=50, verbose_name='SKU名称')
    caption = models.CharField(max_length=100, verbose_name='副标题')
    SPU_ID = models.ForeignKey(SPU, on_delete=models.CASCADE, verbose_name='商品')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='进价')
    market_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='市场价')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    comments = models.IntegerField(default=0, verbose_name='评价数')
    is_launched = models.BooleanField(default=True, verbose_name='是否上架销售')
    default_image_url = models.ImageField(verbose_name='默认图片',default=None)
    version = models.IntegerField(default=0,verbose_name="库存版本")
    class Meta:
        db_table = 'DDSC_SKU'
        verbose_name = 'SKU表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.id, self.name)


class SaleAttrValue(models.Model):
    """
    销售属性值表
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    sale_attr_id = models.ForeignKey(SPUSaleAttr, on_delete=models.CASCADE, verbose_name='销售属性')
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='sku')
    sale_attr_value_name = models.CharField(max_length=20, verbose_name='销售属性值名称')

    class Meta:
        db_table = 'DDSC_SALE_ATTR_VALUE'
        verbose_name = '销售属性值'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s - %s' % (self.sale_attr_id, self.sku.name, self.sale_attr_value_name)



class SKUImage(models.Model):
    """
    SKU图片
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    sku_id = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='sku')
    image = models.ImageField(verbose_name='图片路径')

    class Meta:
        db_table = 'DDSC_SKU_IMAGE'
        verbose_name = 'SKU图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.sku_id.name, self.id)


#class SKUSaleAttrValue(models.Model):
    """
    SKU销售属性值表
    """
#    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
#    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
#    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='sku')
#    sale_attr_value_id = models.ForeignKey(SaleAttrValue, on_delete=models.PROTECT, verbose_name='销售属性值')

#    class Meta:
#        db_table = 'DDSC_SKU_SALE_ATTR_VALUE'
#        verbose_name = 'SKU销售属性值表'
#        verbose_name_plural = verbose_name

#    def __str__(self):
#        return '%s' % (self.sku,)


class SPUSpec(models.Model):
    """
    SPU规格表
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    spu = models.ForeignKey(SPU, on_delete=models.CASCADE, verbose_name='SPU')
    spec_name = models.CharField(max_length=20, verbose_name='SPU规格名称')

    class Meta:
        db_table = 'DDSC_SPU_SPEC'
        verbose_name = 'SPU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.spu.name, self.spec_name)


class SKUSpecValue(models.Model):
    """
    SKU规格属性表
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='sku')
    spu_spec = models.ForeignKey(SPUSpec, on_delete=models.CASCADE, verbose_name='SPU规格名称')
    name = models.CharField(max_length=20, verbose_name='SKU规格名称值')

    class Meta:
        db_table = 'DDSC_SKU_SPEC_VALUE'
        verbose_name = 'SKU规格属性值表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s: %s' % (self.sku, self.spu_spec.spec_name, self.name)
