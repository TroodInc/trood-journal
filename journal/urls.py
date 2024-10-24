# encoding: utf-8
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from journal.api.views import JournalViewSet, HistoryRecordViewSet

router = routers.DefaultRouter()
router.register(r'journal', JournalViewSet, base_name='journal')
router.register(r'history', HistoryRecordViewSet, base_name='history')

urlpatterns = [
    url(r'^api/v1.0/', include(router.urls, namespace='api')),
]
if settings.DEBUG:
    urlpatterns.append(url(r'^docs/', include_docs_urls(title='Trood Journal')))