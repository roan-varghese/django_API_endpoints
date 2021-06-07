from django.urls import path
from api.views import APIOneView, APITwoView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('1', APIOneView, basename='APIOne')
router.register('2', APITwoView, basename='APITwo')

urlpatterns = router.urls
