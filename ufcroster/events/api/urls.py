from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'events', views.EventViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
