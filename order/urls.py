from django.conf.urls import url
from . import views

urlpatterns = [
    url('^/processing/$', views.OrderProcessingnView.as_view()),
    url('^/success/$',views.AlipayResultView.as_view())
]