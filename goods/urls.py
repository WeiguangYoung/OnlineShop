from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^/index$', views.GoodsIndexView.as_view()),

]