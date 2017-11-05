from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'fighters', views.FighterViewSet)
router.register(r'fighters/(?P<slug>[\w-]+)/fights', views.FightViewSet, base_name='fight')


urlpatterns = [
    url(r'^', include(router.urls)),
]
