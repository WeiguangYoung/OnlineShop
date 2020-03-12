from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^/catalogs/(?P<catalog_id>\d+)$', views.GoodsListView.as_view()),
    url(r'^/detail/(?P<sku_id>\d+)$', views.GoodsDetailView.as_view()),
    url(r'^/index$', views.GoodsIndexView.as_view()),
    url(r'^/search$', views.GoodsSearchView.as_view()),
    url(r'^/sku$', views.GoodsChangeSkuView.as_view())
]
