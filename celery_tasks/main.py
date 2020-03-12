# -*- coding:utf-8 -*-
import os
from celery import Celery

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'dadashop.settings'


celery_app = Celery('dadashop')
# 导入celery配置
celery_app.config_from_object('dadashop.settings')
# 自动注册celery任务
celery_app.autodiscover_tasks(['celery_tasks.user_tasks'])

# celery 启动命令

# celery -A celery_tasks.main worker -l info
