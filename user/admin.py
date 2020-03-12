from django.contrib import admin

# Register your models here.
from .models import UserProfile,Address,WeiboUser
admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(WeiboUser)